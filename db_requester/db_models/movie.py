from typing import Any, Dict
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MovieDBModel(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)  # integer в БД
    name = Column(String)  # text в БД
    description = Column(String)  # text в БД
    image_url = Column(String)  # text в БД
    price = Column(Integer)  # integer в БД
    rating = Column(Float)  # double precision в БД
    genre_id = Column(Integer)  # integer в БД
    location = Column(String)  # USER-DEFINED / enum в БД
    published = Column(Boolean)  # boolean в БД
    created_at = Column(DateTime)  # timestamp without time zone в БД

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "price": self.price,
            "rating": self.rating,
            "genre_id": self.genre_id,
            "location": self.location,
            "published": self.published,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        return f"<Movie(id={self.id}, name='{self.name}')>"