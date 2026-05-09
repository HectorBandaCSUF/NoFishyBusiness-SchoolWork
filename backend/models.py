"""
backend/models.py

Pydantic data models shared across the NoFishyBusiness backend.
"""

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------

class KBRecord(BaseModel):
    """A single record retrieved from the knowledge base."""

    id: int
    species_name: str
    category: str
    content: str


# ---------------------------------------------------------------------------
# Volume Calculator
# ---------------------------------------------------------------------------

class VolumeRequest(BaseModel):
    length: float = Field(gt=0, description="Tank length in inches")
    width: float = Field(gt=0, description="Tank width in inches")
    depth: float = Field(gt=0, description="Water depth in inches")


class VolumeResponse(BaseModel):
    volume_gallons: float
    weight_pounds: float


# ---------------------------------------------------------------------------
# Species Tool
# ---------------------------------------------------------------------------

class SpeciesRequest(BaseModel):
    species_name: str = Field(min_length=1)


# ---------------------------------------------------------------------------
# Maintenance Guide
# ---------------------------------------------------------------------------

class MaintenanceRequest(BaseModel):
    tank_gallons: float = Field(gt=0)
    fish_count: int = Field(ge=0)
    fish_species: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Setup Guide
# ---------------------------------------------------------------------------

class SetupRequest(BaseModel):
    tank_gallons: float = Field(gt=0, le=500)
    experience_level: str = Field(pattern="^(beginner|intermediate|advanced)$")


# ---------------------------------------------------------------------------
# Chemistry Analyzer
# ---------------------------------------------------------------------------

class ChemistryRequest(BaseModel):
    description: str
    image_base64: Optional[str] = None


# ---------------------------------------------------------------------------
# AI Assistant
# ---------------------------------------------------------------------------

class AssistantRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[dict] = Field(default_factory=list, max_length=10)


# ---------------------------------------------------------------------------
# Error Response
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    message: str
    error_type: str
