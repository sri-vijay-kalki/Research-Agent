from pydantic import BaseModel, Field
from typing import List

class ResearchPlan(BaseModel):
    sub_questions: List[str] = Field(..., description="List of sub-questions to research")
    reasoning: str = Field(..., description="Reasoning for the sub-questions")
    

class Evaluation(BaseModel):
    score: int = Field(..., ge=1, le=10, description="Score between 1 and 10")
    feedback: str = Field(..., description="Feedback for improvement")    