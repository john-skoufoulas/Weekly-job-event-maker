from __future__ import print_function
from datetime import datetime, timedelta
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils import EVENT_TITLE

SCOPES = ['https://www.googleapis.com/auth/calendar']


class myCalendar:
    creds = None
    service = None


    def __init__(self):
        if os.path.exists('auth/token.json'):
            self.creds = Credentials.from_authorized_user_file('auth/token.json', SCOPES)

        # If no valid credentials, run the OAuth flow
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'auth/client_secret.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('auth/token.json', 'w') as token:
                    token.write(self.creds.to_json())
        
        # Connect to Google Calendar API
        self.service = build('calendar', 'v3', credentials=self.creds)


    def create_event(self, event):
        # Insert the event into the primary calendar
        created_event = self.service.events().insert(calendarId='primary', body=event).execute()

        # Print the link to the event
        print(f"✅ Event created: {created_event.get('htmlLink')}")
    
    def check_events_exist(self, week='this'):
        events = self.get_weeks_events(week)
        for event in events:
            if event["summary"] == EVENT_TITLE:
                return True
        
        return False

    def get_weeks_events(self, week):
        # Get current date in UTC
        today = datetime.now()

        # Calculate start of the current week (Monday)
        start_of_this_week = today - timedelta(days=today.weekday())

        if week == 'this':
            start = start_of_this_week
        elif week == 'next':
            start = start_of_this_week + timedelta(days=7)
        else:
            raise ValueError("Argument 'week' must be 'this' or 'next'")

        end = start + timedelta(days=7)

        # Convert to RFC3339 format (required by Google Calendar API)
        time_min = start.isoformat() + 'Z'
        time_max = end.isoformat() + 'Z'

        # Fetch events
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])

mc = myCalendar()
print(mc.check_events_exist())