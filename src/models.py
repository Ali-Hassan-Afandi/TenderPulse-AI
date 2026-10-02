from pydantic import BaseModel, Field
from typing import List

class CompanyProfile(BaseModel):
    company_name: str
    email: str
    pec_license: str = ""
    pec_category: str = ""
    pec_codes: List[str] = Field(default_factory=list)
    ntn: str = ""
    province: str = ""
    city: str = ""
    years_experience: int = 0
    annual_turnover_m: float = 0
    employees: int = 0
    completed_projects: int = 0
    largest_project_m: float = 0
    sectors: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

class Tender(BaseModel):
    id: str
    title: str
    agency: str
    province: str
    category: str
    deadline: str
    security_m: float = 0
    min_category: str = ""
    required_codes: List[str] = Field(default_factory=list)
    min_turnover_m: float = 0
    min_experience: int = 0
    estimated_value_m: float = 0
    source: str = "SIMULATION"
