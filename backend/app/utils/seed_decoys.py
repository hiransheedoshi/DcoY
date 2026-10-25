"""Seed sample decoy assets for PS 03 demonstration."""

import logging
from datetime import datetime, timezone
from app.database import SessionLocal
from app.models.decoy_models import DBDecoyAsset

logger = logging.getLogger(__name__)


SAMPLE_DECOYS = [
    {
        "name": "SSH Honeypot Server",
        "decoy_type": "Service",
        "description": "Fake SSH server listening on port 22. Logs all authentication attempts and commands.",
        "endpoint_location": "192.168.100.50:22",
        "severity": "Critical",
        "metadata": {"service": "openssh", "version": "7.4", "port": 22}
    },
    {
        "name": "Admin Credentials - aws_admin",
        "decoy_type": "Credential",
        "description": "Fake AWS admin credentials planted in developer workstation.",
        "endpoint_location": "C:\\Users\\developer\\.aws\\credentials",
        "severity": "Critical",
        "metadata": {"username": "aws_admin", "access_key": "AKIAIOSFODNN7EXAMPLE"}
    },
    {
        "name": "Financial Database - Oracle Prod",
        "decoy_type": "Database",
        "description": "Fake Oracle database with fake financial records.",
        "endpoint_location": "oracle://192.168.100.75:1521/FINPROD",
        "severity": "High",
        "metadata": {"db_type": "oracle", "version": "19c", "records": 50000}
    },
    {
        "name": "API Key - stripe_live_key",
        "decoy_type": "API_Key",
        "description": "Fake Stripe API key embedded in source code repository.",
        "endpoint_location": "/var/www/html/config/payment.conf",
        "severity": "High",
        "metadata": {"api_type": "stripe", "scope": "full_access"}
    },
    {
        "name": "File Share - HR Documents",
        "decoy_type": "File",
        "description": "Decoy file share containing fake employee records and salary data.",
        "endpoint_location": "\\\\fileserver\\hr\\confidential",
        "severity": "Medium",
        "metadata": {"file_count": 245, "total_size_mb": 1200}
    },
    {
        "name": "MySQL Development Server",
        "decoy_type": "Service",
        "description": "Fake MySQL server with weak credentials for attracting lateral movement.",
        "endpoint_location": "192.168.100.80:3306",
        "severity": "Medium",
        "metadata": {"service": "mysql", "version": "8.0", "weak_password": True}
    },
    {
        "name": "RDP Honeypot - Admin Desktop",
        "decoy_type": "Service",
        "description": "Fake Windows RDP server simulating administrator workstation.",
        "endpoint_location": "192.168.100.100:3389",
        "severity": "High",
        "metadata": {"service": "rdp", "os": "Windows Server 2019"}
    },
    {
        "name": "Credentials - root@production",
        "decoy_type": "Credential",
        "description": "Fake root credentials for production Linux server.",
        "endpoint_location": "/home/devops/.bash_history",
        "severity": "Critical",
        "metadata": {"username": "root", "password_hash": "fake_hash_12345"}
    },
    {
        "name": "Customer Database Export",
        "decoy_type": "Document",
        "description": "Fake SQL dump file containing customer PII data.",
        "endpoint_location": "/backups/customer_export_20261001.sql",
        "severity": "High",
        "metadata": {"file_type": "sql", "size_mb": 850, "records": 120000}
    },
    {
        "name": "Kubernetes API Token",
        "decoy_type": "API_Key",
        "description": "Fake Kubernetes cluster admin token in CI/CD pipeline.",
        "endpoint_location": "/var/lib/jenkins/secrets/k8s-admin-token",
        "severity": "Critical",
        "metadata": {"api_type": "kubernetes", "cluster": "prod-cluster-01"}
    }
]


def seed_decoys():
    """Seed sample decoy assets into the database."""
    db = SessionLocal()
    try:
        # Check if decoys already exist
        existing_count = db.query(DBDecoyAsset).count()
        if existing_count > 0:
            logger.info(f"Decoys already seeded ({existing_count} exist). Skipping.")
            return existing_count
        
        logger.info("Seeding sample decoy assets...")
        
        for decoy_data in SAMPLE_DECOYS:
            decoy = DBDecoyAsset(
                name=decoy_data["name"],
                decoy_type=decoy_data["decoy_type"],
                description=decoy_data["description"],
                endpoint_location=decoy_data["endpoint_location"],
                metadata=decoy_data.get("metadata"),
                severity=decoy_data["severity"],
                enabled=True,
                interaction_count=0,
                created_by="system",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(decoy)
        
        db.commit()
        logger.info(f"Successfully seeded {len(SAMPLE_DECOYS)} decoy assets")
        return len(SAMPLE_DECOYS)
        
    except Exception as e:
        logger.error(f"Error seeding decoys: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_decoys()
