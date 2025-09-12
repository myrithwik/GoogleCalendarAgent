#from swarm import Agent
#from agents import Agent
#from prompts import calendar_agent_system_prompt, main_agent_system_prompt
#from calendar_tools import list_calendar_list, list_calendar_events, insert_calendar_event, create_calendar
from api_keys.openai_api import client
from utils_and_tools.data_models import RequestType, CalendarRequestType, generate_data_model
from utils_and_tools.calendar_tools import list_calendar_list, list_calendar_events, create_calendar, insert_calendar_event
from utils_and_tools.logger import logger
import json

MODEL = "gpt-5-nano"

# def transfer_to_main_agent():
#     return main_agent

# def transfer_to_calendar_agent():
#     return calendar_agent

# calendar_agent = Agent(
#     name="Google Calendar Agent",
#     model=MODEL,
#     instructions=calendar_agent_system_prompt,
#     tools=[list_calendar_list, list_calendar_events, insert_calendar_event, create_calendar]
# )
# #calendar_agent.functions.extend([list_calendar_list, list_calendar_events, insert_calendar_event, create_calendar])


# main_agent = Agent(
#     name="Main Agent",
#     model=MODEL,
#     instructions=main_agent_system_prompt,
#     handoffs=[calendar_agent]
# )

def extract_request_type(messages, prompt):
    """Router LLM call to determine the type of request"""
    system_prompt = """
        Determine what type of request the most recent request is. Choose from the following options:
            - Date Scheduler Request: Any request to schedule a date. This is different from a regular event, but is a romantic date.
            - Calendar Request: Any request regarding listing, creating, scheduling, modifying, or removing calendar events.
            - General Request: All other general requests.
    """
    classify_message = messages[:-1].copy()
    classify_message.extend([
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]
    )

    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=classify_message,
        response_format=RequestType,
    )
    result = completion.choices[0].message.parsed

    return result

def general_agent(messages, prompt):
    
    general_messages = messages[:-1].copy()
    general_messages.extend(
        [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {"role": "user", "content": prompt},
        ]
    )

    print(general_messages)

    completion = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    result = completion.choices[0].message.content

    response = {'role':'assistant', 'content':result}
    return response    

def calendar_agent(messages, prompt):
    calendar_request_type = extract_calendar_request_type(messages, prompt)
    if calendar_request_type.request_type == "list_calendards":
        result = list_calendar_list(max_capacity=200)
    elif calendar_request_type.request_type == "list_events":
        calendar_id = extract_calendar_id(messages, prompt)
        result = list_calendar_events(calendar_id, max_capacity=20)
    elif calendar_request_type.request_type == "create_calendar":
        calendar_name = extract_calendar_name(messages, prompt)
        if calendar_name == "NAME ALREADY EXISTS":
            result = "Could not create a new calendar with that name because a calendar already exists with that name."
        else:
            result = create_calendar(calendar_name)
            result["action"] = f"Successfuly created a new calendar with the name {calendar_name} as per user request."
    elif calendar_request_type.request_type == "create_event":
        calendar_id = extract_calendar_id(messages, prompt)
        event_details = extract_event_details(messages,prompt)
        result = insert_calendar_event(calendar_id, event_details)
    formatting_prompt = f"""
    Given the message history us the following raw data to provide a helpful answer to the user query.
    
    Data:
    {json.dumps(result, indent=2)}
    """

    history = messages[:-1].copy()
    history.extend(
        [
            {"role": "system","content": formatting_prompt},
            {"role": "user", "content": prompt},
        ]
    )
    completion = client.chat.completions.create(
        model=MODEL,
        messages=history,
    )
    result = completion.choices[0].message.content
    response = {'role':'assistant', 'content':result}
    return response

def extract_calendar_request_type(messages, prompt):
    """Router LLM call to determine the type of calendar request"""
    system_prompt = """
        Determine what type of calendar request the most recent request is. Choose from the following options:
            - List Calendar: A request to list users calendars
            - List Events: A request to list calendar events
            - Create Event: A request to create a new calendar event
    """
    history = messages[:-1].copy()
    history.extend(
        [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]
    )

    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=CalendarRequestType,
    )
    result = completion.choices[0].message.parsed
    
    logger.info(
        f"Calendar request routed as: {result.request_type} with confidence: {result.confidence_score}"
    )

    return result

## Implementation 1
def extract_calendar_id(messages, prompt):
    logger.debug("Extracting the Calendar ID")
    """LLM call to extract the calendar id"""
    system_prompt = """
        Given the history of the chat and the user request, determine the name of the calendar that is being requested. If none is provided use "primary".
    """
    classify_message = messages[:-1].copy()
    classify_message.extend([
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]
    )

    #Find all calendar ID's
    calendars = list_calendar_list(max_capacity=200)
    names = set()
    ids = set()
    values = []
    name_to_id = {}
    for calendar in calendars:
        names.add(calendar["name"])
        ids.add(calendar["id"])
        values.append(calendar["name"])
        values.append(calendar["id"])
        name_to_id[calendar["name"]] = calendar["id"]
    calendar_id_model = generate_data_model(values, "The name or id of the Calendar that is being requested")
    
    logger.debug(f"Extracting Name from {values}")

    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=classify_message,
        response_format=calendar_id_model,
    )
    result = completion.choices[0].message.parsed

    logger.info(
        f"Extracted calendar as: {result.return_values} with confidence: {result.confidence_score}"
    )
    result_id = "primary"
    if result.return_values in ids:
        result_id = result.return_values
    elif result.return_values in names:
        result_id = name_to_id[result.return_values]
    else:
        logger.warning("Requested calendar not found, using primary instead.")
    logger.debug(f"Using {result_id} as calendar ID")
    return result_id

def extract_calendar_name(messages, prompt):
    logger.debug("Extracting the New Calendar Name")
    """LLM call to extract the name of a new calendar to be created"""
    system_prompt = """
        Given the history of the chat and the user request, determine the name of the calendar that is requested to be created. Return only the requested calendar name and nothing else.
    """
    classify_message = messages[:-1].copy()
    classify_message.extend([
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]
    )

    calendars = list_calendar_list(max_capacity=200)
    names = set()
    for calendar in calendars:
        names.add(calendar["name"])
    
    completion = client.chat.completions.create(
        model=MODEL,
        messages=classify_message,
    )
    result = completion.choices[0].message.content

    logger.info(
        f"Extracted calendar name as: {result}"
    )
    if result in names:
        logger.warning("Provided new calendar name already exists")
        return "NAME ALREADY EXISTS"
    else:
        return result

def extract_event_details(messages,prompt):
    system_prompt = """
    Given the chat history in the most recent user request, extract the following event details from the user's message. 
    Return only a JSON object with these keys: 
    event_name, location, description, start (which has nested keys dateTime and timeZone), end (which has nested keys dateTime and timeZone), attendees (a list of pairs with key email). 
    If a field is not present in the input, set it to null. 
    Use ISO 8601 format for time fields (e.g. '2025-08-25T15:00:00'). 
    Return only the JSON object, with no extra text.

    Follow this example:
     event_details = {
        'event_name': 'Meeting with Bob',
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
    """

    extract_message = messages[:-1].copy()
    extract_message.extend([
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=extract_message,
    )

    event_details = json.loads(response.choices[0].message.content)
    logger.info(f"Event Details Extracts: {event_details}")

    return event_details