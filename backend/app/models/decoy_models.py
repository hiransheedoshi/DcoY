"""SQLAlchemy Database Models for PS 03 Decoy Asset Management and Blockchain Event Tracking."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DBDecoyAsset(Base):
    """Decoy asset (honeypot, fake credential, trap file, etc.) in the deception environment."""
    __tablename__ = "decoy_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    decoy_type: Mapped[str] = mapped_column(String, nullable=False, index=True)  # File, Credential, Service, Database, Document, API_Key
    description: Mapped[str] = mapped_column(Text, nullable=False)
    endpoint_location: Mapped[str] = mapped_column(String, nullable=False)  # Network location, file path, API endpoint, etc.
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Additional decoy-specific data
    severity: Mapped[str] = mapped_column(String, default="Medium", index=True)  # Critical, High, Medium, Low
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    last_interaction_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str] = mapped_column(String, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship to events
    events: Mapped[list["DBDecoyEvent"]] = relationship("DBDecoyEvent", back_populates="decoy", cascade="all, delete-orphan")


class DBDecoyEvent(Base):
    """Blockchain-verified event triggered when an attacker interacts with a decoy asset."""
    __tablename__ = "decoy_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    decoy_id: Mapped[int] = mapped_column(Integer, ForeignKey("decoy_assets.id"), nullable=False, index=True)
    event_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)  # SHA-256 hash of event data
    previous_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)  # Hash of previous event (blockchain linkage)
    
    # Event details
    source_ip: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_endpoint: Mapped[str] = mapped_column(String, nullable=False)
    interaction_type: Mapped[str] = mapped_column(String, nullable=False, index=True)  # accessed, credential_used, file_opened, service_probed, etc.
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)  # Link multi-step attacks
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Alert linkage
    incident_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("investigations.id"), nullable=True, index=True)
    alert_created: Mapped[bool] = mapped_column(Boolean, default=False)
    severity: Mapped[str] = mapped_column(String, default="Medium", index=True)
    
    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    decoy: Mapped["DBDecoyAsset"] = relationship("DBDecoyAsset", back_populates="events")
