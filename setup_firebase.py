#!/usr/bin/env python3
"""
Firebase Setup Script for Bank Application
This script helps set up Firebase credentials for deployment.
"""

import os
import json
import base64
import sys

def check_firebase_credentials():
    """Check if Firebase credentials are properly configured"""
    print("🔍 Checking Firebase credentials...")
    
    # Check if serviceAccountKey.json exists
    if os.path.exists('serviceAccountKey.json'):
        print("✅ serviceAccountKey.json found")
        try:
            with open('serviceAccountKey.json', 'r') as f:
                creds = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in creds]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            else:
                print("✅ Firebase credentials are valid")
                return True
        except json.JSONDecodeError:
            print("❌ Invalid JSON in serviceAccountKey.json")
            return False
    else:
        print("❌ serviceAccountKey.json not found")
        return False

def create_example_credentials():
    """Create example credentials file"""
    example_creds = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
    with open('serviceAccountKey.example.json', 'w') as f:
        json.dump(example_creds, f, indent=2)
    print("✅ Created serviceAccountKey.example.json")

def setup_environment_variable():
    """Help set up environment variable for production"""
    if os.path.exists('serviceAccountKey.json'):
        try:
            with open('serviceAccountKey.json', 'r') as f:
                content = f.read()
            
            # Encode to base64
            encoded = base64.b64encode(content.encode()).decode()
            
            print("\n🌐 For production deployment, set this environment variable:")
            print(f"FIREBASE_SERVICE_ACCOUNT_KEY={encoded}")
            print("\nOr use this command:")
            print(f"export FIREBASE_SERVICE_ACCOUNT_KEY='{encoded}'")
            
        except Exception as e:
            print(f"❌ Error encoding credentials: {e}")
    else:
        print("❌ serviceAccountKey.json not found. Cannot create environment variable.")

def main():
    print("🚀 Firebase Setup for Bank Application")
    print("=" * 50)
    
    # Check current setup
    if check_firebase_credentials():
        print("\n✅ Firebase is properly configured!")
        setup_environment_variable()
    else:
        print("\n❌ Firebase is not properly configured.")
        print("\n📋 Setup Instructions:")
        print("1. Go to Firebase Console: https://console.firebase.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Go to Project Settings > Service Accounts")
        print("4. Click 'Generate new private key'")
        print("5. Download the JSON file")
        print("6. Rename it to 'serviceAccountKey.json'")
        print("7. Place it in the project root directory")
        print("8. Run this script again")
        
        # Create example file
        create_example_credentials()
        print("\n📄 Created serviceAccountKey.example.json for reference")
    
    print("\n" + "=" * 50)
    print("🎯 Next steps:")
    print("- For local development: Ensure serviceAccountKey.json is in project root")
    print("- For production: Use environment variable FIREBASE_SERVICE_ACCOUNT_KEY")
    print("- Test the setup: python app.py")

if __name__ == "__main__":
    main() 