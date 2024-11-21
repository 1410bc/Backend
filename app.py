from flask import Flask, request, jsonify
import datetime
import os
import json
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
    return 'Hola Andy, este es mi servidor de Render'

@app.route('/create-event', methods=['POST'])
def create_google_calendar_event():
    """Recibe parámetros de una solicitud POST y crea un evento en Google Calendar."""
    try:
        # Extraer datos del cuerpo de la solicitud
        data = request.get_json()
        event_title = data.get('title')
        event_description = data.get('description')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not all([event_title, start_time, end_time]):
            return jsonify({"error": "Los campos 'title', 'start_time' y 'end_time' son obligatorios"}), 400

        # Autenticar con Google Calendar
        creds = authenticate_google_calendar()
        service = build('calendar', 'v3', credentials=creds)

        # Definir el evento
        event = {
            'summary': event_title,
            'description': event_description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Mexico_City',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Mexico_City',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        # Insertar el evento en Google Calendar
        event_result = service.events().insert(calendarId='primary', body=event).execute()

        return jsonify({
            "message": "Evento creado exitosamente",
            "event_link": event_result.get('htmlLink'),
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def authenticate_google_calendar():
    """Autenticación para acceder a la API de Google Calendar."""
    creds = None
    # Verifica si existe un token de autenticación guardado
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, se procede a autenticarse
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Guarda las credenciales para futuras ejecuciones
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

if __name__ == '__main__':
    app.run(debug=True)