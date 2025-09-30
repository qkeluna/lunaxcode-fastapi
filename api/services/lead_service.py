"""Lead service with AI prompt generation"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List, Optional
from api.models.lead import Lead
from api.models.pricing import PricingPlan
from api.models.onboarding import OnboardingQuestion
from api.schemas.lead import LeadCreate, LeadUpdate
from api.utils.exceptions import NotFoundException, ValidationException


def format_ai_prompt(lead_data: Dict[str, Any], pricing_info: Dict[str, Any], questions: List[Dict[str, Any]]) -> str:
    """
    Convert structured lead data into AI-friendly prompt format.

    This is the critical business logic for dual data storage.
    The generated prompt is optimized for AI/LLM consumption.

    Args:
        lead_data: The lead submission data
        pricing_info: Pricing and timeline information for the service
        questions: Question definitions for the service type

    Returns:
        Formatted prompt string ready for AI processing
    """
    # Build header
    prompt_parts = [
        f"Project: {pricing_info['name']} for {lead_data['full_name']}",
    ]

    if lead_data.get('company'):
        prompt_parts[0] += f" ({lead_data['company']})"

    prompt_parts.extend([
        f"Service Type: {pricing_info['name']}",
        f"Email: {lead_data['email']}",
    ])

    if lead_data.get('phone'):
        prompt_parts.append(f"Phone: {lead_data['phone']}")

    # Project description
    prompt_parts.extend([
        "",
        "Project Description:",
        lead_data.get('project_description', 'Not provided'),
        "",
        "Requirements:"
    ])

    # Format answers based on question labels
    answers = lead_data['answers']
    question_map = {q['id']: q for q in questions}

    for q_id, value in answers.items():
        if q_id in question_map:
            label = question_map[q_id]['label']

            # Format arrays nicely
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)

            prompt_parts.append(f"- {label}: {value}")

    # Add pricing and timeline
    prompt_parts.extend([
        "",
        f"Timeline: {pricing_info['timeline']}",
        f"Price: ₱{pricing_info['price']:,}"
    ])

    return "\n".join(prompt_parts)


async def create_lead(lead_create: LeadCreate, db: AsyncSession) -> Lead:
    """
    Create a new lead with both structured answers and AI prompt.

    This function implements the dual data storage pattern:
    1. Store structured answers (JSONB) for SQL queries
    2. Generate and store AI-formatted prompt (TEXT) for LLM usage
    """
    # Get pricing information
    result = await db.execute(
        select(PricingPlan).filter(PricingPlan.id == lead_create.service_type)
    )
    pricing = result.scalar_one_or_none()

    if not pricing:
        raise ValidationException(f"Invalid service type: {lead_create.service_type}")

    # Get questions for this service type
    result = await db.execute(
        select(OnboardingQuestion).filter(OnboardingQuestion.service_type == lead_create.service_type)
    )
    onboarding = result.scalar_one_or_none()

    if not onboarding:
        raise ValidationException(f"No onboarding questions found for service type: {lead_create.service_type}")

    # Generate AI prompt
    ai_prompt = format_ai_prompt(
        lead_data=lead_create.model_dump(),
        pricing_info={
            'name': pricing.name,
            'timeline': pricing.timeline,
            'price': pricing.price
        },
        questions=onboarding.questions
    )

    # Create lead with both formats
    lead = Lead(
        **lead_create.model_dump(),
        ai_prompt=ai_prompt,
        status="new"
    )

    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return lead


async def get_lead(lead_id: int, db: AsyncSession) -> Lead:
    """Get a lead by ID"""
    result = await db.execute(select(Lead).filter(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise NotFoundException(f"Lead with id {lead_id} not found")
    return lead


async def get_leads(db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Lead]:
    """Get all leads with optional filtering"""
    query = select(Lead)

    if status:
        query = query.filter(Lead.status == status)

    query = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_lead(lead_id: int, lead_update: LeadUpdate, db: AsyncSession) -> Lead:
    """Update lead status"""
    lead = await get_lead(lead_id, db)

    if lead_update.status:
        lead.status = lead_update.status

    await db.commit()
    await db.refresh(lead)

    return lead


async def delete_lead(lead_id: int, db: AsyncSession) -> None:
    """Delete a lead"""
    lead = await get_lead(lead_id, db)
    await db.delete(lead)
    await db.commit()