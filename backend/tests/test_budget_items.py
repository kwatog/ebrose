import pytest

from app.auth import now_utc


def test_create_budget_item(client, admin_user, admin_token, test_group):
    """Test creating a budget item."""
    response = client.post(
        "/budget-items",
        json={
            "workday_ref": "WD-2025-001",
            "title": "IT Infrastructure Budget",
            "description": "Budget for IT infrastructure",
            "budget_amount": 100000.00,
            "currency": "USD",
            "fiscal_year": 2025,
            "owner_group_id": test_group.id
        },
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["workday_ref"] == "WD-2025-001"
    assert data["title"] == "IT Infrastructure Budget"
    assert data["budget_amount"] == "100000.00"  # Decimal serializes to string
    assert data["fiscal_year"] == 2025
    assert data["created_by"] == admin_user.id


def test_create_budget_item_duplicate_workday_ref(client, admin_user, admin_token, test_group, db_session):
    """Test creating budget item with duplicate workday_ref fails."""
    from app.models import BudgetItem

    # Create first budget item
    budget_item = BudgetItem(
        workday_ref="WD-2025-001",
        title="First Budget",
        budget_amount=50000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(budget_item)
    db_session.commit()

    # Try to create duplicate
    response = client.post(
        "/budget-items",
        json={
            "workday_ref": "WD-2025-001",
            "title": "Duplicate Budget",
            "budget_amount": 60000,
            "currency": "USD",
            "fiscal_year": 2025,
            "owner_group_id": test_group.id
        },
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 400 or response.status_code == 500  # Unique constraint violation


def test_list_budget_items(client, admin_user, admin_token, test_group, db_session):
    """Test listing budget items."""
    from app.models import BudgetItem

    # Create test budget items
    for i in range(3):
        budget_item = BudgetItem(
            workday_ref=f"WD-2025-{i:03d}",
            title=f"Budget {i}",
            budget_amount=10000 * (i + 1),
            currency="USD",
            fiscal_year=2025,
            owner_group_id=test_group.id,
            created_by=admin_user.id,
            created_at=now_utc()
        )
        db_session.add(budget_item)
    db_session.commit()

    response = client.get(
        "/budget-items",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_update_budget_item(client, admin_user, admin_token, test_group, db_session):
    """Test updating a budget item."""
    from app.models import BudgetItem

    budget_item = BudgetItem(
        workday_ref="WD-2025-001",
        title="Original Title",
        budget_amount=50000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(budget_item)
    db_session.commit()
    db_session.refresh(budget_item)

    response = client.put(
        f"/budget-items/{budget_item.id}",
        json={
            "title": "Updated Title",
            "budget_amount": 75000
        },
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["budget_amount"] == "75000.00"  # Decimal serializes to string
    assert data["updated_by"] == admin_user.id


def test_delete_budget_item(client, admin_user, admin_token, test_group, db_session):
    """Test deleting a budget item."""
    from app.models import BudgetItem

    budget_item = BudgetItem(
        workday_ref="WD-2025-001",
        title="To Be Deleted",
        budget_amount=50000,
        currency="USD",
        fiscal_year=2025,
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(budget_item)
    db_session.commit()
    db_session.refresh(budget_item)

    response = client.delete(
        f"/budget-items/{budget_item.id}",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200

    # Verify deleted
    response = client.get(
        f"/budget-items/{budget_item.id}",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 404


def test_pagination_budget_items(client, admin_user, admin_token, test_group, db_session):
    """Test pagination on budget items list."""
    from app.models import BudgetItem

    # Create 10 budget items
    for i in range(10):
        budget_item = BudgetItem(
            workday_ref=f"WD-2025-{i:03d}",
            title=f"Budget {i}",
            budget_amount=10000,
            currency="USD",
            fiscal_year=2025,
            owner_group_id=test_group.id,
            created_by=admin_user.id,
            created_at=now_utc()
        )
        db_session.add(budget_item)
    db_session.commit()

    # Test first page
    response = client.get(
        "/budget-items?skip=0&limit=5",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

    # Test second page
    response = client.get(
        "/budget-items?skip=5&limit=5",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
