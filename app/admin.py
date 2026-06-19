from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from .config import settings
from . import db

app=FastAPI(title=f"{settings.brand_name} Admin")
templates=Jinja2Templates(directory="app/templates")
security=HTTPBasic()

def auth(creds:HTTPBasicCredentials=Depends(security)):
    ok_user=secrets.compare_digest(creds.username, settings.admin_username)
    ok_pass=secrets.compare_digest(creds.password, settings.admin_password)
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate":"Basic"})
    return creds.username

@app.get('/health')
def health(): return {'ok': True}

@app.get('/', response_class=HTMLResponse)
def home(request:Request, admin=Depends(auth)):
    return templates.TemplateResponse('dashboard.html', {'request':request,'brand':settings.brand_name,'kycs':db.list_kyc(),'ops':db.list_ops()})

@app.get('/kyc/{rid}', response_class=HTMLResponse)
def kyc_detail(rid:int, request:Request, admin=Depends(auth)):
    item=db.get_kyc(rid)
    if not item: raise HTTPException(404)
    return templates.TemplateResponse('kyc_detail.html', {'request':request,'brand':settings.brand_name,'r':item})

@app.post('/kyc/{rid}/review')
def kyc_review(rid:int, status:str=Form(...), reason:str=Form(''), admin=Depends(auth)):
    db.review_kyc(rid,status,reason,admin)
    return RedirectResponse('/', status_code=303)

@app.get('/file')
def file(path:str, admin=Depends(auth)):
    return FileResponse(path)
