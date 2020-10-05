from firebase_admin import credentials, initialize_app

creds = credentials.Certificate("notifications/firebase/firebase_credentials.json")
initialize_app(creds)
