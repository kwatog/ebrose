from datetime import timedelta
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import check_business_case_access, get_current_user, now_utc
from ..database import get_db
from .goods_receipts import get_accessible_gr_ids
from .purchase_orders import get_accessible_po_ids
from .resources import get_accessible_resource_ids

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_user_group_ids(db: Session, user_id: int) -> List[int]:
    memberships = db.query(models.UserGroupMembership).filter(
        models.UserGroupMembership.user_id == user_id
    ).all()
    return [membership.group_id for membership in memberships]


def get_accessible_budget_ids(db: Session, user: models.User) -> Optional[List[int]]:
    if user.role in ["Admin", "Manager"]:
        return None

    user_group_ids = get_user_group_ids(db, user.id)

    accessible_ids_query = db.query(models.BudgetItem.id).filter(
        (models.BudgetItem.owner_group_id.in_(user_group_ids)) |
        (models.BudgetItem.created_by == user.id)
    )

    explicit_user_access = db.query(models.RecordAccess.record_id).filter(
        models.RecordAccess.record_type == "BudgetItem",
        models.RecordAccess.user_id == user.id,
        (models.RecordAccess.expires_at.is_(None)) | (models.RecordAccess.expires_at > now_utc())
    )

    explicit_group_access = db.query(models.RecordAccess.record_id).filter(
        models.RecordAccess.record_type == "BudgetItem",
        models.RecordAccess.group_id.in_(user_group_ids),
        (models.RecordAccess.expires_at.is_(None)) | (models.RecordAccess.expires_at > now_utc())
    )

    accessible_ids = [item.id for item in accessible_ids_query.all()]
    accessible_ids += [access.record_id for access in explicit_user_access.all()]
    accessible_ids += [access.record_id for access in explicit_group_access.all()]

    return list(set(accessible_ids))


def get_group_options(db: Session, user: models.User) -> List[schemas.DashboardGroupOption]:
    if user.role in ["Admin", "Manager"]:
        groups = db.query(models.UserGroup).order_by(models.UserGroup.name.asc()).all()
        return [schemas.DashboardGroupOption.model_validate(group) for group in groups]

    group_ids = set(get_user_group_ids(db, user.id))
    if user.primary_group_id:
        group_ids.add(user.primary_group_id)

    budget_ids = get_accessible_budget_ids(db, user)
    if budget_ids:
        budget_group_ids = db.query(models.BudgetItem.owner_group_id).filter(
            models.BudgetItem.id.in_(budget_ids)
        ).distinct().all()
        group_ids.update([row[0] for row in budget_group_ids])

    if not group_ids:
        return []

    groups = db.query(models.UserGroup).filter(
        models.UserGroup.id.in_(group_ids)
    ).order_by(models.UserGroup.name.asc()).all()
    return [schemas.DashboardGroupOption.model_validate(group) for group in groups]


def normalize_decimal(value: Optional[Decimal]) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(
    owner_group_id: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> schemas.DashboardSummary:
    current_year = year or now_utc().year
    previous_year = current_year - 1

    groups = get_group_options(db, current_user)
    group_ids = [group.id for group in groups]

    selected_group_id = owner_group_id
    if selected_group_id is None:
        if current_user.primary_group_id:
            selected_group_id = current_user.primary_group_id
        elif group_ids:
            selected_group_id = group_ids[0]

    if selected_group_id is not None and selected_group_id not in group_ids:
        raise HTTPException(status_code=403, detail="Selected group is not accessible")

    selected_group = next((group for group in groups if group.id == selected_group_id), None)

    budget_ids = get_accessible_budget_ids(db, current_user)
    if budget_ids is not None and not budget_ids:
        budget_current_total = Decimal("0")
        budget_previous_total = Decimal("0")
        budget_current_count = 0
        budget_previous_count = 0
    else:
        budget_query = db.query(models.BudgetItem)
        if budget_ids is not None:
            budget_query = budget_query.filter(models.BudgetItem.id.in_(budget_ids))
        if selected_group_id is not None:
            budget_query = budget_query.filter(models.BudgetItem.owner_group_id == selected_group_id)

        budget_current_total = normalize_decimal(
            budget_query.filter(models.BudgetItem.fiscal_year == current_year)
            .with_entities(func.coalesce(func.sum(models.BudgetItem.budget_amount), 0))
            .scalar()
        )
        budget_previous_total = normalize_decimal(
            budget_query.filter(models.BudgetItem.fiscal_year == previous_year)
            .with_entities(func.coalesce(func.sum(models.BudgetItem.budget_amount), 0))
            .scalar()
        )
        budget_current_count = budget_query.filter(models.BudgetItem.fiscal_year == current_year).count()
        budget_previous_count = budget_query.filter(models.BudgetItem.fiscal_year == previous_year).count()

    po_ids = get_accessible_po_ids(db, current_user)
    if po_ids is not None and not po_ids:
        spend_current_total = Decimal("0")
        spend_previous_total = Decimal("0")
        open_pos_count = 0
        open_pos_value = Decimal("0")
    else:
        po_query = db.query(models.PurchaseOrder)
        if po_ids is not None:
            po_query = po_query.filter(models.PurchaseOrder.id.in_(po_ids))
        if selected_group_id is not None:
            po_query = po_query.filter(models.PurchaseOrder.owner_group_id == selected_group_id)

        spend_current_total = normalize_decimal(
            po_query.filter(
                models.PurchaseOrder.planned_commit_date.isnot(None),
                extract("year", models.PurchaseOrder.planned_commit_date) == current_year
            ).with_entities(func.coalesce(func.sum(models.PurchaseOrder.total_amount), 0)).scalar()
        )
        spend_previous_total = normalize_decimal(
            po_query.filter(
                models.PurchaseOrder.planned_commit_date.isnot(None),
                extract("year", models.PurchaseOrder.planned_commit_date) == previous_year
            ).with_entities(func.coalesce(func.sum(models.PurchaseOrder.total_amount), 0)).scalar()
        )

        open_statuses = ["Open", "Approved", "In Progress"]
        open_pos_query = po_query.filter(models.PurchaseOrder.status.in_(open_statuses))
        open_pos_count = open_pos_query.count()
        open_pos_value = normalize_decimal(
            open_pos_query.with_entities(func.coalesce(func.sum(models.PurchaseOrder.total_amount), 0)).scalar()
        )

    gr_ids = get_accessible_gr_ids(db, current_user)
    if gr_ids is not None and not gr_ids:
        recent_grs_count = 0
    else:
        gr_query = db.query(models.GoodsReceipt)
        if gr_ids is not None:
            gr_query = gr_query.filter(models.GoodsReceipt.id.in_(gr_ids))
        if selected_group_id is not None:
            gr_query = gr_query.filter(models.GoodsReceipt.owner_group_id == selected_group_id)

        thirty_days_ago = now_utc() - timedelta(days=30)
        recent_grs_count = gr_query.filter(
            models.GoodsReceipt.created_at.isnot(None),
            models.GoodsReceipt.created_at >= thirty_days_ago
        ).count()

    resource_ids = get_accessible_resource_ids(db, current_user)
    if resource_ids is not None and not resource_ids:
        active_resources_count = 0
    else:
        resource_query = db.query(models.Resource)
        if resource_ids is not None:
            resource_query = resource_query.filter(models.Resource.id.in_(resource_ids))
        if selected_group_id is not None:
            resource_query = resource_query.filter(models.Resource.owner_group_id == selected_group_id)
        active_resources_count = resource_query.filter(models.Resource.status == "Active").count()

    pending_statuses = ["Draft", "Submitted", "Under Review"]
    if current_user.role in ["Admin", "Manager"]:
        bc_query = db.query(models.BusinessCase)
        if selected_group_id is not None:
            bc_query = bc_query.filter(models.BusinessCase.lead_group_id == selected_group_id)
        pending_business_cases = bc_query.filter(models.BusinessCase.status.in_(pending_statuses)).count()
    else:
        bc_query = db.query(models.BusinessCase)
        if selected_group_id is not None:
            bc_query = bc_query.filter(models.BusinessCase.lead_group_id == selected_group_id)
        pending_business_cases = 0
        for bc in bc_query.all():
            if bc.status in pending_statuses and check_business_case_access(current_user, bc, db, "Read"):
                pending_business_cases += 1

    return schemas.DashboardSummary(
        current_year=current_year,
        previous_year=previous_year,
        group=selected_group,
        groups=groups,
        budgets=schemas.DashboardBudgetTotals(
            current_year=current_year,
            previous_year=previous_year,
            current_year_total=budget_current_total,
            previous_year_total=budget_previous_total,
            current_year_count=budget_current_count,
            previous_year_count=budget_previous_count,
        ),
        spend=schemas.DashboardSpendTotals(
            current_year=current_year,
            previous_year=previous_year,
            current_year_total=spend_current_total,
            previous_year_total=spend_previous_total,
        ),
        open_pos=schemas.DashboardOpenPOTotals(
            count=open_pos_count,
            value=open_pos_value,
        ),
        recent_grs_count=recent_grs_count,
        active_resources_count=active_resources_count,
        pending_business_cases=pending_business_cases,
    )
