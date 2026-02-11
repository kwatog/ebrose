from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas
from ..database import SessionLocal, get_db
from ..auth import get_current_user, require_role, check_record_access, audit_log_change, now_utc

router = APIRouter(prefix="/business-case-line-items", tags=["business-case-line-items"])


@router.get("/", response_model=List[schemas.BusinessCaseLineItem])
@router.get("", response_model=List[schemas.BusinessCaseLineItem], include_in_schema=False)
def list_business_case_line_items(
    skip: int = 0,
    limit: int = 100,
    business_case_id: Optional[int] = None,
    owner_group_id: Optional[int] = None,
    spend_category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all business case line items with pagination and filtering."""
    query = db.query(models.BusinessCaseLineItem)

    # CRITICAL: Filter by owner_group_id access (only show records user can access)
    if current_user.role not in ["Admin", "Manager"]:
        # Get all groups the user is a member of
        user_groups = db.query(models.UserGroupMembership).filter(
            models.UserGroupMembership.user_id == current_user.id
        ).all()
        group_ids = [membership.group_id for membership in user_groups]

        # Filter to accessible records
        accessible_ids_query = db.query(models.BusinessCaseLineItem.id).filter(
            (models.BusinessCaseLineItem.owner_group_id.in_(group_ids)) |
            (models.BusinessCaseLineItem.created_by == current_user.id)
        )

        # Add explicit user-level RecordAccess grants
        explicit_user_access = db.query(models.RecordAccess.record_id).filter(
            models.RecordAccess.record_type == "BusinessCaseLineItem",
            models.RecordAccess.user_id == current_user.id,
            (models.RecordAccess.expires_at.is_(None)) | (models.RecordAccess.expires_at > now_utc())
        )

        # Add explicit group-level RecordAccess grants
        explicit_group_access = db.query(models.RecordAccess.record_id).filter(
            models.RecordAccess.record_type == "BusinessCaseLineItem",
            models.RecordAccess.group_id.in_(group_ids),
            (models.RecordAccess.expires_at.is_(None)) | (models.RecordAccess.expires_at > now_utc())
        )

        accessible_ids = [item.id for item in accessible_ids_query.all()]
        accessible_ids += [access.record_id for access in explicit_user_access.all()]
        accessible_ids += [access.record_id for access in explicit_group_access.all()]

        # If no accessible business case line items, return empty list
        if not accessible_ids:
            return []

        query = query.filter(models.BusinessCaseLineItem.id.in_(accessible_ids))

    # Apply filters
    if business_case_id:
        query = query.filter(models.BusinessCaseLineItem.business_case_id == business_case_id)
    if owner_group_id:
        query = query.filter(models.BusinessCaseLineItem.owner_group_id == owner_group_id)
    if spend_category:
        query = query.filter(models.BusinessCaseLineItem.spend_category == spend_category)

    # Order by created_at descending
    query = query.order_by(models.BusinessCaseLineItem.created_at.desc())

    # Apply pagination
    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/{id}", response_model=schemas.BusinessCaseLineItem)
def get_line_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_record_access("BusinessCaseLineItem", "id", "Read"))
):
    """Get a specific business case line item by ID."""
    line_item = db.get(models.BusinessCaseLineItem, id)
    if not line_item:
        raise HTTPException(status_code=404, detail="Business case line item not found")
    return line_item


@router.post("/", response_model=schemas.BusinessCaseLineItem)
@router.post("", response_model=schemas.BusinessCaseLineItem, include_in_schema=False)
@audit_log_change(action="CREATE", table_name="business_case_line_item")
async def create_line_item(
    line_item: schemas.BusinessCaseLineItemCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("User"))
):
    """Create a new business case line item."""
    # CRITICAL: Viewers cannot create any records
    if current_user.role == "Viewer":
        raise HTTPException(
            status_code=403,
            detail="Viewers cannot create business case line items"
        )

    # Verify business case exists
    business_case = db.get(models.BusinessCase, line_item.business_case_id)
    if not business_case:
        raise HTTPException(status_code=404, detail="Business case not found")

    # Verify budget item exists
    budget_item = db.get(models.BudgetItem, line_item.budget_item_id)
    if not budget_item:
        raise HTTPException(status_code=404, detail="Budget item not found")

    # Create new line item
    db_line_item = models.BusinessCaseLineItem(
        **line_item.model_dump(),
        created_by=current_user.id,
        created_at=now_utc()
    )

    db.add(db_line_item)
    db.flush()
    db.commit()
    db.refresh(db_line_item)
    return db_line_item


@router.put("/{id}", response_model=schemas.BusinessCaseLineItem)
@audit_log_change(action="UPDATE", table_name="business_case_line_item")
async def update_line_item(
    id: int,
    line_item_update: schemas.BusinessCaseLineItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_record_access("BusinessCaseLineItem", "id", "Write"))
):
    """Update an existing business case line item."""
    db_line_item = db.get(models.BusinessCaseLineItem, id)
    if not db_line_item:
        raise HTTPException(status_code=404, detail="Business case line item not found")

    # Update fields
    update_data = line_item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_line_item, key, value)

    db_line_item.updated_by = current_user.id
    db_line_item.updated_at = now_utc()

    db.commit()
    db.refresh(db_line_item)
    return db_line_item


@router.delete("/{id}")
@audit_log_change(action="DELETE", table_name="business_case_line_item")
async def delete_line_item(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("Manager"))
):
    """Delete a business case line item (Manager+ only)."""
    db_line_item = db.get(models.BusinessCaseLineItem, id)
    if not db_line_item:
        raise HTTPException(status_code=404, detail="Business case line item not found")

    # Check if line item has associated WBS items
    wbs_items = db.query(models.WBS).filter(
        models.WBS.business_case_line_item_id == id
    ).first()
    if wbs_items:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete line item with associated WBS items"
        )

    db.delete(db_line_item)
    db.commit()

    return {"message": "Business case line item deleted successfully"}
