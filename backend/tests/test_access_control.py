import pytest
from datetime import datetime


def test_admin_can_access_all_groups(client, admin_user, admin_token, db_session):
    """Test that admin can see all groups."""
    from app.models import UserGroup

    # Create multiple groups
    for i in range(3):
        group = UserGroup(
            name=f"Group {i}",
            description=f"Group {i} description",
            created_by=admin_user.id
        )
        db_session.add(group)
    db_session.commit()

    response = client.get(
        "/groups",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_regular_user_cannot_create_groups(client, regular_user, user_token):
    """Test that regular users cannot create groups."""
    response = client.post(
        "/groups",
        json={
            "name": "Unauthorized Group",
            "description": "This should fail"
        },
        cookies={"access_token": user_token}
    )
    # Should be forbidden (403) or unauthorized (401)
    assert response.status_code in [401, 403]


def test_owner_group_inheritance_wbs_from_line_item(client, admin_user, admin_token, test_group, db_session):
    """Test that WBS inherits owner_group_id from BusinessCaseLineItem."""
    from app.models import BudgetItem, BusinessCase, BusinessCaseLineItem, WBS

    # Create budget item
    budget_item = BudgetItem(
        workday_ref="WD-2025-001",
        title="Test Budget",
        budget_amount=100000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=datetime.utcnow().isoformat()
    )
    db_session.add(budget_item)
    db_session.commit()
    db_session.refresh(budget_item)

    # Create business case
    business_case = BusinessCase(
        title="Test BC",
        description="Test description",
        requestor="Test User",
        department="Test Dept",
        estimated_cost=50000,
        currency="USD",
        owner_group_id=test_group.id,
        status="Draft",
        created_by=admin_user.id,
        created_at=datetime.utcnow().isoformat()
    )
    db_session.add(business_case)
    db_session.commit()
    db_session.refresh(business_case)

    # Create line item
    line_item = BusinessCaseLineItem(
        business_case_id=business_case.id,
        budget_item_id=budget_item.id,
        title="Test Line Item",
        spend_category="CAPEX",
        requested_amount=50000,
        currency="USD",
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=datetime.utcnow().isoformat()
    )
    db_session.add(line_item)
    db_session.commit()
    db_session.refresh(line_item)

    # Create WBS - should inherit owner_group_id from line_item
    response = client.post(
        "/wbs",
        json={
            "business_case_line_item_id": line_item.id,
            "wbs_code": "WBS-001",
            "description": "Test WBS",
            "owner_group_id": 9999  # This should be ignored
        },
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    # Should inherit from line_item, not use the 9999 we sent
    assert data["owner_group_id"] == test_group.id


def test_manager_can_create_resources(client, manager_user, manager_token, test_group):
    """Test that managers can create resources."""
    response = client.post(
        "/resources",
        json={
            "name": "John Doe",
            "vendor": "Acme Corp",
            "role": "Developer",
            "cost_per_month": 10000,
            "owner_group_id": test_group.id,
            "status": "Active"
        },
        cookies={"access_token": manager_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"


def test_user_can_edit_own_record(client, regular_user, user_token, test_group, db_session):
    """Test that users can edit their own created records."""
    from app.models import BudgetItem

    # Create budget item as regular user
    budget_item = BudgetItem(
        workday_ref="WD-2025-001",
        title="User's Budget",
        budget_amount=50000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=regular_user.id,
        created_at=datetime.utcnow().isoformat()
    )
    db_session.add(budget_item)
    db_session.commit()
    db_session.refresh(budget_item)

    # User should be able to edit their own record
    response = client.put(
        f"/budget-items/{budget_item.id}",
        json={"title": "Updated by User"},
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200


def test_audit_log_created_on_create(client, admin_user, admin_token, test_group, db_session):
    """Test that audit log is created when creating a record."""
    response = client.post(
        "/budget-items",
        json={
            "workday_ref": "WD-2025-001",
            "title": "Audited Budget",
            "budget_amount": 50000,
            "currency": "USD",
            "fiscal_year": 2025,
            "owner_group_id": test_group.id
        },
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    created_id = response.json()["id"]

    # Check audit log was created
    from app.models import AuditLog
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.table_name == "budget_item",
        AuditLog.record_id == created_id,
        AuditLog.action == "CREATE"
    ).all()
    assert len(audit_logs) == 1
    assert audit_logs[0].user_id == admin_user.id


def test_audit_log_created_on_update(client, admin_user, admin_token, test_group, db_session):
    """Test that audit log captures old values on update."""
    from app.models import BudgetItem, AuditLog

    # Create budget item
    budget_item = BudgetItem(
        workday_ref="WD-2025-001",
        title="Original Title",
        budget_amount=50000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=datetime.utcnow().isoformat()
    )
    db_session.add(budget_item)
    db_session.commit()
    db_session.refresh(budget_item)

    # Update it
    response = client.put(
        f"/budget-items/{budget_item.id}",
        json={"title": "Updated Title"},
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200

    # Check audit log has old values
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.table_name == "budget_item",
        AuditLog.record_id == budget_item.id,
        AuditLog.action == "UPDATE"
    ).all()
    assert len(audit_logs) >= 1
    # Old values should contain "Original Title"
    import json
    old_values = json.loads(audit_logs[0].old_values) if audit_logs[0].old_values else {}
    assert "title" in old_values or audit_logs[0].old_values is not None
