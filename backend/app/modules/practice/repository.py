"""Database repository for practice sessions, questions, attempts, and report recommendations."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models.practice import PracticeAttempt, PracticeQuestion, PracticeSession
from app.db.models.report import InterviewReport


class PracticeRepository:
    def create_session(
        self,
        db: Session,
        *,
        user_id: int,
        interview_type: str,
        target_role: str,
        topic: str,
        experience_level: str,
        source_report_id: int | None = None,
        weakness_context: str | None = None,
    ) -> PracticeSession:
        session = PracticeSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            interview_type=interview_type,
            target_role=target_role,
            topic=topic,
            source_report_id=source_report_id,
            experience_level=experience_level,
            weakness_context=weakness_context,
            status="active",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def get_session(
        self,
        db: Session,
        session_id: str,
        user_id: int,
    ) -> PracticeSession | None:
        stmt = (
            select(PracticeSession)
            .options(
                joinedload(PracticeSession.questions).joinedload(PracticeQuestion.attempts)
            )
            .where(
                PracticeSession.id == session_id,
                PracticeSession.user_id == user_id,
                PracticeSession.deleted_at.is_(None),
            )
        )
        return db.scalars(stmt).unique().first()

    def list_sessions(
        self,
        db: Session,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[PracticeSession]:
        stmt = (
            select(PracticeSession)
            .options(
                joinedload(PracticeSession.questions).joinedload(PracticeQuestion.attempts)
            )
            .where(
                PracticeSession.user_id == user_id,
                PracticeSession.deleted_at.is_(None),
            )
            .order_by(desc(PracticeSession.updated_at))
            .limit(limit)
            .offset(offset)
        )
        return list(db.scalars(stmt).unique().all())

    def soft_delete_session(
        self,
        db: Session,
        session_id: str,
        user_id: int,
    ) -> bool:
        session = self.get_session(db, session_id, user_id)
        if not session:
            return False
        session.deleted_at = datetime.now(timezone.utc)
        session.status = "abandoned"
        db.commit()
        return True

    def create_question(
        self,
        db: Session,
        *,
        session_id: str,
        question_text: str,
        topic: str,
        difficulty: str,
        hints: dict[str, str],
        reference_answer: str,
        reference_explanation: str | None = None,
    ) -> PracticeQuestion:
        question = PracticeQuestion(
            id=str(uuid.uuid4()),
            session_id=session_id,
            question_text=question_text,
            topic=topic,
            difficulty=difficulty,
            hints=hints,
            reference_answer=reference_answer,
            reference_explanation=reference_explanation,
            hints_revealed=[],
            reference_revealed=False,
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question

    def get_question(
        self,
        db: Session,
        question_id: str,
        user_id: int,
    ) -> PracticeQuestion | None:
        stmt = (
            select(PracticeQuestion)
            .join(PracticeSession, PracticeQuestion.session_id == PracticeSession.id)
            .options(
                joinedload(PracticeQuestion.session),
                joinedload(PracticeQuestion.attempts),
            )
            .where(
                PracticeQuestion.id == question_id,
                PracticeSession.user_id == user_id,
                PracticeSession.deleted_at.is_(None),
            )
        )
        return db.scalars(stmt).unique().first()

    def reveal_hint(
        self,
        db: Session,
        question: PracticeQuestion,
        level: int,
    ) -> list[int]:
        revealed = list(question.hints_revealed or [])
        if level not in revealed:
            revealed.append(level)
            revealed.sort()
            question.hints_revealed = revealed
            db.commit()
            db.refresh(question)
        return revealed

    def reveal_reference(
        self,
        db: Session,
        question: PracticeQuestion,
    ) -> bool:
        if not question.reference_revealed:
            question.reference_revealed = True
            question.reference_revealed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(question)
        return True

    def create_attempt(
        self,
        db: Session,
        *,
        question_id: str,
        user_id: int,
        answer_text: str,
        assistance_level: str,
        hints_used: list[int],
        reference_revealed: bool,
        feedback: dict[str, Any],
    ) -> PracticeAttempt:
        # Determine attempt number
        count_stmt = select(func.count(PracticeAttempt.id)).where(
            PracticeAttempt.question_id == question_id
        )
        current_count = db.scalar(count_stmt) or 0
        attempt_number = current_count + 1

        attempt = PracticeAttempt(
            id=str(uuid.uuid4()),
            question_id=question_id,
            user_id=user_id,
            attempt_number=attempt_number,
            answer_text=answer_text,
            assistance_level=assistance_level,
            hints_used=hints_used,
            reference_revealed=reference_revealed,
            feedback=feedback,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    def list_attempts(
        self,
        db: Session,
        question_id: str,
        user_id: int,
    ) -> list[PracticeAttempt]:
        stmt = (
            select(PracticeAttempt)
            .where(
                PracticeAttempt.question_id == question_id,
                PracticeAttempt.user_id == user_id,
            )
            .order_by(PracticeAttempt.attempt_number)
        )
        return list(db.scalars(stmt).all())

    def get_recommendations_from_reports(
        self,
        db: Session,
        user_id: int,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Extract prioritized practice recommendations from user's completed interview reports."""
        stmt = (
            select(InterviewReport)
            .where(
                InterviewReport.user_id == user_id,
                InterviewReport.status == "completed",
            )
            .order_by(desc(InterviewReport.created_at))
            .limit(3)
        )
        reports = list(db.scalars(stmt).all())
        recommendations = []
        seen_topics = set()

        for rep in reports:
            # 1. From recommendations roadmap
            recs = rep.recommendations or []
            for r in recs:
                area = r.get("area") or r.get("topic")
                if not area or area.lower() in seen_topics:
                    continue
                seen_topics.add(area.lower())
                recommendations.append(
                    {
                        "topic": area,
                        "interview_type": rep.interview_type,
                        "target_role": rep.target_role,
                        "observed_gap": r.get("observed_gap", "Identified growth area in recent interview."),
                        "suggested_action": r.get("action", f"Practice {area} fundamentals with guided coaching."),
                        "source_report_id": rep.id,
                        "priority": r.get("priority", "medium"),
                    }
                )
                if len(recommendations) >= limit:
                    return recommendations

            # 2. From weaknesses list
            weaknesses = rep.weaknesses or []
            for w in weaknesses:
                w_str = str(w)
                topic_cand = w_str.split(":")[0] if ":" in w_str else w_str[:30]
                if topic_cand.lower() in seen_topics:
                    continue
                seen_topics.add(topic_cand.lower())
                recommendations.append(
                    {
                        "topic": topic_cand.strip(),
                        "interview_type": rep.interview_type,
                        "target_role": rep.target_role,
                        "observed_gap": w_str,
                        "suggested_action": f"Practice targeted questions on {topic_cand.strip()}.",
                        "source_report_id": rep.id,
                        "priority": "high",
                    }
                )
                if len(recommendations) >= limit:
                    return recommendations

        # Default fallback recommendations if user has no reports yet
        if not recommendations:
            recommendations = [
                {
                    "topic": "Authentication & Authorization",
                    "interview_type": "technical",
                    "target_role": "Software Engineer",
                    "observed_gap": "Essential core concept for modern full-stack engineering interviews.",
                    "suggested_action": "Practice explaining authentication vs authorization mechanisms.",
                    "source_report_id": 0,
                    "priority": "high",
                },
                {
                    "topic": "SQL Joins & Indexing",
                    "interview_type": "technical",
                    "target_role": "Software Engineer",
                    "observed_gap": "Critical database querying and query optimization fundamentals.",
                    "suggested_action": "Practice comparing INNER vs LEFT JOIN query execution.",
                    "source_report_id": 0,
                    "priority": "high",
                },
                {
                    "topic": "Conflict Resolution & Team Alignment",
                    "interview_type": "hr",
                    "target_role": "Software Engineer",
                    "observed_gap": "Key behavioral competency for collaborative engineering teams.",
                    "suggested_action": "Practice structuring answers on navigating technical disagreements.",
                    "source_report_id": 0,
                    "priority": "medium",
                },
            ]

        return recommendations[:limit]
