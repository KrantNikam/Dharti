from fastapi import Request, APIRouter, File, UploadFile, Form
from pydantic import BaseModel, Field
from typing import Optional
from src.handler.intent_detector import kisan_agent_router
from src.handler.optimize_farming_agent import ask_gemini_farming_planner
import tempfile

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    responses={500: {"description": "Something went wrong"}}
)

class AgentRequest(BaseModel):
    query: str = Field("", description="User query to determine the intent")
    crop_type: Optional[str] = Field("", description="Type of crop for agronomist agent")
    crop_age: Optional[str] = Field("", description="Age of the crop for agronomist agent")
    language: Optional[str] = Field("en", description="Language for the response, default is English")

class FarmingPlannerRequest(BaseModel):
    crop_name: str = Field(..., description="Name of crop for optimized farming")
    farmland_length: str = Field(..., description="Farmland length")
    farmland_width: str = Field(..., description="Farmland width")
    spacing_distance: str = Field(..., description="Spacing distance")
    irrigation_type: str = Field(..., description="Type of irrigation system")
    soil_condition: str = Field(..., description="Condition of the soil")
    weather_condition: str = Field(..., description="Current weather condition")

@router.post("/optimize-farming")
def optimizedfarming_planner(request: Request, 
                            payload: FarmingPlannerRequest):
    payload = payload.model_dump()
    response = ask_gemini_farming_planner(payload)
    return response

@router.post("/")
async def get_agents(
    request: Request,
    query: str = Form(None),
    crop_type: Optional[str] = Form(None),
    crop_age: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    language: Optional[str] = Form("en")
):
    """
    Route to handle different agents based on user query.

    Accepts optional file upload and other form fields.
    """
    image_bytes = None
    if file is not None:
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp.flush()
            tmp.seek(0)
            image_bytes = tmp.read()

    if not query:
        return {"message": "Please provide a query to route to the appropriate agent."}

    response = kisan_agent_router(
        query, crop_type, crop_age, image_bytes, language
    )
    return response
