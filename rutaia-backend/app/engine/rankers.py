# app/engine/rankers.py

from typing import List
from app.engine.models import GenerationContext, ScoredItem
from abc import ABC, abstractmethod

class BaseScorer(ABC):
    @abstractmethod
    def score(self, items: List[ScoredItem], context: GenerationContext) -> List[ScoredItem]:
        pass

class PreferenceScorer(BaseScorer):
    """
    Adds weight to items that match user preference tags.
    """
    def __init__(self, user_tags: List[str]):
        self.user_tags = set(user_tags)

    def score(self, items: List[ScoredItem], context: GenerationContext) -> List[ScoredItem]:
        for item in items:
            item_tags = set(item.metadata.get("tags", []))
            matches = len(self.user_tags.intersection(item_tags))
            item.score += matches * 2.0  # Weight per match
        return items

class PopularityScorer(BaseScorer):
    """
    Adds weight based on item rating or popularity.
    """
    def score(self, items: List[ScoredItem], context: GenerationContext) -> List[ScoredItem]:
        for item in items:
            rating = item.metadata.get("rating", 0.0)
            item.score += rating * 1.5
        return items

class DiversityScorer(BaseScorer):
    """
    Penalizes items whose categories are already over-represented in the current day/queue.
    """
    def __init__(self, current_categories: List[str]):
        self.current_categories = current_categories

    def score(self, items: List[ScoredItem], context: GenerationContext) -> List[ScoredItem]:
        for item in items:
            cat = item.metadata.get("category")
            if cat in self.current_categories:
                count = self.current_categories.count(cat)
                item.score -= count * 3.0  # Penalty per repetition
        return items

class ScoringPipeline:
    def __init__(self, scorers: List[BaseScorer]):
        self.scorers = scorers

    def run(self, items: List[ScoredItem], context: GenerationContext) -> List[ScoredItem]:
        for scorer in self.scorers:
            items = scorer.score(items, context)
        # Final sort by score
        return sorted(items, key=lambda x: x.score, reverse=True)
