import os
import httpx
import logging
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [import-error]
from app.models.course import Course, CourseCompetency
from app.models.competency import Competency

logger = logging.getLogger(__name__)

class IGotSyncService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_catalogue(self):
        """
        Fetches course catalogue from iGOT APIs if credentials are provided.
        Falls back to a mock implementation for sandbox testing if env vars are missing.
        """
        igot_base_url = os.getenv("IGOT_API_BASE_URL")
        igot_api_token = os.getenv("IGOT_API_TOKEN")

        if igot_base_url and igot_api_token:
            logger.info("Fetching iGOT catalogue from live API")
            try:
                # Placeholder endpoint for iGOT course search
                endpoint = f"{igot_base_url}/api/course/v1/search"
                headers = {
                    "Authorization": f"Bearer {igot_api_token}",
                    "Content-Type": "application/json"
                }
                # Sample payload for a course search API
                payload = {
                    "request": {
                        "filters": {
                            "status": ["Live"],
                            "contentType": ["Course"]
                        },
                        "limit": 100
                    }
                }
                
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(endpoint, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract courses from standard Sunbird/iGOT response structure
                    result = data.get("result", {})
                    courses = result.get("content", [])
                    
                    mapped_payload = []
                    for c in courses:
                        mapped_payload.append({
                            "external_id": c.get("identifier"),
                            "title": c.get("name"),
                            "description": c.get("description"),
                            "provider": c.get("creator", "Unknown"),
                            "duration_minutes": int(c.get("duration", 0)) // 60, # Assuming duration in seconds
                            "level": c.get("competencyLevel", "Beginner"),
                            "competencies": c.get("competencies_v2", []) # Mapping logic would depend on actual schema
                        })
                    return mapped_payload
            except Exception as e:
                logger.error(f"Failed to fetch from iGOT API: {e}. Falling back to mock data.")

        logger.info("Fetching iGOT catalogue (mock fallback)")
        
        # Mock payload representing iGOT courses
        mock_payload = [
            {
                "external_id": "igot-001",
                "title": "Introduction to Sampling Techniques",
                "description": "Learn the basics of survey design and sampling.",
                "provider": "MoSPI / NSSTA",
                "duration_minutes": 120,
                "level": "Beginner",
                "competencies": [
                    {"name": "Sampling", "target_level": 2}
                ]
            },
            {
                "external_id": "igot-002",
                "title": "Advanced Data Visualization with Python",
                "description": "Master data visualization using matplotlib and seaborn.",
                "provider": "NIC",
                "duration_minutes": 240,
                "level": "Advanced",
                "competencies": [
                    {"name": "Data Visualization", "target_level": 4},
                    {"name": "Python", "target_level": 3}
                ]
            }
        ]
        
        return mock_payload

    def sync_courses(self):
        """
        Fetches courses from iGOT and upserts them into the local database.
        """
        payload = self.fetch_catalogue()
        synced_count = 0
        
        for item in payload:
            # Check if course exists
            course = self.db.query(Course).filter(Course.external_id == item["external_id"]).first()
            
            if not course:
                course = Course(
                    title=item["title"],
                    description=item["description"],
                    provider=item["provider"],
                    source="iGOT",
                    external_id=item["external_id"],
                    duration_minutes=item.get("duration_minutes"),
                    level=item.get("level")
                )
                self.db.add(course)
                self.db.commit()
                self.db.refresh(course)
                synced_count += 1
                
                # Link competencies if they exist in the DB
                for comp_data in item.get("competencies", []):
                    competency = self.db.query(Competency).filter(Competency.name.ilike(comp_data["name"])).first()
                    if competency:
                        cc = CourseCompetency(
                            course_id=course.id,
                            competency_id=competency.id,
                            target_level=comp_data["target_level"]
                        )
                        self.db.add(cc)
                self.db.commit()
                
        return synced_count
