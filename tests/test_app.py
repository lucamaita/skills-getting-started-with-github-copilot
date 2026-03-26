import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a deep copy of the original activities for resetting
original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the global activities dictionary before each test to ensure isolation."""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(original_activities))

client = TestClient(app)

def test_get_activities():
    """Test GET /activities returns all activities with correct structure."""
    # Arrange - No special setup needed, using default activities
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Based on the initial activities count
    for activity_name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_successful():
    """Test successful signup for an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test duplicate signup error."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # Pre-signup
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"

def test_signup_activity_not_found():
    """Test signup for non-existent activity."""
    # Arrange
    activity_name = "NonExistentActivity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_successful():
    """Test successful unregister from an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # Pre-signup
    
    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_signed_up():
    """Test unregister error when not signed up."""
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student not signed up for this activity"

def test_unregister_activity_not_found():
    """Test unregister from non-existent activity."""
    # Arrange
    activity_name = "NonExistentActivity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"