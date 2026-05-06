from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class ScanStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SEOScore(BaseModel):
    score: int = Field(ge=0, le=100)
    title_tag: Dict = {}
    meta_description: Dict = {}
    headings: Dict = {}
    images: Dict = {}
    links: Dict = {}
    mobile_friendly: bool = False
    load_time: float = 0.0
    ssl_certificate: Dict = {}
    
class SecurityScore(BaseModel):
    score: int = Field(ge=0, le=100)
    ssl_valid: bool = False
    http_headers: Dict = {}
    cookies: Dict = {}
    open_ports: List[int] = []
    vulnerabilities: List[str] = []
    
class ScanRequest(BaseModel):
    url: HttpUrl
    scan_type: str = "full"  # full, seo, security
    
class ScanResponse(BaseModel):
    id: str
    url: str
    status: ScanStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    seo_score: Optional[SEOScore] = None
    security_score: Optional[SecurityScore] = None
    ai_summary: Optional[str] = None
    ai_suggestions: Optional[List[str]] = None
    error: Optional[str] = None