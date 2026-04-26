from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship
from backend.db.base import Base
from backend.core.logging import logger

# PRODUCTION PATTERN: DRY Audit Mixin
class AuditMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class User(AuditMixin, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    preferences = Column(JSONB, default=dict, server_default="{}")
    
    trips = relationship("Trip", back_populates="owner")

    __table_args__ = (
        # B-Tree is default, explicitly stating for clarity on search fields
        Index('ix_user_username', 'username'), 
    )

class Trip(AuditMixin, Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination = Column(String(100), nullable=False, index=True)
    duration_days = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    
    # PRODUCTION PATTERN: JSONB instead of Text. Allows Postgres to internally index/query JSON.
    final_plan_json = Column(JSONB, default=dict, server_default="{}")

    owner = relationship("User", back_populates="trips")
    itineraries = relationship("Itinerary", back_populates="trip", cascade="all, delete-orphan")

    __table_args__ = (
        # B-Tree on Foreign Key for fast joins
        Index('ix_trip_user_id', 'user_id'),
        # PRODUCTION PATTERN: BRIN Index. Perfect for append-only time-series data (like audit trails/created_at). 
        # Takes 99% less space than B-Tree on large tables.
        Index('ix_trip_created_at_brin', 'created_at', postgresql_using='brin'),
    )

class Itinerary(AuditMixin, Base):
    __tablename__ = "itineraries"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False)
    activities = Column(JSONB, default=list, server_default="[]")

    trip = relationship("Trip", back_populates="itineraries")

    __table_args__ = (
        Index('ix_itinerary_trip_id', 'trip_id'),
    )