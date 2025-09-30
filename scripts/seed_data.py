"""
Seed script to populate the Lunaxcode API database with initial data.
Run this after creating the database schema with Alembic migrations.

Usage: python scripts/seed_data.py
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import re

# Add parent directory to path to import api modules
sys.path.append(str(Path(__file__).parent.parent))

from api.models import (
    PricingPlan, Addon, Service, Feature,
    CompanyInfo, OnboardingQuestion
)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Convert to sync format for seeding (uses psycopg2-binary)
database_url = DATABASE_URL
database_url = re.sub(r'[?&]sslmode=[^&]*', '', database_url)
database_url = re.sub(r'[?&]channel_binding=[^&]*', '', database_url)
# Ensure it's standard postgresql:// for psycopg2
if '+asyncpg' in database_url:
    database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')

# Seed data
PRICING_PLANS = [
    {
        "id": "landing_page",
        "name": "Landing Page",
        "price": 8000,
        "currency": "PHP",
        "timeline": "48-hour delivery",
        "features": [
            "1 Professional Landing Page",
            "AI Chat Widget Integration",
            "Mobile Responsive Design",
            "Basic SEO Optimization",
            "Google Analytics Setup",
            "1 Round of Revisions"
        ],
        "popular": False
    },
    {
        "id": "basic_website",
        "name": "Basic Website",
        "price": 18000,
        "currency": "PHP",
        "timeline": "5-7 days delivery",
        "features": [
            "3-5 Static Pages",
            "AI Chat Widget",
            "Mobile Responsive Design",
            "SEO Optimization",
            "Analytics Integration",
            "Contact Forms",
            "2 Rounds of Revisions"
        ],
        "popular": False
    },
    {
        "id": "advanced_website",
        "name": "Advanced Website",
        "price": 40000,
        "currency": "PHP",
        "timeline": "2-3 weeks delivery",
        "features": [
            "8-12 Pages",
            "Content Management System",
            "Advanced AI Features",
            "Advanced SEO & Analytics",
            "Blog Setup",
            "E-commerce Ready",
            "3 Rounds of Revisions"
        ],
        "popular": False
    },
    {
        "id": "basic_mobile_app",
        "name": "Basic Mobile App",
        "price": 80000,
        "currency": "PHP",
        "timeline": "4-6 weeks delivery",
        "features": [
            "iOS + Android (Cross-platform)",
            "Basic UI/UX Design",
            "Core Functionality",
            "AI Integration",
            "App Store Submission",
            "Basic Analytics",
            "3 Months Support"
        ],
        "popular": False
    },
    {
        "id": "advanced_mobile_app",
        "name": "Advanced Mobile App",
        "price": 150000,
        "currency": "PHP",
        "timeline": "8-12 weeks delivery",
        "features": [
            "iOS + Android (Cross-platform)",
            "Custom UI/UX Design",
            "Backend Integration",
            "Push Notifications",
            "Advanced AI Features",
            "Payment Integration",
            "6 Months Support"
        ],
        "popular": False
    }
]

ADDONS = [
    {
        "name": "Additional Pages",
        "price_range": "1500-2000",
        "currency": "PHP",
        "unit": "each"
    },
    {
        "name": "AI Content Generation",
        "price_range": "3000-5000",
        "currency": "PHP",
        "unit": "project"
    },
    {
        "name": "Monthly Maintenance",
        "price_range": "3000-5000",
        "currency": "PHP",
        "unit": "monthly"
    }
]

SERVICES = [
    {
        "id": "landing_page",
        "name": "Landing Page",
        "description": "48-Hour Landing Pages",
        "details": "While competitors take 3-5 days minimum, we deliver professional landing pages in just 48 hours. No compromises on quality.",
        "icon": "⚡",
        "timeline": "48 hours"
    },
    {
        "id": "basic_website",
        "name": "Basic Website",
        "description": "Full Website Development",
        "details": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
        "icon": "🌐",
        "timeline": "5-7 days"
    },
    {
        "id": "advanced_website",
        "name": "Advanced Website",
        "description": "Full Website Development",
        "details": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
        "icon": "🌐",
        "timeline": "2-3 weeks"
    },
    {
        "id": "basic_mobile_app",
        "name": "Basic Mobile App",
        "description": "Mobile App Development",
        "details": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
        "icon": "📱",
        "timeline": "4-6 weeks"
    },
    {
        "id": "advanced_mobile_app",
        "name": "Advanced Mobile App",
        "description": "Mobile App Development",
        "details": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
        "icon": "📱",
        "timeline": "8-12 weeks"
    }
]

FEATURES = [
    {
        "icon": "⚡",
        "title": "48-Hour Landing Pages",
        "description": "While competitors take 3-5 days minimum, we deliver professional landing pages in just 48 hours. No compromises on quality.",
        "display_order": 1
    },
    {
        "icon": "🌐",
        "title": "Full Website Development",
        "description": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
        "display_order": 2
    },
    {
        "icon": "📱",
        "title": "Mobile App Development",
        "description": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
        "display_order": 3
    },
    {
        "icon": "🤖",
        "title": "AI Integration Included",
        "description": "Every project comes with intelligent AI features - chat widgets for websites, smart features for mobile apps.",
        "display_order": 4
    },
    {
        "icon": "💰",
        "title": "SME-Friendly Pricing",
        "description": "Starting at just ₱8,000 for landing pages, ₱18,000 for websites, and ₱80,000 for mobile apps. Affordable for all business sizes.",
        "display_order": 5
    },
    {
        "icon": "🔧",
        "title": "AI-Powered Development",
        "description": "Using cutting-edge AI tools to accelerate development while maintaining high quality and modern design standards across all services.",
        "display_order": 6
    }
]

COMPANY_INFO = {
    "id": 1,
    "name": "Lunaxcode",
    "tagline": "Code at the Speed of Light",
    "description": "Professional websites and mobile apps for Filipino SMEs",
    "contact": {
        "email": "hello@lunaxcode.site",
        "phone": "+63 912 345 6789",
        "location": "Antipolo City, Rizal, Philippines"
    },
    "payment_terms": {
        "deposit": "30-50%",
        "balance": "on delivery",
        "methods": ["GCash", "PayMaya", "Bank Transfer"]
    }
}

ONBOARDING_QUESTIONS = [
    {
        "service_type": "landing_page",
        "title": "Landing Page Requirements",
        "questions": [
            {
                "id": "pageType",
                "label": "What type of landing page?",
                "type": "select",
                "options": ["Product Launch", "Lead Generation", "Event Registration", "App Download", "Service Promotion", "Newsletter Signup"],
                "required": True
            },
            {
                "id": "designStyle",
                "label": "Preferred design style",
                "type": "select",
                "options": ["Modern/Minimalist", "Bold/Colorful", "Professional/Corporate", "Creative/Artistic", "Tech/Startup"],
                "required": True
            },
            {
                "id": "sections",
                "label": "Required sections",
                "type": "checkbox",
                "options": ["Hero Section", "Features/Benefits", "Testimonials", "Pricing", "FAQ", "Contact Form", "About Us", "Gallery/Portfolio"],
                "required": True
            },
            {
                "id": "ctaGoal",
                "label": "Primary call-to-action goal",
                "type": "text",
                "placeholder": "e.g., Sign up for free trial, Download app, Contact sales...",
                "required": True
            }
        ]
    },
    {
        "service_type": "basic_website",
        "title": "Website Requirements",
        "questions": [
            {
                "id": "websiteType",
                "label": "Website type",
                "type": "select",
                "options": ["Corporate Website", "Portfolio", "Blog/News", "E-commerce", "Directory/Listing", "Educational", "Non-profit"],
                "required": True
            },
            {
                "id": "pageCount",
                "label": "Approximate number of pages",
                "type": "select",
                "options": ["3-5 pages", "6-10 pages", "11-20 pages", "20+ pages"],
                "required": True
            },
            {
                "id": "features",
                "label": "Required features",
                "type": "checkbox",
                "options": ["Contact Forms", "Blog/News Section", "Image Gallery", "Video Integration", "Social Media Integration", "Newsletter Signup", "Online Booking", "User Accounts"],
                "required": True
            },
            {
                "id": "contentSource",
                "label": "Content source",
                "type": "select",
                "options": ["I will provide all content", "I need help with copywriting", "Mix of both"],
                "required": True
            }
        ]
    },
    {
        "service_type": "advanced_website",
        "title": "Advanced Website Requirements",
        "questions": [
            {
                "id": "websiteType",
                "label": "Website type",
                "type": "select",
                "options": ["Corporate Website", "Portfolio", "Blog/News", "E-commerce", "Directory/Listing", "Educational", "Non-profit"],
                "required": True
            },
            {
                "id": "pageCount",
                "label": "Approximate number of pages",
                "type": "select",
                "options": ["3-5 pages", "6-10 pages", "11-20 pages", "20+ pages"],
                "required": True
            },
            {
                "id": "features",
                "label": "Required features",
                "type": "checkbox",
                "options": ["Contact Forms", "Blog/News Section", "Image Gallery", "Video Integration", "Social Media Integration", "Newsletter Signup", "Online Booking", "User Accounts", "CMS", "E-commerce", "Multi-language"],
                "required": True
            },
            {
                "id": "contentSource",
                "label": "Content source",
                "type": "select",
                "options": ["I will provide all content", "I need help with copywriting", "Mix of both"],
                "required": True
            }
        ]
    },
    {
        "service_type": "basic_mobile_app",
        "title": "Mobile App Requirements",
        "questions": [
            {
                "id": "appCategory",
                "label": "App category",
                "type": "select",
                "options": ["Business/Productivity", "Social Networking", "E-commerce/Shopping", "Health/Fitness", "Education", "Entertainment", "Finance", "Food & Drink"],
                "required": True
            },
            {
                "id": "platforms",
                "label": "Target platforms",
                "type": "checkbox",
                "options": ["iOS (iPhone/iPad)", "Android", "Both Platforms"],
                "required": True
            },
            {
                "id": "coreFeatures",
                "label": "Core features needed",
                "type": "checkbox",
                "options": ["User Registration/Login", "Push Notifications", "Offline Mode", "Camera/Photos", "GPS/Location", "Social Sharing", "In-app Purchases", "Real-time Chat"],
                "required": True
            },
            {
                "id": "backend",
                "label": "Backend requirements",
                "type": "checkbox",
                "options": ["User Management", "Data Storage", "Push Notifications", "Analytics", "Payment Processing", "File Storage", "API Integration"],
                "required": True
            }
        ]
    },
    {
        "service_type": "advanced_mobile_app",
        "title": "Advanced Mobile App Requirements",
        "questions": [
            {
                "id": "appCategory",
                "label": "App category",
                "type": "select",
                "options": ["Business/Productivity", "Social Networking", "E-commerce/Shopping", "Health/Fitness", "Education", "Entertainment", "Finance", "Food & Drink"],
                "required": True
            },
            {
                "id": "platforms",
                "label": "Target platforms",
                "type": "checkbox",
                "options": ["iOS (iPhone/iPad)", "Android", "Both Platforms"],
                "required": True
            },
            {
                "id": "coreFeatures",
                "label": "Core features needed",
                "type": "checkbox",
                "options": ["User Registration/Login", "Push Notifications", "Offline Mode", "Camera/Photos", "GPS/Location", "Social Sharing", "In-app Purchases", "Real-time Chat", "Advanced Analytics", "Custom Integrations"],
                "required": True
            },
            {
                "id": "backend",
                "label": "Backend requirements",
                "type": "checkbox",
                "options": ["User Management", "Data Storage", "Push Notifications", "Analytics", "Payment Processing", "File Storage", "API Integration", "Real-time Features", "Advanced Security"],
                "required": True
            }
        ]
    }
]


def seed_database():
    """Populate database with initial data"""
    print("🌱 Starting database seeding...")

    engine = create_engine(database_url)
    session = Session(engine)

    try:
        # Clear existing data (optional - comment out for production)
        print("🗑️  Clearing existing data...")
        session.query(OnboardingQuestion).delete()
        session.query(CompanyInfo).delete()
        session.query(Feature).delete()
        session.query(Service).delete()
        session.query(Addon).delete()
        session.query(PricingPlan).delete()
        session.commit()

        # Insert Services first (referenced by other tables)
        print("📦 Inserting services...")
        for service_data in SERVICES:
            service = Service(**service_data)
            session.add(service)
        session.commit()
        print(f"✅ Inserted {len(SERVICES)} services")

        # Insert Pricing Plans
        print("💰 Inserting pricing plans...")
        for plan_data in PRICING_PLANS:
            plan = PricingPlan(**plan_data)
            session.add(plan)
        session.commit()
        print(f"✅ Inserted {len(PRICING_PLANS)} pricing plans")

        # Insert Add-ons
        print("🔧 Inserting add-ons...")
        for addon_data in ADDONS:
            addon = Addon(**addon_data)
            session.add(addon)
        session.commit()
        print(f"✅ Inserted {len(ADDONS)} add-ons")

        # Insert Features
        print("⭐ Inserting features...")
        for feature_data in FEATURES:
            feature = Feature(**feature_data)
            session.add(feature)
        session.commit()
        print(f"✅ Inserted {len(FEATURES)} features")

        # Insert Company Info
        print("🏢 Inserting company info...")
        company = CompanyInfo(**COMPANY_INFO)
        session.add(company)
        session.commit()
        print("✅ Inserted company info")

        # Insert Onboarding Questions
        print("📝 Inserting onboarding questions...")
        for question_data in ONBOARDING_QUESTIONS:
            question = OnboardingQuestion(**question_data)
            session.add(question)
        session.commit()
        print(f"✅ Inserted {len(ONBOARDING_QUESTIONS)} question sets")

        print("\n🎉 Database seeding completed successfully!")

        # Verify counts
        print("\n📊 Verification:")
        print(f"  - Services: {session.query(Service).count()}")
        print(f"  - Pricing Plans: {session.query(PricingPlan).count()}")
        print(f"  - Add-ons: {session.query(Addon).count()}")
        print(f"  - Features: {session.query(Feature).count()}")
        print(f"  - Company Info: {session.query(CompanyInfo).count()}")
        print(f"  - Onboarding Questions: {session.query(OnboardingQuestion).count()}")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()