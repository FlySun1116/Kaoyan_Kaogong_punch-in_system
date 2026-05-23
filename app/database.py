#数据库连接
from sqlalchemy import create_engine,event
from sqlalchemy.orm import sessionmaker,DeclarativeBase

from app.config import DATABASE_URL

class Base(DeclarativeBase):
    pass

engine=create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread':False} #允许sqlite在不同线程中使用
)

# 每次连接的时候开启外键
@event.listens_for(engine,'connect')
def set_sqlite_pragma(dbapi_connection,connection_record):
    cursor=dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

#创建数据库会话
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

