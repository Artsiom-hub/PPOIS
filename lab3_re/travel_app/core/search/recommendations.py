from typing import Dict, List

from core.geography.destinations import Destination
from core.users.models import Customer


class RecommendationEngine:
    """Рекомендации на основе истории путешествий клиента."""

    def __init__(self):
        # customer_id -> List[Destination]
        self.history: Dict[str, List[Destination]] = {}

    def add_history(self, customer: Customer, destination: Destination) -> None:
        """Добавляет посещённую или просмотренную точку назначения в историю пользователя."""
        self.history.setdefault(customer.user_id, []).append(destination)

    def recommend(self, customer: Customer, all_destinations: List[Destination]) -> List[Destination]:
        """Рекомендации строятся по совпадению тегов с ранее посещёнными направлениями."""

        seen = self.history.get(customer.user_id, [])
        seen_tags = {t for d in seen for t in d.tags}

        scored = []
        for dest in all_destinations:
            score = len(seen_tags.intersection(dest.tags))
            scored.append((score, dest))

        # сортируем по количеству совпадений тегов
        scored.sort(key=lambda x: x[0], reverse=True)

        # возвращаем только те, у которых score > 0
        return [d for score, d in scored if score > 0]
