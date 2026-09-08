from app.adapters.learning_adapter import LearningAdapter


class MockLearningAdapter(LearningAdapter):
    """
    Mock learning provider used for the SIH MVP.

    This follows the same interface that a real
    iGOT or TPAC adapter can implement later.
    """

    def get_courses(self) -> list[dict]:
        return [
            {
                "title": "Python for Data Analysis",
                "provider": "Internal Training",
                "source": "mock",
                "external_id": "PYTHON-001",
                "url": "https://example.com/python-data-analysis",
                "duration_minutes": 240,
                "level": "beginner",
                "competencies": {
                    "Python": 3,
                },
            },
            {
                "title": "Advanced Python for Data Science",
                "provider": "Internal Training",
                "source": "mock",
                "external_id": "PYTHON-002",
                "url": "https://example.com/advanced-python",
                "duration_minutes": 360,
                "level": "advanced",
                "competencies": {
                    "Python": 5,
                    "Data Visualization": 3,
                },
            },
            {
                "title": "SQL Fundamentals",
                "provider": "Internal Training",
                "source": "mock",
                "external_id": "SQL-001",
                "url": "https://example.com/sql-fundamentals",
                "duration_minutes": 180,
                "level": "beginner",
                "competencies": {
                    "SQL": 3,
                },
            },
            {
                "title": "Advanced SQL and Analytics",
                "provider": "Internal Training",
                "source": "mock",
                "external_id": "SQL-002",
                "url": "https://example.com/advanced-sql",
                "duration_minutes": 300,
                "level": "advanced",
                "competencies": {
                    "SQL": 5,
                    "Data Quality": 4,
                },
            },
            {
                "title": "Statistical Methods for Official Statistics",
                "provider": "NSSTA Mock Catalogue",
                "source": "mock",
                "external_id": "STAT-001",
                "url": "https://example.com/statistical-methods",
                "duration_minutes": 360,
                "level": "intermediate",
                "competencies": {
                    "Statistical Analysis": 4,
                    "Data Quality": 4,
                },
            },
            {
                "title": "Survey Sampling Techniques",
                "provider": "NSSTA Mock Catalogue",
                "source": "mock",
                "external_id": "STAT-002",
                "url": "https://example.com/sampling",
                "duration_minutes": 300,
                "level": "advanced",
                "competencies": {
                    "Sampling": 4,
                    "Survey Design": 4,
                },
            },
            {
                "title": "Survey Design Fundamentals",
                "provider": "NSSTA Mock Catalogue",
                "source": "mock",
                "external_id": "STAT-003",
                "url": "https://example.com/survey-design",
                "duration_minutes": 240,
                "level": "intermediate",
                "competencies": {
                    "Survey Design": 4,
                },
            },
            {
                "title": "Data Visualization and Storytelling",
                "provider": "Internal Training",
                "source": "mock",
                "external_id": "VIZ-001",
                "url": "https://example.com/data-visualization",
                "duration_minutes": 240,
                "level": "intermediate",
                "competencies": {
                    "Data Visualization": 4,
                    "Communication": 4,
                },
            },
            {
                "title": "Machine Learning Fundamentals",
                "provider": "Internal Training",
                "source": "mock",
                "external_id": "ML-001",
                "url": "https://example.com/ml-fundamentals",
                "duration_minutes": 360,
                "level": "intermediate",
                "competencies": {
                    "Machine Learning": 3,
                    "Python": 3,
                },
            },
            {
                "title": "Cybersecurity for Government Systems",
                "provider": "Government Training",
                "source": "mock",
                "external_id": "SEC-001",
                "url": "https://example.com/cybersecurity",
                "duration_minutes": 240,
                "level": "intermediate",
                "competencies": {
                    "Cybersecurity": 4,
                    "Data Privacy": 4,
                },
            },
        ]