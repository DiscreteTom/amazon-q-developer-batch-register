#!/usr/bin/env python3

"""
Script to create IAM Identity Center users from CSV file using boto3
Usage: python3 main.py <csv_file> <identity_store_id>

CSV format: email,username,display_name,given_name,family_name
Example: john.doe@example.com,johndoe,John Doe,John,Doe
"""

import argparse
import csv
import sys
from typing import Dict, List
import boto3
from create_user import create_user
from subscribe import subscribe


def read_users_from_csv(csv_file: str) -> List[Dict[str, str]]:
    """Read user data from CSV file."""
    users = []

    with open(csv_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row_num, row in enumerate(
            reader, start=2
        ):  # Start at 2 because header is row 1
            # Strip whitespace from all fields
            user_data = {key: value.strip() for key, value in row.items()}

            # Skip empty rows
            if not any(user_data.values()):
                continue

            # Validate required fields
            missing_fields = [key for key, value in user_data.items() if not value]
            if missing_fields:
                print(
                    f"❌ Skipping row {row_num} with missing fields: {missing_fields}"
                )
                print(f"   Row data: {dict(user_data)}")
                continue

            # Basic validation for username (IAM Identity Center restrictions)
            if user_data["username"].lower() in ["administrator", "awsadministrators"]:
                print(
                    f"❌ Skipping row {row_num}: Username '{user_data['username']}' is reserved"
                )
                continue

            if len(user_data["username"]) > 128:
                print(
                    f"❌ Skipping row {row_num}: Username '{user_data['username']}' exceeds 128 characters"
                )
                continue

            users.append(user_data)

    return users


def main():
    """Main function to orchestrate the user creation process."""
    parser = argparse.ArgumentParser(
        description="Create IAM Identity Center users from CSV file using boto3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV file format (with header):
email,username,display_name,given_name,family_name

Example:
john.doe@example.com,johndoe,John Doe,John,Doe
jane.smith@example.com,janesmith,Jane Smith,Jane,Smith

Requirements:
- boto3 library (pip install boto3)
- AWS credentials configured
- identitystore:CreateUser permission
        """,
    )

    parser.add_argument(
        "csv_file", help="Path to the CSV file containing user information"
    )
    parser.add_argument(
        "identity_store_id", help="IAM Identity Center Identity Store ID"
    )

    args = parser.parse_args()

    print("IAM Identity Center Bulk User Creation Script (boto3)")
    print("===================================================")
    print(f"CSV File: {args.csv_file}")
    print(f"Identity Store ID: {args.identity_store_id}")
    print()

    # Initialize AWS client
    client = boto3.client("identitystore")

    # Read users from CSV
    try:
        users = read_users_from_csv(args.csv_file)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    if not users:
        print("No valid users found in CSV file")
        sys.exit(1)

    print(f"Found {len(users)} valid users to create")
    print()

    # Initialize counters
    total_users = len(users)
    successful_users = 0
    failed_users = 0
    successful_subscriptions = 0
    failed_subscriptions = 0
    results = []

    # Process each user
    for i, user_data in enumerate(users, 1):
        print(f"[{i}/{total_users}] ", end="")
        success, message, user_id = create_user(client, user_data, args.identity_store_id)
        
        subscription_success = False
        subscription_message = ""
        
        if success and user_id:
            # User created successfully, now subscribe them
            print(f"  Subscribing user {user_data['username']} to Amazon Q Developer...")
            try:
                response = subscribe(user_id, "USER")
                if response.status_code == 200:
                    subscription_success = True
                    subscription_message = f"✅ Successfully subscribed user: {user_data['username']}"
                    print(f"  {subscription_message}")
                    successful_subscriptions += 1
                else:
                    subscription_message = f"❌ Failed to subscribe user {user_data['username']}: HTTP {response.status_code} - {response.text}"
                    print(f"  {subscription_message}")
                    failed_subscriptions += 1
            except Exception as e:
                subscription_message = f"❌ Error subscribing user {user_data['username']}: {e}"
                print(f"  {subscription_message}")
                failed_subscriptions += 1
        else:
            # User creation failed, skip subscription
            failed_subscriptions += 1
            subscription_message = "❌ Skipped subscription due to user creation failure"
        
        results.append((
            user_data["username"], 
            success, 
            message, 
            subscription_success, 
            subscription_message
        ))

        if success:
            successful_users += 1
        else:
            failed_users += 1

        print()  # Add blank line between users

    # Summary
    print("===================================================")
    print("Bulk User Creation and Subscription Summary")
    print("===================================================")
    print(f"Total users processed: {total_users}")
    print(f"Successfully created: {successful_users}")
    print(f"Failed to create: {failed_users}")
    print(f"Successfully subscribed: {successful_subscriptions}")
    print(f"Failed to subscribe: {failed_subscriptions}")
    print()

    if failed_users > 0 or failed_subscriptions > 0:
        print("⚠️  Some operations failed. Please check the errors above.")
        
        if failed_users > 0:
            print("\nFailed user creations:")
            for username, success, message, _, _ in results:
                if not success:
                    print(f"  - {username}: {message}")
        
        if failed_subscriptions > 0:
            print("\nFailed subscriptions:")
            for username, user_success, _, sub_success, sub_message in results:
                if user_success and not sub_success:
                    print(f"  - {username}: {sub_message}")
        
        sys.exit(1)
    else:
        print("🎉 All users created and subscribed successfully!")


if __name__ == "__main__":
    main()
