"""
Test cases for the User API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# Define URLs for user creation and token generation
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

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

    def test_create_token_for_user(self):
        """Test generating a token for user."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        # Create a user
        create_user(**payload)

        # Generate token for the user
        res = self.client.post(TOKEN_URL, {
            'email': payload['email'],
            'password': payload['password']
        })

        # Check the response status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify the token is returned in the response
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """Test token is not created if invalid credentials are given."""
        # Create a user with known credentials
        create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

        # Attempt to generate a token with invalid credentials
        res = self.client.post(TOKEN_URL, {
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        })

        # Check the response status code
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the token is not returned in the response
        self.assertNotIn('token', res.data)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        # Create a user with known credentials
        create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

        # Attempt to generate a token with a blank password
        res = self.client.post(TOKEN_URL, {
            'email': 'test@example.com',
            'password': ''
        })

        # Check the response status code
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the token is not returned in the response
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users."""
        # Attempt to access the user profile endpoint without authentication
        res = self.client.get(ME_URL)

        # Check for unauthorized response
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    # Set up the test client and authenticate a user
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        # Make a GET request to retrieve the user profile
        res = self.client.get(ME_URL)

        # Check the response status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify the response data matches the authenticated user
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me endpoint."""
        # Attempt to make a POST request to the user profile endpoint
        res = self.client.post(ME_URL, {})

        # Check for method not allowed response
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user."""
        payload = {
            'name': 'Updated Name',
            'password': 'newpassword123'
        }

        # Make a PATCH request to update the user profile
        res = self.client.patch(ME_URL, payload)

        # Refresh the user instance from the database
        self.user.refresh_from_db()

        # Verify the user's name was updated
        self.assertEqual(self.user.name, payload['name'])

        # Check that the password was updated correctly
        self.assertTrue(self.user.check_password(payload['password']))

        # Check the response status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)