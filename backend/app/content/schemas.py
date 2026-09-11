from typing import List, Optional
from pydantic import BaseModel, Field

class LessonContent(BaseModel):
    sign: str = Field(..., description="Target sign character (e.g., 'A')")
    description: str = Field(..., description="Hand posture description")
    meaning: str = Field(..., description="Sign language meaning or alphabet character designation")
    reference_image: Optional[str] = Field(None, description="URL or relative path to reference image")
    optional_video: Optional[str] = Field(None, description="URL to video demonstration")
    difficulty: str = Field("Easy", description="'Easy', 'Intermediate', or 'Advanced'")
    instructions: List[str] = Field(..., description="Step-by-step physical hand formation instructions")
    common_mistakes: List[str] = Field(..., description="Frequent anatomical errors and confusion points")
    example_usage: str = Field(..., description="Example word or context usage")
    course_module_relation: str = Field(..., description="Associated curriculum course or module name")
