"""Pricing plan endpoint tests"""

import pytest
from api.models.pricing import PricingPlan


@pytest.fixture
def sample_pricing_plan(db_session):
    """Create sample pricing plan for testing"""
    plan = PricingPlan(
        id="test_plan",
        name="Test Plan",
        price=10000,
        currency="PHP",
        timeline="3 days",
        features=["Feature 1", "Feature 2"],
        popular=False
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


def test_get_pricing_plans_empty(client):
    """Test getting pricing plans when none exist"""
    response = client.get("/api/v1/pricing")
    assert response.status_code == 200
    assert response.json() == []


def test_get_pricing_plans(client, sample_pricing_plan):
    """Test getting all pricing plans"""
    response = client.get("/api/v1/pricing")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "test_plan"
    assert data[0]["name"] == "Test Plan"


def test_get_pricing_plan_by_id(client, sample_pricing_plan):
    """Test getting specific pricing plan"""
    response = client.get("/api/v1/pricing/test_plan")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test_plan"
    assert data["price"] == 10000


def test_get_pricing_plan_not_found(client):
    """Test getting non-existent pricing plan"""
    response = client.get("/api/v1/pricing/nonexistent")
    assert response.status_code == 404


def test_create_pricing_plan(client, api_key):
    """Test creating pricing plan with admin auth"""
    plan_data = {
        "id": "new_plan",
        "name": "New Plan",
        "price": 15000,
        "currency": "PHP",
        "timeline": "5 days",
        "features": ["Feature A", "Feature B"],
        "popular": True
    }
    response = client.post(
        "/api/v1/pricing",
        json=plan_data,
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "new_plan"
    assert data["popular"] is True


def test_create_pricing_plan_without_auth(client):
    """Test creating pricing plan without authentication"""
    plan_data = {
        "id": "new_plan",
        "name": "New Plan",
        "price": 15000,
        "currency": "PHP",
        "timeline": "5 days",
        "features": ["Feature A"],
        "popular": False
    }
    response = client.post("/api/v1/pricing", json=plan_data)
    assert response.status_code == 403