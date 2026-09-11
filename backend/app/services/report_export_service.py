import io
import csv
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain import User, AssessmentAttempt, LearnerAlphabetState, LearnerProfile, PracticeSession

class ReportExportService:
    """
    Production Report Export Engine:
    Exports learner performance reports and session summaries directly from live database tables
    into PDF (HTML-printable format) and Excel/CSV tabular formats.
    No hardcoded values.
    """
    def generate_csv_report(self, db: Session, user: User) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        # Header section
        writer.writerow(["ASL SIGN LANGUAGE LEARNING AND ASSESSMENT PLATFORM"])
        writer.writerow(["PERFORMANCE REPORT FOR LEARNER", user.full_name, user.email])
        writer.writerow([])

        # Summary Metrics
        profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user.id).first()
        score = profile.overall_performance_score if profile else 0.0
        streak = profile.practice_streak_days if profile else 0

        writer.writerow(["METRIC", "VALUE"])
        writer.writerow(["Overall Learning Performance Score", f"{score:.2f}%"])
        writer.writerow(["Practice Streak (Days)", streak])
        writer.writerow([])

        # Alphabet Mastery Table
        writer.writerow(["ALPHABET MASTERY METRICS"])
        writer.writerow(["Sign", "Current State", "Total Attempts", "Successful Attempts", "Average Accuracy", "Mastery %"])

        states = db.query(LearnerAlphabetState).filter(
            LearnerAlphabetState.learner_id == user.id
        ).order_by(LearnerAlphabetState.sign_character.asc()).all()

        for s in states:
            writer.writerow([
                s.sign_character,
                s.current_state.value,
                s.total_attempts,
                s.successful_attempts,
                f"{s.average_accuracy:.1f}%",
                f"{s.mastery_percentage:.1f}%"
            ])

        writer.writerow([])
        # Recent Assessment Attempts
        writer.writerow(["RECENT ASSESSMENT ATTEMPTS (LAST 20)"])
        writer.writerow(["Attempt ID", "Timestamp", "Expected Sign", "Predicted Sign", "Correct", "Confidence %", "Gesture Accuracy %"])

        attempts = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.learner_id == user.id
        ).order_by(AssessmentAttempt.timestamp.desc()).limit(20).all()

        for a in attempts:
            writer.writerow([
                a.id,
                a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                a.expected_sign,
                a.predicted_sign,
                "YES" if a.is_correct else "NO",
                f"{a.confidence*100.0:.1f}%",
                f"{a.gesture_accuracy:.1f}%"
            ])

        return output.getvalue()

    def generate_pdf_html_report(self, db: Session, user: User) -> str:
        """Generates HTML-formatted printable PDF report."""
        profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user.id).first()
        score = profile.overall_performance_score if profile else 0.0

        states = db.query(LearnerAlphabetState).filter(
            LearnerAlphabetState.learner_id == user.id
        ).order_by(LearnerAlphabetState.sign_character.asc()).all()

        mastery_rows = "".join([
            f"<tr><td>{s.sign_character}</td><td>{s.current_state.value}</td><td>{s.total_attempts}</td><td>{s.successful_attempts}</td><td>{s.average_accuracy:.1f}%</td><td>{s.mastery_percentage:.1f}%</td></tr>"
            for s in states
        ])

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ASL Performance Report - {user.full_name}</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; padding: 24px; color: #1e293b; }}
        h1 {{ color: #0284c7; margin-bottom: 4px; }}
        .header-card {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; font-size: 13px; }}
        th {{ background: #0f172a; color: #ffffff; }}
        tr:nth-child(even) {{ background: #f1f5f9; }}
    </style>
</head>
<body>
    <h1>ASL Platform Learner Performance Report</h1>
    <div class="header-card">
        <p><strong>Learner Name:</strong> {user.full_name} ({user.email})</p>
        <p><strong>Overall Learning Score:</strong> {score:.2f}%</p>
        <p><strong>Practice Streak:</strong> {profile.practice_streak_days if profile else 0} Days</p>
    </div>

    <h2>Alphabet Skill Mastery Matrix</h2>
    <table>
        <thead>
            <tr>
                <th>Sign</th>
                <th>Status State</th>
                <th>Total Attempts</th>
                <th>Successful</th>
                <th>Avg Accuracy</th>
                <th>Mastery %</th>
            </tr>
        </thead>
        <tbody>
            {mastery_rows}
        </tbody>
    </table>
</body>
</html>"""
        return html_content

report_export_service = ReportExportService()
