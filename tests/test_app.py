import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Helper to reset activities for test isolation
@pytest.fixture(autouse=True)
def reset_activities():
    for activity in activities.values():
        if isinstance(activity["participants"], list):
            activity["participants"].clear()
    # Add initial participants for Chess Club, Programming Class, Gym Class
    activities["Chess Club"]["participants"] += ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] += ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] += ["john@mergington.edu", "olivia@mergington.edu"]
    yield


def test_get_activities():
    # Arrange
    # (No setup needed, uses default activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_success():
    # Arrange
    activity = "Math Olympiad"
    email = "testuser@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert f"Signed up {email} for {activity}" in response.json()["message"]


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
