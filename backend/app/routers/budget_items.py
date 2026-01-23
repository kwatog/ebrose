from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user, require_role, check_record_access, audit_log_change, now_utc

router = APIRouter(prefix="/budget-items", tags=["budget-items"])


@router.get("/", response_model=List[schemas.BudgetItem])
@router.get("", response_model=List[schemas.BudgetItem], include_in_schema=False)
def list_budget_items(
    skip: int = 0,
    limit: int = 100,
    fiscal_year: int = None,
    owner_group_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all budget items with pagination and filtering."""
    from app.auth import user_in_owner_group

    query = db.query(models.BudgetItem)

    if current_user.role not in ["Admin", "Manager"]:
        user_groups = db.query(models.UserGroupMembership).filter(
            models.UserGroupMembership.user_id == current_user.id
        ).all()
        group_ids = [membership.group_id for membership in user_groups]

        accessible_ids_query = db.query(models.BudgetItem.id).filter(
            (models.BudgetItem.owner_group_id.in_(group_ids)) |
            (models.BudgetItem.created_by == current_user.id)
        )

        explicit_user_access = db.query(models.RecordAccess.record_id).filter(
            models.RecordAccess.record_type == "BudgetItem",
            models.RecordAccess.user_id == current_user.id,
            (models.RecordAccess.expires_at.is_(None)) | (models.RecordAccess.expires_at > now_utc())
        )

        explicit_group_access = db.query(models.RecordAccess.record_id).filter(
            models.RecordAccess.record_type == "BudgetItem",
            models.RecordAccess.group_id.in_(group_ids),
            (models.RecordAccess.expires_at.is_(None)) | (models.RecordAccess.expires_at > now_utc())
        )

        accessible_ids = [item.id for item in accessible_ids_query.all()]
        accessible_ids += [access.record_id for access in explicit_user_access.all()]
        accessible_ids += [access.record_id for access in explicit_group_access.all()]

        query = query.filter(models.BudgetItem.id.in_(accessible_ids))

    if fiscal_year:
        query = query.filter(models.BudgetItem.fiscal_year == fiscal_year)
    if owner_group_id:
        query = query.filter(models.BudgetItem.owner_group_id == owner_group_id)

    query = query.order_by(models.BudgetItem.created_at.desc())

    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/{id}", response_model=schemas.BudgetItem)
def get_budget_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_record_access("BudgetItem", "id", "Read"))
):
    """Get a specific budget item by ID."""
    budget_item = db.get(models.BudgetItem, id)
    if not budget_item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    return budget_item


@router.post("/", response_model=schemas.BudgetItem)
@router.post("", response_model=schemas.BudgetItem, include_in_schema=False)
@audit_log_change(action="CREATE", table_name="budget_item")
async def create_budget_item(
    budget_item: schemas.BudgetItemCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("User"))
):
    """Create a new budget item (User+ only)."""
    if current_user.role == "Viewer":
        raise HTTPException(
            status_code=403,
            detail="Viewers cannot create budget items"
        )

    existing = db.query(models.BudgetItem).filter(
        models.BudgetItem.workday_ref == budget_item.workday_ref
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Budget item with this Workday reference already exists")

    db_budget_item = models.BudgetItem(
        **budget_item.model_dump(),
        created_by=current_user.id,
        created_at=now_utc()
    )

    db.add(db_budget_item)
    db.flush()
    db.commit()
    db.refresh(db_budget_item)
    return db_budget_item


@router.put("/{id}", response_model=schemas.BudgetItem)
@audit_log_change(action="UPDATE", table_name="budget_item")
async def update_budget_item(
    id: int,
    budget_item_update: schemas.BudgetItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_record_access("BudgetItem", "id", "Write"))
):
    """Update an existing budget item."""
    db_budget_item = db.get(models.BudgetItem, id)
    if not db_budget_item:
        raise HTTPException(status_code=404, detail="Budget item not found")

    update_data = budget_item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_budget_item, key, value)

    db_budget_item.updated_by = current_user.id
    db_budget_item.updated_at = now_utc()

    db.commit()
    db.refresh(db_budget_item)
    return db_budget_item


@router.delete("/{id}")
@audit_log_change(action="DELETE", table_name="budget_item")
async def delete_budget_item(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("Manager"))
):
    """Delete a budget item (Manager+ only)."""
    db_budget_item = db.get(models.BudgetItem, id)
    if not db_budget_item:
        raise HTTPException(status_code=404, detail="Budget item not found")

    line_items = db.query(models.BusinessCaseLineItem).filter(
        models.BusinessCaseLineItem.budget_item_id == id
    ).first()
    if line_items:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete budget item with associated business case line items"
        )

    db.delete(db_budget_item)
    db.commit()

    return {"message": "Budget item deleted successfully"}
