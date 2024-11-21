from flask import Flask, request, jsonify
import datetime
import os
import json
from openai import OpenAI
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pprint import pprint
import pickle

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

@app.route('/', methods=['GET'])
def home():
    return 'Hola mundo'

@app.route('/create-event', methods=['POST'])
def handle_create_event():
    try:
        event_link = create_event()
        return jsonify({'status': 'success', 'event_link': event_link})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_google_calendar_service():
    # Cargar las credenciales desde la variable de entorno
    credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    credentials = Credentials.from_service_account_info(credentials_info, scopes=['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=credentials)
    return service

def create_event():
    service = get_google_calendar_service()

    event = {
        'summary': 'Reunión de prueba',
        'location': 'Virtual',
        'description': 'Descripción del evento',
        'start': {
            'dateTime': '2024-11-21T10:00:00-06:00',
            'timeZone': 'America/Mexico_City',
        },
        'end': {
            'dateTime': '2024-11-21T11:00:00-06:00',
            'timeZone': 'America/Mexico_City',
        },
        'attendees': [
            {'email': 'correo@ejemplo.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event['htmlLink']


if __name__ == '__main__':
    app.run(debug=True)
