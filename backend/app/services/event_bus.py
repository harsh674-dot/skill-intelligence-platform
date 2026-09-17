import uuid
import json
import logging
import os
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class EventBus:
    """
    Event Bus (Section 2):
    Event-driven backbone for system events.

    Uses file-based persistence for durability across restarts.
    In production this connects to Kafka or RabbitMQ.
    """

    def __init__(self, persist_path: str = None):
        self._handlers: dict[str, list[callable]] = {}
        self._event_log: list[dict] = []
        self._persist_path = persist_path or os.environ.get(
            "EVENT_BUS_DB",
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "event_bus.json"),
        )
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load persisted events from disk."""
        try:
            if os.path.exists(self._persist_path):
                with open(self._persist_path, "r", encoding="utf-8") as f:
                    self._event_log = json.load(f)
                logger.info(f"Loaded {len(self._event_log)} events from {self._persist_path}")
        except Exception as exc:
            logger.warning(f"Failed to load event bus persistence: {exc}")
            self._event_log = []

    def _save_to_disk(self) -> None:
        """Persist events to disk."""
        try:
            dir_path = os.path.dirname(self._persist_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._event_log, f, default=str)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self._persist_path)
        except Exception as exc:
            logger.warning(f"Failed to persist event bus: {exc}")

    def subscribe(self, event_type: str, handler: callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to event: {event_type}")

    def publish(self, event_type: str, data: dict) -> dict:
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._event_log.append(event)
        self._save_to_disk()
        logger.info(f"Published event: {event_type}")

        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                logger.error(f"Event handler error for {event_type}: {exc}")

        return event

    def get_events(self, event_type: Optional[str] = None, limit: int = 100) -> list[dict]:
        events = self._event_log
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[-limit:]

    def get_event_count(self) -> int:
        return len(self._event_log)

    def clear(self) -> None:
        """Clear all persisted events."""
        self._event_log = []
        try:
            if os.path.exists(self._persist_path):
                os.remove(self._persist_path)
        except Exception:
            pass


event_bus = EventBus()


def publish_competency_update(user_id: str, competency_id: str, new_level: int) -> dict:
    """Publish a competency level update event."""
    return event_bus.publish("competency.updated", {
        "user_id": user_id,
        "competency_id": competency_id,
        "new_level": new_level,
    })


def publish_course_completion(user_id: str, course_id: str, score: float) -> dict:
    """Publish a course completion event."""
    return event_bus.publish("course.completed", {
        "user_id": user_id,
        "course_id": course_id,
        "score": score,
    })


def publish_recommendation(user_id: str, course_id: str, priority_score: float) -> dict:
    """Publish a recommendation event."""
    return event_bus.publish("recommendation.generated", {
        "user_id": user_id,
        "course_id": course_id,
        "priority_score": priority_score,
    })