#!/usr/bin/env python3
"""
calendar_sync.py - Google Calendar Synchronization Tool
Handles authentication and calendar operations
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

import sys
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Get the directory where the script is located
SCRIPT_DIR = Path(__file__).parent.absolute()

# Use relative paths from script location (works everywhere!)
TOKEN_FILE = SCRIPT_DIR / 'secrets' / 'token.pickle'
CREDS_FILE = SCRIPT_DIR / 'secrets' / 'credentials.json'

# Ensure secrets directory exists
(SCRIPT_DIR / 'secrets').mkdir(exist_ok=True)


class CalendarSync:
    """Handles all Google Calendar operations"""

    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Calendar"""
        creds = None

        # Load existing token
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDS_FILE):
                    print(f"Error: {CREDS_FILE} not found!")
                    print("   Download credentials from Google Cloud Console")
                    sys.exit(1)

                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save token
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)
        print("Connected to Google Calendar")

    def get_calendars(self):
        """List all accessible calendars"""
        if not self.service:
            print("Error: Not authenticated")
            return []

        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except Exception as e:
            print(f"Error fetching calendars: {e}")
            return []

    def get_events(self, calendar_id, days=7):
        """Get events from calendar for next N days"""
        if not self.service:
            print("Error: Not authenticated")
            return []

        try:
            now = datetime.utcnow()
            end = now + timedelta(days=days)

            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now.isoformat() + 'Z',
                timeMax=end.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []

    def create_event(self, calendar_id, summary, description, start_time, end_time, attendees=None):
        """Create a calendar event"""
        if not self.service:
            print("Error: Not authenticated")
            return None

        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'Africa/Johannesburg'},
            'end': {'dateTime': end_time, 'timeZone': 'Africa/Johannesburg'},
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        if attendees:
            # Create empty list to store attendee dictionaries
            attendee_list = []

            # Loop through each email in attendees
            for email in attendees:
                # Create dictionary for this attendee
                attendee_dict = {'email': email}

                # Add to list
                attendee_list.append(attendee_dict)

            # Assign the list to event
            event['attendees'] = attendee_list

        try:
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'
            ).execute()
            return created_event.get('id')
        except Exception as e:
            print(f"Error creating event: {e}")
            return None

    def delete_event(self, calendar_id, event_id):
        """Delete a calendar event"""
        if not self.service:
            print("Error: Not authenticated")
            return False

        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False


if __name__ == "__main__":
    # Test the connection
    print("Testing Google Calendar connection...\n")
    sync = CalendarSync()

    calendars = sync.get_calendars()
    print(f"\nFound {len(calendars)} calendar(s):\n")

    for cal in calendars:
        print(f"{cal['summary']}")
        print(f"ID: {cal['id']}")
        if cal.get('primary'):
            print(f"(Primary Calendar)")
        print()
