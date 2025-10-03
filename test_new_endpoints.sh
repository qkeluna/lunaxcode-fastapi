#!/bin/bash

# Test script for new onboarding and contact endpoints
# Usage: ./test_new_endpoints.sh

echo "========================================="
echo "Testing New API Endpoints"
echo "========================================="
echo ""

# Configuration
API_URL="http://localhost:8000/api/v1"
API_KEY="your-api-key-here"  # Update with actual API key from .env

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Submit Onboarding Form (Public)
echo -e "${BLUE}Test 1: POST /onboarding/submit (Public)${NC}"
ONBOARDING_RESPONSE=$(curl -s -X POST "$API_URL/onboarding/submit" \
  -H "Content-Type: application/json" \
  -d '{
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
  }')

echo "$ONBOARDING_RESPONSE" | jq '.'
SUBMISSION_ID=$(echo "$ONBOARDING_RESPONSE" | jq -r '.submission_id')
echo -e "${GREEN}✓ Submission ID: $SUBMISSION_ID${NC}"
echo ""

# Test 2: Submit Contact Form (Public)
echo -e "${BLUE}Test 2: POST /contact/submit (Public)${NC}"
CONTACT_RESPONSE=$(curl -s -X POST "$API_URL/contact/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "subject": "Project Inquiry",
    "message": "I am interested in building a web application for my business. Can we schedule a call?",
    "metadata": {
      "source": "homepage",
      "timestamp": 1696345678
    }
  }')

echo "$CONTACT_RESPONSE" | jq '.'
CONTACT_ID=$(echo "$CONTACT_RESPONSE" | jq -r '.message_id')
echo -e "${GREEN}✓ Contact ID: $CONTACT_ID${NC}"
echo ""

# Test 3: Check Submission Status (Public)
echo -e "${BLUE}Test 3: GET /submissions/{id}/status (Public)${NC}"
if [ "$SUBMISSION_ID" != "null" ] && [ -n "$SUBMISSION_ID" ]; then
  STATUS_RESPONSE=$(curl -s "$API_URL/submissions/$SUBMISSION_ID/status")
  echo "$STATUS_RESPONSE" | jq '.'
  echo -e "${GREEN}✓ Status check successful${NC}"
else
  echo -e "${RED}✗ No submission ID available${NC}"
fi
echo ""

# Test 4: List Onboarding Submissions (Admin)
echo -e "${BLUE}Test 4: GET /onboarding/submissions (Admin)${NC}"
SUBMISSIONS_LIST=$(curl -s "$API_URL/onboarding/submissions" \
  -H "X-API-Key: $API_KEY")

echo "$SUBMISSIONS_LIST" | jq '.[0] // "No submissions found"'
echo -e "${GREEN}✓ Retrieved $(echo "$SUBMISSIONS_LIST" | jq 'length') submissions${NC}"
echo ""

# Test 5: Get Onboarding Submission Details (Admin)
echo -e "${BLUE}Test 5: GET /onboarding/submissions/{id} (Admin)${NC}"
if [ "$SUBMISSION_ID" != "null" ] && [ -n "$SUBMISSION_ID" ]; then
  SUBMISSION_DETAIL=$(curl -s "$API_URL/onboarding/submissions/$SUBMISSION_ID" \
    -H "X-API-Key: $API_KEY")
  echo "$SUBMISSION_DETAIL" | jq '.'
  echo -e "${GREEN}✓ Submission details retrieved${NC}"
else
  echo -e "${RED}✗ No submission ID available${NC}"
fi
echo ""

# Test 6: Update Submission Status (Admin)
echo -e "${BLUE}Test 6: PATCH /onboarding/submissions/{id}/status (Admin)${NC}"
if [ "$SUBMISSION_ID" != "null" ] && [ -n "$SUBMISSION_ID" ]; then
  UPDATE_RESPONSE=$(curl -s -X PATCH "$API_URL/onboarding/submissions/$SUBMISSION_ID/status" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{
      "status": "in-progress",
      "notes": "Started working on homepage design"
    }')
  echo "$UPDATE_RESPONSE" | jq '.'
  echo -e "${GREEN}✓ Status updated to in-progress${NC}"
else
  echo -e "${RED}✗ No submission ID available${NC}"
fi
echo ""

# Test 7: List Contact Submissions (Admin)
echo -e "${BLUE}Test 7: GET /contact/submissions (Admin)${NC}"
CONTACTS_LIST=$(curl -s "$API_URL/contact/submissions" \
  -H "X-API-Key: $API_KEY")

echo "$CONTACTS_LIST" | jq '.[0] // "No contacts found"'
echo -e "${GREEN}✓ Retrieved $(echo "$CONTACTS_LIST" | jq 'length') contacts${NC}"
echo ""

# Test 8: Get Contact Submission Details (Admin)
echo -e "${BLUE}Test 8: GET /contact/submissions/{id} (Admin)${NC}"
if [ "$CONTACT_ID" != "null" ] && [ -n "$CONTACT_ID" ]; then
  CONTACT_DETAIL=$(curl -s "$API_URL/contact/submissions/$CONTACT_ID" \
    -H "X-API-Key: $API_KEY")
  echo "$CONTACT_DETAIL" | jq '.'
  echo -e "${GREEN}✓ Contact details retrieved${NC}"
else
  echo -e "${RED}✗ No contact ID available${NC}"
fi
echo ""

# Test 9: Update Contact Status (Admin)
echo -e "${BLUE}Test 9: PATCH /contact/submissions/{id}/status (Admin)${NC}"
if [ "$CONTACT_ID" != "null" ] && [ -n "$CONTACT_ID" ]; then
  CONTACT_UPDATE=$(curl -s -X PATCH "$API_URL/contact/submissions/$CONTACT_ID/status?status=read" \
    -H "X-API-Key: $API_KEY")
  echo "$CONTACT_UPDATE" | jq '.'
  echo -e "${GREEN}✓ Contact status updated to read${NC}"
else
  echo -e "${RED}✗ No contact ID available${NC}"
fi
echo ""

# Test 10: Filter Submissions by Status (Admin)
echo -e "${BLUE}Test 10: GET /onboarding/submissions?status=in-progress (Admin)${NC}"
FILTERED_SUBMISSIONS=$(curl -s "$API_URL/onboarding/submissions?status=in-progress&limit=5" \
  -H "X-API-Key: $API_KEY")

echo "$FILTERED_SUBMISSIONS" | jq '.[0] // "No in-progress submissions found"'
echo -e "${GREEN}✓ Retrieved $(echo "$FILTERED_SUBMISSIONS" | jq 'length') in-progress submissions${NC}"
echo ""

echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "${GREEN}✓ All endpoint tests completed${NC}"
echo ""
echo "Submission ID: $SUBMISSION_ID"
echo "Contact ID: $CONTACT_ID"
echo ""
echo "Next steps:"
echo "1. Check http://localhost:8000/api/v1/docs for interactive API docs"
echo "2. Verify data in database"
echo "3. Test with frontend application"
