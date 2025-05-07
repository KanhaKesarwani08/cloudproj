# Budget Tracker FastAPI App

This is a simple budget tracker application built with FastAPI and a plain HTML, CSS, and JavaScript frontend.
The primary goal of this project is to demonstrate integration with Google Cloud Platform (GCP).

## Features (Conceptual)

*   User Login
*   Add Expenses
*   Categorize Expenses (using labels)
*   Save Expenses to a Database
*   Display Spending via a Graph

## Project Structure

```
budget_tracker/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app
│   ├── routers/            # FastAPI routers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── expenses.py
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── expense.py
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   └── budget_service.py
│   ├── templates/          # HTML templates
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   └── partials/
│   │       ├── header.html
│   │       └── footer.html
│   └── static/             # CSS and JS files
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── script.js
├── requirements.txt
├── Dockerfile              # For containerization
└── README.md
```

## Google Cloud Platform (GCP) Setup Guide

*(This section will be filled in with detailed steps for setting up the necessary GCP services, such as Cloud Run, Cloud SQL, Artifact Registry, etc.)*

### 0. Firebase Authentication Setup (Google Identity Platform)

Before deploying, you'll need to set up Firebase Authentication to handle user logins. This service is part of Google Cloud.

1.  **Go to the Firebase Console**:
    *   Navigate to [https://console.firebase.google.com/](https://console.firebase.google.com/).
    *   Click "Add project" and select your existing Google Cloud Project that you intend to use for this application. If you don't have one, create it first in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Enable Authentication**:
    *   Once your project is open in the Firebase console, go to "Authentication" (in the "Build" section of the left-hand menu).
    *   Click "Get started".
3.  **Choose Sign-in Methods**:
    *   Go to the "Sign-in method" tab.
    *   Enable the sign-in providers you want to use (e.g., "Email/Password", "Google", etc.). For this project, "Email/Password" is a good start. Configure it as needed.
4.  **Register Your Web App**:
    *   Go back to "Project Overview" (click the gear icon next to Project Overview, then "Project settings").
    *   Scroll down to "Your apps".
    *   Click the web icon (`</>`) to add a web app.
    *   Give your app a nickname (e.g., "Budget Tracker Web").
    *   You *don't* need to set up Firebase Hosting if we're serving the frontend from FastAPI or another GCP service like Cloud Storage.
    *   Click "Register app".
5.  **Get Firebase Configuration for Web**:
    *   After registering, Firebase will provide you with a `firebaseConfig` JavaScript object. This object contains API keys and project identifiers. **Copy this configuration object.** You will need to add this to your frontend JavaScript (`app/static/js/script.js` or a dedicated config file) to initialize the Firebase SDK.
    *   It will look something like this:
        ```javascript
        const firebaseConfig = {
          apiKey: "YOUR_API_KEY",
          authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
          projectId: "YOUR_PROJECT_ID",
          storageBucket: "YOUR_PROJECT_ID.appspot.com",
          messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
          appId: "YOUR_APP_ID"
        };
        ```
6.  **Service Account for Backend (Admin SDK)**:
    *   To allow your FastAPI backend to verify ID tokens, it needs Firebase Admin SDK credentials.
    *   In the Firebase console, go to "Project settings" (gear icon) > "Service accounts" tab.
    *   Select "Python" for the Admin SDK configuration snippet.
    *   Click "Generate new private key". A JSON file will be downloaded. **Store this file securely.**
    *   You'll need to make this JSON file available to your backend application when it's deployed on GCP (e.g., by storing it securely and providing its path via an environment variable, or using Google Secret Manager). For local development, you can set an environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of this JSON file.
        ```bash
        # Example for local development (in your terminal)
        # export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/serviceAccountKey.json"
        ```

This setup provides the foundation for user authentication. The frontend will use the `firebaseConfig` to interact with Firebase for login/signup, and the backend will use the service account JSON to verify tokens.

### Prerequisites

*   Google Cloud SDK installed and configured.
*   A GCP project.

### Steps

1.  **Database Setup (e.g., Cloud SQL)**
    *   ...
2.  **Containerization (Dockerfile)**
    *   ...
3.  **Pushing to Artifact Registry**
    *   ...
4.  **Deploying to Cloud Run (or App Engine)**
    *   ...
5.  **Setting up IAM permissions**
    *   ...
6.  **Frontend Hosting (e.g., Cloud Storage or served via FastAPI)**
    *   ...

## Local Development

*(Instructions for running the app locally will go here)*

To set up and run the application locally, follow these steps:

1.  **Clone the repository** (if you haven't already).

2.  **Navigate to the project directory**:
    ```bash
    cd budget_tracker
    ```

3.  **Create and activate a Python virtual environment**:
    *   Create the environment (e.g., named `venv`):
        ```bash
        python3 -m venv venv
        # Or: python -m venv venv
        ```
    *   Activate it:
        *   On macOS/Linux:
            ```bash
            source venv/bin/activate
            ```
        *   On Windows (Command Prompt):
            ```bash
            venv\Scripts\activate.bat
            ```
        *   On Windows (PowerShell):
            ```bash
            venv\Scripts\Activate.ps1
            ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up Firebase Admin SDK credentials (for local development)**:
    *   Ensure you have downloaded your Firebase service account JSON key file (as described in the Firebase Authentication Setup section).
    *   Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of this file. For example:
        *   On macOS/Linux:
            ```bash
            export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/serviceAccountKey.json"
            ```
        *   On Windows (Command Prompt):
            ```bash
            set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\serviceAccountKey.json"
            ```
        *   On Windows (PowerShell):
            ```bash
            $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\serviceAccountKey.json"
            ```
    *   **Important**: Add this JSON key file to your `.gitignore` file to prevent committing it to your repository.
        Create a `.gitignore` file in your project root if it doesn't exist, and add the filename:
        ```
        serviceAccountKey.json # Or whatever you named your key file
        venv/
        __pycache__/
        *.pyc
        .env
        ```

6.  **Run the FastAPI application**:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The application should now be accessible at `http://localhost:8000`.

```bash
# Example commands (summary)
# cd budget_tracker
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/serviceAccountKey.json" # (macOS/Linux)
# uvicorn app.main:app --reload
``` 