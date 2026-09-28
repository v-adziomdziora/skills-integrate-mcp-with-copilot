"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import Optional
import os
from pathlib import Path

try:
    from . import outcomes as outcomes_store
except ImportError:  # pragma: no cover - allows running "python app.py"
    import outcomes as outcomes_store

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


def _parse_filter_date(field: str, value: Optional[str]):
    """Parse a date filter, raising a 400 error when it is not a valid date"""
    if not value:
        return None

    try:
        return outcomes_store.parse_date(value)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field}. Expected the format YYYY-MM-DD"
        ) from error


@app.get("/outcomes/filters")
def get_outcome_filters():
    """List the filter values available for the staff analytics dashboard"""
    return outcomes_store.available_filters(outcomes_store.load_outcomes())


@app.get("/outcomes/analytics")
def get_outcome_analytics(
    start_date: Optional[str] = Query(
        None, description="Only include outcomes on or after this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(
        None, description="Only include outcomes on or before this date (YYYY-MM-DD)"),
    academic_year: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
):
    """Aggregate metrics about extracurricular outcomes for staff.

    Only aggregated counts are returned, so no individual student data is
    exposed by this endpoint. The application has no authentication yet, so the
    metrics are intentionally limited to non-identifying aggregates.
    """
    # Validate the review status filter
    if status is not None and status not in outcomes_store.REVIEW_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Expected one of: {', '.join(outcomes_store.REVIEW_STATUSES)}"
        )

    # Validate the date range filter
    parsed_start = _parse_filter_date("start_date", start_date)
    parsed_end = _parse_filter_date("end_date", end_date)

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise HTTPException(
            status_code=400,
            detail="start_date must not be after end_date"
        )

    records = outcomes_store.filter_outcomes(
        outcomes_store.load_outcomes(),
        start_date=parsed_start,
        end_date=parsed_end,
        academic_year=academic_year,
        category=category,
        status=status,
    )

    analytics = outcomes_store.build_analytics(records)
    analytics["filters"] = {
        "start_date": start_date,
        "end_date": end_date,
        "academic_year": academic_year,
        "category": category,
        "status": status,
    }
    return analytics
