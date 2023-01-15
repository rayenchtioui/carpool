from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, nullable=False)
    description = Column(String, nullable=False)
    stars = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    user = relationship("User", foreign_keys="Review.user_id")
    reviewer = relationship("User", foreign_keys="Review.reviewer_id")

