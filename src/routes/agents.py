from fastapi import Request, APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional
from handler.intent_detector import kisan_agent_router

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    responses={500: {"description": "Something went wrong"}}
)

class AgentRequest(BaseModel):
    query: str = Field("", description="User query to determine the intent")
    crop_type: Optional[str] = Field("", description="Type of crop for agronomist agent")
    crop_age: Optional[str] = Field("", description="Age of the crop for agronomist agent")
    image_path: Optional[str] = Field("", description="Path to an image for agronomist agent")
    language: Optional[str] = Field("en", description="Language for the response, default is English")

@router.post("/")
def get_agents(request: Request, payload: AgentRequest):
    """
    Route to handle different agents based on user query.
    
    Parameters:
    - query: The user query to determine the intent.
    - crop_type: Optional, type of crop for agronomist agent.
    - crop_age: Optional, age of the crop for agronomist agent.
    - image_path: Optional, path to an image for agronomist agent.
    """
    payload = payload.model_dump()
    query = payload.get("query")
    crop_type = payload.get("crop_type", None)
    crop_age = payload.get("crop_age", None)
    image_path = payload.get("image_path", None)
    language = payload.get("language", "en")

    if not query:
        return {"message": "Please provide a query to route to the appropriate agent."}

    response = kisan_agent_router(query, crop_type, crop_age, image_path, language)
    return response