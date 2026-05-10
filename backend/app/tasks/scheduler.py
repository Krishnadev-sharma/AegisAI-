"""
Background scheduler — periodic compliance snapshots and reassessment reminders.
Copyright (C) 2024 Sarthak Doshi (github.com/SdSarthak)
SPDX-License-Identifier: AGPL-3.0-only

TODO for contributors (high priority):
  - Install APScheduler: add `apscheduler>=3.10` to backend/requirements.txt.
  - Implement `snapshot_compliance_scores()`:
      * Open a DB session.
      * Query all active AISystem rows.
      * For each system, insert a ComplianceSnapshot row with the current
        compliance_score, compliance_status, and risk_level.
  - Implement `send_reassessment_reminders()`:
      * Query RiskAssessment rows where valid_until is within 30 days
        from today and the system owner has not been notified recently.
      * Create a Notification row of type REASSESSMENT_DUE for the owner.
  - Wire both jobs into the APScheduler instance below and start the
    scheduler when the FastAPI app starts (use app lifespan or startup event).
  - Acceptance criteria: after the scheduler runs, ComplianceSnapshot rows
    appear in the DB and REASSESSMENT_DUE notifications appear for affected users.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.database import SessionLocal
from app.models.ai_system import AISystem
from app.models.notification import Notification, NotificationType

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("cron", hour=2, minute=0)
def snapshot_compliance_scores():
    """Daily job: capture a ComplianceSnapshot for every AI system."""
    pass


@scheduler.scheduled_job("cron", hour=3, minute=0)
def send_reassessment_reminders():
    """Daily job: notify users when reassessment is due."""

    db = SessionLocal()

    try:
        systems = db.query(AISystem).all()

        for system in systems:
            snapshot = ComplianceSnapshot(
                ai_system_id=system.id,
                compliance_score=system.compliance_score,
                compliance_status=system.compliance_status,
                risk_level=system.risk_level,
            )

            db.add(snapshot)

        db.commit()

    finally:
        db.close()


@scheduler.scheduled_job("cron", hour=3, minute=0)
def send_reassessment_reminders():
    """
    Daily job: notify users when a risk assessment
    is expiring within 30 days.
    """

    db = SessionLocal()

    try:
        current_time = datetime.utcnow()
        cutoff_date = current_time + timedelta(days=30)

        due_assessments = (
            db.query(RiskAssessment)
            .filter(RiskAssessment.valid_until <= cutoff_date)
            .filter(RiskAssessment.valid_until >= current_time)
            .all()
        )

        for assessment in due_assessments:

            system = assessment.ai_system

            # Prevent duplicate notifications within last 7 days
            existing_notification = (
                db.query(Notification)
                .filter(Notification.resource_id == system.id)
                .filter(
                    Notification.notification_type
                    == NotificationType.REASSESSMENT_DUE
                )
                .filter(
                    Notification.created_at
                    >= current_time - timedelta(days=7)
                )
                .first()
            )

            if existing_notification:
                continue

            notification = Notification(
                user_id=system.owner_id,
                notification_type=NotificationType.REASSESSMENT_DUE,
                title="Risk assessment due soon",
                message=(
                    f"{system.name} requires re-assessment "
                    f"by {assessment.valid_until.date()}"
                ),
                resource_type="ai_system",
                resource_id=system.id,
            )

            db.add(notification)

        db.commit()

    finally:
        db.close()