from api_keys.openai_api import client
from utils_and_tools.logger import logger
import json
from utils_and_tools.date_scheduler_tools import extract_free_time, generate_date_idea, create_date_event

MODEL = "gpt-5-nano"

coordinating_date_agent_prompt = """
Folow the steps provided in this content strictly. Do not respond on your own, only follow the steps listed here.
You are a helpful assistant that will schedule a romantic virtual date for Boy and Girl by strictly following the following steps. 
You will take specific steps to find an optinmal time for the date in the overlapping free time for the Boy and Girl, then you will generate a virtual date idea, then create a date calendar event, and then report back the details of the event.
You are equiped with the following tools:
1. extract_free_time(person1: str, person2: str, start_time: str, end_time: str)
    - This tool will allow you to extract the overlapping free time for two people over a specific time frame from start_time to end_time
    - The person1 and person2 argument is a string either "Boy" or "Girl"
    - start_time and end_time are the start and end times of the possible times the date can be scheduled. Provide the start_time and end_time arguments as a string formatted in the dateTime format as the example: '2025-08-13T10:00:00-07:00'
    - The tool will determine the overlapping free times in the two people's calendar and will select a 1 hour optimal time slot for the virtual date.
    - The tool will return a list of 2 items with the start_time and end_time of the 1 hour virtual date slot
2. generate_date_idea(date_type: str)
    - This tool will allow you to generate a date idea based on the date type the user provided in the request
    - Some example virtual date types could be watching a tv show, playing online games, online shopping, fall vibe virtual date, etc.
    - If no date type is provided in the user request then classify the date type as "general virtual date"
    - The tool will return a title for the date idea generated and a description for it in one string
3. create_date_event(start_time: str, end_time: str, date_idea_title: str, date_idea_description: str)
    - This tool will allow you to create a Google Calendar event for the virtual date
    - The start_time argument will be the string with the start time of the virtual date and end_time argument will be the string with the end time of the virtual date returned by the extract_free_time tool
    - The generate_date_idea tool will return a string that first provides the virtual date idea title and then followed by the date idea description. Extract the date idea title to use as the date_idea_title argument and extract the date idea description to use as the date_idea_description argument.
    - The tool will return a message whether creating the Google Calendar was successful or not.

To do your job follow these steps in order. Take all 5 steps in order and do not return before all steps are completed:

1. When a request comes in extract what time frame the date should be scheduled:
    - If the user requests a specific day set the start time to 9am pacific time that day and end time to 10pm pacific time that day
    - If the user specifies a specific week range set the start time to 9am pacific time on the first day of that week and the end time to 10pm pacific on the last day of that week
    - If the user requests this week set the start time to the current time and the end time to 10pm pacific time on the last day of this week
    - If the user requesrs today set the start time to the current time and the end time to 10pm pacific time today
    - If no specific time request is made, make the start time the current time and the end time 10pm pacifitc time a week from today

    Remember to set the start time and end time strings in the dateTime format as the example: '2025-08-13T10:00:00-07:00'

2. Call the extract_free_time tool to find the overlapping free time for Boy and Girl:
    - Call the extract_free_time tool to find the overlapping free time for Boy and Girl.
    - Use "Boy" as person1 and "Girl" as person2 and the start time and end time extracted in the first step as start_time and end_time
    - The tool returns the one hour slot for a date. It is formatted as a list with the start time and end time
    
3. Call the generate_date_idea tool to generate a virtual date idea:
    - Check if the user has requested a specific type of date type and store this as the date_type
    - Some example virtual date types could be watching a tv show, playing online games, online shopping, fall vibe virtual date, etc.
    - If no date type is provided in the user request then classify the date type as "general virtual date"
    - Call the generate_date_idea tool and use the date_type you extracted above as the input string argument date_type to the tool
    - The tool returns a string with a virtual date iidea title, followed by a description of the virtual date idea
    
4. Call the create_date_event tool to create a Google Calendar event with the time and date idea determined above
    - Take the date idea returned by the generate_date_idea tool and split it into two fields, date idea title and date idea description
    - Separate the scheduled time from extract_free_time tool to separate it into the start_time and the end_time each in the format following the example: '2025-08-13T11:00:00-07:00'
    - Call the create_date_event tool to create a Google Calendar event for the virtual date
    - Use the scheduled time returned from the extract_free_time tool and split it into the start_time and the end_time each in the format following the example: '2025-08-13T11:00:00-07:00' for the arguments start_time and end_time the date idea title as date_idea_title, and the date idea description as date_idea_description
    - The tool returns a string suggesting if creating the event was successful or not.
    
5. Return the date time window (returned from the extract_free_time tool), the generated date idea (returned from the generate_date_idea tool), and whether a Google Event was created (returned from the create_date_event tool) to the user in the format: "Start Time: {start_time}, End Time: {end_time}, Date Idea: {date_idea}, Google Calendar Event: "Success"/"Fail""

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
    },
    {
        "type": "function",
        "function": {
            "name": "generate_date_idea",
            "description": "Generate a virtual date idea",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_type": {
                        "type": "string",
                        "description": "The type of virtual date to generate an idea for",
                    }
                },
                "required": ["date_type"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_date_event",
            "description": "Create a Google Calendar event for the virtual date",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "The start time of the window of time for the virtual date to be scheduled",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "The end time of the window of time for the virtual date to be scheduled",
                    },
                    "date_idea_title": {
                        "type": "string",
                        "description": "Title of the generated virtual ate idea",
                    },
                    "date_idea_description": {
                        "type": "string",
                        "description": "Description of the generated virtual date idea",
                    },
                },
                "required": ["start_time", "end_time", "date_idea_title", "date_idea_description"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    }
]

def call_function(name, args):
    if name == "extract_free_time":
        return extract_free_time(**args)
    elif name == "generate_date_idea":
        return generate_date_idea(**args)
    elif name == "create_date_event":
        return create_date_event(**args)

def handle_tools(msg, messages):
    for tool_call in msg.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

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

    while True:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=general_messages,
            tools=tools
        )

        logger.debug(completion.model_dump())
        msg = completion.choices[0].message
        general_messages.append(msg)
        
        if msg.tool_calls:
            handle_tools(msg, general_messages)
        else:
            result = msg.content
            response = {'role':'assistant', 'content':result}
            return response      