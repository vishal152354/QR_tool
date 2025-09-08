import qrcode
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

class Item(BaseModel):
    laptopModel: str
    employeeId: str

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Allow frontend JS calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Serve login page
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Handle login (POST request with form data or JSON)
@app.post("/login")
async def login_QR(email: str = Form(...), password: str = Form(...)):
    # Dummy authentication (replace with DB or real logic)
    if email == "vishalshiva45@gmail.com" and password == "1234":
        return RedirectResponse(url="/index", status_code=303)
    return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

# After login → load QR generator page
@app.get("/index", response_class=HTMLResponse)
async def qr_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Generate QR code from data
@app.post("/submit-data")
async def handle_data(item: Item):
    qr_data = f"Laptop Model: {item.laptopModel}, Employee ID: {item.employeeId}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    filename = f"qrcode_{item.employeeId}.png"
    img_path = Path("./qrcodes") / filename

    img_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(img_path)

    return {
        "status": "success", 
        "message": "Data received and QR code generated successfully!",
        "file_path": str(img_path),
        "download_url": f"/download-qr/{filename}"
    }

# Allow QR download
@app.get("/download-qr/{filename}")
async def download_qr(filename: str):
    file_path = Path("./qrcodes") / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="image/png",   # ✅ fixed to PNG
        filename=filename
    )
