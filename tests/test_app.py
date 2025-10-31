"""
Test suite for Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the API"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    activities.clear()
    activities.update({
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
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly games",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ella@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce school plays and performances",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["jack@mergington.edu", "grace@mergington.edu"]
        },
        "Mathletes": {
            "description": "Compete in math competitions and solve challenging problems",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["oliver@mergington.edu", "chloe@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["benjamin@mergington.edu", "zoe@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activities_have_correct_structure(self, client):
        """Test that activities have the correct data structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_activities_have_correct_participant_counts(self, client):
        """Test that activities show correct number of participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student(self, client):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_student_to_participants(self, client):
        """Test that signup actually adds student to participants list"""
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 3

    def test_signup_duplicate_student(self, client):
        """Test that signing up the same student twice returns an error"""
        # First signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response1.status_code == 400
        data = response1.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_students(self, client):
        """Test signing up multiple different students"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/Chess%20Club/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data["Chess Club"]["participants"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student(self, client):
        """Test unregistering a student from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_student_from_participants(self, client):
        """Test that unregister actually removes student from participants list"""
        client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 1

    def test_unregister_nonexistent_student(self, client):
        """Test unregistering a student who isn't registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_all_students(self, client):
        """Test unregistering all students from an activity"""
        participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        for email in participants:
            response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 0


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""

    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow: signup then unregister"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify added
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify removed
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count
        assert email not in response.json()[activity]["participants"]

    def test_signup_to_multiple_activities(self, client):
        """Test signing up the same student to multiple activities"""
        email = "multisport@mergington.edu"
        activities_list = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities_list:
            assert email in data[activity]["participants"]

    def test_activity_capacity_tracking(self, client):
        """Test that activity capacity is properly tracked"""
        response = client.get("/activities")
        data = response.json()
        
        mathletes = data["Mathletes"]
        max_capacity = mathletes["max_participants"]
        current_count = len(mathletes["participants"])
        
        # Add students up to capacity
        spots_available = max_capacity - current_count
        for i in range(spots_available):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/Mathletes/signup?email={email}")
            assert response.status_code == 200
        
        # Verify at capacity
        response = client.get("/activities")
        data = response.json()
        assert len(data["Mathletes"]["participants"]) == max_capacity
