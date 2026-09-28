"""Tests for the staff outcome analytics endpoints."""

from fastapi.testclient import TestClient

from src.app import app
from src import outcomes as outcomes_store

client = TestClient(app)


def test_analytics_totals_from_persisted_records():
    records = outcomes_store.load_outcomes()
    response = client.get("/outcomes/analytics")
    assert response.status_code == 200

    data = response.json()
    assert data["totals"]["total_records"] == len(records)
    assert data["totals"]["distinct_students"] == len(
        {record["student_email"] for record in records})
    assert data["totals"]["pending_reviews"] == len(
        [r for r in records if r["status"] == "pending"])
    assert data["totals"]["approved_records"] == len(
        [r for r in records if r["status"] == "approved"])
    assert data["empty"] is False


def test_analytics_does_not_expose_student_data():
    assert "student_email" not in client.get("/outcomes/analytics").text


def test_analytics_filters_by_status_and_academic_year():
    response = client.get(
        "/outcomes/analytics",
        params={"status": "approved", "academic_year": "2025-2026"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["totals"]["pending_reviews"] == 0
    assert data["totals"]["total_records"] == data["totals"]["approved_records"]
    assert [group["academic_year"]
            for group in data["by_academic_year"]] == ["2025-2026"]
    assert data["filters"]["status"] == "approved"


def test_analytics_filters_by_date_range_and_category():
    response = client.get(
        "/outcomes/analytics",
        params={
            "start_date": "2025-09-01",
            "end_date": "2026-06-30",
            "category": "Competition",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert [group["category"]
            for group in data["by_category"]] == ["Competition"]
    assert data["totals"]["total_records"] == data["by_category"][0]["total"]


def test_analytics_empty_state():
    response = client.get(
        "/outcomes/analytics",
        params={"start_date": "1999-01-01", "end_date": "1999-12-31"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["empty"] is True
    assert data["totals"] == {
        "total_records": 0,
        "distinct_students": 0,
        "pending_reviews": 0,
        "approved_records": 0,
    }
    assert data["by_category"] == []


def test_analytics_rejects_invalid_filters():
    assert client.get("/outcomes/analytics",
                      params={"status": "unknown"}).status_code == 400
    assert client.get("/outcomes/analytics",
                      params={"start_date": "not-a-date"}).status_code == 400
    assert client.get(
        "/outcomes/analytics",
        params={"start_date": "2026-01-01", "end_date": "2025-01-01"},
    ).status_code == 400


def test_outcome_filters_endpoint():
    response = client.get("/outcomes/filters")
    assert response.status_code == 200

    data = response.json()
    records = outcomes_store.load_outcomes()
    assert data["categories"] == sorted({r["category"] for r in records})
    assert data["academic_years"] == sorted(
        {r["academic_year"] for r in records})
    assert data["statuses"] == ["pending", "approved", "rejected"]
