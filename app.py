import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from google.cloud.firestore_v1 import _helpers

# Initialize Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize Firebase Admin
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print("Error initializing Firebase:", e)
    db = None

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email'].lower()
            password = request.form['password']
            hashed_password = generate_password_hash(password)

            user_ref = db.collection('users').document(email)
            user = user_ref.get()

            if user.exists:
                flash('Email already registered. Please login.', 'warning')
                return redirect(url_for('login'))

            user_ref.set({
                'name': name,
                'email': email,
                'password': hashed_password,
                'balance': 0.0
            })

            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print("Registration error:", e)
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email'].lower()
            password = request.form['password']

            user_ref = db.collection('users').document(email)
            user_doc = user_ref.get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                if check_password_hash(user_data['password'], password):
                    session['email'] = email
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Incorrect password.', 'danger')
            else:
                flash('Email not found. Please register.', 'warning')
        except Exception as e:
            print("Login error:", e)
            flash('Login failed. Please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    try:
        email = session['email']
        user_ref = db.collection('users').document(email)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            # Fetch the 2 most recent transactions and their doc IDs
            transactions_ref = db.collection('transaction').where('email', '==', email).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(2)
            recent_transactions = []
            last_doc_id = None
            docs = list(transactions_ref.stream())
            for txn_doc in docs:
                data = txn_doc.to_dict()
                timestamp = data.get('timestamp')
                if hasattr(timestamp, 'to_datetime'):
                    timestamp = timestamp.to_datetime()
                recent_transactions.append({
                    'type': data.get('type', 'unknown'),
                    'amount': data.get('amount', 0.0),
                    'recipient_email': data.get('recipient_email', ''),
                    'timestamp': timestamp,
                    'description': data.get('description', data.get('type', 'Transaction').replace('_', ' ').title()),
                    'status': data.get('status', 'completed'),
                    'category': data.get('category', data.get('type', 'Other').title()),
                    'doc_id': txn_doc.id
                })
            if docs:
                last_doc_id = docs[-1].id
            return render_template('dashboard.html', user=user_data, recent_transactions=recent_transactions, last_doc_id=last_doc_id)
        else:
            flash('User data not found.', 'danger')
            return redirect(url_for('login'))
    except Exception as e:
        print("Dashboard error:", e)
        flash('Error loading dashboard.', 'danger')
        return redirect(url_for('login'))

# Deposit
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            email = session['email']
            user_ref = db.collection('users').document(email)
            user_doc = user_ref.get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                new_balance = user_data['balance'] + amount
                user_ref.update({'balance': new_balance})

                db.collection('transaction').add({
                    'email': email,
                    'recipient_email': email,
                    'amount': amount,
                    'type': 'deposit',
                    'timestamp': firestore.SERVER_TIMESTAMP
                })

                flash(f'Deposited ${amount:.2f} successfully.', 'success')
                return redirect(url_for('dashboard'))
        except Exception as e:
            print("Deposit error:", e)
            flash('Deposit failed. Please try again.', 'danger')
            return redirect(url_for('deposit'))
    return render_template('deposit.html')

# Withdraw
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            email = session['email']
            user_ref = db.collection('users').document(email)
            user_doc = user_ref.get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                if user_data['balance'] >= amount:
                    new_balance = user_data['balance'] - amount
                    user_ref.update({'balance': new_balance})

                    db.collection('transaction').add({
                        'email': email,
                        'recipient_email': email,
                        'amount': amount,
                        'type': 'withdraw',
                        'timestamp': firestore.SERVER_TIMESTAMP
                    })

                    flash(f'Withdrew ${amount:.2f} successfully.', 'success')
                else:
                    flash('Insufficient balance.', 'danger')
                return redirect(url_for('dashboard'))
        except Exception as e:
            print("Withdraw error:", e)
            flash('Withdrawal failed. Please try again.', 'danger')
            return redirect(url_for('withdraw'))
    return render_template('withdraw.html')

# Transfer
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            recipient_email = request.form['recipient'].lower()
            amount = float(request.form['amount'])
            sender_email = session['email']

            sender_ref = db.collection('users').document(sender_email)
            recipient_ref = db.collection('users').document(recipient_email)
            sender_doc = sender_ref.get()
            recipient_doc = recipient_ref.get()

            if not recipient_doc.exists:
                flash('Recipient not found.', 'danger')
                return redirect(url_for('transfer'))

            if sender_doc.exists:
                sender_data = sender_doc.to_dict()
                if sender_data['balance'] >= amount:
                    sender_ref.update({'balance': sender_data['balance'] - amount})
                    recipient_data = recipient_doc.to_dict()
                    recipient_ref.update({'balance': recipient_data['balance'] + amount})

                    db.collection('transaction').add({
                        'email': sender_email,
                        'recipient_email': recipient_email,
                        'amount': amount,
                        'type': 'transfer_sent',
                        'timestamp': firestore.SERVER_TIMESTAMP
                    })

                    db.collection('transaction').add({
                        'email': recipient_email,
                        'recipient_email': sender_email,
                        'amount': amount,
                        'type': 'transfer_received',
                        'timestamp': firestore.SERVER_TIMESTAMP
                    })

                    flash(f'Transferred ${amount:.2f} to {recipient_email}.', 'success')
                else:
                    flash('Insufficient balance.', 'danger')
                return redirect(url_for('dashboard'))
        except Exception as e:
            print("Transfer error:", e)
            flash('Transfer failed. Please try again.', 'danger')
            return redirect(url_for('transfer'))
    return render_template('transfer.html')

# History
@app.route('/history')
def history():
    if 'email' not in session:
        return redirect(url_for('login'))

    try:
        email = session['email'].lower()
        transactions_ref = db.collection('transaction').where('email', '==', email).order_by('timestamp', direction=firestore.Query.DESCENDING)
        transactions = []
        for txn_doc in transactions_ref.stream():
            data = txn_doc.to_dict()
            timestamp = data['timestamp']
            if hasattr(timestamp, 'to_datetime'):
                timestamp = timestamp.to_datetime()
            transactions.append({
                'type': data.get('type', 'unknown'),
                'amount': data.get('amount', 0.0),
                'recipient_email': data.get('recipient_email', ''),
                'timestamp': timestamp.strftime("%d %B %Y %H:%M:%S"),
            })
        return render_template('history.html', transactions=transactions)
    except Exception as e:
        print("History error:", e)
        flash('Failed to load transaction history.', 'danger')
        return redirect(url_for('dashboard'))

# Load More Transactions
@app.route('/load_more_transactions')
def load_more_transactions():
    if 'email' not in session:
        return jsonify({'transactions': [], 'has_more': False, 'last_doc_id': None})
    try:
        email = session['email']
        last_doc_id = request.args.get('last_doc_id')
        transactions_ref = db.collection('transaction').where('email', '==', email).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(2)
        if last_doc_id:
            # Get the last doc snapshot
            last_doc = db.collection('transaction').document(last_doc_id).get()
            if last_doc.exists:
                transactions_ref = db.collection('transaction').where('email', '==', email).order_by('timestamp', direction=firestore.Query.DESCENDING).start_after(last_doc).limit(2)
        docs = list(transactions_ref.stream())
        transactions = []
        new_last_doc_id = None
        for txn_doc in docs:
            data = txn_doc.to_dict()
            timestamp = data.get('timestamp')
            if hasattr(timestamp, 'to_datetime'):
                timestamp_dt = timestamp.to_datetime()
                timestamp_val = timestamp_dt.timestamp()
                timestamp_str = timestamp_dt.strftime('%Y-%m-%d %H:%M')
            else:
                timestamp_val = ''
                timestamp_str = ''
            transactions.append({
                'type': data.get('type', 'unknown'),
                'amount': data.get('amount', 0.0),
                'recipient_email': data.get('recipient_email', ''),
                'timestamp': timestamp_val,
                'timestamp_str': timestamp_str,
                'description': data.get('description', data.get('type', 'Transaction').replace('_', ' ').title()),
                'status': data.get('status', 'completed'),
                'category': data.get('category', data.get('type', 'Other').title()),
                'doc_id': txn_doc.id
            })
        if docs:
            new_last_doc_id = docs[-1].id
        has_more = len(docs) == 2
        return jsonify({'transactions': transactions, 'has_more': has_more, 'last_doc_id': new_last_doc_id})
    except Exception as e:
        print('Load more transactions error:', e)
        return jsonify({'transactions': [], 'has_more': False, 'last_doc_id': None})

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# Clear flashed messages
@app.after_request
def clear_flashes(response):
    session.pop('_flashes', None)
    return response

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
