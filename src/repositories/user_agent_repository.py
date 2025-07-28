from sqlalchemy.orm import Session
from src.models.user_agent_model import UserAgent


class UserAgentRepository:

    @staticmethod
    def get_agent_id(db: Session, user_number: str) -> str | None:
        """Gets the agent_id for a user_number from the database."""
        user_agent = (
            db.query(UserAgent).filter(UserAgent.user_number == user_number).first()
        )
        return user_agent.agent_id if user_agent else None

    @staticmethod
    def store_agent_id(db: Session, user_number: str, agent_id: str) -> UserAgent:
        """Creates or updates the user_number -> agent_id mapping."""
        user_agent = (
            db.query(UserAgent).filter(UserAgent.user_number == user_number).first()
        )
        if user_agent:
            user_agent.agent_id = agent_id
        else:
            user_agent = UserAgent(user_number=user_number, agent_id=agent_id)
            db.add(user_agent)

        db.commit()
        db.refresh(user_agent)
        return user_agent

    @staticmethod
    def delete_agent_id(db: Session, user_number: str) -> bool:
        """Deletes the mapping for a user_number."""
        user_agent = (
            db.query(UserAgent).filter(UserAgent.user_number == user_number).first()
        )
        if user_agent:
            db.delete(user_agent)
            db.commit()
            return True
        return False
