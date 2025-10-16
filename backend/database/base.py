"""
SQLAlchemy Base Model and Declarative Base
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session

Base = declarative_base()


class BaseModel:
    """
    Base model with common fields and methods for all models
    """

    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name"""
        return cls.__name__.lower() + 's'

    def to_dict(self):
        """
        Convert model instance to dictionary

        Returns:
            dict: Dictionary representation of the model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert datetime to ISO format string
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def update(self, **kwargs):
        """
        Update model attributes from kwargs

        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save(self, session: Session):
        """
        Save model instance to database

        Args:
            session: SQLAlchemy session
        """
        session.add(self)
        session.flush()

    def delete(self, session: Session):
        """
        Delete model instance from database

        Args:
            session: SQLAlchemy session
        """
        session.delete(self)
        session.flush()

    def __repr__(self):
        """String representation of model"""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"