from typing import Dict, Tuple, Optional
import boto3
from botocore.exceptions import ClientError


def create_user(
    client: boto3.client, user_data: Dict[str, str], identity_store_id: str
) -> Tuple[bool, str, Optional[str]]:
    """
    Create a single user in IAM Identity Center using boto3.

    Returns:
        Tuple of (success: bool, message: str, user_id: Optional[str])
    """
    email = user_data["email"]
    username = user_data["username"]
    display_name = user_data["display_name"]
    given_name = user_data["given_name"]
    family_name = user_data["family_name"]

    print(f"Creating user: {username} ({display_name})")

    try:
        response = client.create_user(
            IdentityStoreId=identity_store_id,
            UserName=username,
            DisplayName=display_name,
            Name={"GivenName": given_name, "FamilyName": family_name},
            Emails=[{"Value": email, "Type": "Work", "Primary": True}],
        )

        user_id = response.get("UserId")
        success_msg = f"✅ Successfully created user: {username} (ID: {user_id})"
        print(success_msg)
        return True, success_msg, user_id

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        # Handle specific error cases
        if error_code == "ConflictException":
            error_msg = f"❌ User already exists: {username}"
        elif error_code == "ValidationException":
            error_msg = f"❌ Validation error for user {username}: {error_message}"
        elif error_code == "AccessDeniedException":
            error_msg = f"❌ Access denied creating user {username}. Check IAM permissions."
        elif error_code == "ResourceNotFoundException":
            error_msg = f"❌ Identity store not found. Check identity_store_id: {identity_store_id}"
        else:
            error_msg = f"❌ Failed to create user {username}: {error_code} - {error_message}"

        print(error_msg)
        return False, error_msg, None

    except Exception as e:
        error_msg = f"❌ Unexpected error creating user {username}: {e}"
        print(error_msg)
        return False, error_msg, None
