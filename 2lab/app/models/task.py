from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    progress = Column(Integer, nullable=False)
    result = Column(String, nullable=True)