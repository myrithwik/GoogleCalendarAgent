import json
from typing import Dict, Any
from api_keys.google_apis import create_service
from agents import function_tool
from datetime import datetime
from dateutil import parser

client_secret = 'client_secret.json'

def construct_google_calendar_client(client_secret):
    """
    Constructs a Google Calendar API client.

    Parameters:
    - client_secret (str): The path to the client secret JSON file.

    Returns:
    - service: The Google Calendar API service instance
    """
    API_NAME = 'calendar'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    service = create_service(client_secret, API_NAME, API_VERSION, SCOPES)
    return service

calendar_service = construct_google_calendar_client(client_secret)

def create_calendar(calendar_name: str):
    """
    Creates a new calendar list.

    Parameters:
    - calendar_name (str): The name of the new calendar list.

    Returns:
    - dict: A dictionary containing the ID of the new calendar list.
    """

    calendar_list = {
        'summary': calendar_name
    }
    created_calendar_list = calendar_service.calendars().insert(body=calendar_list).execute()
    return created_calendar_list

#@function_tool
def list_calendar_list(max_capacity: int =200):
    """
    Lists calendar lists until the total number of items reaches max_capacity.

    Parameters:
    - max_capacity (int): The maximum number of calendar lists to retrieve. Defaults to 200. If a string is provided, it will be converted to an integer.

    Returns:
    - list: A list of dictionaries containing cleaned calendar list infomration with 'id', 'name', and 'description'.
    """
    
    all_calendars = []
    all_calendars_cleaned = []
    next_page_token = None
    capacity_tracker = 0

    while True:
        calendar_list = calendar_service.calendarList().list(
            maxResults=min(200, max_capacity - capacity_tracker),
            pageToken = next_page_token
        ).execute()
        calendars = calendar_list.get('items', [])
        all_calendars.extend(calendars)
        capacity_tracker += len(calendars)
        if capacity_tracker >= max_capacity:
            break
        next_page_token = calendar_list.get('nextPageToken')
        if not next_page_token:
            break
    
    for calendar in all_calendars:
        all_calendars_cleaned.append(
            {
                'id': calendar['id'],
                'name': calendar['summary'],
                'description': calendar.get('description', ''),
            }
        )
    return all_calendars_cleaned

#@function_tool
def list_calendar_events(calendar_id: str, max_capacity: int =20):
    """
    Lists events from a specified calendar until the total number of events reaches max_capacity.

    Parameters:
    - calendar_id (str): The ID of the calendar from which to list events.
    - max_capacity (int or str, optional): The maximum number of events to retrieve. Defaults to 20. If a string is provided, it will be converted to an integer.

    Returns:
    - list: A list of events from the specified calendar.
    """
    # if isinstance(max_capacity, str):
    #     max_capacity = int(max_capacity)
    
    all_events = []
    next_page_token = None
    capacity_tracker = 0
    
    while True:
        events_list = calendar_service.events().list(
            calendarId = calendar_id,
            maxResults = min(20, max_capacity - capacity_tracker),
            pageToken=next_page_token
        ).execute()
        events = events_list.get('items', [])
        all_events.extend(events)
        capacity_tracker += len(events)
        if capacity_tracker >= max_capacity:
            break
        next_page_token = events_list.get('nextPageToken')
        if not next_page_token:
            break
    return all_events

def insert_calendar_event(calendar_id: str, event_details: Dict[str,Any]):
    """
    Inserts an event into the specified calendar.

    Parameters:
    - service: The Google Calendar API service instance.
    - calendar_id: The ID of the calendar where the event will be inserted.
    #####- **kwargs: Additional keyword arguments representing the event details.
    - event_details: Dictionary with additional keyword arguements for the event details
    Returns:
    - The created event.
    """
    #request_body = json.loads(kwargs['kwargs'])
    '''
    event_details = {
        'summary': 'Meeting with Bob',
        'location': '123 Main St, Anytown, USA',
        'description': 'Discuss project updates.'
        'start': {
            'dateTime': '2025-08-13T10:00:00-07:00',
            'timeZone': 'America/California',
        },
        'end': {
            'dateTime': '2025-08-13T11:00:00-07:00',
            'timeZone': 'America/California',
        },
        'attendees': [
            {'email': 'bob@example.com'}
        ]                                        
    }
    '''

    event_details["summary"] = event_details["event_name"]
    print(event_details)
    event = calendar_service.events().insert(
        calendarId=calendar_id,
        body=event_details
    ).execute()
    return event

def get_free_times(email: str, start_time_str: str, end_time_str: str):
    # body = {
    #     "timeMin": start_time.isoformat(),
    #     "timeMax": end_time.isoformat(),
    #     "items": [{"id": email}]
    # }

    body = {
        "timeMin": start_time_str,
        "timeMax": end_time_str,
        "items": [{"id": email}]
    }

    events_result = calendar_service.freebusy().query(body=body).execute()
    busy_times = events_result['calendars'][email]['busy']

    start_time = parser.isoparse(start_time_str)
    end_time = parser.isoparse(end_time_str)

    # Invert busy to get free
    free_times = []
    current = start_time

    for busy in busy_times:
        busy_start = parser.isoparse(busy['start'])
        if current < busy_start:
            free_times.append((current, busy_start))
        current = max(current, parser.isoparse(busy['end']))

    if current < end_time:
        free_times.append((current, end_time))

    return free_times