from typing import List, Optional
from pydantic import BaseModel, Field

class LandmarkPoint(BaseModel):
    x: float = Field(..., description="Normalized X coordinate [0.0, 1.0]")
    y: float = Field(..., description="Normalized Y coordinate [0.0, 1.0]")
    z: float = Field(..., description="Landmark depth relative to wrist landmark")
    visibility: Optional[float] = Field(1.0, description="Landmark visibility confidence [0.0, 1.0]")

class BoundingBox(BaseModel):
    xmin: int
    ymin: int
    width: int
    height: int

class HandDetectionResult(BaseModel):
    handedness: str = Field(..., description="'Right' or 'Left'")
    score: float = Field(..., description="Hand detection confidence score [0.0, 1.0]")
    landmarks: List[LandmarkPoint] = Field(..., description="21 3D hand keypoints")
    world_landmarks: Optional[List[LandmarkPoint]] = Field(None, description="21 3D world coordinates in meters")
    bbox: BoundingBox = Field(..., description="Pixel bounding box surrounding hand")
    visibility_valid: bool = Field(True, description="True if all 21 keypoints satisfy visibility threshold")
