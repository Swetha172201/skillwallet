# app/models.py - PocketSmart AI Models
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

# ===== USER =====
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ===== HOME BUDGET =====
class HomeBudgetRequest(BaseModel):
    total_budget: int
    needs: str
    family_size: Optional[int] = 4

class HomeItem(BaseModel):
    name: str
    price: float
    store: str = "Local"
    link: str = ""

# ===== PARTY BUDGET =====
class PartyBudgetRequest(BaseModel):
    total_budget: int
    party_type: str
    guest_count: int

# ===== JEWELRY - MUKKIYAM DA! =====
class JewelryBudgetRequest(BaseModel):
    total_budget: int
    occasion: str
    style_preferences: Optional[str] = "casual"
    has_image: bool = False

class JewelryItem(BaseModel):
    type: str
    price: float
    description: str
    shopping_links: List[str] = []

# ===== HOME INTERIOR - NEW =====
class InteriorBudgetRequest(BaseModel):
    total_budget: int
    room_type: str
    room_size: str
    style: str
    requirements: str
    has_image: bool = False

# ===== COMMON RESPONSE =====
class BudgetSummary(BaseModel):
    total: float
    spent: float = 0
    remaining: float

# ===== HELPER - JSON CLEAN =====
def clean_json_string(text: str):
    """Gemini ```json ellam remove pannum da"""
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except:
        return {"raw_text": text, "budget_summary": {"total": 5000, "remaining": 1000}, "items": [{"name": "Sample Item", "price": 500}]}