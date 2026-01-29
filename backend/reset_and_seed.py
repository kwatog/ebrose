#!/usr/bin/env python3
"""
Database Reset and Seed Script for Ebrose

This script:
1. Deletes the existing SQLite database
2. Creates all tables from scratch
3. Seeds initial data (admin user, groups, sample records)

Usage:
    python reset_and_seed.py
"""

import os
import sys
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import Base, engine, SessionLocal
from app import models
from app.auth import get_password_hash, now_utc


def reset_database():
    """Delete existing database file."""
    db_file = "../ebrose.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✓ Deleted existing database: {db_file}")
    else:
        print("✓ No existing database found")


def create_tables():
    """Create all tables from models."""
    Base.metadata.create_all(bind=engine)
    print("✓ Created all database tables")


def seed_data():
    """Seed initial data."""
    db = SessionLocal()
    try:
        now = now_utc()

        # 1. Create Admin User
        admin_user = models.User(
            username="admin",
            email="admin@ebrose.local",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            department="IT",
            role="Admin",
            is_active=True,
            created_at=now
        )
        db.add(admin_user)
        db.flush()  # Get ID without committing
        print(f"✓ Created admin user (ID: {admin_user.id})")

        # 2. Create Manager User
        manager_user = models.User(
            username="manager",
            email="manager@ebrose.local",
            hashed_password=get_password_hash("manager123"),
            full_name="Finance Manager",
            department="Finance",
            role="Manager",
            is_active=True,
            created_at=now
        )
        db.add(manager_user)
        db.flush()
        print(f"✓ Created manager user (ID: {manager_user.id})")

        # 3. Create Regular User
        regular_user = models.User(
            username="user",
            email="user@ebrose.local",
            hashed_password=get_password_hash("user123"),
            full_name="Regular User",
            department="Operations",
            role="User",
            is_active=True,
            created_at=now
        )
        db.add(regular_user)
        db.flush()
        print(f"✓ Created regular user (ID: {regular_user.id})")

        # 4. Create User Groups
        finance_group = models.UserGroup(
            name="Finance",
            description="Finance department group",
            created_by=admin_user.id,
            created_at=now
        )
        db.add(finance_group)
        db.flush()
        print(f"✓ Created Finance group (ID: {finance_group.id})")

        ops_group = models.UserGroup(
            name="Operations",
            description="Operations department group",
            created_by=admin_user.id,
            created_at=now
        )
        db.add(ops_group)
        db.flush()
        print(f"✓ Created Operations group (ID: {ops_group.id})")

        it_group = models.UserGroup(
            name="IT",
            description="IT department group",
            created_by=admin_user.id,
            created_at=now
        )
        db.add(it_group)
        db.flush()
        print(f"✓ Created IT group (ID: {it_group.id})")

        admin_user.primary_group_id = it_group.id
        manager_user.primary_group_id = finance_group.id
        regular_user.primary_group_id = ops_group.id

        # 5. Add users to groups
        db.add(models.UserGroupMembership(
            user_id=manager_user.id,
            group_id=finance_group.id,
            added_by=admin_user.id,
            added_at=now
        ))
        db.add(models.UserGroupMembership(
            user_id=regular_user.id,
            group_id=ops_group.id,
            added_by=admin_user.id,
            added_at=now
        ))
        db.add(models.UserGroupMembership(
            user_id=admin_user.id,
            group_id=it_group.id,
            added_by=admin_user.id,
            added_at=now
        ))
        print("✓ Added users to groups")

        # 6. Create Sample Budget Items
        budget_items = [
            models.BudgetItem(
                workday_ref="WD-2025-FIN-001",
                title="Cloud Infrastructure Budget 2025",
                description="Annual budget for AWS cloud services",
                budget_amount=500000.00,
                currency="USD",
                fiscal_year=2025,
                owner_group_id=finance_group.id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.BudgetItem(
                workday_ref="WD-2025-IT-002",
                title="Software Licenses 2025",
                description="Enterprise software licensing and subscriptions",
                budget_amount=250000.00,
                currency="USD",
                fiscal_year=2025,
                owner_group_id=it_group.id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.BudgetItem(
                workday_ref="WD-2025-OPS-003",
                title="Operations Equipment 2025",
                description="Operational equipment and tooling budget",
                budget_amount=180000.00,
                currency="USD",
                fiscal_year=2025,
                owner_group_id=ops_group.id,
                created_by=manager_user.id,
                created_at=now
            ),
            models.BudgetItem(
                workday_ref="WD-2025-FIN-004",
                title="Security & Compliance 2025",
                description="Security tools, audits, and compliance initiatives",
                budget_amount=320000.00,
                currency="USD",
                fiscal_year=2025,
                owner_group_id=finance_group.id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.BudgetItem(
                workday_ref="WD-2026-IT-005",
                title="Digital Transformation 2026",
                description="Next-gen platform modernization budget",
                budget_amount=750000.00,
                currency="USD",
                fiscal_year=2026,
                owner_group_id=it_group.id,
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for item in budget_items:
            db.add(item)
        db.flush()
        budget_item = budget_items[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(budget_items)} budget items")

        # 7. Create Sample Business Cases
        business_cases = [
            models.BusinessCase(
                title="Cloud Migration Project",
                description="Migrate legacy systems to AWS cloud infrastructure",
                requestor="IT Department",
                dept="IT",
                lead_group_id=it_group.id,
                estimated_cost=250000.00,
                status="Approved",
                created_by=admin_user.id,
                created_at=now
            ),
            models.BusinessCase(
                title="ERP System Upgrade",
                description="Upgrade enterprise resource planning system to latest version",
                requestor="Finance Manager",
                dept="Finance",
                lead_group_id=finance_group.id,
                estimated_cost=180000.00,
                status="In Progress",
                created_by=manager_user.id,
                created_at=now
            ),
            models.BusinessCase(
                title="Warehouse Automation Initiative",
                description="Implement automated inventory management and robotics",
                requestor="Operations Director",
                dept="Operations",
                lead_group_id=ops_group.id,
                estimated_cost=425000.00,
                status="Pending Approval",
                created_by=regular_user.id,
                created_at=now
            ),
            models.BusinessCase(
                title="Cybersecurity Enhancement Program",
                description="Implement zero-trust architecture and advanced threat detection",
                requestor="CISO",
                dept="IT",
                lead_group_id=it_group.id,
                estimated_cost=320000.00,
                status="Approved",
                created_by=admin_user.id,
                created_at=now
            ),
            models.BusinessCase(
                title="Customer Portal Redesign",
                description="Modernize customer-facing portal with improved UX",
                requestor="Product Manager",
                dept="IT",
                lead_group_id=it_group.id,
                estimated_cost=95000.00,
                status="Draft",
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for case in business_cases:
            db.add(case)
        db.flush()
        business_case = business_cases[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(business_cases)} business cases")

        # 8. Create Business Case Line Items
        line_items = [
            models.BusinessCaseLineItem(
                business_case_id=business_cases[0].id,
                budget_item_id=budget_items[0].id,
                owner_group_id=it_group.id,
                title="AWS EC2 Infrastructure",
                description="Compute resources for migrated applications",
                spend_category="OPEX",
                requested_amount=150000.00,
                currency="USD",
                planned_commit_date=datetime(2025, 2, 1, tzinfo=timezone.utc),
                status="Approved",
                created_by=admin_user.id,
                created_at=now
            ),
            models.BusinessCaseLineItem(
                business_case_id=business_cases[0].id,
                budget_item_id=budget_items[0].id,
                owner_group_id=it_group.id,
                title="AWS RDS Database Services",
                description="Managed database services for cloud applications",
                spend_category="OPEX",
                requested_amount=75000.00,
                currency="USD",
                planned_commit_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
                status="Approved",
                created_by=admin_user.id,
                created_at=now
            ),
            models.BusinessCaseLineItem(
                business_case_id=business_cases[1].id,
                budget_item_id=budget_items[1].id,
                owner_group_id=finance_group.id,
                title="SAP Licensing",
                description="ERP software licenses and support",
                spend_category="CAPEX",
                requested_amount=120000.00,
                currency="USD",
                planned_commit_date=datetime(2025, 4, 1, tzinfo=timezone.utc),
                status="In Progress",
                created_by=manager_user.id,
                created_at=now
            ),
            models.BusinessCaseLineItem(
                business_case_id=business_cases[3].id,
                budget_item_id=budget_items[3].id,
                owner_group_id=it_group.id,
                title="Zero Trust Network Access",
                description="ZTNA solution implementation",
                spend_category="CAPEX",
                requested_amount=185000.00,
                currency="USD",
                planned_commit_date=datetime(2025, 5, 1, tzinfo=timezone.utc),
                status="Approved",
                created_by=admin_user.id,
                created_at=now
            ),
            models.BusinessCaseLineItem(
                business_case_id=business_cases[3].id,
                budget_item_id=budget_items[3].id,
                owner_group_id=it_group.id,
                title="Security Operations Center Tools",
                description="SIEM and threat intelligence platform",
                spend_category="OPEX",
                requested_amount=95000.00,
                currency="USD",
                planned_commit_date=datetime(2025, 6, 1, tzinfo=timezone.utc),
                status="Approved",
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for item in line_items:
            db.add(item)
        db.flush()
        line_item = line_items[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(line_items)} business case line items")

        # 9. Create WBS entries (inherits owner_group_id from line_item)
        wbs_entries = [
            models.WBS(
                business_case_line_item_id=line_items[0].id,
                wbs_code="WBS-2025-IT-001",
                description="Cloud Migration Phase 1",
                owner_group_id=line_items[0].owner_group_id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
            models.WBS(
                business_case_line_item_id=line_items[1].id,
                wbs_code="WBS-2025-IT-002",
                description="Database Migration Services",
                owner_group_id=line_items[1].owner_group_id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
            models.WBS(
                business_case_line_item_id=line_items[2].id,
                wbs_code="WBS-2025-FIN-001",
                description="ERP Implementation Phase 1",
                owner_group_id=line_items[2].owner_group_id,
                status="Planning",
                created_by=manager_user.id,
                created_at=now
            ),
            models.WBS(
                business_case_line_item_id=line_items[3].id,
                wbs_code="WBS-2025-SEC-001",
                description="ZTNA Deployment",
                owner_group_id=line_items[3].owner_group_id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for entry in wbs_entries:
            db.add(entry)
        db.flush()
        wbs = wbs_entries[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(wbs_entries)} WBS entries")

        # 10. Create Assets (inherits owner_group_id from wbs)
        assets = [
            models.Asset(
                wbs_id=wbs_entries[0].id,
                asset_code="ASSET-AWS-EC2-001",
                asset_type="CAPEX",
                description="AWS EC2 Production Cluster",
                owner_group_id=wbs_entries[0].owner_group_id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
            models.Asset(
                wbs_id=wbs_entries[0].id,
                asset_code="ASSET-AWS-S3-001",
                asset_type="OPEX",
                description="AWS S3 Storage Buckets",
                owner_group_id=wbs_entries[0].owner_group_id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
            models.Asset(
                wbs_id=wbs_entries[1].id,
                asset_code="ASSET-AWS-RDS-001",
                asset_type="OPEX",
                description="AWS RDS PostgreSQL Instances",
                owner_group_id=wbs_entries[1].owner_group_id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
            models.Asset(
                wbs_id=wbs_entries[2].id,
                asset_code="ASSET-SAP-LIC-001",
                asset_type="CAPEX",
                description="SAP ERP User Licenses",
                owner_group_id=wbs_entries[2].owner_group_id,
                status="Planning",
                created_by=manager_user.id,
                created_at=now
            ),
            models.Asset(
                wbs_id=wbs_entries[3].id,
                asset_code="ASSET-SEC-ZTNA-001",
                asset_type="CAPEX",
                description="Zscaler Private Access License",
                owner_group_id=wbs_entries[3].owner_group_id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for asset_item in assets:
            db.add(asset_item)
        db.flush()
        asset = assets[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(assets)} assets")

        # 11. Create Purchase Orders (inherits owner_group_id from asset)
        purchase_orders = [
            models.PurchaseOrder(
                asset_id=assets[0].id,
                po_number="PO-2025-001",
                ariba_pr_number="PR-2025-AWS-001",
                supplier="Amazon Web Services",
                po_type="Service",
                start_date=datetime(2025, 2, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                total_amount=120000.00,
                currency="USD",
                spend_category="OPEX",
                planned_commit_date=datetime(2025, 1, 15, tzinfo=timezone.utc),
                actual_commit_date=datetime(2025, 1, 20, tzinfo=timezone.utc),
                owner_group_id=assets[0].owner_group_id,
                status="Open",
                created_by=admin_user.id,
                created_at=now
            ),
            models.PurchaseOrder(
                asset_id=assets[1].id,
                po_number="PO-2025-002",
                ariba_pr_number="PR-2025-AWS-002",
                supplier="Amazon Web Services",
                po_type="Service",
                start_date=datetime(2025, 2, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                total_amount=45000.00,
                currency="USD",
                spend_category="OPEX",
                planned_commit_date=datetime(2025, 1, 20, tzinfo=timezone.utc),
                actual_commit_date=datetime(2025, 1, 25, tzinfo=timezone.utc),
                owner_group_id=assets[1].owner_group_id,
                status="Open",
                created_by=admin_user.id,
                created_at=now
            ),
            models.PurchaseOrder(
                asset_id=assets[2].id,
                po_number="PO-2025-003",
                ariba_pr_number="PR-2025-AWS-003",
                supplier="Amazon Web Services",
                po_type="Service",
                start_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 2, 28, tzinfo=timezone.utc),
                total_amount=85000.00,
                currency="USD",
                spend_category="OPEX",
                planned_commit_date=datetime(2025, 2, 15, tzinfo=timezone.utc),
                owner_group_id=assets[2].owner_group_id,
                status="Pending",
                created_by=admin_user.id,
                created_at=now
            ),
            models.PurchaseOrder(
                asset_id=assets[3].id,
                po_number="PO-2025-004",
                ariba_pr_number="PR-2025-SAP-001",
                supplier="SAP SE",
                po_type="License",
                start_date=datetime(2025, 4, 1, tzinfo=timezone.utc),
                end_date=datetime(2028, 3, 31, tzinfo=timezone.utc),
                total_amount=120000.00,
                currency="USD",
                spend_category="CAPEX",
                planned_commit_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
                owner_group_id=assets[3].owner_group_id,
                status="Draft",
                created_by=manager_user.id,
                created_at=now
            ),
            models.PurchaseOrder(
                asset_id=assets[4].id,
                po_number="PO-2025-005",
                ariba_pr_number="PR-2025-SEC-001",
                supplier="Zscaler Inc",
                po_type="License",
                start_date=datetime(2025, 5, 1, tzinfo=timezone.utc),
                end_date=datetime(2027, 4, 30, tzinfo=timezone.utc),
                total_amount=185000.00,
                currency="USD",
                spend_category="CAPEX",
                planned_commit_date=datetime(2025, 4, 15, tzinfo=timezone.utc),
                actual_commit_date=datetime(2025, 4, 20, tzinfo=timezone.utc),
                owner_group_id=assets[4].owner_group_id,
                status="Open",
                created_by=admin_user.id,
                created_at=now
            ),
            models.PurchaseOrder(
                asset_id=assets[0].id,
                po_number="PO-2025-006",
                ariba_pr_number="PR-2025-AWS-004",
                supplier="Amazon Web Services",
                po_type="Service",
                start_date=datetime(2025, 6, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 5, 31, tzinfo=timezone.utc),
                total_amount=95000.00,
                currency="USD",
                spend_category="OPEX",
                planned_commit_date=datetime(2025, 5, 1, tzinfo=timezone.utc),
                owner_group_id=assets[0].owner_group_id,
                status="Pending",
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for po_item in purchase_orders:
            db.add(po_item)
        db.flush()
        po = purchase_orders[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(purchase_orders)} purchase orders")

        # 12. Create Goods Receipts (inherits owner_group_id from po)
        goods_receipts = [
            models.GoodsReceipt(
                po_id=purchase_orders[0].id,
                gr_number="GR-2025-001",
                gr_date=datetime(2025, 2, 15, tzinfo=timezone.utc),
                amount=10000.00,
                description="First month AWS EC2 services",
                owner_group_id=purchase_orders[0].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.GoodsReceipt(
                po_id=purchase_orders[0].id,
                gr_number="GR-2025-002",
                gr_date=datetime(2025, 3, 15, tzinfo=timezone.utc),
                amount=10000.00,
                description="Second month AWS EC2 services",
                owner_group_id=purchase_orders[0].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.GoodsReceipt(
                po_id=purchase_orders[1].id,
                gr_number="GR-2025-003",
                gr_date=datetime(2025, 2, 20, tzinfo=timezone.utc),
                amount=3750.00,
                description="First month AWS S3 storage",
                owner_group_id=purchase_orders[1].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.GoodsReceipt(
                po_id=purchase_orders[1].id,
                gr_number="GR-2025-004",
                gr_date=datetime(2025, 3, 20, tzinfo=timezone.utc),
                amount=3750.00,
                description="Second month AWS S3 storage",
                owner_group_id=purchase_orders[1].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.GoodsReceipt(
                po_id=purchase_orders[4].id,
                gr_number="GR-2025-005",
                gr_date=datetime(2025, 5, 10, tzinfo=timezone.utc),
                amount=92500.00,
                description="Zscaler license activation - Year 1",
                owner_group_id=purchase_orders[4].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for gr_item in goods_receipts:
            db.add(gr_item)
        db.flush()
        gr = goods_receipts[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(goods_receipts)} goods receipts")

        # 13. Create Resources
        resources = [
            models.Resource(
                name="John Smith",
                vendor="TechCorp Consulting",
                role="Cloud Architect",
                start_date=datetime(2025, 2, 1, tzinfo=timezone.utc),
                end_date=datetime(2025, 12, 31, tzinfo=timezone.utc),
                cost_per_month=15000.00,
                owner_group_id=it_group.id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
            models.Resource(
                name="Sarah Johnson",
                vendor="DevOps Partners LLC",
                role="DevOps Engineer",
                start_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
                end_date=datetime(2026, 2, 28, tzinfo=timezone.utc),
                cost_per_month=12000.00,
                owner_group_id=it_group.id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
            models.Resource(
                name="Michael Chen",
                vendor="Security Solutions Inc",
                role="Security Consultant",
                start_date=datetime(2025, 5, 1, tzinfo=timezone.utc),
                end_date=datetime(2025, 10, 31, tzinfo=timezone.utc),
                cost_per_month=18000.00,
                owner_group_id=it_group.id,
                status="Planned",
                created_by=admin_user.id,
                created_at=now
            ),
            models.Resource(
                name="Emily Rodriguez",
                vendor="SAP Consultants Group",
                role="SAP Functional Consultant",
                start_date=datetime(2025, 4, 1, tzinfo=timezone.utc),
                end_date=datetime(2025, 9, 30, tzinfo=timezone.utc),
                cost_per_month=16500.00,
                owner_group_id=finance_group.id,
                status="Planned",
                created_by=manager_user.id,
                created_at=now
            ),
            models.Resource(
                name="David Park",
                vendor="Cloud Native Technologies",
                role="Kubernetes Engineer",
                start_date=datetime(2025, 2, 15, tzinfo=timezone.utc),
                end_date=datetime(2025, 8, 15, tzinfo=timezone.utc),
                cost_per_month=14000.00,
                owner_group_id=it_group.id,
                status="Active",
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for resource_item in resources:
            db.add(resource_item)
        db.flush()
        resource = resources[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(resources)} resources")

        # 14. Create Resource-PO Allocations (inherits owner_group_id from po)
        allocations = [
            models.ResourcePOAllocation(
                resource_id=resources[0].id,
                po_id=purchase_orders[0].id,
                allocation_start=datetime(2025, 2, 1, tzinfo=timezone.utc),
                allocation_end=datetime(2025, 12, 31, tzinfo=timezone.utc),
                expected_monthly_burn=15000.00,
                owner_group_id=purchase_orders[0].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.ResourcePOAllocation(
                resource_id=resources[1].id,
                po_id=purchase_orders[0].id,
                allocation_start=datetime(2025, 3, 1, tzinfo=timezone.utc),
                allocation_end=datetime(2026, 2, 28, tzinfo=timezone.utc),
                expected_monthly_burn=12000.00,
                owner_group_id=purchase_orders[0].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.ResourcePOAllocation(
                resource_id=resources[2].id,
                po_id=purchase_orders[4].id,
                allocation_start=datetime(2025, 5, 1, tzinfo=timezone.utc),
                allocation_end=datetime(2025, 10, 31, tzinfo=timezone.utc),
                expected_monthly_burn=18000.00,
                owner_group_id=purchase_orders[4].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
            models.ResourcePOAllocation(
                resource_id=resources[3].id,
                po_id=purchase_orders[3].id,
                allocation_start=datetime(2025, 4, 1, tzinfo=timezone.utc),
                allocation_end=datetime(2025, 9, 30, tzinfo=timezone.utc),
                expected_monthly_burn=16500.00,
                owner_group_id=purchase_orders[3].owner_group_id,
                created_by=manager_user.id,
                created_at=now
            ),
            models.ResourcePOAllocation(
                resource_id=resources[4].id,
                po_id=purchase_orders[0].id,
                allocation_start=datetime(2025, 2, 15, tzinfo=timezone.utc),
                allocation_end=datetime(2025, 8, 15, tzinfo=timezone.utc),
                expected_monthly_burn=14000.00,
                owner_group_id=purchase_orders[0].owner_group_id,
                created_by=admin_user.id,
                created_at=now
            ),
        ]
        for alloc in allocations:
            db.add(alloc)
        db.flush()
        allocation = allocations[0]  # Keep reference for backward compatibility
        print(f"✓ Created {len(allocations)} resource allocations")

        # Commit all changes
        db.commit()
        print("\n✅ Database seeded successfully!")
        print("\n📝 Login Credentials:")
        print("   Admin:   admin / admin123")
        print("   Manager: manager / manager123")
        print("   User:    user / user123")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


def main():
    """Main execution."""
    print("=" * 60)
    print("Ebrose Database Reset & Seed")
    print("=" * 60)
    print()

    reset_database()
    create_tables()
    seed_data()

    print()
    print("=" * 60)
    print("✅ All done! Database is ready to use.")
    print("=" * 60)


if __name__ == "__main__":
    main()
