from datetime import datetime, timezone
from decimal import Decimal

from app.auth import now_utc
from app import models


def test_dashboard_summary_scoped_to_group_and_years(client, admin_user, admin_token, test_group, db_session):
    current_year = now_utc().year
    previous_year = current_year - 1

    budget_current = models.BudgetItem(
        workday_ref="WD-CUR-001",
        title="Current Year Budget",
        budget_amount=Decimal("1000.00"),
        currency="USD",
        fiscal_year=current_year,
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=now_utc()
    )
    budget_previous = models.BudgetItem(
        workday_ref="WD-PREV-001",
        title="Previous Year Budget",
        budget_amount=Decimal("800.00"),
        currency="USD",
        fiscal_year=previous_year,
        owner_group_id=test_group.id,
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add_all([budget_current, budget_previous])
    db_session.flush()

    business_case = models.BusinessCase(
        title="Dashboard Summary Case",
        status="Draft",
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(business_case)
    db_session.flush()

    line_item = models.BusinessCaseLineItem(
        business_case_id=business_case.id,
        budget_item_id=budget_current.id,
        owner_group_id=test_group.id,
        title="Line Item",
        spend_category="OPEX",
        requested_amount=Decimal("500.00"),
        currency="USD",
        status="Approved",
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(line_item)
    db_session.flush()

    wbs = models.WBS(
        business_case_line_item_id=line_item.id,
        wbs_code="WBS-DASH-001",
        owner_group_id=test_group.id,
        status="Active",
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(wbs)
    db_session.flush()

    asset = models.Asset(
        wbs_id=wbs.id,
        asset_code="ASSET-DASH-001",
        asset_type="OPEX",
        description="Dashboard Asset",
        owner_group_id=test_group.id,
        status="Active",
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add(asset)
    db_session.flush()

    po_current = models.PurchaseOrder(
        asset_id=asset.id,
        po_number="PO-DASH-001",
        supplier="Vendor A",
        total_amount=Decimal("400.00"),
        currency="USD",
        spend_category="OPEX",
        planned_commit_date=datetime(current_year, 1, 15, tzinfo=timezone.utc),
        owner_group_id=test_group.id,
        status="Open",
        created_by=admin_user.id,
        created_at=now_utc()
    )
    po_previous = models.PurchaseOrder(
        asset_id=asset.id,
        po_number="PO-DASH-002",
        supplier="Vendor B",
        total_amount=Decimal("300.00"),
        currency="USD",
        spend_category="OPEX",
        planned_commit_date=datetime(previous_year, 6, 1, tzinfo=timezone.utc),
        owner_group_id=test_group.id,
        status="Approved",
        created_by=admin_user.id,
        created_at=now_utc()
    )
    db_session.add_all([po_current, po_previous])
    db_session.commit()

    response = client.get(
        f"/dashboard/summary?owner_group_id={test_group.id}",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["group"]["id"] == test_group.id
    assert data["current_year"] == current_year
    assert data["previous_year"] == previous_year

    assert Decimal(data["budgets"]["current_year_total"]) == Decimal("1000.00")
    assert Decimal(data["budgets"]["previous_year_total"]) == Decimal("800.00")
    assert data["budgets"]["current_year_count"] == 1
    assert data["budgets"]["previous_year_count"] == 1

    assert Decimal(data["spend"]["current_year_total"]) == Decimal("400.00")
    assert Decimal(data["spend"]["previous_year_total"]) == Decimal("300.00")

    assert data["open_pos"]["count"] == 2
    assert Decimal(data["open_pos"]["value"]) == Decimal("700.00")
