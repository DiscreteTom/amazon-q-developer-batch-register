# IAM Identity Center Bulk User Creation Script

This script allows you to create multiple users in AWS IAM Identity Center from a CSV file.

## Prerequisites

1. **AWS CLI** - Must be installed and configured with appropriate credentials
2. **jq** - JSON processor for parsing AWS CLI responses
3. **Permissions** - Your AWS credentials must have `identitystore:CreateUser` permission
4. **Email OTP Configuration** - Enable the "Send email OTP" setting in IAM Identity Center to allow users created via API to receive password setup emails. Follow the instructions in the [AWS documentation](https://docs.aws.amazon.com/singlesignon/latest/userguide/userswithoutpwd.html) to configure this setting.

## Usage

```bash
./create_users_from_csv.sh <csv_file> <identity_store_id>
```

### Parameters

- `csv_file`: Path to the CSV file containing user information
- `identity_store_id`: Your IAM Identity Center Identity Store ID

### Example

```bash
./create_users_from_csv.sh sample_users.csv d-123123123
```

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
