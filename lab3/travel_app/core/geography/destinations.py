from dataclasses import dataclass, field
from typing import List

from core.geography.locations import City


@dataclass
class Destination:
    code: str
    city: City
    description: str
    tags: List[str] = field(default_factory=list)

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags
