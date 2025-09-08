from openai_api import client
from logger import logger
from calendar_tools import get_free_times

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
    free_times_1 = get_free_times(email="my.rithwik@gmail.com", start_time_str=start_time, end_time_str=end_time)
    free_times_2 = get_free_times(email="rakshasen953@gmail.com", start_time_str=start_time, end_time_str=end_time)

    overlap_free_time = find_overlaps(free_times_1, free_times_2)

    formatted_overlap_free_time = [
    [start.isoformat(), end.isoformat()] for start, end in overlap_free_time
    ]

    return formatted_overlap_free_time

def select_date_time(overlap__free_time: list):
    

# def generate_date_idea(date_type: str) -> str:

# def create_date_event(scheduled_time: str, date_idea: str) -> str: