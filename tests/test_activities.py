"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_activities = {
        "Soccer": {
            "description": "Competitive soccer team for all skill levels",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Basketball": {
            "description": "Basketball team and pickup games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["chris@mergington.edu", "taylor@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "avery@mergington.edu"]
        },
        "Music Club": {
            "description": "Learn instruments and perform in ensemble groups",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "mia@mergington.edu"]
        },
        "Math Club": {
            "description": "Solve challenging math problems and compete in competitions",
            "schedule": "Saturdays, 10:00 AM - 11:30 AM",
            "max_participants": 16,
            "participants": ["ryan@mergington.edu", "zoe@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore STEM topics",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
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
        }
    }
    
    # Clear and reset the global activities dict
    activities.clear()
    activities.update(initial_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Soccer" in data
        assert "Basketball" in data

    def test_get_activities_includes_activity_details(self, client):
        """Test that activity details are complete"""
        response = client.get("/activities")
        data = response.json()
        soccer = data["Soccer"]
        
        assert soccer["description"] == "Competitive soccer team for all skill levels"
        assert soccer["schedule"] == "Mondays and Wednesdays, 4:00 PM - 5:30 PM"
        assert soccer["max_participants"] == 25
        assert isinstance(soccer["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """Test that participants list is included"""
        response = client.get("/activities")
        data = response.json()
        soccer = data["Soccer"]
        
        assert "alex@mergington.edu" in soccer["participants"]
        assert "jordan@mergington.edu" in soccer["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Soccer/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Soccer"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_duplicate_signup_returns_error(self, client):
        """Test that signing up twice returns an error"""
        email = "alex@mergington.edu"  # Already registered in Soccer
        response = client.post(f"/activities/Soccer/signup?email={email}")
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_to_multiple_activities(self, client):
        """Test that a student can signup for multiple activities"""
        email = "newstudent@mergington.edu"
        
        # Signup to Soccer
        response1 = client.post(f"/activities/Soccer/signup?email={email}")
        assert response1.status_code == 200
        
        # Signup to Basketball
        response2 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups worked
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Soccer"]["participants"]
        assert email in data["Basketball"]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        email = "alex@mergington.edu"  # Already registered in Soccer
        response = client.post(f"/activities/Soccer/unregister?email={email}")
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "alex@mergington.edu"
        client.post(f"/activities/Soccer/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Soccer"]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_non_participant(self, client):
        """Test that unregistering someone not signed up returns error"""
        response = client.post(
            "/activities/Soccer/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_and_resign(self, client):
        """Test that a student can unregister and sign up again"""
        email = "alex@mergington.edu"
        
        # Unregister
        response1 = client.post(f"/activities/Soccer/unregister?email={email}")
        assert response1.status_code == 200
        
        # Verify removed
        check1 = client.get("/activities")
        assert email not in check1.json()["Soccer"]["participants"]
        
        # Sign up again
        response2 = client.post(f"/activities/Soccer/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify added again
        check2 = client.get("/activities")
        assert email in check2.json()["Soccer"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
