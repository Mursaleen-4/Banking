# Bank Web Application

This is a secure Flask web application for managing bank accounts. Users can register, login, deposit, withdraw, transfer money, and view transaction history. The application uses Firebase Firestore for data storage.

## Project Structure

```
Bank Project
├── app.py                    # Main Flask application with Firebase integration
├── serviceAccountKey.json    # Firebase credentials (DO NOT COMMIT TO GIT)
├── serviceAccountKey.example.json # Example Firebase credentials template
├── requirements.txt          # Python dependencies
├── Procfile                 # Heroku deployment configuration
├── gunicorn.conf.py         # Gunicorn server configuration
├── start.sh                 # Deployment startup script
├── .gitignore               # Git ignore rules for security
├── DEPLOYMENT.md            # Deployment and troubleshooting guide
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Landing page
│   ├── login.html          # User login form
│   ├── register.html       # User registration form
│   ├── dashboard.html      # User dashboard with balance and recent transactions
│   ├── deposit.html        # Money deposit form
│   ├── withdraw.html       # Money withdrawal form
│   ├── transfer.html       # Money transfer form
│   └── history.html        # Transaction history page
├── static/                  # Static assets
│   ├── css/
│   │   └── style.css       # Custom CSS styles
│   ├── js/
│   │   └── main.js         # Custom JavaScript functionality
│   ├── images/             # Application images
│   └── favicon.ico         # Browser favicon
└── README.md               # This documentation
```

## Security Features

- **Firebase Authentication**: Secure user authentication and session management
- **Password Hashing**: Passwords are hashed using Werkzeug's security functions
- **Input Validation**: All user inputs are validated and sanitized
- **Session Management**: Secure session handling with Flask sessions
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- Firebase project with Firestore database
- Firebase service account credentials

### 1. Clone the Repository
```bash
git clone <repository-url>
cd bank-project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore database
3. Create a service account and download the JSON key file
4. Rename the downloaded file to `serviceAccountKey.json`
5. Place it in the project root directory

### 4. Run the Application
```bash
# Development mode
python app.py

# Production mode (using Gunicorn)
gunicorn app:app -c gunicorn.conf.py
```

### 5. Access the Application
Open your browser and go to `http://127.0.0.1:5000`

## Deployment

### Heroku Deployment
1. Create a Heroku app
2. Set up Firebase credentials as environment variables
3. Deploy using the provided Procfile and gunicorn configuration

### Environment Variables
For production deployment, set these environment variables:
- `FIREBASE_SERVICE_ACCOUNT_KEY`: Your Firebase service account JSON (base64 encoded)

## Features

- **User Registration & Login**: Secure user account creation and authentication
- **Dashboard**: Overview of balance and recent transactions
- **Deposit**: Add money to account
- **Withdraw**: Remove money from account (with balance validation)
- **Transfer**: Send money to other users
- **Transaction History**: View all past transactions with pagination
- **Responsive Design**: Works on desktop and mobile devices

## Security Considerations

### ⚠️ IMPORTANT: Firebase Credentials
- **NEVER commit `serviceAccountKey.json` to version control**
- The `.gitignore` file is configured to exclude this file
- Use environment variables in production
- Keep your Firebase credentials secure

### Data Protection
- All passwords are hashed using bcrypt
- User sessions are managed securely
- Input validation prevents injection attacks
- Error messages don't expose sensitive information

## Monitoring and Health Checks

The application includes monitoring features:
- **Health Check Endpoint**: `/health` - Check application status and Firebase connectivity
- **Memory Monitoring**: Tracks memory usage and CPU utilization
- **Request Logging**: Logs slow requests and errors
- **Firebase Connection Monitoring**: Automatic retry logic for connection issues

## Troubleshooting

See `DEPLOYMENT.md` for detailed troubleshooting guide, including:
- Worker timeout issues
- Memory problems
- Firebase connection errors
- Performance optimization tips

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please ensure compliance with local banking regulations if used in production.
