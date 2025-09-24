"""
Test cases for the User API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# URL for creating a new user
CREATE_USER_URL = reverse('user:create')

# Helper function to create a user
def create_user(**params):
    """Create and return a new user."""
    user = get_user_model().objects.create_user(**params)
    return user

class PublicUserApiTests(TestCase):
    """Test the public features of the User API."""

    # Set up the test client
    def setUp(self):
        self.client = APIClient()

    # Test for successful user creation
    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        # Make a POST request to create a new user
        res = self.client.post(CREATE_USER_URL, payload)

        # Check the response status code
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Verify the user was created correctly
        user = get_user_model().objects.get(email=payload['email'])

        # Check password is correct
        self.assertTrue(user.check_password(payload['password']))

        # Ensure password is not returned in the response
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        # Create a user with the same email
        create_user(**payload)

        # Attempt to create another user with the same email
        res = self.client.post(CREATE_USER_URL, payload)

        # Check for bad request response
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is too short."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test User'
        }

        # Attempt to create a user with a short password
        res = self.client.post(CREATE_USER_URL, payload)

        # Check for bad request response
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the user was not created
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        # Assert that the user does not exist
        self.assertFalse(user_exists)