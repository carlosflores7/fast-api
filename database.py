from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL="mysql+pymysql://ukotnsqognyuistz:QZCxqaUUXJ0UbWZCgMqW@b7a2fwbdsnewkhmfpybz-mysql.services.clever-cloud.com/b7a2fwbdsnewkhmfpybz"

engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        return db
    finally:
        db.close()