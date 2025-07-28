#!/bin/bash

# Script to create IAM Identity Center users from CSV file
# Usage: ./create_users_from_csv.sh <csv_file> <identity_store_id>
#
# CSV format: email,username,display_name,given_name,family_name
# Example: john.doe@example.com,johndoe,John Doe,John,Doe

set -e  # Exit on any error

# Function to display usage
usage() {
    echo "Usage: $0 <csv_file> <identity_store_id>"
    echo ""
    echo "CSV file format (with header):"
    echo "email,username,display_name,given_name,family_name"
    echo ""
    echo "Example:"
    echo "john.doe@example.com,johndoe,John Doe,John,Doe"
    echo "jane.smith@example.com,janesmith,Jane Smith,Jane,Smith"
    exit 1
}

# Function to validate AWS CLI is installed and configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo "Error: AWS CLI is not installed or not in PATH"
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "Error: AWS CLI is not configured or credentials are invalid"
        exit 1
    fi
}

# Function to validate CSV file format
validate_csv() {
    local csv_file="$1"
    
    if [[ ! -f "$csv_file" ]]; then
        echo "Error: CSV file '$csv_file' does not exist"
        exit 1
    fi
    
    # Check if file has header
    local header=$(head -n 1 "$csv_file")
    if [[ "$header" != "email,username,display_name,given_name,family_name" ]]; then
        echo "Error: CSV file must have header: email,username,display_name,given_name,family_name"
        echo "Found header: $header"
        exit 1
    fi
    
    # Check if file has data beyond header
    local line_count=$(wc -l < "$csv_file")
    if [[ $line_count -lt 2 ]]; then
        echo "Error: CSV file must contain at least one data row"
        exit 1
    fi
}

# Function to create a single user
create_user() {
    local email="$1"
    local username="$2"
    local display_name="$3"
    local given_name="$4"
    local family_name="$5"
    local identity_store_id="$6"
    
    echo "Creating user: $username ($display_name)"
    
    # Create the user using AWS CLI
    local result
    if result=$(aws identitystore create-user \
        --identity-store-id "$identity_store_id" \
        --user-name "$username" \
        --display-name "$display_name" \
        --name "{\"GivenName\":\"$given_name\",\"FamilyName\":\"$family_name\"}" \
        --emails "[{\"Value\":\"$email\",\"Type\":\"Work\",\"Primary\":true}]" \
        --output json 2>&1); then
        
        local user_id=$(echo "$result" | jq -r '.UserId')
        echo "✅ Successfully created user: $username (ID: $user_id)"
        return 0
    else
        echo "❌ Failed to create user: $username"
        echo "Error: $result"
        return 1
    fi
}

# Main function
main() {
    # Check arguments
    if [[ $# -ne 2 ]]; then
        usage
    fi
    
    local csv_file="$1"
    local identity_store_id="$2"
    
    echo "IAM Identity Center Bulk User Creation Script"
    echo "============================================="
    echo "CSV File: $csv_file"
    echo "Identity Store ID: $identity_store_id"
    echo ""
    
    # Validate prerequisites
    echo "Checking AWS CLI..."
    check_aws_cli
    echo "AWS CLI check passed"
    
    echo "Validating CSV file..."
    validate_csv "$csv_file"
    echo "CSV validation passed"
    
    # Check if jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required for JSON parsing but not installed"
        echo "Install with: sudo yum install jq (Amazon Linux) or sudo apt-get install jq (Ubuntu)"
        exit 1
    fi
    
    # Initialize counters
    local total_users=0
    local successful_users=0
    local failed_users=0
    
    # Process CSV file (skip header)
    while IFS=',' read -r email username display_name given_name family_name; do
        # Skip empty lines
        [[ -z "$email" ]] && continue
        
        ((total_users++))
        
        # Trim whitespace
        email=$(echo "$email" | xargs)
        username=$(echo "$username" | xargs)
        display_name=$(echo "$display_name" | xargs)
        given_name=$(echo "$given_name" | xargs)
        family_name=$(echo "$family_name" | xargs)
        
        # Validate required fields
        if [[ -z "$email" || -z "$username" || -z "$display_name" || -z "$given_name" || -z "$family_name" ]]; then
            echo "❌ Skipping row with missing fields: $email,$username,$display_name,$given_name,$family_name"
            ((failed_users++))
            continue
        fi
        
        # Create the user
        if create_user "$email" "$username" "$display_name" "$given_name" "$family_name" "$identity_store_id"; then
            ((successful_users++))
        else
            ((failed_users++))
        fi
        
        echo ""  # Add blank line between users
        
    done < <(tail -n +2 "$csv_file")  # Skip header line
    
    # Summary
    echo "============================================="
    echo "Bulk User Creation Summary"
    echo "============================================="
    echo "Total users processed: $total_users"
    echo "Successfully created: $successful_users"
    echo "Failed: $failed_users"
    echo ""
    
    if [[ $failed_users -gt 0 ]]; then
        echo "⚠️  Some users failed to create. Please check the errors above."
        exit 1
    else
        echo "🎉 All users created successfully!"
    fi
}

# Run main function with all arguments
main "$@"
