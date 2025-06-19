from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import uuid
from datetime import datetime, timedelta
import os
import random
import string
import time
import requests

import firebase_admin
from firebase_admin import credentials, firestore
from flask_mail import Mail, Message

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.elasticemail.com'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'makbaloch4@gmail.com'
app.config['MAIL_PASSWORD'] = '517BF418EBA5C8A67CF1BDC1F7CD1E9BC042'
app.config['MAIL_DEFAULT_SENDER'] = 'makbaloch4@gmail.com'
app.config['MAIL_DEBUG'] = True  # Enable debug mode for Flask-Mail

mail = Mail(app)

# In-memory storage (These will be replaced by Firestore)
# user_data = {}
# transaction_data = {}

def send_2fa_email(email, code):
    try:
        # Web3Forms API endpoint
        url = "https://api.web3forms.com/submit"
        
        # Prepare the payload
        payload = {
            "access_key": "1b216561-5b01-4f82-bcc1-075832daea26",  # Your key
            "subject": "Your 2FA Code",
            "from_name": "Bank App",
            "email": email,
            "message": f"Your 2FA code is: {code}\n\nThis code will expire in 5 minutes. Please use it to complete your login.\n\nIf you did not request this code, please ignore this email.",
            "headers": {
                "Reply-To": "makbaloch4@gmail.com",
                "X-Mailer": "Bank App 2FA System"
            }
        }
        
        # Send the request
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        # Check response
        if response.status_code == 200:
            print(f"2FA code sent successfully to {email}")
            return True
        else:
            print(f"Web3Forms API error: Status {response.status_code}")
            print(f"Error details: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("Request timed out while sending 2FA code")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error sending 2FA code: {str(e)}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        # Basic password strength check (server-side, complementing client-side)
        if len(password) < 8 or \
           not any(char.isupper() for char in password) or \
           not any(char.islower() for char in password) or \
           not any(char.isdigit() for char in password) or \
           not any(char in '!@#$%^&*' for char in password):
            flash('Password must be at least 8 characters long, contain uppercase, lowercase, number, and special character.', 'danger')
            return redirect(url_for('register'))

        # Check if email already exists
        user_ref_email = db.collection('users').where('email', '==', email).limit(1).get()
        if user_ref_email:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        # Check if phone number already exists
        user_ref_phone = db.collection('users').where('phone', '==', phone).limit(1).get()
        if user_ref_phone:
            flash('Phone number already registered', 'danger')
            return redirect(url_for('register'))

        try:
            # Create new user
            user_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'gender': gender,
                'password': password,  # In a real app, use proper password hashing
                'balance': 0,
                'created_at': datetime.now()
            }
            db.collection('users').add(user_data)

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        
        # First check if email exists
        user_ref = db.collection('users').where('email', '==', email).limit(1).get()
        if not user_ref:
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
            
        user = user_ref[0].to_dict()
        
        # Case-insensitive password comparison
        if user['password'].lower() == password.lower():
            # Set user session
            session['user'] = email
            
            # Add success message
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password', 'danger')
        return render_template('login.html')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session['user']
    user_ref = db.collection('users').where('email', '==', email).limit(1).get()
    if not user_ref:
        flash('User not found')
        return redirect(url_for('login'))
    user = user_ref[0].to_dict()
    return render_template('dashboard.html', user=user)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        email = session['user']
        user_ref = db.collection('users').where('email', '==', email).limit(1).get()
        if not user_ref:
            flash('User not found')
            return redirect(url_for('login'))
        user = user_ref[0]
        user_id = user.id
        user_data = user.to_dict()
        new_balance = user_data['balance'] + amount
        db.collection('users').document(user_id).update({'balance': new_balance})
        flash('Deposit successful!')
        return redirect(url_for('dashboard'))
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        email = session['user']
        user_ref = db.collection('users').where('email', '==', email).limit(1).get()
        if not user_ref:
            flash('User not found')
            return redirect(url_for('login'))
        user = user_ref[0]
        user_id = user.id
        user_data = user.to_dict()
        if user_data['balance'] < amount:
            flash('Insufficient funds')
            return redirect(url_for('withdraw'))
        new_balance = user_data['balance'] - amount
        db.collection('users').document(user_id).update({'balance': new_balance})
        flash('Withdrawal successful!')
        return redirect(url_for('dashboard'))
    return render_template('withdraw.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            to_uid = request.form.get('target_uid')
            amount = float(request.form['amount'])
            
            if amount <= 0:
                flash('Amount must be positive', 'error')
                return redirect(url_for('transfer'))
                
            from_uid = session['user_id']
            
            # Cannot transfer to self
            if from_uid == to_uid:
                flash('Cannot transfer to your own UID.', 'error')
                return redirect(url_for('transfer'))

            from_user_ref = db.collection('users').document(from_uid)
            to_user_ref = db.collection('users').document(to_uid)

            # Use a transaction to safely transfer funds between accounts
            @firestore.transactional
            def transfer_funds_in_transaction(transaction, from_u_ref, to_u_ref, amt):
                from_snapshot = from_u_ref.get(transaction=transaction)
                to_snapshot = to_u_ref.get(transaction=transaction)

                if not from_snapshot.exists or not to_snapshot.exists:
                    return False # One or both users do not exist
                
                from_balance = from_snapshot.get('money')

                if from_balance is not None and from_balance >= amt:
                    transaction.update(from_u_ref, {'money': firestore.Increment(-amt)})
                    transaction.update(to_u_ref, {'money': firestore.Increment(amt)})
                    return True
                return False # Insufficient balance

            # Correct way to run the transaction for transfer
            transaction = db.transaction()
            if transfer_funds_in_transaction(transaction, from_user_ref, to_user_ref, amount):
                # Record transaction for sender
                db.collection('transactions').add({
                    'user_id': from_uid,
                    'type': 'transfer_sent',
                    'amount': amount,
                    'timestamp': datetime.now(),
                    'description': f'Transfer of ${amount:.2f} to {to_uid}'
                })
                
                # Record transaction for recipient
                db.collection('transactions').add({
                    'user_id': to_uid,
                    'type': 'transfer_received',
                    'amount': amount,
                    'timestamp': datetime.now(),
                    'description': f'Received ${amount:.2f} from {from_uid}'
                })
                
                flash('Transfer successful!', 'success')
            else:
                flash('Transfer failed: Insufficient funds or invalid recipient.', 'error')
                
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid amount', 'error')
            return redirect(url_for('transfer'))
        except Exception as e:
            flash(f'Error processing transfer: {e}', 'error')
            return redirect(url_for('transfer'))
            
    return render_template('transfer.html')

@app.route('/balance')
def balance():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    try:
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            flash('User not found.', 'error')
            return redirect(url_for('login'))
        
        balance = user_doc.get('money')
        return render_template('balance.html', balance=balance)
    except Exception as e:
        flash(f'Error loading balance: {e}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    try:
        transactions_ref = db.collection('transactions').where(filter=firestore.FieldFilter('user_id', '==', user_id)).order_by('timestamp', direction=firestore.Query.DESCENDING)
        history = [doc.to_dict() for doc in transactions_ref.stream()]

        return render_template('history.html', history=history)
    except Exception as e:
        flash(f'Error loading history: {e}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
