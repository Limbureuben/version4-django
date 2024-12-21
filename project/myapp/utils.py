# utils.py
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from graphql_jwt.exceptions import PermissionDenied



def authenticate_user(token):
    """Authenticate a user by decoding their JWT token and fetching their user."""
    try:
        # Decode the JWT token to get the payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        # Retrieve the user based on user_id from the token
        user = User.objects.get(id=user_id)
        return user
    except jwt.ExpiredSignatureError:
        raise PermissionDenied("Token has expired")
    except jwt.DecodeError:
        raise PermissionDenied("Error decoding token")
    except User.DoesNotExist:
        raise PermissionDenied("User not found")



# utils.py
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.models import User

def reset_user_password(user, old_password, new_password, new_password_confirm):
    """Reset the user's password, ensuring the old password is correct and new passwords match."""
    try:
        # Check if the new passwords match
        if new_password != new_password_confirm:
            return {
                'success': False,
                'message': 'New password does not match confirmation'
            }

        # Verify the old password
        if not user.check_password(old_password):
            return {
                'success': False,
                'message': 'The old password is incorrect'
            }

        # Validate the new password using Django's built-in password validators
        password_validation.validate_password(new_password, user)

        # Set and save the new password
        user.set_password(new_password)
        user.save()

        return {
            'success': True,
            'message': 'Password reset successfully'
        }

    except ValidationError as e:
        # Handle password validation errors (e.g., too short, too common, etc.)
        return {
            'success': False,
            'message': ' '.join(e.messages)  # Join multiple validation error messages
        }

    except Exception as e:
        # General exception handling
        print(f"Error resetting password: {e}")
        return {
            'success': False,
            'message': 'An error occurred during password reset'
        }




# utils.py
from graphql_jwt.exceptions import PermissionDenied

def check_user_permissions(user, permission):
    """Check if the user has the required permission."""
    if not user.has_perm(permission):
        raise PermissionDenied(f"User does not have permission: {permission}")
