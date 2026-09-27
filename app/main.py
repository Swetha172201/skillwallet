from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fpdf import FPDF
import os, re, copy, json
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
load_dotenv()

app = FastAPI()

class UserRequest(BaseModel):
    prompt: str

BASE_DATA = {
  "total_budget": 100000,
  "remaining_budget": 500,
  "rooms": [
    {"room_name": "Living Room", "allocation": 30000, "items": [
      {"item": "Wakefit 3 Seater Sofa", "desc": "Grey fabric sofa", "price": 14500, "qty": 1},
      {"item": "TV Stand", "desc": "Engineered wood unit", "price": 4500, "qty": 1},
      {"item": "Coffee Table", "desc": "Minimalist white table", "price": 1900, "qty": 1},
      {"item": "Curtains", "desc": "Set of 2 blackout", "price": 1200, "qty": 2},
    ]},
    {"room_name": "Master Bedroom", "allocation": 35000, "items": [
      {"item": "Queen Bed", "desc": "Engineered wood bed", "price": 11000, "qty": 1},
      {"item": "Mattress", "desc": "Orthopedic Foam", "price": 8000, "qty": 1},
    ]},
    {"room_name": "Second Bedroom", "allocation": 25000, "items": [
      {"item": "Single Bed", "desc": "Solid wood bed", "price": 7500, "qty": 1},
      {"item": "Study Desk", "desc": "Compact desk", "price": 6000, "qty": 1},
    ]}
  ]
}

LAST_DATA = copy.deepcopy(BASE_DATA)

def make_budget(prompt, base):
    new = copy.deepcopy(base)
    m = re.search(r'(\d{3,6})', prompt.replace(',', ''))
    if m:
        b = int(m.group(1))
        if b < 1000:
            b = b * 1000
        if b < 4000:
            return base
        new["total_budget"] = b
        new["remaining_budget"] = 500
        factor = b / 100000
        for r in new["rooms"]:
            r["allocation"] = int(r["allocation"] * factor)
            for it in r["items"]:
                it["price"] = int(it["price"] * factor)
        return new
    return base

@app.post("/generate")
async def generate_plan(req: UserRequest):
    global LAST_DATA
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"PROMPT: {req.prompt}")
    if not api_key:
        LAST_DATA = make_budget(req.prompt, BASE_DATA)
        return LAST_DATA
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        txt_prompt = "User wants: " + req.prompt + ". Return ONLY JSON with total_budget from prompt."
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=txt_prompt)
        txt = resp.text.replace("```json","").replace("```","").strip()
        parsed = json.loads(txt)
        LAST_DATA = parsed
        return parsed
    except Exception as e:
        print(f"Model error {e}")
        LAST_DATA = make_budget(req.prompt, BASE_DATA)
        return LAST_DATA

@app.get("/download-pdf")
def download_pdf():
    d = LAST_DATA
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_fill_color(13,139,242)
    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial","B",11)
    pdf.cell(0,10,f'  Budget Summary - Total Rs.{d["total_budget"]} | Remaining Rs.{d["remaining_budget"]}', fill=True, ln=True)
    pdf.ln(3)
    pdf.set_text_color(0,0,0)
    for r in d["rooms"]:
        pdf.set_font("Arial","B",10)
        pdf.set_text_color(13,91,150)
        pdf.cell(0,7,f'{r["room_name"]} - Rs.{r["allocation"]}', ln=True)
        pdf.set_font("Arial","B",7)
        pdf.set_text_color(0,0,0)
        pdf.cell(45,5,"Item",1);pdf.cell(60,5,"Description",1);pdf.cell(18,5,"Price",1);pdf.cell(12,5,"Qty",1);pdf.cell(55,5,"Links",1,ln=True)
        pdf.set_font("Arial","",7)
        for it in r["items"]:
            pdf.cell(45,5,it["item"][:28],1);pdf.cell(60,5,it["desc"][:38],1);pdf.cell(18,5,f'Rs.{it["price"]}',1);pdf.cell(12,5,str(it["qty"]),1);pdf.cell(55,5,"Amazon Flipkart",1,ln=True)
        pdf.ln(3)
    pdf.output("PocketSmart.pdf")
    return FileResponse("PocketSmart.pdf", filename="PocketSmart.pdf", media_type='application/pdf')