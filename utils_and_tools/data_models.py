from pydantic import BaseModel, Field
from typing import Literal
from utils_and_tools.logger import logger

class RequestType(BaseModel):
     """Router LLM Call: Determine the type of request"""

     request_type: Literal["date", "calendar", "general"] = Field(
          description="The type of request being made. A request to schedule a date is a date request, a request regarding google calendars is a calendar request, and any other request is a general request."
     )
     confidence_score: float = Field(description="Confidence score between 0 and 1")
     description: str = Field(description="Cleaned description of the request")
    
class CalendarRequestType(BaseModel):
     """Calendar Router LLM Call: Determine the type of calendar request"""

     request_type: Literal["list_calendards", "list_events", "create_calendar", "create_event"] = Field(
          description= "The type of calendar request being made"
     )
     confidence_score: float = Field(description="Confidence score between 0 and 1")
     description: str = Field(description="Cleaned up description of the request")

def generate_data_model(values: list[str], given_description: str):
    ret_values = Literal[*values]
    logger.debug(f"Values given: {ret_values}")
    class GeneratedModel(BaseModel):
        return_values: ret_values = Field(
        description= given_description
    )
        confidence_score: float = Field(description="Confidence score between 0 and 1")
        description: str = Field(description="Cleaned up description of the request")
    return GeneratedModel