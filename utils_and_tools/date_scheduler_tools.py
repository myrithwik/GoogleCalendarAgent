from api_keys.openai_api import client
from utils_and_tools.logger import logger
from utils_and_tools.calendar_tools import get_free_times, insert_calendar_event
import ast
import json

MODEL = "gpt-5-nano"

def find_overlaps(free_times_1, free_times_2):
    overlaps = []
    i, j = 0, 0
    
    while i < len(free_times_1) and j < len(free_times_2):
        start1, end1 = free_times_1[i]
        start2, end2 = free_times_2[j]

        # Find the overlap between the two intervals
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        if overlap_start < overlap_end:  # valid overlap
            overlaps.append([overlap_start, overlap_end])

        # Move forward in whichever interval ends first
        if end1 < end2:
            i += 1
        else:
            j += 1

    return overlaps

def extract_free_time(person1: str, person2:str, start_time: str, end_time: str) -> list:
    logger.debug("Called the extract_free_time tool")

    free_times_1 = get_free_times(email="my.rithwik@gmail.com", start_time_str=start_time, end_time_str=end_time)
    free_times_2 = get_free_times(email="rakshasen953@gmail.com", start_time_str=start_time, end_time_str=end_time)

    overlap_free_time = find_overlaps(free_times_1, free_times_2)

    formatted_overlap_free_time = [
    [start.isoformat(), end.isoformat()] for start, end in overlap_free_time
    ]

    logger.debug(f"Found the overlapped freetimes: {overlap_free_time}")
    logger.debug(f"Formatted the overlapped free times: {formatted_overlap_free_time}")

    llm_response = select_date_time(formatted_overlap_free_time)

    return llm_response

def select_date_time(overlap__free_time: list):
    logger.debug("Calling independant LLM for optimal date time selection")

    str_overlapped_free_time = str(overlap__free_time)

    system_prompt = """
    You are a helpful assistant that determines an optimal hour time window for a virtual date. 
    The user will provide a string which represents a list of free times. The freetimes have a start time and an end time.
    Your job is to return a 1 hour time frame best suited for a virtual date in the format of '[start_time, end_time]' with both start_time and end_time being formatted as the example: '2025-08-13T10:00:00-07:00'
    Here are the critertia you should follow:
        - Best times for the virtual date if available are in the window: 6:30pm-8:30pm PST. 
        - If that is not available find the best suited time frame that would work for the Boy being in a PST timezone and the Girl being in the EST timezone
    
    Return the '[start_time, end_time]' time window and nothing else.
"""

    user_prompt = f"""
    Find a 1 hour slot for a virtual date given that the free times are as follows:
    {str_overlapped_free_time}
"""

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system","content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    result = completion.choices[0].message.content

    logger.debug(f"Independant LLM picked: {result}")

    return result

def generate_date_idea(date_type: str) -> str:
    logger.debug("Calling independant LLM to generate a date idea")

    system_prompt = """
    You are a helpful assistant that will generate an idea for a virtual date. 
    The user will provide a string which represents the type of virtual date they would like you to generate an idea for.
    Some example virtual date types could be watching a tv show, playing online games, online shopping, fall vibe virtual date, etc.
    Your job is to take the date type is a basis and generate a virtual date idea based on it. 
    Be creative and generate ideas that can be done over video call or phone.
    
    Return a title for the date idea and then a description for it 
"""

    user_prompt = f"""
    Generate a virtuate date idea following the date type {date_type}
"""

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system","content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    result = completion.choices[0].message.content

    logger.debug(f"LLM generated date idea: {result}")

    return result

def create_date_event(start_time: str, end_time: str, date_idea_title: str, date_idea_description: str) -> str:
    logger.debug("Entering event creating tool")
    # times_split = scheduled_time.split(",")
    # start_time = times_split[0].replace("[","").replace("'","")
    # end_time = times_split[1].replace("]","").replace("'","")

    #time_list = ast.literal_eval(scheduled_time)
    print(start_time)
    print(end_time)
    # time_list = json.loads(scheduled_time)
    # start_str = time_list[0]
    # end_str = time_list[1]

    event_details = {
        'event_name': date_idea_title,
        'summary': date_idea_title,
        'location': 'Virtual',
        'description': date_idea_description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        },
        'attendees': [
            {'email': 'my.rithwik@berkeley.edu'}
        ]                                        
    }

    try:
        logger.debug("Trying to create event")
        insert_calendar_event(calendar_id="primary", event_details=event_details)
    except Exception as e:
        logger.error(f"Could not make event with error {e}")
        return f"Could not create event due to ERROR: {e}"
    logger.debug("Created Calendar Event")
    return "Successfully Created Date Calendar Event!"