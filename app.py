import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client.get_default_database()
users_col = db["users"]
transactions_col = db["transactions"]

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

            user = users_col.find_one({"email": email})
            if user:
                flash('Email already registered. Please login.', 'warning')
                return redirect(url_for('login'))

            users_col.insert_one({
                'name': name,
                'email': email,
                'password': hashed_password,
                'balance': 0.0
            })

            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Registration error: {e}")
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
            user = users_col.find_one({"email": email})
            if user and check_password_hash(user['password'], password):
                session['user'] = email
                flash('Login successful.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('Login failed. Please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session['user']
    user = users_col.find_one({"email": email})
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))
    # Fetch only the latest transaction
    transactions = list(transactions_col.find({"user": email}).sort("timestamp", -1).limit(1))
    for txn in transactions:
        txn['description'] = txn.get('type', '').replace('_', ' ').title()
        if txn['type'] == 'transfer_sent':
            txn['recipient_email'] = txn.get('to', '-')
        elif txn['type'] == 'transfer_received':
            txn['recipient_email'] = txn.get('from', '-')
        else:
            txn['recipient_email'] = '-'
        txn['status'] = txn.get('status', 'completed')
    return render_template('dashboard.html', user=user, recent_transactions=transactions)

# Load more transactions (AJAX)
@app.route('/load_more_transactions')
def load_more_transactions():
    if 'user' not in session:
        return jsonify({'transactions': [], 'has_more': False})
    email = session['user']
    skip = int(request.args.get('skip', 1))
    limit = int(request.args.get('limit', 5))
    logger.info(f"/load_more_transactions called: skip={skip}, limit={limit}, user={email}")
    transactions = list(transactions_col.find({"user": email}).sort("timestamp", -1).skip(skip).limit(limit))
    logger.info(f"Transactions returned: {len(transactions)}")
    for txn in transactions:
        txn['_id'] = str(txn['_id'])  # Convert ObjectId to string
        txn['description'] = txn.get('type', '').replace('_', ' ').title()
        if txn['type'] == 'transfer_sent':
            txn['recipient_email'] = txn.get('to', '-')
        elif txn['type'] == 'transfer_received':
            txn['recipient_email'] = txn.get('from', '-')
        else:
            txn['recipient_email'] = '-'
        txn['status'] = txn.get('status', 'completed')
        txn['timestamp'] = txn['timestamp'].isoformat() if txn.get('timestamp') else ''
    has_more = len(transactions) == limit
    logger.info(f"has_more: {has_more}")
    return jsonify({'transactions': transactions, 'has_more': has_more})

# Refresh transactions (AJAX)
@app.route('/refresh_transactions')
def refresh_transactions():
    if 'user' not in session:
        return jsonify({'transactions': []})
    email = session['user']
    transactions = list(transactions_col.find({"user": email}).sort("timestamp", -1).limit(1))
    for txn in transactions:
        txn['_id'] = str(txn['_id'])  # Convert ObjectId to string
        txn['description'] = txn.get('type', '').replace('_', ' ').title()
        if txn['type'] == 'transfer_sent':
            txn['recipient_email'] = txn.get('to', '-')
        elif txn['type'] == 'transfer_received':
            txn['recipient_email'] = txn.get('from', '-')
        else:
            txn['recipient_email'] = '-'
        txn['status'] = txn.get('status', 'completed')
        txn['timestamp'] = txn['timestamp'].isoformat() if txn.get('timestamp') else ''
    return jsonify({'transactions': transactions})

# Deposit
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session['user']
    user = users_col.find_one({"email": email})
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Amount must be positive.', 'warning')
                return redirect(url_for('deposit'))
            new_balance = user['balance'] + amount
            users_col.update_one({"email": email}, {"$set": {"balance": new_balance}})
            transactions_col.insert_one({
                "user": email,
                "type": "deposit",
                "amount": amount,
                "timestamp": datetime.utcnow(),
                "status": "completed"
            })
            flash('Deposit successful.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Deposit error: {e}")
            flash('Deposit failed. Please try again.', 'danger')
            return redirect(url_for('deposit'))
    return render_template('deposit.html', user=user)

# Withdraw
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session['user']
    user = users_col.find_one({"email": email})
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Amount must be positive.', 'warning')
                return redirect(url_for('withdraw'))
            if user['balance'] < amount:
                flash('Insufficient balance.', 'danger')
                return redirect(url_for('withdraw'))
            new_balance = user['balance'] - amount
            users_col.update_one({"email": email}, {"$set": {"balance": new_balance}})
            transactions_col.insert_one({
                "user": email,
                "type": "withdraw",
                "amount": amount,
                "timestamp": datetime.utcnow(),
                "status": "completed"
            })
            flash('Withdrawal successful.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Withdraw error: {e}")
            flash('Withdrawal failed. Please try again.', 'danger')
            return redirect(url_for('withdraw'))
    return render_template('withdraw.html', user=user)

# Transfer
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session['user']
    user = users_col.find_one({"email": email})
    if request.method == 'POST':
        try:
            recipient_email = request.form['recipient'].lower()
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Amount must be positive.', 'warning')
                return redirect(url_for('transfer'))
            if user['balance'] < amount:
                flash('Insufficient balance.', 'danger')
                return redirect(url_for('transfer'))
            recipient = users_col.find_one({"email": recipient_email})
            if not recipient:
                flash('Recipient not found.', 'danger')
                return redirect(url_for('transfer'))
            # Update balances
            users_col.update_one({"email": email}, {"$set": {"balance": user['balance'] - amount}})
            users_col.update_one({"email": recipient_email}, {"$set": {"balance": recipient['balance'] + amount}})
            # Log transactions for both users
            transactions_col.insert_one({
                "user": email,
                "type": "transfer_sent",
                "amount": amount,
                "to": recipient_email,
                "timestamp": datetime.utcnow(),
                "status": "completed"
            })
            transactions_col.insert_one({
                "user": recipient_email,
                "type": "transfer_received",
                "amount": amount,
                "from": email,
                "timestamp": datetime.utcnow(),
                "status": "completed"
            })
            flash('Transfer successful.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Transfer error: {e}")
            flash('Transfer failed. Please try again.', 'danger')
            return redirect(url_for('transfer'))
    return render_template('transfer.html', user=user)

# Transaction History
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session['user']
    transactions = list(transactions_col.find({"user": email}).sort("timestamp", -1))
    # Add recipient_email and status for each transaction
    for txn in transactions:
        if txn['type'] == 'transfer_sent':
            txn['recipient_email'] = txn.get('to', '-')
        elif txn['type'] == 'transfer_received':
            txn['recipient_email'] = txn.get('from', '-')
        else:
            txn['recipient_email'] = '-'
        txn['status'] = txn.get('status', 'completed')
    return render_template('history.html', transactions=transactions)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# Flash message clearing
@app.after_request
def clear_flashes(response):
    session.pop('_flashes', None)
    return response

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
