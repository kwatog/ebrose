from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Boolean, Numeric, DateTime
from sqlalchemy.orm import relationship, column_property
from .database import Base


def now_utc():
    """Get current UTC timestamp as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    department = Column(String(255))
    role = Column(String(50), default="User")  # Viewer, User, Manager, Admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships for audit
    # Note: We are not adding back_populates on the User side for every single entity 
    # to avoid cluttering the User model, unless necessary.


class UserGroup(Base):
    __tablename__ = "user_group"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))


class UserGroupMembership(Base):
    __tablename__ = "user_group_membership"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    group_id = Column(Integer, ForeignKey("user_group.id"))
    added_by = Column(Integer, ForeignKey("user.id"))
    added_at = Column(DateTime(timezone=True))


class RecordAccess(Base):
    __tablename__ = "record_access"

    id = Column(Integer, primary_key=True, index=True)
    record_type = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("user_group.id"), nullable=True)
    access_level = Column(String(20), nullable=False)  # Read, Write, Full
    granted_by = Column(Integer, ForeignKey("user.id"))
    granted_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    updated_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    timestamp = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)


class BudgetItem(Base):
    __tablename__ = "budget_item"

    id = Column(Integer, primary_key=True, index=True)
    workday_ref = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    budget_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False, index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    line_items = relationship("BusinessCaseLineItem", back_populates="budget_item")


class BusinessCase(Base):
    __tablename__ = "business_case"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    requestor = Column(String(255))
    dept = Column(String(255))
    lead_group_id = Column(Integer, ForeignKey("user_group.id"))
    estimated_cost = Column(Numeric(10, 2))
    status = Column(String(50), index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    line_items = relationship("BusinessCaseLineItem", back_populates="business_case")


class BusinessCaseLineItem(Base):
    __tablename__ = "business_case_line_item"

    id = Column(Integer, primary_key=True, index=True)
    business_case_id = Column(Integer, ForeignKey("business_case.id"), nullable=False)
    budget_item_id = Column(Integer, ForeignKey("budget_item.id"), nullable=False)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    spend_category = Column(String(20), nullable=False)  # CAPEX, OPEX
    requested_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    planned_commit_date = Column(DateTime(timezone=True))
    status = Column(String(50), index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    business_case = relationship("BusinessCase", back_populates="line_items")
    budget_item = relationship("BudgetItem", back_populates="line_items")
    wbs_items = relationship("WBS", back_populates="line_item")


class WBS(Base):
    __tablename__ = "wbs"

    id = Column(Integer, primary_key=True, index=True)
    business_case_line_item_id = Column(Integer, ForeignKey("business_case_line_item.id"), nullable=False)
    wbs_code = Column(String(255), unique=True, index=True)
    description = Column(Text)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False, index=True)
    status = Column(String(50), index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    line_item = relationship("BusinessCaseLineItem", back_populates="wbs_items")
    assets = relationship("Asset", back_populates="wbs")
    business_case = relationship("BusinessCase",
        primaryjoin="WBS.business_case_line_item_id == BusinessCaseLineItem.id",
        secondaryjoin="BusinessCaseLineItem.business_case_id == BusinessCase.id",
        secondary="business_case_line_item",
        viewonly=True,
        uselist=False)


class Asset(Base):
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True, index=True)
    wbs_id = Column(Integer, ForeignKey("wbs.id"), nullable=False)
    asset_code = Column(String(255), unique=True, index=True)
    asset_type = Column(String(50))
    description = Column(Text)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False, index=True)
    status = Column(String(50), index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    wbs = relationship("WBS", back_populates="assets")
    purchase_orders = relationship("PurchaseOrder", back_populates="asset")


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False)
    po_number = Column(String(255), unique=True, index=True)
    ariba_pr_number = Column(String(255))
    supplier = Column(String(255))
    po_type = Column(String(50))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    total_amount = Column(Numeric(10, 2))
    currency = Column(String(10), default="USD")
    spend_category = Column(String(20), nullable=False)  # CAPEX, OPEX
    planned_commit_date = Column(DateTime(timezone=True))
    actual_commit_date = Column(DateTime(timezone=True))
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False, index=True)
    status = Column(String(50), index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("Asset", back_populates="purchase_orders")
    goods_receipts = relationship("GoodsReceipt", back_populates="po")
    allocations = relationship("ResourcePOAllocation", back_populates="po")


class GoodsReceipt(Base):
    __tablename__ = "goods_receipt"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_order.id"), nullable=False)
    gr_number = Column(String(255), unique=True, index=True)
    gr_date = Column(DateTime(timezone=True))
    amount = Column(Numeric(10, 2))
    description = Column(Text)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False, index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    po = relationship("PurchaseOrder", back_populates="goods_receipts")


class Resource(Base):
    __tablename__ = "resource"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    vendor = Column(String(255))
    role = Column(String(255))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    cost_per_month = Column(Numeric(10, 2))
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False, index=True)
    status = Column(String(50), index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    allocations = relationship("ResourcePOAllocation", back_populates="resource")


class ResourcePOAllocation(Base):
    __tablename__ = "resource_po_allocation"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resource.id"))
    po_id = Column(Integer, ForeignKey("purchase_order.id"))
    allocation_start = Column(DateTime(timezone=True))
    allocation_end = Column(DateTime(timezone=True))
    expected_monthly_burn = Column(Numeric(10, 2))
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False, index=True)

    # Audit
    created_by = Column(Integer, ForeignKey("user.id"), index=True)
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    resource = relationship("Resource", back_populates="allocations")
    po = relationship("PurchaseOrder", back_populates="allocations")