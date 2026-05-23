from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SystemSetting

app=FastAPI(title="考研考公学习打卡系统")

@app.get("/")
def read_root():
    return{"message":"系统运行中"}

@app.get("/api/settings")
def read_settings(db:Session=Depends(get_db)):
    settings=db.query(SystemSetting).all()
    return {item.key:item.value for item in settings}




