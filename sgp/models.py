
from dataclasses import dataclass, field


@dataclass
class Member:
    id: int
    name: str
    username: str
    availability: dict = field(default_factory=dict)
    availability_completed: bool = False
    notification_preferences: list = field(default_factory=list)
    contact_info: dict = field(default_factory=dict)


@dataclass
class Group:
    id: int
    name: str
    members: list[Member] = field(default_factory=list)
    last_notified_meeting: tuple | None = None
