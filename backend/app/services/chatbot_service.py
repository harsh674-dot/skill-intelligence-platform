import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.competency import RoleCompetency, UserCompetency, Competency
from app.models.course import Course
from app.models.learning import Recommendation
from app.models.chat import ChatSession, ChatMessage
from app.services.vector_search import search_content


def get_employee_rag_context(db: Session, user: User) -> dict:
    """
    Retrieve employee's current profile, competency gaps, and active course recommendations
    to ground the RAG chatbot responses.
    """
    gaps_info = []
    if user.job_role_id:
        role_competencies = (
            db.query(RoleCompetency, Competency)
            .join(Competency, RoleCompetency.competency_id == Competency.id)
            .filter(RoleCompetency.role_id == user.job_role_id)
            .all()
        )

        user_competencies = {
            uc.competency_id: uc.current_level
            for uc in db.query(UserCompetency).filter(UserCompetency.user_id == user.id).all()
        }

        for rc, comp in role_competencies:
            current_lvl = user_competencies.get(comp.id, 1)
            required_lvl = rc.required_level
            gap = max(required_lvl - current_lvl, 0)
            if gap > 0:
                gaps_info.append({
                    "competency_id": str(comp.id),
                    "name": comp.name,
                    "domain": comp.domain,
                    "current_level": current_lvl,
                    "required_level": required_lvl,
                    "gap": gap,
                    "is_critical": rc.is_critical,
                })

    # Sort gaps by critical first, then gap size descending
    gaps_info.sort(key=lambda g: (not g["is_critical"], -g["gap"]))

    # Recommendations
    recommendations = (
        db.query(Recommendation, Course, Competency)
        .join(Course, Recommendation.course_id == Course.id)
        .join(Competency, Recommendation.competency_id == Competency.id)
        .filter(
            Recommendation.user_id == user.id,
            Recommendation.status.in_(["pending", "accepted"]),
        )
        .order_by(Recommendation.priority_score.desc())
        .limit(5)
        .all()
    )

    recs_info = [
        {
            "course_title": course.title,
            "provider": course.provider or "Official Training Portal",
            "competency": comp.name,
            "priority": float(rec.priority_score),
        }
        for rec, course, comp in recommendations
    ]

    role_title = user.job_role.name if user.job_role else (user.designation or "Statistical Officer")

    return {
        "user_name": user.full_name,
        "designation": user.designation or role_title,
        "department": user.department or "National Statistical System",
        "role_title": role_title,
        "gaps": gaps_info,
        "recommendations": recs_info,
    }


def synthesize_rag_response(
    query: str,
    context: dict,
    sources: list[dict],
) -> str:
    """
    Synthesize an authoritative, personalized response grounded in the employee's
    specific competency gaps, courses, and semantic search knowledge snippets.
    """
    name = context["user_name"]
    role = context["role_title"]
    dept = context["department"]
    gaps = context["gaps"]
    recs = context["recommendations"]

    q_lower = query.lower()

    # Formulate contextual response parts
    greeting = f"Hello {name}, as a {role} in {dept}:"

    # Gaps summary
    top_gaps = [f"**{g['name']}** (Current: L{g['current_level']} / Required: L{g['required_level']}, Gap: -{g['gap']})" for g in gaps[:3]]
    gaps_text = ", ".join(top_gaps) if top_gaps else "No active critical competency deficits identified."

    # Top course recommendations
    top_courses = [f"• **{r['course_title']}** ({r['provider']}) targeting *{r['competency']}*" for r in recs[:3]]
    courses_text = "\n".join(top_courses) if top_courses else "• All baseline coursework completed."

    # Retrieved content snippet grounding
    snippet_text = ""
    if sources:
        top_snippet = sources[0]["text"]
        # Trim snippet if needed
        clean_snip = top_snippet[:300].strip().replace("\n", " ")
        snippet_text = f"\n\n**Relevant Learning Material Reference:**\n> \"{clean_snip}...\""

    if any(k in q_lower for k in ["gap", "deficit", "weakness", "need", "skill"]):
        return (
            f"{greeting}\n\n"
            f"### Identified Competency Gaps\n"
            f"Based on your benchmark role requirements, here are your prioritized focus areas:\n"
            f"{chr(10).join(['• ' + g for g in top_gaps]) if top_gaps else 'You have met all required levels for your current role!'}\n\n"
            f"### Recommended Learning Action\n"
            f"To bridge these deficits effectively, your top recommended courses are:\n"
            f"{courses_text}"
            f"{snippet_text}"
        )

    if any(k in q_lower for k in ["course", "recommend", "train", "learn", "study", "next"]):
        return (
            f"{greeting}\n\n"
            f"### Personalized Course Pathway\n"
            f"Based on your current skill gaps ({gaps_text}), the platform prioritizes these courses for you:\n\n"
            f"{courses_text}\n\n"
            f"Completing these will elevate your proficiency score and help close your role benchmark gaps."
            f"{snippet_text}"
        )

    # General inquiry or domain specific question
    domain_insights = ""
    if sources:
        domain_insights = (
            f"\n\n### Official Curriculum Guidance\n"
            f"According to verified learning modules in the repository:\n"
            f"{chr(10).join([f'- {s['text'][:180]}...' for s in sources[:2]])}"
        )

    return (
        f"{greeting}\n\n"
        f"Regarding your query on **\"{query}\"**:\n\n"
        f"In your capacity as {role}, mastering this relates directly to your target competencies: {gaps_text}.\n\n"
        f"### Next Steps to Upskill:\n"
        f"{courses_text}"
        f"{domain_insights}\n\n"
        f"Would you like me to recommend specific assessment modules or practice questions for this topic?"
    )


def process_chat_message(
    db: Session,
    user: User,
    message_text: str,
    session_id: Optional[uuid.UUID] = None,
) -> dict:
    """
    End-to-end RAG chat processor:
    1. Resolve or create ChatSession
    2. Retrieve employee profile & gaps
    3. Run vector similarity search over ContentChunks
    4. Synthesize grounded answer
    5. Save ChatMessages
    """
    clean_message = message_text.strip()
    if not clean_message:
        raise ValueError("Message cannot be empty.")

    # 1. Resolve Session
    if session_id:
        session = db.get(ChatSession, session_id)
        if not session or session.user_id != user.id:
            # Create fresh session if not found or unauthorized
            session = ChatSession(
                user_id=user.id,
                title=clean_message[:50] + ("..." if len(clean_message) > 50 else ""),
            )
            db.add(session)
            db.flush()
    else:
        session = ChatSession(
            user_id=user.id,
            title=clean_message[:50] + ("..." if len(clean_message) > 50 else ""),
        )
        db.add(session)
        db.flush()

    # 2. Retrieve Employee Context
    employee_context = get_employee_rag_context(db, user)

    # 3. Vector Similarity Search over uploaded ContentChunks
    raw_sources = []
    try:
        results = search_content(db, clean_message, limit=3)
        for r in results:
            raw_sources.append({
                "chunk_id": str(r.id),
                "text": str(r.chunk_text),
                "similarity": round(float(r.similarity), 4),
            })
    except Exception as exc:
        # Resilient fallback if no content chunks uploaded yet
        raw_sources = []

    # 4. Synthesize Grounded Response
    assistant_content = synthesize_rag_response(
        query=clean_message,
        context=employee_context,
        sources=raw_sources,
    )

    # 5. Save Messages
    user_msg = ChatMessage(
        session_id=session.id,
        user_id=user.id,
        role="user",
        content=clean_message,
    )
    assistant_msg = ChatMessage(
        session_id=session.id,
        user_id=user.id,
        role="assistant",
        content=assistant_content,
    )

    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)
    db.refresh(session)

    return {
        "session_id": session.id,
        "user_message": user_msg,
        "assistant_message": assistant_msg,
        "sources": raw_sources,
        "grounded_gaps": [g["name"] for g in employee_context["gaps"][:5]],
        "recommended_courses": [r["course_title"] for r in employee_context["recommendations"][:3]],
    }
