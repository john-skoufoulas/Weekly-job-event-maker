import datetime
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils import *
import copy

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
        today = datetime.datetime.now()

        # Calculate start of the current week (Monday)
        start_of_this_week = today - datetime.timedelta(days=today.weekday())

        if week == 'this':
            start = start_of_this_week
        elif week == 'next':
            start = start_of_this_week + datetime.timedelta(days=7)
        else:
            raise ValueError("Argument 'week' must be 'this' or 'next'")

        end = start + datetime.timedelta(days=7)

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

    def create_schedule(self, schedule_string: str): 
        """schedule_string example: '['ε', 'ε', 'ε', 'β', 'π', 'π', 'π']'"""
        
        schedule_validation = self.schedule_is_valid(schedule_string)
        if not schedule_validation['is_valid']:
            return(schedule_validation['error_message'])
        
        user_schedule = schedule_string.split(',')

        if datetime.datetime.now().weekday() == 6: 
            week = "next" 
        else: 
            week = "this"
        
        # Check if the events already exist
        if self.check_events_exist(week):
            return("Scheduled events already exist for this week.")

        week_events = []

        for shift_type, day in zip(user_schedule, DAYS.keys()):
            
            if shift_type.lower() == 'ρ':
                continue

            # create starting reminder
            starting_event = copy.deepcopy(BASIC_EVENT)
            starting_time = SHIFTS[shift_type.lower()]["start"]

            starting_event["start"]["dateTime"] = get_datetime_for_weekday(day, starting_time-1, 55, week) # 5 minutes earlier
            starting_event["end"]["dateTime"] = get_datetime_for_weekday(day, starting_time-1, 56, week)
            starting_event["description"] = "Προσέλευση"

            # create ending reminder
            end_event = copy.deepcopy(BASIC_EVENT)
            end_time = SHIFTS[shift_type.lower()]["end"]
            
            if end_time > starting_time:
                end_event["start"]["dateTime"] = get_datetime_for_weekday(day, end_time, 5, week) # 5 minutes later
                end_event["end"]["dateTime"] = get_datetime_for_weekday(day, end_time, 6, week)
            else:
                end_event["start"]["dateTime"] = get_datetime_for_weekday(get_next_day(day), end_time, 5, week) # 5 minutes later
                end_event["end"]["dateTime"] = get_datetime_for_weekday(get_next_day(day), end_time, 6, week)
            end_event["description"] = "Αποχώρηση"
            
            week_events.extend([starting_event, end_event])

        for event in week_events:
            self.create_event(event)
        
        return('✅ Created '+str(len(week_events))+' events.')
    
    def schedule_is_valid(self, schedule_string):
        if type(schedule_string) != str:
            return({"is_valid":False, "error_message":"Error: Input type must be string. Got"+ str(type(schedule_string))})
        
        user_schedule = schedule_string.split(',')
        
        if len(user_schedule) != 7:
            return({"is_valid":False, "error_message":"Error: Enter a 7 day schedule."})
        for letter in user_schedule:
            if letter not in SHIFTS.keys() or len(letter) != 1:
                return({"is_valid":False, "error_message":"Error: Invalid shift letters."})
        
        return({"is_valid":True, "error_message":""}) 