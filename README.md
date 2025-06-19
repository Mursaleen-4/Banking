# Bank Web Application

This is a simple Flask web application for managing bank accounts. Users can register, deposit money, and check their balance.

## Project Structure

```
bank_web
├── app.py                # Main entry point of the Flask application
├── templates             # Directory for HTML templates
│   ├── index.html       # Homepage of the application
│   ├── register.html     # Registration form for new users
│   ├── deposit.html      # Form for depositing money
│   └── balance.html      # Displays user's current balance
├── static                # Directory for static files
│   └── css
│       └── style.css     # Custom CSS styles for the application
├── userdata.txt          # File for storing user data
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd bank_web
   ```

2. **Install dependencies**:
   Make sure you have Python and pip installed. Then run:
   ```
   pip install Flask
   ```

3. **Run the application**:
   ```
   python app.py
   ```

4. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage Guidelines

- **Register**: Navigate to the registration page to create a new account.
- **Deposit**: After registering, you can deposit money into your account.
- **Check Balance**: View your current balance at any time.

## Note

User data is stored in `userdata.txt`. Ensure this file is secure and not publicly accessible.