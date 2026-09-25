from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fpdf import FPDF

app = FastAPI()
MODEL_NAME = "gemini-2.5-flash"
DATA = {
  "total_budget": 100000,
  "remaining_budget": 500,
  "rooms": [
    {"room_name": "Living Room", "allocation": 30000, "items": [
      {"item": "Wakefit 3 Seater Sofa", "desc": "Grey fabric sofa with high-density foam", "price": 14500, "qty": 1},
      {"item": "DeckUp Giona TV Stand", "desc": "Engineered wood TV unit in walnut finish", "price": 4500, "qty": 1},
      {"item": "IKEA LACK Coffee Table", "desc": "Minimalist white coffee table", "price": 1900, "qty": 1},
      {"item": "Home Sizzler Curtains", "desc": "Set of 2 blackout curtains", "price": 1200, "qty": 2},
    ]},
    {"room_name": "Master Bedroom", "allocation": 35000, "items": [
      {"item": "Nilkamal Arthur Queen Bed", "desc": "Engineered wood bed with storage", "price": 11000, "qty": 1},
      {"item": "SleepyCat Hybrid Mattress", "desc": "6-inch Orthopedic Memory Foam", "price": 8000, "qty": 1},
    ]},
    {"room_name": "Second Bedroom", "allocation": 25000, "items": [
      {"item": "Wakefit Single Bed", "desc": "Solid engineered wood single bed", "price": 7500, "qty": 1},
      {"item": "IKEA MICKE Study Desk", "desc": "Compact desk for study/work", "price": 6000, "qty": 1},
    ]}
  ]
}

def get_html():
    d = DATA
    h = f'''
    <div style="background:white;padding:20px;border-radius:12px;box-shadow:0 4px 12px #0001">
      <div style="background:#0d8bf2;color:white;padding:15px;border-radius:8px;display:flex;justify-content:space-between">
        <div><b>📊 Budget Summary</b><br>Total Budget: ₹{d["total_budget"]}.00</div>
        <div>Remaining Budget: ₹{d["remaining_budget"]}.00</div>
      </div>
    '''
    for r in d["rooms"]:
        h += f'<div style="margin-top:20px"><b style="color:#0d5bb5">💡 {r["room_name"]}</b> <small style="background:#e8f4ff;padding:3px 8px;border-radius:8px">Allocation: ₹{r["allocation"]}.00</small><table style="width:100%;border-collapse:collapse;margin-top:8px"><tr style="font-size:12px;color:#666;border-bottom:2px solid #eee"><th style="text-align:left;padding:8px">Item</th><th style="text-align:left">Description</th><th>Price</th><th>Quantity</th><th>Shopping Links</th></tr>'
        for it in r["items"]:
            h += f'<tr style="border-bottom:1px solid #eee;font-size:13px"><td style="padding:8px"><b>{it["item"]}</b></td><td>{it["desc"]}</td><td>₹{it["price"]}.00</td><td align="center">{it["qty"]}</td><td style="font-size:11px;color:#0d8bf2">Amazon Flipkart Ikea Myntra Ajio</td></tr>'
        h += '</table></div>'
    h += '</div><br><center><a href="/download-pdf"><button style="padding:12px 25px;background:orange;border:none;border-radius:8px;font-weight:bold">📥 Download PDF - Full Box</button></a></center>'
    return h

PAGE = """
<html><body style="font-family:Arial;background:#f6f8fc;padding:20px">
<center><button style="background:#0d5b96;color:white;padding:12px 22px;border-radius:25px;border:none;font-weight:bold">📋 Generate Recommendations</button>
<h1 style="color:#0d3b66">Your Personalized Budget Plan</h1>
<div style="background:white;padding:15px;border-radius:30px;width:90%;display:flex;box-shadow:0 2px 10px #0001">
<input style="flex:1;border:none;outline:none" value="Create full 2BHK home interior budget plan for 1 lakh rupees, explain each room separately - living room, master bedroom, second bedroom">
<button style="background:#0d8bf2;color:white;border:none;border-radius:20px;padding:10px 20px">Generate</button>
</div></center><br>{result}
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
def root(): return HTMLResponse('<h1>Server Running da Swetha! 🎉</h1><a href="/home-planner"><h2>Click to Go Home Planner</h2></a>')

@app.get("/home-planner", response_class=HTMLResponse)
def home(): return HTMLResponse(PAGE.format(result=get_html()))

@app.get("/download-pdf")
def pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 1. Mela 3 line
    pdf.set_fill_color(13, 91, 150)
    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial","B",10)
    pdf.cell(0,10,"  Generate Recommendations", fill=True, ln=True, align='C')
    pdf.ln(3)
    pdf.set_text_color(13, 59, 102)
    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"Your Personalized Budget Plan", ln=True, align='C')
    pdf.ln(2)
    pdf.set_text_color(80,80,80)
    pdf.set_font("Arial","",9)
    pdf.multi_cell(0,5,f"Query: Create full 2BHK home interior budget plan for 1 lakh rupees, explain each room separately - living room, master bedroom, second bedroom")
    pdf.ln(4)
    
    # 2. Budget Summary
    pdf.set_fill_color(13,139,242)
    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial","B",11)
    pdf.cell(0,10,f"  Budget Summary - Total Rs.{DATA['total_budget']} | Remaining Rs.{DATA['remaining_budget']}", fill=True, ln=True)
    pdf.ln(3)
    
    for r in DATA["rooms"]:
        pdf.set_font("Arial","B",10)
        pdf.set_text_color(13,91,150)
        pdf.cell(0,7,f"{r['room_name']} - Allocation Rs.{r['allocation']}", ln=True)
        pdf.set_font("Arial","B",7)
        pdf.set_text_color(0,0,0)
        pdf.cell(45,5,"Item",1);pdf.cell(60,5,"Description",1);pdf.cell(18,5,"Price",1);pdf.cell(12,5,"Qty",1);pdf.cell(55,5,"Shopping Links",1,ln=True)
        pdf.set_font("Arial","",7)
        for it in r["items"]:
            pdf.set_text_color(0,0,0)
            pdf.cell(45,5,it["item"][:28],1);pdf.cell(60,5,it["desc"][:38],1);pdf.cell(18,5,f"Rs.{it['price']}",1);pdf.cell(12,5,str(it["qty"]),1)
            pdf.set_text_color(13,139,242) # BLUE LINK DA!
            pdf.cell(55,5,"Amazon Flipkart Ikea Myntra Ajio",1,ln=True)
            pdf.set_text_color(0,0,0)
        pdf.ln(3)
    pdf.output("PocketSmart.pdf")
    return FileResponse("PocketSmart.pdf", filename="PocketSmart_BLUE_LINKS.pdf", media_type='application/pdf')