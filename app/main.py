from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
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

def get_html(d):
    total = d["total_budget"]
    remain = d["remaining_budget"]
    h = ""
    h += f'<div style="background:white;padding:20px;border-radius:12px;"><div style="background:#0d8bf2;color:white;padding:15px;border-radius:8px;display:flex;justify-content:space-between"><div><b>Budget Summary</b><br>Total Budget: Rs.{total}</div><div>Remaining: Rs.{remain}</div></div>'
    for r in d["rooms"]:
        alloc = r["allocation"]
        rname = r["room_name"]
        h += f'<div style="margin-top:20px"><b style="color:#0d5bb5">{rname}</b> <small style="background:#e8f4ff;padding:3px 8px;border-radius:8px">Allocation: Rs.{alloc}</small>'
        h += '<table style="width:100%;border-collapse:collapse;margin-top:8px"><tr style="font-size:12px;color:#666;border-bottom:2px solid #eee"><th style="text-align:left;padding:8px">Item</th><th style="text-align:left">Description</th><th>Price</th><th>Qty</th><th>Links</th></tr>'
        for it in r["items"]:
            iname = it["item"]
            idesc = it["desc"]
            iprice = it["price"]
            iqty = it["qty"]
            q = iname.replace(" ", "+")
            h += f'<tr style="border-bottom:1px solid #eee;font-size:13px"><td style="padding:8px"><b>{iname}</b></td><td>{idesc}</td><td>Rs.{iprice}</td><td align="center">{iqty}</td><td style="font-size:11px;"><a href="https://www.amazon.in/s?k={q}" target="_blank">Amazon</a> <a href="https://www.flipkart.com/search?q={q}" target="_blank">Flipkart</a></td></tr>'
        h += '</table></div>'
    h += '</div><br><center><a href="/download-pdf"><button style="padding:12px 25px;background:orange;border:none;border-radius:8px;font-weight:bold">Download PDF</button></a></center>'
    return h

PAGE_START = """<html><body style="font-family:Arial;background:#f6f8fc;padding:20px">
<center><h1 style="color:#0d3b66">Your Personalized Budget Plan</h1>
<div style="background:white;padding:15px;border-radius:30px;width:95%;max-width:800px;display:flex;gap:10px;box-shadow:0 2px 10px #0001">
<input id="promptInput" style="flex:1;border:none;outline:none;font-size:14px" value="Create full 2BHK home interior budget plan for 5000 rupees">
<button onclick="generate()" id="genBtn" style="background:#0d8bf2;color:white;border:none;border-radius:20px;padding:12px 25px;cursor:pointer;font-weight:bold">Generate</button>
</div><p id="status" style="color:#666;margin-top:10px"></p></center><br><div id="resultArea">"""

PAGE_END = """</div>
<script>
async function generate(){
    let prompt = document.getElementById('promptInput').value;
    let btn = document.getElementById('genBtn');
    let status = document.getElementById('status');
    btn.innerText = "Generating..."; btn.disabled = true;
    status.innerText = "Wait pannu da...";
    try{
        let res = await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json'},body: JSON.stringify({prompt: prompt})});
        let data = await res.json();
        let html = '<div style="background:white;padding:20px;border-radius:12px;"><div style="background:#0d8bf2;color:white;padding:15px;border-radius:8px;display:flex;justify-content:space-between"><div><b>Budget Summary</b><br>Total Budget: Rs.'+data.total_budget+'</div><div>Remaining: Rs.'+data.remaining_budget+'</div></div>';
        data.rooms.forEach(r=>{
            html+='<div style="margin-top:20px"><b style="color:#0d5bb5">'+r.room_name+'</b> <small style="background:#e8f4ff;padding:3px 8px;border-radius:8px">Allocation: Rs.'+r.allocation+'</small><table style="width:100%;border-collapse:collapse;margin-top:8px"><tr style="font-size:12px;color:#666;border-bottom:2px solid #eee"><th style="text-align:left;padding:8px">Item</th><th style="text-align:left">Description</th><th>Price</th><th>Qty</th><th>Links</th></tr>';
            r.items.forEach(it=>{
                let q = it.item.replace(/ /g, '+');
                html+='<tr style="border-bottom:1px solid #eee;font-size:13px"><td style="padding:8px"><b>'+it.item+'</b></td><td>'+it.desc+'</td><td>Rs.'+it.price+'</td><td align="center">'+it.qty+'</td><td style="font-size:11px;"><a href="https://www.amazon.in/s?k='+q+'" target="_blank">Amazon</a> <a href="https://www.flipkart.com/search?q='+q+'" target="_blank">Flipkart</a></td></tr>';
            });
            html+='</table></div>';
        });
        html+='</div><br><center><a href="/download-pdf"><button style="padding:12px 25px;background:orange;border:none;border-radius:8px;font-weight:bold">Download PDF</button></a></center>';
        document.getElementById('resultArea').innerHTML = html;
        status.innerText = "Success da! Budget update aagiduchu!";
    }catch(e){ status.innerText = "Error da: "+e; }
    btn.innerText = "Generate"; btn.disabled = false;
}
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse('<h1>Server Running da!</h1><a href="/home-planner"><h2>Click to Go Home Planner</h2></a>')

@app.get("/home-planner", response_class=HTMLResponse)
def home():
    html_content = get_html(LAST_DATA)
    return HTMLResponse(PAGE_START + html_content + PAGE_END)

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
        resp = client.models.generate_content(model="gemini-2.0-flash", contents=txt_prompt)
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
    total = d["total_budget"]
    remain = d["remaining_budget"]
    pdf.cell(0,10,f'  Budget Summary - Total Rs.{total} | Remaining Rs.{remain}', fill=True, ln=True)
    pdf.ln(3)
    pdf.set_text_color(0,0,0)
    for r in d["rooms"]:
        pdf.set_font("Arial","B",10)
        pdf.set_text_color(13,91,150)
        alloc = r["allocation"]
        pdf.cell(0,7,f'{r["room_name"]} - Rs.{alloc}', ln=True)
        pdf.set_font("Arial","B",7)
        pdf.set_text_color(0,0,0)
        pdf.cell(45,5,"Item",1);pdf.cell(60,5,"Description",1);pdf.cell(18,5,"Price",1);pdf.cell(12,5,"Qty",1);pdf.cell(55,5,"Links",1,ln=True)
        pdf.set_font("Arial","",7)
        for it in r["items"]:
            iname = it["item"][:28]
            idesc = it["desc"][:38]
            iprice = it["price"]
            iqty = it["qty"]
            pdf.cell(45,5,iname,1);pdf.cell(60,5,idesc,1);pdf.cell(18,5,f'Rs.{iprice}',1);pdf.cell(12,5,str(iqty),1);pdf.cell(55,5,"Amazon Flipkart",1,ln=True)
        pdf.ln(3)
    pdf.output("PocketSmart.pdf")
    return FileResponse("PocketSmart.pdf", filename="PocketSmart.pdf", media_type='application/pdf')