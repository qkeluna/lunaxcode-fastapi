#!/usr/bin/env python3
"""
Test script for new onboarding and contact endpoints
Usage: python test_new_endpoints.py
"""

import asyncio
import os
import sys
from uuid import UUID
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "your-api-key-here")

# ANSI color codes
GREEN = "\033[0;32m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
YELLOW = "\033[0;33m"
NC = "\033[0m"  # No Color


async def test_onboarding_submit(client: httpx.AsyncClient):
    """Test: Submit onboarding form (public)"""
    print(f"\n{BLUE}Test 1: POST /onboarding/submit (Public){NC}")
    
    data = {
        "service_type": "website",
        "answers": {
            "fullName": "John Doe",
            "email": "john@example.com",
            "company": "Acme Inc",
            "phone": "+1234567890",
            "websiteType": "e-commerce",
            "pages": ["Home", "Shop", "About"],
            "timeline": "2-4 weeks"
        },
        "metadata": {
            "timestamp": 1696345678,
            "referrer": "https://google.com"
        }
    }
    
    response = await client.post(f"{API_URL}/onboarding/submit", json=data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"{GREEN}✓ Success! Submission created{NC}")
        print(f"  Submission ID: {result.get('submission_id')}")
        print(f"  Message: {result.get('message')}")
        return result.get('submission_id')
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")
        return None


async def test_contact_submit(client: httpx.AsyncClient):
    """Test: Submit contact form (public)"""
    print(f"\n{BLUE}Test 2: POST /contact/submit (Public){NC}")
    
    data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "subject": "Project Inquiry",
        "message": "I'm interested in building a web application for my business. Can we schedule a call?",
        "metadata": {
            "source": "homepage",
            "timestamp": 1696345678
        }
    }
    
    response = await client.post(f"{API_URL}/contact/submit", json=data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"{GREEN}✓ Success! Contact submitted{NC}")
        print(f"  Message ID: {result.get('message_id')}")
        print(f"  Message: {result.get('message')}")
        return result.get('message_id')
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")
        return None


async def test_submission_status(client: httpx.AsyncClient, submission_id: str):
    """Test: Check submission status (public)"""
    print(f"\n{BLUE}Test 3: GET /submissions/{{id}}/status (Public){NC}")
    
    if not submission_id:
        print(f"{YELLOW}⊘ Skipped: No submission ID available{NC}")
        return
    
    response = await client.get(f"{API_URL}/submissions/{submission_id}/status")
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✓ Success! Status retrieved{NC}")
        print(f"  Status: {result.get('status')}")
        print(f"  Payment Status: {result.get('payment_status')}")
        print(f"  Created: {result.get('created_at')}")
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")


async def test_list_onboarding_submissions(client: httpx.AsyncClient):
    """Test: List onboarding submissions (admin)"""
    print(f"\n{BLUE}Test 4: GET /onboarding/submissions (Admin){NC}")
    
    headers = {"X-API-Key": API_KEY}
    response = await client.get(f"{API_URL}/onboarding/submissions", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✓ Success! Retrieved {len(result)} submissions{NC}")
        if result:
            print(f"  Latest submission: {result[0].get('customer_name')} ({result[0].get('service_type')})")
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")


async def test_get_submission_detail(client: httpx.AsyncClient, submission_id: str):
    """Test: Get submission details (admin)"""
    print(f"\n{BLUE}Test 5: GET /onboarding/submissions/{{id}} (Admin){NC}")
    
    if not submission_id:
        print(f"{YELLOW}⊘ Skipped: No submission ID available{NC}")
        return
    
    headers = {"X-API-Key": API_KEY}
    response = await client.get(f"{API_URL}/onboarding/submissions/{submission_id}", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✓ Success! Submission details retrieved{NC}")
        print(f"  Customer: {result.get('customer_name')}")
        print(f"  Email: {result.get('customer_email')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Service: {result.get('service_type')}")
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")


async def test_update_submission_status(client: httpx.AsyncClient, submission_id: str):
    """Test: Update submission status (admin)"""
    print(f"\n{BLUE}Test 6: PATCH /onboarding/submissions/{{id}}/status (Admin){NC}")
    
    if not submission_id:
        print(f"{YELLOW}⊘ Skipped: No submission ID available{NC}")
        return
    
    headers = {"X-API-Key": API_KEY}
    data = {
        "status": "in-progress",
        "notes": "Started working on homepage design"
    }
    
    response = await client.patch(
        f"{API_URL}/onboarding/submissions/{submission_id}/status",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✓ Success! Status updated{NC}")
        print(f"  New Status: {result.get('status')}")
        if result.get('metadata', {}).get('admin_notes'):
            notes = result['metadata']['admin_notes']
            print(f"  Notes added: {len(notes)} note(s)")
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")


async def test_list_contact_submissions(client: httpx.AsyncClient):
    """Test: List contact submissions (admin)"""
    print(f"\n{BLUE}Test 7: GET /contact/submissions (Admin){NC}")
    
    headers = {"X-API-Key": API_KEY}
    response = await client.get(f"{API_URL}/contact/submissions", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✓ Success! Retrieved {len(result)} contacts{NC}")
        if result:
            print(f"  Latest contact: {result[0].get('name')} - {result[0].get('subject')}")
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")


async def test_get_contact_detail(client: httpx.AsyncClient, contact_id: str):
    """Test: Get contact details (admin)"""
    print(f"\n{BLUE}Test 8: GET /contact/submissions/{{id}} (Admin){NC}")
    
    if not contact_id:
        print(f"{YELLOW}⊘ Skipped: No contact ID available{NC}")
        return
    
    headers = {"X-API-Key": API_KEY}
    response = await client.get(f"{API_URL}/contact/submissions/{contact_id}", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✓ Success! Contact details retrieved{NC}")
        print(f"  Name: {result.get('name')}")
        print(f"  Email: {result.get('email')}")
        print(f"  Subject: {result.get('subject')}")
        print(f"  Status: {result.get('status')}")
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")


async def test_update_contact_status(client: httpx.AsyncClient, contact_id: str):
    """Test: Update contact status (admin)"""
    print(f"\n{BLUE}Test 9: PATCH /contact/submissions/{{id}}/status (Admin){NC}")
    
    if not contact_id:
        print(f"{YELLOW}⊘ Skipped: No contact ID available{NC}")
        return
    
    headers = {"X-API-Key": API_KEY}
    response = await client.patch(
        f"{API_URL}/contact/submissions/{contact_id}/status?status=read",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✓ Success! Contact status updated{NC}")
        print(f"  {result.get('message')}")
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")


async def test_filter_submissions(client: httpx.AsyncClient):
    """Test: Filter submissions by status (admin)"""
    print(f"\n{BLUE}Test 10: GET /onboarding/submissions?status=in-progress (Admin){NC}")
    
    headers = {"X-API-Key": API_KEY}
    response = await client.get(
        f"{API_URL}/onboarding/submissions?status=in-progress&limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✓ Success! Retrieved {len(result)} in-progress submissions{NC}")
        if result:
            for sub in result:
                print(f"  - {sub.get('customer_name')} ({sub.get('service_type')})")
    else:
        print(f"{RED}✗ Failed: {response.status_code}{NC}")
        print(f"  {response.text}")


async def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing New API Endpoints")
    print("=" * 50)
    print(f"API URL: {API_URL}")
    print(f"API Key: {'*' * len(API_KEY) if API_KEY != 'your-api-key-here' else 'NOT SET'}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health endpoint first
        try:
            health = await client.get(f"{API_URL.replace('/api/v1', '')}/api/v1/health")
            if health.status_code != 200:
                print(f"\n{RED}✗ API server not responding. Please start the server first:{NC}")
                print(f"  uvicorn api.main:app --reload --port 8000")
                return
            print(f"{GREEN}✓ API server is running{NC}")
        except Exception as e:
            print(f"\n{RED}✗ Cannot connect to API server: {e}{NC}")
            print(f"  Please start the server: uvicorn api.main:app --reload --port 8000")
            return
        
        # Run tests
        submission_id = await test_onboarding_submit(client)
        contact_id = await test_contact_submit(client)
        await test_submission_status(client, submission_id)
        await test_list_onboarding_submissions(client)
        await test_get_submission_detail(client, submission_id)
        await test_update_submission_status(client, submission_id)
        await test_list_contact_submissions(client)
        await test_get_contact_detail(client, contact_id)
        await test_update_contact_status(client, contact_id)
        await test_filter_submissions(client)
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"{GREEN}✓ All endpoint tests completed{NC}")
    print(f"\nSubmission ID: {submission_id}")
    print(f"Contact ID: {contact_id}")
    print("\nNext steps:")
    print("1. Check http://localhost:8000/api/v1/docs for interactive API docs")
    print("2. Verify data in database")
    print("3. Test with frontend application")


if __name__ == "__main__":
    asyncio.run(main())
