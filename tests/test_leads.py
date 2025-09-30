"""Lead endpoint tests with dual data storage"""

import pytest
from api.models.service import Service
from api.models.pricing import PricingPlan
from api.models.onboarding import OnboardingQuestion


@pytest.fixture
def setup_lead_dependencies(db_session):
    """Setup required data for lead testing"""
    # Create service
    service = Service(
        id="landing_page",
        name="Landing Page",
        description="Test service",
        details="Test details",
        icon="⚡",
        timeline="48 hours"
    )
    db_session.add(service)

    # Create pricing plan
    pricing = PricingPlan(
        id="landing_page",
        name="Landing Page",
        price=8000,
        currency="PHP",
        timeline="48-hour delivery",
        features=["Feature 1"],
        popular=False
    )
    db_session.add(pricing)

    # Create onboarding questions
    questions = OnboardingQuestion(
        service_type="landing_page",
        title="Landing Page Requirements",
        questions=[
            {
                "id": "pageType",
                "label": "What type of landing page?",
                "type": "select",
                "options": ["Product Launch"],
                "required": True
            }
        ]
    )
    db_session.add(questions)

    db_session.commit()
    return service, pricing, questions


def test_submit_lead(client, setup_lead_dependencies):
    """Test submitting new lead with AI prompt generation"""
    lead_data = {
        "service_type": "landing_page",
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "+63 912 345 6789",
        "company": "Test Corp",
        "project_description": "Test project description",
        "answers": {
            "pageType": "Product Launch"
        }
    }

    response = client.post("/api/v1/leads", json=lead_data)
    assert response.status_code == 201

    data = response.json()
    assert data["full_name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["status"] == "new"

    # Verify AI prompt was generated
    assert "ai_prompt" in data
    assert "Landing Page for Test User" in data["ai_prompt"]
    assert "₱8,000" in data["ai_prompt"]


def test_submit_lead_invalid_phone(client, setup_lead_dependencies):
    """Test submitting lead with invalid phone number"""
    lead_data = {
        "service_type": "landing_page",
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "0912345678",  # Invalid - should start with +63
        "project_description": "Test",
        "answers": {"pageType": "Product Launch"}
    }

    response = client.post("/api/v1/leads", json=lead_data)
    assert response.status_code == 422


def test_get_leads_requires_auth(client):
    """Test that getting leads requires authentication"""
    response = client.get("/api/v1/leads")
    assert response.status_code == 403


def test_get_leads_with_auth(client, api_key, setup_lead_dependencies):
    """Test getting leads with authentication"""
    # First create a lead
    lead_data = {
        "service_type": "landing_page",
        "full_name": "Test User",
        "email": "test@example.com",
        "project_description": "Test",
        "answers": {"pageType": "Product Launch"}
    }
    client.post("/api/v1/leads", json=lead_data)

    # Then get all leads
    response = client.get(
        "/api/v1/leads",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Test User"