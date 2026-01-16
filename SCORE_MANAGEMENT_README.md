# Score Management Backend - Implementation Summary

## Overview
A complete backend system for managing assignment scores with database persistence, REST API endpoints, and web form interface.

## What Was Implemented

### 1. Database Schema
- **New Column**: Added `score` (REAL/Float) column to the `assignments` table
- **Migration**: Successfully ran migration to update existing database
- **Location**: `app/models/assignment.py`

### 2. Data Model Updates
- Updated `Assignment` model class with `score` field
- Added score parameter to constructor and initialization

### 3. Repository Layer (`app/repositories/assignmentRepo.py`)
Added three new methods:
- `updateScore(user_id, assignment_id, score)` - Update/set a score for an assignment
- `getScore(user_id, assignment_id)` - Retrieve a specific assignment's score
- `getAllScores(user_id)` - Get all assignments with their scores for a user

### 4. Forms (`app/forms/scoreForm.py`)
Created `ScoreForm` with:
- Score input field (float, min: 0)
- Assignment ID (hidden field)
- Form validation

### 5. Routes & API Endpoints (`app/Website/Scores/scoreManager.py`)

#### REST API Endpoints:
- `GET /api/scores/` - Get all scores for current user (JSON response)
- `GET /api/scores/<assignment_id>/` - Get score for specific assignment
- `POST/PUT /api/scores/<assignment_id>/` - Update score for specific assignment

#### Web Form Endpoint:
- `GET/POST /scores/update/<assignment_id>/` - Web form to update score

### 6. Web Interface
- Created modern, responsive HTML template (`templates/updateScore.html`)
- Displays assignment details and current score
- Form validation and error handling
- Beautiful gradient design with animations

## How to Use the Backend

### Via REST API (JSON)

#### Get All Scores:
```bash
GET /api/scores/
Response: {
  "status": "success",
  "scores": [
    {
      "assignment_id": 1,
      "title": "Homework 1",
      "course_name": "Math 101",
      "points_possible": 100,
      "score": 95.5,
      "due": "2026-01-15"
    },
    ...
  ]
}
```

#### Get Specific Score:
```bash
GET /api/scores/1/
Response: {
  "status": "success",
  "assignment_id": 1,
  "score": 95.5
}
```

#### Update Score:
```bash
POST /api/scores/1/
Content-Type: application/json
Body: {"score": 95.5}

Response: {
  "status": "success",
  "message": "Score updated successfully",
  "assignment_id": 1,
  "score": 95.5
}
```

### Via Web Form
1. Navigate to `/scores/update/<assignment_id>/`
2. Enter the score in the form
3. Click "Save Score"
4. Redirects to dashboard with success message

### Example JavaScript Usage (Frontend)
```javascript
// Update a score
async function updateScore(assignmentId, score) {
  const response = await fetch(`/api/scores/${assignmentId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ score: score })
  });
  
  const data = await response.json();
  console.log(data);
}

// Get all scores
async function getAllScores() {
  const response = await fetch('/api/scores/');
  const data = await response.json();
  return data.scores;
}

// Usage
updateScore(1, 95.5);
```

## Files Modified/Created

### Modified:
- `app/models/assignment.py` - Added score field
- `app/repositories/assignmentRepo.py` - Added score management methods
- `app/main.py` - Registered scores blueprint

### Created:
- `app/forms/scoreForm.py` - Score input form
- `app/Website/Scores/scoreManager.py` - Score routes/API
- `app/Website/Scores/__init__.py` - Module initialization
- `app/Website/Scores/templates/updateScore.html` - Web form template
- `app/migrate_add_score.py` - Database migration script

## Testing the Backend

### 1. Start the Flask Server:
```bash
cd "c:\Users\ravel\Documents\Coding\Assignment Tracker (Antigravity)\assignment-tracker\app"
python main.py
```

### 2. Access the Web Form:
Navigate to: `http://localhost:5000/scores/update/<assignment_id>/`
(Replace `<assignment_id>` with an actual assignment ID from your database)

### 3. Test the API:
Use curl, Postman, or browser developer tools:
```bash
curl http://localhost:5000/api/scores/
```

## Next Steps (Optional Enhancements)
- Add score history tracking (track score changes over time)
- Add percentage calculation (score/points_possible * 100)
- Add grade letter calculation (A, B, C, etc.)
- Add bulk score import feature
- Add score statistics (average, median, etc.)
- Integrate score display in the dashboard template
