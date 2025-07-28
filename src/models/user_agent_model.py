from sqlalchemy import Column, String
from src.db.database import Base

class UserAgent(Base):
    __tablename__ = "user_agents"

    user_number = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, unique=True)
