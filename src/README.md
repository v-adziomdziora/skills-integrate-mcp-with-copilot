# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/outcomes/filters`                                               | Get the filter values available for the staff analytics dashboard   |
| GET    | `/outcomes/analytics`                                             | Get aggregate outcome metrics for staff                             |

The analytics endpoint accepts the optional filters `start_date`, `end_date`
(both `YYYY-MM-DD`), `academic_year`, `category` and `status` (`pending`,
`approved` or `rejected`). It returns only aggregated counts, so individual
student data is never exposed.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:

   - Name
   - Grade level

3. **Outcome records** - Uses a record id as identifier:
   - Student email
   - Activity name
   - Category
   - Date and academic year
   - Review status (pending, approved or rejected)

Activities are stored in memory, which means they will be reset when the server
restarts. Outcome records are persisted in `src/data/outcomes.json` so that
staff analytics are always computed from stored records.
