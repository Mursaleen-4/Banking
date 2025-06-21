#!/bin/bash

echo "Starting Bank Application..."

# Check if service account key exists
if [ ! -f "serviceAccountKey.json" ]; then
    echo "ERROR: serviceAccountKey.json not found!"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
python -c "import flask, firebase_admin, gunicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Test Firebase connection
echo "Testing Firebase connection..."
python -c "
import firebase_admin
from firebase_admin import credentials, firestore
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    db.collection('users').limit(1).stream()
    print('Firebase connection successful')
except Exception as e:
    print(f'Firebase connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "ERROR: Firebase connection test failed!"
    exit 1
fi

echo "Starting Gunicorn server..."
exec gunicorn app:app -c gunicorn.conf.py 