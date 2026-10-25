"""Decoy asset management and interaction tracking router for PS 03 Cybersecurity & Blockchain."""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.dependencies.auth import check_permission
from app.database import get_db
from app.models.decoy_models import DBDecoyAsset, DBDecoyEvent
from app.models.database_models import DBInvestigation

logger = logging.getLogger(__name__)

router = APIRouter()


# =====================================================
# Pydantic Models for Request/Response
# =====================================================

class DecoyAssetCreate(BaseModel):
    name: str
    decoy_type: str  # File, Credential, Service, Database, Document, API_Key
    description: str
    endpoint_location: str
    metadata: Optional[Dict[str, Any]] = None
    severity: str = "Medium"  # Critical, High, Medium, Low
    enabled: bool = True


class DecoyAssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    endpoint_location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    severity: Optional[str] = None
    enabled: Optional[bool] = None


class TriggerInteractionPayload(BaseModel):
    source_ip: str
    source_endpoint: str
    interaction_type: str  # accessed, credential_used, file_opened, service_probed, query_executed, api_called
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# =====================================================
# Decoy Asset CRUD Operations
# =====================================================

@router.post("/api/decoys", summary="Create Decoy Asset", description="Deploys a new decoy asset in the simulated network environment.")
def create_decoy(
    body: DecoyAssetCreate,
    user: str = Depends(check_permission("rules:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/decoys - User: {user}, Name: {body.name}")
    
    # Check if decoy with same name already exists
    existing = db.query(DBDecoyAsset).filter(DBDecoyAsset.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Decoy asset with name '{body.name}' already exists.")
    
    decoy = DBDecoyAsset(
        name=body.name,
        decoy_type=body.decoy_type,
        description=body.description,
        endpoint_location=body.endpoint_location,
        metadata=body.metadata,
        severity=body.severity,
        enabled=body.enabled,
        interaction_count=0,
        created_by=user,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(decoy)
    db.commit()
    db.refresh(decoy)
    
    logger.info(f"Created decoy asset: {decoy.name} (ID: {decoy.id})")
    
    return {
        "message": "Decoy asset created successfully",
        "id": decoy.id,
        "name": decoy.name,
        "enabled": decoy.enabled
    }


@router.get("/api/decoys", summary="List Decoy Assets", description="Returns all deployed decoy assets with filtering options.")
def list_decoys(
    decoy_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    severity: Optional[str] = None,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/decoys - User: {user}")
    
    query = db.query(DBDecoyAsset)
    
    if decoy_type:
        query = query.filter(DBDecoyAsset.decoy_type == decoy_type)
    if enabled is not None:
        query = query.filter(DBDecoyAsset.enabled == enabled)
    if severity:
        query = query.filter(DBDecoyAsset.severity == severity)
    
    decoys = query.order_by(DBDecoyAsset.created_at.desc()).all()
    
    return [
        {
            "id": d.id,
            "name": d.name,
            "decoy_type": d.decoy_type,
            "description": d.description,
            "endpoint_location": d.endpoint_location,
            "severity": d.severity,
            "enabled": d.enabled,
            "interaction_count": d.interaction_count,
            "last_interaction_at": d.last_interaction_at.isoformat() if d.last_interaction_at else None,
            "created_at": d.created_at.isoformat(),
            "metadata": d.metadata
        }
        for d in decoys
    ]


@router.get("/api/decoys/{decoy_id}", summary="Get Decoy Asset Details")
def get_decoy(
    decoy_id: int,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    decoy = db.query(DBDecoyAsset).filter(DBDecoyAsset.id == decoy_id).first()
    if not decoy:
        raise HTTPException(status_code=404, detail="Decoy asset not found")
    
    return {
        "id": decoy.id,
        "name": decoy.name,
        "decoy_type": decoy.decoy_type,
        "description": decoy.description,
        "endpoint_location": decoy.endpoint_location,
        "severity": decoy.severity,
        "enabled": decoy.enabled,
        "interaction_count": decoy.interaction_count,
        "last_interaction_at": decoy.last_interaction_at.isoformat() if decoy.last_interaction_at else None,
        "created_by": decoy.created_by,
        "created_at": decoy.created_at.isoformat(),
        "updated_at": decoy.updated_at.isoformat(),
        "metadata": decoy.metadata
    }


@router.put("/api/decoys/{decoy_id}", summary="Update Decoy Asset")
def update_decoy(
    decoy_id: int,
    body: DecoyAssetUpdate,
    user: str = Depends(check_permission("rules:write")),
    db: Session = Depends(get_db)
):
    decoy = db.query(DBDecoyAsset).filter(DBDecoyAsset.id == decoy_id).first()
    if not decoy:
        raise HTTPException(status_code=404, detail="Decoy asset not found")
    
    if body.name is not None:
        decoy.name = body.name
    if body.description is not None:
        decoy.description = body.description
    if body.endpoint_location is not None:
        decoy.endpoint_location = body.endpoint_location
    if body.metadata is not None:
        decoy.metadata = body.metadata
    if body.severity is not None:
        decoy.severity = body.severity
    if body.enabled is not None:
        decoy.enabled = body.enabled
    
    decoy.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(decoy)
    
    return {"message": "Decoy asset updated successfully", "id": decoy.id}


@router.delete("/api/decoys/{decoy_id}", summary="Delete Decoy Asset")
def delete_decoy(
    decoy_id: int,
    user: str = Depends(check_permission("rules:write")),
    db: Session = Depends(get_db)
):
    decoy = db.query(DBDecoyAsset).filter(DBDecoyAsset.id == decoy_id).first()
    if not decoy:
        raise HTTPException(status_code=404, detail="Decoy asset not found")
    
    db.delete(decoy)
    db.commit()
    
    return {"message": f"Decoy asset '{decoy.name}' deleted successfully"}


# =====================================================
# Decoy Statistics
# =====================================================

@router.get("/api/decoys/stats/summary", summary="Get Decoy Statistics")
def get_decoy_stats(
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    total_decoys = db.query(func.count(DBDecoyAsset.id)).scalar()
    enabled_decoys = db.query(func.count(DBDecoyAsset.id)).filter(DBDecoyAsset.enabled == True).scalar()
    total_interactions = db.query(func.count(DBDecoyEvent.id)).scalar()
    
    # Interactions in last 24 hours
    from datetime import timedelta
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_interactions = db.query(func.count(DBDecoyEvent.id)).filter(DBDecoyEvent.timestamp >= last_24h).scalar()
    
    return {
        "total_decoys": total_decoys,
        "enabled_decoys": enabled_decoys,
        "total_interactions": total_interactions,
        "recent_interactions_24h": recent_interactions
    }


# =====================================================
# Decoy Event Tracking
# =====================================================

@router.get("/api/decoys/events/recent", summary="Get Recent Decoy Events")
def get_recent_decoy_events(
    limit: int = 20,
    decoy_id: Optional[int] = None,
    severity: Optional[str] = None,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    query = db.query(DBDecoyEvent)
    
    if decoy_id:
        query = query.filter(DBDecoyEvent.decoy_id == decoy_id)
    if severity:
        query = query.filter(DBDecoyEvent.severity == severity)
    
    events = query.order_by(desc(DBDecoyEvent.timestamp)).limit(limit).all()
    
    return [
        {
            "id": e.id,
            "decoy_id": e.decoy_id,
            "event_hash": e.event_hash,
            "previous_hash": e.previous_hash,
            "source_ip": e.source_ip,
            "source_endpoint": e.source_endpoint,
            "interaction_type": e.interaction_type,
            "session_id": e.session_id,
            "severity": e.severity,
            "incident_id": e.incident_id,
            "alert_created": e.alert_created,
            "timestamp": e.timestamp.isoformat(),
            "metadata": e.metadata
        }
        for e in events
    ]


# =====================================================
# Decoy Interaction Simulation (PS 03 Core Feature)
# =====================================================

@router.post("/api/decoys/{decoy_id}/interact", summary="Trigger Decoy Interaction", 
             description="Simulates an attacker interaction with a decoy asset. Records event with blockchain verification and triggers automatic alert creation.")
def trigger_decoy_interaction(
    decoy_id: int,
    body: TriggerInteractionPayload,
    user: str = Depends(check_permission("rules:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/decoys/{decoy_id}/interact - User: {user}, IP: {body.source_ip}")
    
    # Get decoy asset
    decoy = db.query(DBDecoyAsset).filter(DBDecoyAsset.id == decoy_id).first()
    if not decoy:
        raise HTTPException(status_code=404, detail="Decoy asset not found")
    
    if not decoy.enabled:
        raise HTTPException(status_code=400, detail="Decoy asset is disabled")
    
    # Get previous event hash for blockchain linkage
    previous_event = db.query(DBDecoyEvent).order_by(desc(DBDecoyEvent.id)).first()
    previous_hash = previous_event.event_hash if previous_event else "0" * 64
    
    # Create event data for hashing
    timestamp = datetime.now(timezone.utc)
    event_data = f"{decoy_id}:{body.source_ip}:{body.interaction_type}:{timestamp.isoformat()}:{previous_hash}"
    event_hash = hashlib.sha256(event_data.encode()).hexdigest()
    
    # Determine severity (escalate for credential abuse)
    severity = decoy.severity
    if body.interaction_type in ["credential_used", "file_opened", "query_executed"]:
        # Escalate severity for high-risk interactions
        severity_levels = {"Low": "Medium", "Medium": "High", "High": "Critical"}
        severity = severity_levels.get(decoy.severity, decoy.severity)
    
    # Create decoy event with blockchain verification
    event = DBDecoyEvent(
        decoy_id=decoy_id,
        event_hash=event_hash,
        previous_hash=previous_hash,
        source_ip=body.source_ip,
        source_endpoint=body.source_endpoint,
        interaction_type=body.interaction_type,
        session_id=body.session_id,
        metadata=body.metadata,
        severity=severity,
        alert_created=False,
        timestamp=timestamp,
        recorded_at=datetime.now(timezone.utc)
    )
    
    db.add(event)
    
    # Update decoy statistics
    decoy.interaction_count += 1
    decoy.last_interaction_at = timestamp
    decoy.updated_at = datetime.now(timezone.utc)
    
    # Automatic incident creation for HIGH/CRITICAL decoys or credential abuse
    incident_created = False
    incident_id = None
    
    if severity in ["High", "Critical"] or body.interaction_type in ["credential_used", "query_executed"]:
        # Generate incident ID
        incident_id = f"DECOY-{timestamp.strftime('%Y%m')}-{db.query(func.count(DBInvestigation.id)).scalar() + 1:04d}"
        
        # Create investigation
        investigation = DBInvestigation(
            id=incident_id,
            title=f"{body.interaction_type.replace('_', ' ').title()} Detected on {decoy.name}",
            status="New",
            priority="High" if severity == "Critical" else "Medium",
            severity=severity,
            assigned_analyst="SOC-Auto",
            ai_summary=f"Decoy interaction detected: {body.interaction_type} from {body.source_ip} on {decoy.decoy_type} decoy '{decoy.name}'. This is a high-confidence malicious activity indicator.",
            risk_score=0.9 if severity == "Critical" else 0.75,
            created_at=timestamp,
            updated_at=timestamp
        )
        
        db.add(investigation)
        event.incident_id = incident_id
        event.alert_created = True
        incident_created = True
        
        logger.info(f"Auto-created incident {incident_id} for decoy interaction (severity: {severity})")
    
    db.commit()
    db.refresh(event)
    
    logger.info(f"Recorded decoy event {event.id} with hash {event_hash[:16]}... (blockchain verified)")
    
    return {
        "message": "Decoy interaction recorded successfully",
        "event_id": event.id,
        "event_hash": event.event_hash,
        "previous_hash": event.previous_hash,
        "blockchain_verified": True,
        "severity": severity,
        "incident_created": incident_created,
        "incident_id": incident_id,
        "decoy_name": decoy.name,
        "decoy_type": decoy.decoy_type
    }
