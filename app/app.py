from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import copy

app = FastAPI()

BASE_DATA = {
    "total_budget": 100000,
    "remaining_budget": 500,
    "rooms": [
        {"room_name": "Living Room", "allocation": 30000, "items": [
            {"item": "Wakefit 3 Seater Sofa", "desc": "Grey fabric sofa", "price": 14500, "qty": 1},
            {"item": "TV Stand", "desc": "Engineered wood unit", "price": 4500, "qty": 1},
            {"item": "Coffee Table", "desc": "Modern center table", "price": 3500, "qty": 1},
            {"item": "Wall Paint", "desc": "Asian Paints light grey", "price": 7500, "qty": 1},
        ]},
        {"room_name": "Master Bedroom", "allocation": 35000, "items": [
            {"item": "Queen Bed", "desc": "Engineered wood bed", "price": 11000, "qty": 1},
            {"item": "Mattress", "desc": "Wakefit Orthopaedic", "price": 8000, "qty": 1},
            {"item": "Wardrobe", "desc": "2-door sliding wardrobe", "price": 12000, "qty": 1},
            {"item": "Study Table", "desc": "Compact wooden table", "price": 4000, "qty": 1},
        ]},
        {"room_name": "Kitchen", "allocation": 20000, "items": [
            {"item": "Modular Setup", "desc": "L-shape kitchen", "price": 10000, "qty": 1},
            {"item": "Chimney", "desc": "Faber 60cm chimney", "price": 6000, "qty": 1},
            {"item": "Dining Table", "desc": "4 Seater dining set", "price": 4000, "qty": 1},
        ]},
        {"room_name": "Kids Bedroom", "allocation": 15000, "items": [
            {"item": "Bunk Bed", "desc": "Wooden bunk bed", "price": 9000, "qty": 1},
            {"item": "Bookshelf", "desc": "Small open shelf", "price": 2500, "qty": 1},
            {"item": "Wall Decor", "desc": "Cartoon wall stickers", "price": 3500, "qty": 1},
        ]},
    ]
}

LAST_DATA = copy.deepcopy(BASE_DATA)

def make_budget(prompt, base):
    import re
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
async def generate_plan(req: dict):
    global LAST_DATA
    prompt = req.get("prompt", "")
    LAST_DATA = make_budget(prompt, BASE_DATA)
    return LAST_DATA

def get_html(d):
    total = d["total_budget"]
    remain = d["remaining_budget"]
    h = f'<div style="background:white;padding:20px;border-radius:12px;"><div style="background:#0d8bf2;color:white;padding:15px;border-radius:8px;display:flex;justify-content:space-between"><div><b>Budget Summary</b><br>Total Budget: Rs.{total}</div><div>Remaining: Rs.{remain}</div></div>'
    for r in d["rooms"]:
        h += f'<div style="margin-top:20px"><b style="color:#0d5bb5">{r["room_name"]}</b> <small>Allocation: Rs.{r["allocation"]}</small><table style="width:100%;border-collapse:collapse;margin-top:8px"><tr><th>Item</th><th>Description</th><th>Price</th><th>Qty</th><th>Links</th></tr>'
        for it in r["items"]:
            q = it["item"].replace(" ", "+")
            h += f'<tr><td><b>{it["item"]}</b></td><td>{it["desc"]}</td><td>Rs.{it["price"]}</td><td>{it["qty"]}</td><td><a href="https://www.amazon.in/s?k={q}" target="_blank">Amazon</a> <a href="https://www.flipkart.com/search?q={q}" target="_blank">Flipkart</a></td></tr>'
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
            html+='<div style="margin-top:20px"><b style="color:#0d5bb5">'+r.room_name+'</b> <small>Allocation: Rs.'+r.allocation+'</small><table><tr><th>Item</th><th>Description</th><th>Price</th><th>Qty</th><th>Links</th></tr>';
            r.items.forEach(it=>{
                let q = it.item.replace(/ /g, '+');
                html+='<tr><td><b>'+it.item+'</b></td><td>'+it.desc+'</td><td>Rs.'+it.price+'</td><td align="center">'+it.qty+'</td><td><a href="https://www.amazon.in/s?k='+q+'" target="_blank">Amazon</a> <a href="https://www.flipkart.com/search?q='+q+'" target="_blank">Flipkart</a></td></tr>';
            });
            html+='</table></div>';
        });
        html+='</div><br><center><a href="/download-pdf"><button>Download PDF</button></a></center>';
        document.getElementById('resultArea').innerHTML = html;
        status.innerText = "Success da! Budget update aagiduchu!";
    }catch(e){ status.innerText = "Error da: "+e; }
    btn.innerText = "Generate"; btn.disabled = false;
}
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse('<h1> Server Running da!</h1><a href="/home-planner"><h2>Go Home Planner</h2></a>')

@app.get("/home-planner", response_class=HTMLResponse)
def home():
    html_content = get_html(BASE_DATA)
    return HTMLResponse(PAGE_START + html_content + PAGE_END)

@app.get("/download-pdf", response_class=HTMLResponse)
def download_pdf():
    html_content = get_html(LAST_DATA)
    return HTMLResponse(f"""
    <html><body onload="window.print()">
    {PAGE_START + html_content + PAGE_END}
    </body></html>
    """)