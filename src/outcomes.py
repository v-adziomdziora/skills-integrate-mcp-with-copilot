"""
Extracurricular outcome records.

Outcome records are persisted as JSON so that staff analytics are always
computed from stored data instead of runtime state. The helpers in this module
only ever return aggregated numbers, never individual student information.
"""

from datetime import date
from pathlib import Path
from typing import Optional
import json

DATA_FILE = Path(__file__).parent / "data" / "outcomes.json"

REVIEW_STATUSES = ["pending", "approved", "rejected"]


def load_outcomes():
    """Load the persisted outcome records."""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


def parse_date(value: str) -> date:
    """Parse a YYYY-MM-DD string, raising ValueError when invalid."""
    return date.fromisoformat(value)


def filter_outcomes(
    records,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    academic_year: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
):
    """Return the records matching the given filter context."""
    filtered = []
    for record in records:
        try:
            record_date = parse_date(record["date"])
        except (KeyError, TypeError, ValueError):
            # A record without a usable date cannot match a date range
            record_date = None

        if (start_date or end_date) and record_date is None:
            continue
        if start_date and record_date < start_date:
            continue
        if end_date and record_date > end_date:
            continue
        if academic_year and record.get("academic_year") != academic_year:
            continue
        if category and record.get("category") != category:
            continue
        if status and record.get("status") != status:
            continue

        filtered.append(record)

    return filtered


def _group_value(record, key: str) -> str:
    """Return a record field as a group label, falling back to "Unknown"."""
    value = record.get(key)
    return value if isinstance(value, str) and value else "Unknown"


def _breakdown(records, key: str):
    """Group records by a field and count totals per review status."""
    groups = {}
    for record in records:
        value = _group_value(record, key)
        group = groups.setdefault(
            value,
            {key: value, "total": 0, "pending": 0,
             "approved": 0, "rejected": 0}
        )
        group["total"] += 1
        if record.get("status") in REVIEW_STATUSES:
            group[record["status"]] += 1

    return sorted(groups.values(), key=lambda group: group[key])


def build_analytics(records):
    """Build the aggregate staff metrics for the given records.

    The result never contains student identifiers, only counts.
    """
    return {
        "totals": {
            "total_records": len(records),
            "distinct_students": len(
                {record["student_email"] for record in records
                 if record.get("student_email")}),
            "pending_reviews": len(
                [r for r in records if r.get("status") == "pending"]),
            "approved_records": len(
                [r for r in records if r.get("status") == "approved"]),
        },
        "by_category": _breakdown(records, "category"),
        "by_academic_year": _breakdown(records, "academic_year"),
        "empty": len(records) == 0,
    }


def available_filters(records):
    """List the category and academic year values present in the records."""
    return {
        "categories": sorted(
            {_group_value(record, "category") for record in records}),
        "academic_years": sorted(
            {_group_value(record, "academic_year") for record in records}),
        "statuses": list(REVIEW_STATUSES),
    }
