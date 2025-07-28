# Batch Register Amazon Q Developer Pro Account For Kiro

This script allows you to create multiple users in AWS IAM Identity Center from a CSV file and automatically subscribe them to Amazon Q Developer.

## Prerequisites

1. **AWS Credentials** - Must be configured with appropriate credentials via:
   - `aws configure` command
   - IAM roles (for EC2 instances)
   - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
2. **Python 3.6+**
3. **boto3** - Install with `pip install boto3`
4. **requests** - Install with `pip install requests`
5. **Permissions** - Your AWS credentials must have:
   - `identitystore:CreateUser` and `identitystore:ListUsers` permissions
   - `q:CreateAssignment` permission
6. **Email OTP Configuration** - Enable the "Send email OTP" setting in IAM Identity Center to allow users created via API to receive password setup emails. Follow the instructions in the [AWS documentation](https://docs.aws.amazon.com/singlesignon/latest/userguide/userswithoutpwd.html) to configure this setting.

## Usage

```bash
python3 main.py <csv_file> <identity_store_id>
```

### Parameters

- `csv_file`: Path to the CSV file containing user information
- `identity_store_id`: Your IAM Identity Center Identity Store ID

### Example

```bash
python3 main.py sample_users.csv d-123123123
```

## File Structure

- `main.py` - Main script that creates users and subscribes them to Amazon Q Developer
- `create_user.py` - Module for creating IAM Identity Center users
- `subscribe.py` - Module for subscribing users to Amazon Q Developer

## CSV File Format

The CSV file must have the following header (exact format):

```
email,username,display_name,given_name,family_name
```

### Example CSV Content

```csv
email,username,display_name,given_name,family_name
john.doe@example.com,johndoe,John Doe,John,Doe
jane.smith@example.com,janesmith,Jane Smith,Jane,Smith
bob.wilson@example.com,bobwilson,Bob Wilson,Bob,Wilson
```

### Field Requirements

- **email**: User's email address (will be set as primary work email)
- **username**: Unique username (max 128 characters, cannot be `Administrator` or `AWSAdministrators`)
- **display_name**: Display name for the user
- **given_name**: User's first name (required by IAM Identity Center)
- **family_name**: User's last name (required by IAM Identity Center)
