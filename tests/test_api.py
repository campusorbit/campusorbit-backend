"""Tests for core API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.fee import Fee
from app.models.lead import Lead
from app.models.campus import CampusNews
from app.models.inventory import InventoryItem
from app.models.user import User


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestCoursesAPI:
    @pytest.mark.asyncio
    async def test_list_courses_empty(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/courses/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_and_list_course(self, client: AsyncClient, auth_headers: dict, seed_user: User):
        # Create course
        course_data = {
            "code": "TST101",
            "name": "Test Course",
            "instructor_id": seed_user.id,
            "semester": "Fall 2024",
            "credits": 3,
            "description": "A test course",
        }
        create_resp = await client.post("/api/v1/courses/", json=course_data, headers=auth_headers)
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["code"] == "TST101"

        # List courses
        list_resp = await client.get("/api/v1/courses/", headers=auth_headers)
        assert list_resp.status_code == 200


class TestFeesAPI:
    @pytest.mark.asyncio
    async def test_create_and_list_fee(self, client: AsyncClient, auth_headers: dict, seed_user: User):
        fee_data = {
            "student_id": seed_user.id,
            "amount": 50000,
            "due_date": "2024-12-15",
            "status": "pending",
            "payment_mode": "online",
        }
        create_resp = await client.post("/api/v1/fees/", json=fee_data, headers=auth_headers)
        assert create_resp.status_code == 201

        list_resp = await client.get("/api/v1/fees/", headers=auth_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

    @pytest.mark.asyncio
    async def test_financial_kpis(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/fees/kpis", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_collected" in data
        assert "collection_rate" in data

    @pytest.mark.asyncio
    async def test_fee_chart_data(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/fees/chart-data", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_payment_gateways(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/fees/gateways", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestLeadsAPI:
    @pytest.mark.asyncio
    async def test_create_and_list_lead(self, client: AsyncClient, auth_headers: dict):
        lead_data = {
            "name": "Test Lead",
            "email": "lead@test.com",
            "phone": "+91-9888888888",
            "source": "Website",
            "status": "interested",
        }
        create_resp = await client.post("/api/v1/leads/", json=lead_data, headers=auth_headers)
        assert create_resp.status_code == 201

        list_resp = await client.get("/api/v1/leads/", headers=auth_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1


class TestCampusAPI:
    @pytest.mark.asyncio
    async def test_get_news(self, client: AsyncClient):
        response = await client.get("/api/v1/campus/news")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_news(self, client: AsyncClient, auth_headers: dict):
        news_data = {
            "title": "Test News",
            "content": "Test content",
            "date": "2024-11-15",
            "category": "announcement",
            "author": "Admin",
        }
        response = await client.post("/api/v1/campus/news", json=news_data, headers=auth_headers)
        assert response.status_code == 201


class TestInventoryAPI:
    @pytest.mark.asyncio
    async def test_inventory_crud(self, client: AsyncClient, auth_headers: dict):
        item_data = {
            "name": "Test Item",
            "category": "Electronics",
            "quantity": 10,
            "location": "Lab-X",
            "condition": "Good",
            "last_updated": "2024-11-15",
        }
        create_resp = await client.post("/api/v1/inventory/", json=item_data, headers=auth_headers)
        assert create_resp.status_code == 201

        list_resp = await client.get("/api/v1/inventory/", headers=auth_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1


class TestPricingAPI:
    @pytest.mark.asyncio
    async def test_pricing_plans(self, client: AsyncClient):
        response = await client.get("/api/v1/pricing/plans")
        assert response.status_code == 200


class TestMarketplaceAPI:
    @pytest.mark.asyncio
    async def test_marketplace_integrations(self, client: AsyncClient):
        response = await client.get("/api/v1/marketplace/integrations")
        assert response.status_code == 200


class TestPaymentsAPI:
    @pytest.mark.asyncio
    async def test_razorpay_config(self, client: AsyncClient):
        response = await client.get("/api/v1/payments/razorpay-config")
        assert response.status_code == 200
        data = response.json()
        assert "payment_button_id" in data
        assert "script_url" in data


class TestAttendanceAPI:
    @pytest.mark.asyncio
    async def test_mark_and_list_attendance(self, client: AsyncClient, auth_headers: dict, seed_user: User):
        att_data = {"student_id": seed_user.id, "date": "2024-11-15", "status": "present"}
        create_resp = await client.post("/api/v1/attendance/", json=att_data, headers=auth_headers)
        assert create_resp.status_code == 201

        list_resp = await client.get("/api/v1/attendance/", headers=auth_headers)
        assert list_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_attendance_report(self, client: AsyncClient, auth_headers: dict, seed_user: User):
        # Create some attendance records first
        for s in ["present", "present", "absent"]:
            await client.post(
                "/api/v1/attendance/",
                json={"student_id": seed_user.id, "date": f"2024-11-1{['5','6','7'].pop()}", "status": s},
                headers=auth_headers,
            )

        response = await client.get(f"/api/v1/attendance/report?student_id={seed_user.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "percentage" in data


class TestComplaintsAPI:
    @pytest.mark.asyncio
    async def test_create_and_list_complaint(self, client: AsyncClient, auth_headers: dict):
        complaint_data = {
            "subject": "Test Complaint",
            "description": "Testing the complaints system",
            "category": "academic",
            "priority": "medium",
        }
        create_resp = await client.post("/api/v1/complaints/", json=complaint_data, headers=auth_headers)
        assert create_resp.status_code == 201
        complaint_id = create_resp.json()["id"]

        list_resp = await client.get("/api/v1/complaints/", headers=auth_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        # Update complaint
        update_resp = await client.put(
            f"/api/v1/complaints/{complaint_id}",
            json={"status": "resolved", "resolution": "Fixed"},
            headers=auth_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "resolved"


class TestUsersAPI:
    @pytest.mark.asyncio
    async def test_list_users(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_user_profile(self, client: AsyncClient, auth_headers: dict, seed_user: User):
        response = await client.get(f"/api/v1/users/{seed_user.id}/profile", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == seed_user.email

    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient, auth_headers: dict, seed_user: User):
        response = await client.put(
            f"/api/v1/users/{seed_user.id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
