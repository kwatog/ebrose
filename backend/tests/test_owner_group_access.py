import pytest

from app.auth import now_utc


def test_list_budget_items_filters_by_owner_group(client, admin_user, regular_user, user_token, test_group, db_session):
    """Test that list endpoints filter by owner_group_id membership."""
    from app.models import BudgetItem, UserGroupMembership

    # Create a budget item owned by test_group (admin is member)
    budget1 = BudgetItem(
        workday_ref="WD-TEST-001",
        title="Group Budget",
        budget_amount=10000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(budget1)

    # Create another budget owned by non-existent group (regular_user is NOT member)
    budget2 = BudgetItem(
        workday_ref="WD-TEST-002",
        title="Other Group Budget",
        budget_amount=20000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=999,  # Group that regular_user is not member of
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(budget2)
    db_session.commit()

    # Regular user should only see budgets from their groups OR created by them
    response = client.get(
        "/budget-items",
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    data = response.json()

    # Regular user is not in test_group, so should see 0 items (or only created by them)
    # Since admin created both, regular user sees neither
    assert len(data) == 0


def test_user_in_owner_group_membership(client, regular_user, user_token, test_group, db_session):
    """Test that users in owner group can access records."""
    from app.models import BudgetItem, UserGroupMembership

    # Add regular_user to test_group
    membership = UserGroupMembership(
        user_id=regular_user.id,
        group_id=test_group.id
    )
    db_session.add(membership)
    db_session.commit()

    # Create budget owned by test_group
    budget = BudgetItem(
        workday_ref="WD-MEMBER-001",
        title="Member Access Budget",
        budget_amount=50000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=1,  # Some other user
        created_at=now_utc()
    )
    db_session.add(budget)
    db_session.commit()
    db_session.refresh(budget)

    # Now regular_user should see this budget
    response = client.get(
        "/budget-items",
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["workday_ref"] == "WD-MEMBER-001"


def test_creator_can_see_own_records_regardless_of_group(client, regular_user, user_token, test_group, db_session):
    """Test that record creators can always see their own records."""
    from app.models import BudgetItem

    # Create budget with group regular_user is NOT member of
    budget = BudgetItem(
        workday_ref="WD-CREATOR-001",
        title="Creator Budget",
        budget_amount=30000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=999,  # Group regular_user is not member of
        created_by=regular_user.id,  # But they created it
        created_at=now_utc()
    )
    db_session.add(budget)
    db_session.commit()

    # Regular user should see their own creation
    response = client.get(
        "/budget-items",
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["workday_ref"] == "WD-CREATOR-001"


def test_admin_sees_all_records(client, admin_user, admin_token, test_group, db_session):
    """Test that Admin sees all records regardless of owner_group_id."""
    from app.models import BudgetItem

    # Create budgets with different owner groups
    for i in range(3):
        budget = BudgetItem(
            workday_ref=f"WD-ADMIN-{i:03d}",
            title=f"Budget {i}",
            budget_amount=10000 * (i + 1),
            currency="USD",
            fiscal_year=2025,
            owner_group_id=i + 1,  # Different groups
            created_by=1,
            created_at=now_utc()
        )
        db_session.add(budget)
    db_session.commit()

    # Admin should see all 3
    response = client.get(
        "/budget-items",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_line_items_filters_by_owner_group(client, regular_user, user_token, test_group, db_session):
    """Test that business case line items are filtered by owner_group_id."""
    from app.models import BudgetItem, BusinessCase, BusinessCaseLineItem, UserGroupMembership

    # Add regular_user to test_group
    membership = UserGroupMembership(
        user_id=regular_user.id,
        group_id=test_group.id
    )
    db_session.add(membership)

    # Create budget item
    budget = BudgetItem(
        workday_ref="WD-LINE-001",
        title="Line Item Budget",
        budget_amount=100000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=regular_user.id,
        created_at=now_utc()
    )
    db_session.add(budget)

    # Create business case
    bc = BusinessCase(
        title="Test BC",
        description="Test",
        status="Draft",
        created_by=regular_user.id,
        created_at=now_utc()
    )
    db_session.add(bc)
    db_session.commit()
    db_session.refresh(budget)
    db_session.refresh(bc)

    # Create line item owned by test_group
    line_item = BusinessCaseLineItem(
        business_case_id=bc.id,
        budget_item_id=budget.id,
        title="Accessible Line Item",
        spend_category="CAPEX",
        requested_amount=50000,
        currency="USD",
        owner_group_id=test_group.id,
        created_by=regular_user.id,
        created_at=now_utc()
    )
    db_session.add(line_item)
    db_session.commit()

    # Regular user should see this line item
    response = client.get(
        "/business-case-line-items",
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["title"] == "Accessible Line Item" for item in data)


def test_list_wbs_filters_by_owner_group(client, regular_user, user_token, test_group, db_session):
    """Test that WBS items are filtered by owner_group_id."""
    from app.models import BudgetItem, BusinessCase, BusinessCaseLineItem, WBS, UserGroupMembership

    # Add regular_user to test_group
    membership = UserGroupMembership(
        user_id=regular_user.id,
        group_id=test_group.id
    )
    db_session.add(membership)

    # Create required parent entities
    budget = BudgetItem(
        workday_ref="WD-WBS-001",
        title="WBS Budget",
        budget_amount=100000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=regular_user.id,
        created_at=now_utc()
    )
    db_session.add(budget)

    bc = BusinessCase(
        title="WBS BC",
        description="Test",
        status="Draft",
        created_by=regular_user.id,
        created_at=now_utc()
    )
    db_session.add(bc)
    db_session.commit()
    db_session.refresh(budget)
    db_session.refresh(bc)

    line_item = BusinessCaseLineItem(
        business_case_id=bc.id,
        budget_item_id=budget.id,
        title="WBS Line Item",
        spend_category="CAPEX",
        requested_amount=50000,
        currency="USD",
        owner_group_id=test_group.id,
        created_by=regular_user.id,
        created_at=now_utc()
    )
    db_session.add(line_item)
    db_session.commit()
    db_session.refresh(line_item)

    # Create WBS owned by test_group
    wbs = WBS(
        business_case_line_item_id=line_item.id,
        wbs_code="WBS-ACCESS-001",
        description="Accessible WBS",
        owner_group_id=test_group.id,
        created_by=regular_user.id,
        created_at=now_utc()
    )
    db_session.add(wbs)
    db_session.commit()

    # Regular user should see this WBS
    response = client.get(
        "/wbs",
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["wbs_code"] == "WBS-ACCESS-001" for item in data)


def test_check_record_access_verifies_owner_group(client, admin_user, regular_user, user_token, test_group, db_session):
    """Test that check_record_access verifies owner_group_id membership."""
    from app.models import BudgetItem

    # Create budget with group regular_user is NOT member of, created by admin (different user)
    budget = BudgetItem(
        workday_ref="WD-DENIED-001",
        title="No Access Budget",
        budget_amount=75000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=999,  # Group that doesn't exist / user not member
        created_by=admin_user.id,  # Created by admin, not regular_user
        created_at=now_utc()
    )
    db_session.add(budget)
    db_session.commit()
    db_session.refresh(budget)

    # Try to access specific budget - should get 403 or 404 (depending on implementation)
    response = client.get(
        f"/budget-items/{budget.id}",
        cookies={"access_token": user_token}
    )
    # Should be denied (403 Forbidden)
    assert response.status_code in [403, 404]
