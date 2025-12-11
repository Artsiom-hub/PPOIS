from dataclasses import dataclass, field
from typing import Dict


@dataclass
class LoyaltyProgram:
    name: str
    levels: Dict[str, int] = field(default_factory=dict)   # level_name → required_points
    base_multiplier: float = 1.0

    def add_level(self, level_name: str, required_points: int) -> None:
        """Добавляет уровень лояльности (например, SILVER, GOLD)."""
        self.levels[level_name] = required_points

    def level_for_points(self, points: int) -> str:
        """Определяет текущий уровень исходя из количества очков."""
        available = [lvl for lvl, req in self.levels.items() if points >= req]
        return max(available, key=lambda l: self.levels[l]) if available else "NONE"
    def points_multiplier(self, level_name: str) -> float:
        """Возвращает множитель очков для данного уровня."""
        level_multipliers = {
            "NONE": 1.0,
            "SILVER": 1.2,
            "GOLD": 1.5,
            "PLATINUM": 2.0
        }
        return level_multipliers.get(level_name, 1.0)