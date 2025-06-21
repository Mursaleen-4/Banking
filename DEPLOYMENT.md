# Deployment Guide - Bank Application

## Overview
This guide helps resolve worker timeout and memory issues when deploying the Flask bank application.

## Issues Fixed

### 1. Worker Timeouts
- **Problem**: Gunicorn workers timing out after 30 seconds
- **Solution**: Increased timeout to 60 seconds, added retry logic for Firebase operations

### 2. Memory Issues
- **Problem**: Memory leaks causing worker crashes
- **Solution**: Added connection pooling, memory monitoring, and worker recycling

### 3. Firebase Connection Issues
- **Problem**: Firebase connections failing or timing out
- **Solution**: Added retry logic, connection testing, and better error handling

### 4. Route Conflicts
- **Problem**: Flask route decorator conflicts
- **Solution**: Removed problematic decorators and implemented retry logic directly

## Configuration Files

### gunicorn.conf.py
- Timeout: 60 seconds
- Workers: 2 (reduces memory usage)
- Max requests: 1000 (prevents memory leaks)
- Preload: True (faster startup)

### app.py Changes
- Firebase connection retry logic
- Memory monitoring
- Request performance tracking
- Health check endpoint
- Environment variable support for Firebase credentials

## Firebase Setup

### Quick Setup
Run the setup script to check your Firebase configuration:
```bash
python setup_firebase.py
```

### Development Setup
1. Download Firebase service account key from Firebase Console
2. Rename to `serviceAccountKey.json`
3. Place in project root directory

### Production Setup
1. Encode your Firebase credentials:
   ```bash
   base64 -w 0 serviceAccountKey.json
   ```
2. Set environment variable:
   ```bash
   export FIREBASE_SERVICE_ACCOUNT_KEY="your-base64-encoded-credentials"
   ```

## Deployment Steps

1. **Ensure all files are present**:
   - `serviceAccountKey.json` (development) OR `FIREBASE_SERVICE_ACCOUNT_KEY` env var (production)
   - `gunicorn.conf.py` (Gunicorn configuration)
   - Updated `app.py` with retry logic

2. **Deploy using Procfile**:
   ```
   web: gunicorn app:app -c gunicorn.conf.py
   ```

3. **Monitor the application**:
   - Check `/health` endpoint for status
   - Monitor logs for slow requests
   - Watch memory usage

## Troubleshooting

### Worker Timeouts
1. Check Firebase connection: `/health`
2. Verify Firebase credentials are properly configured
3. Check network connectivity to Firebase

### Memory Issues
1. Monitor memory usage via `/health` endpoint
2. Check for slow requests in logs
3. Restart workers if memory usage is high

### Firebase Connection Issues
1. Verify Firebase project settings
2. Check service account permissions
3. Ensure network allows Firebase connections
4. Run `python setup_firebase.py` to diagnose issues

### Route Conflicts
1. Ensure no duplicate route decorators
2. Check for conflicting function names
3. Verify Flask app initialization

## Monitoring

### Health Check
```bash
curl https://your-app.herokuapp.com/health
```

### Expected Response
```json
{
  "status": "healthy",
  "firebase": "connected",
  "memory_mb": 45.2,
  "cpu_percent": 2.1
}
```

### Log Monitoring
Watch for these log messages:
- `"Firebase initialized successfully from environment variable"`
- `"Firebase initialized successfully from file"`
- `"Slow request: login took 6.2s, memory: 52.1MB"`
- `"Firebase operation attempt 1 failed"`

## Performance Tips

1. **Use connection pooling**: Firebase connections are reused
2. **Monitor memory**: Check `/health` regularly
3. **Restart workers**: If memory usage exceeds 100MB
4. **Check logs**: Look for slow requests and errors
5. **Use environment variables**: More secure than files in production

## Emergency Recovery

If the app becomes unresponsive:

1. **Restart the dyno**:
   ```bash
   heroku restart
   ```

2. **Check Firebase status**:
   ```bash
   curl https://your-app.herokuapp.com/health
   ```

3. **Monitor logs**:
   ```bash
   heroku logs --tail
   ```

4. **Verify credentials**:
   ```bash
   python setup_firebase.py
   ```

## Expected Behavior

After deployment:
- Login/Register should complete within 5 seconds
- Memory usage should stay under 100MB
- No worker timeouts should occur
- Firebase operations should retry automatically on failure
- Health check should return "healthy" status 
