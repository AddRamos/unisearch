from typing import Dict, Iterable, List, Set
from ..core.models import FeatureRecord


class TokenIndex:
    """
    A simple token-based inverted index for FeatureRecord objects.

    It indexes tokens extracted from feature labels, identifiers and aliases,
    enabling fast lookup of features containing a given token.
    """

    def __init__(self) -> None:
        self.token_to_ids: Dict[str, Set[str]] = {}
        self.feature_map: Dict[str, FeatureRecord] = {}

    def build(self, features: Iterable[FeatureRecord]) -> None:
        """
        Build the token index from an iterable of FeatureRecord instances.
        """
        self.token_to_ids.clear()
        self.feature_map.clear()

        for feature in features:
            # Save the feature for reverse lookup
            self.feature_map[feature.feature_id] = feature
            tokens = self.extract_tokens(feature)
            for token in tokens:
                ids = self.token_to_ids.setdefault(token, set())
                ids.add(feature.feature_id)

    def extract_tokens(self, feature: FeatureRecord) -> List[str]:
        """
        Extract normalized tokens from a feature's label, identifier and aliases.
        Tokens are lower‑cased and split on spaces, dots and underscores.
        """
        tokens: List[str] = []

        text_parts = [
            feature.label,
            feature.identifier,
        ]

        # Include any aliases the feature might have
        text_parts.extend(feature.aliases)

        for text in text_parts:
            normalized = (
                text.lower()
                .replace(".", " ")
                .replace("_", " ")
            )
            tokens.extend(normalized.split())

        return tokens

    def ids_for_query(self, query: str) -> Set[str]:
        """
        Return feature IDs whose tokens match all words in the query.
        Supports multi‑word queries; all tokens must be present.
        """
        normalized = (
            query.lower()
            .strip()
            .replace(".", " ")
            .replace("_", " ")
        )
        query_tokens = normalized.split()

        if not query_tokens:
            return set()

        matched_ids = None
        for token in query_tokens:
            token_ids = self.token_to_ids.get(token, set())
            if matched_ids is None:
                matched_ids = set(token_ids)
            else:
                matched_ids &= token_ids
            if not matched_ids:
                return set()

        return matched_ids or set()