"""Tests for the Mergington High School API"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
    
    def test_get_activities_has_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants_are_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]
        
        assert isinstance(activity["participants"], list)
        assert len(activity["participants"]) > 0


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup returns 400"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_participants(self, client):
        """Test that multiple different participants can sign up"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email1}"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email2}"
        )
        assert response2.status_code == 200
        
        # Verify both were added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 in activities["Chess Club"]["participants"]
        assert email2 in activities["Chess Club"]["participants"]
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with email containing special characters"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test.student+alias@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistration from nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistration of participant not in activity returns 400"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_signup_then_unregister(self, client):
        """Test signup followed by unregister"""
        email = "tempstudent@mergington.edu"
        activity = "Chess%20Club"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]


class TestEdgeCases:
    """Tests for edge cases and error scenarios"""
    
    def test_empty_email_parameter(self, client):
        """Test signup with empty email"""
        response = client.post("/activities/Chess%20Club/signup?email=")
        assert response.status_code in [400, 422]  # Bad request or unprocessable
    
    def test_case_sensitive_activity_names(self, client):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/chess%20club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404  # chess club (lowercase) should not exist
    
    def test_activity_with_url_encoded_spaces(self, client):
        """Test activity names with URL-encoded spaces"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Test signup with proper URL encoding
        signup_response = client.post(
            "/activities/Programming%20Class/signup?email=newdev@mergington.edu"
        )
        assert signup_response.status_code == 200
