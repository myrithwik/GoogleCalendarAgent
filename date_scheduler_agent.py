from openai_api import client
from logger import logger
import json
from date_scheduler_tools import extract_free_time

MODEL = "gpt-5-nano"

coordinating_date_agent_prompt = """
Folow the steps provided in this content strictly. Do not respond on your own, only follow the steps listed here.
You are a helpful assistant that will schedule a romantic date for Boy and Girl by strictly following the following steps. 
You will take specific steps to find the overlapping free time for the Boy and Girl, then given the criteria you will finf an optimal hour to schedule a date time, generate a date idea, create a date calendar event, and then report back the details of the event.
You are equiped with the following tools:
1. extract_free_time(person1: str, person2: str, start_time: str, end_time: str)
    - This tool will allow you to extract the overlapping free time for two people over a specific time frame from start_time to end_time
    - The person1 and person2 argument is a string either "Boy" or "Girl"
    - start_time and end_time are the start and end times of the possible times the date can be scheduled. Provide the start_time and end_time arguments as a string formatted in the dateTime format as the example: '2025-08-13T10:00:00-07:00'
    - The tool will return a list of 2 item lists with the overlapping free times in the two people's calendar

To do your job follow these steps in order:

1. When a request comes in extract what time frame the date should be scheduled:
    - If the user requests a specific day set the start time to 9am pacific time that day and end time to 10pm pacific time that day
    - If the user specifies a specific week range set the start time to 9am pacific time on the first day of that week and the end time to 10pm pacific on the last day of that week
    - If the user requests this week set the start time to the current time and the end time to 10pm pacific time on the last day of this week
    - If the user requesrs today set the start time to the current time and the end time to 10pm pacific time today
    - If no specific time request is made, make the start time the current time and the end time 10pm pacifitc time a week from today

    Remember to set the start time and end time strings in the dateTime format as the example: '2025-08-13T10:00:00-07:00'
    
2. After finding the start and end time extract the date type to be scheduled:
    - Check if the user has requested a specific type of date type and store this as the date_type
3. Find the overlapping free time for Boy and Girl:
    - Call the extract_free_time tool to find the overlapping free time for Boy and Girl.
    - Use "Boy" as person1 and "Girl" as person2 and the start time and end time extracted in the first step as start_time and end_time
    - The tool returns a list of 2 item lists representing the overlapping free time between Boy and Girl
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_free_time",
            "description": "Get the overlapping free time for the given person1 and person2 in the interval from start_time to end_time",
            "parameters": {
                "type": "object",
                "properties": {
                    "person1": {
                        "type": "string",
                        "description": "The first person who's free time is being extracted",
                    },
                    "person2": {
                        "type": "string",
                        "description": "The second person who's free time is being extracted",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "The start time of the time interval the tool is interested in formatted in a dateTime format as the example: '2025-08-13T10:00:00-07:00'",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "The end time of the time interval the tool is interested in formatted in a dateTime format as the example: '2025-08-13T10:00:00-07:00'",
                    }
                },
                "required": ["person1", "person2", "start_time", "end_time"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    }
]

def call_function(name, args):
    if name == "extract_free_time":
        return extract_free_time(**args)

def handle_tools(completion, messages):
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        messages.append(completion.choices[0].message)

        result = call_function(name, args)
        logger.debug(result)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )

def coordinating_date_agent(messages, prompt):
    
    #general_messages = messages[:-1].copy()
    #general_messages.extend(
    
    general_messages =    [
            {
                "role": "system",
                "content": coordinating_date_agent_prompt,
            },
            {"role": "user", "content": prompt},
        ]

    print(general_messages)

    completion = client.chat.completions.create(
        model=MODEL,
        messages=general_messages,
        tools=tools
    )

    logger.debug(completion.model_dump())
    handle_tools(completion, messages)
    #result = completion.choices[0].message.content



    response = {'role':'assistant', 'content':"Ran something"}
    return response   