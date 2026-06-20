from ..providers.rna_provider import (
    collect_rna_features,
)

from ..providers.operator_provider import (
    collect_operator_features,
)

from .token_index import TokenIndex


class FeatureIndex:

    def __init__(self):

        self.features = []

        self.by_id = {}

        # Token index for fast matching
        self.token_index = TokenIndex()

    def rebuild(self):

        self.features.clear()
        self.by_id.clear()

        rna_features = collect_rna_features()

        operator_features = collect_operator_features()

        print("\n")
        print("=" * 60)
        print("UNISEARCH FEATURE BUILD")
        print("=" * 60)

        print(
            "NORMALIZED RNA FEATURES:",
            len(rna_features)
        )

        print(
            "OPERATOR FEATURES:",
            len(operator_features)
        )

        print(
            "TOTAL SEARCHABLE FEATURES:",
            (
                len(rna_features)
                +
                len(operator_features)
            )
        )

        print("=" * 60)

        all_features = []

        all_features.extend(rna_features)

        all_features.extend(operator_features)

        for feature in all_features:

            self.features.append(feature)

            self.by_id[
                feature.feature_id
            ] = feature

        # Build the token index using the full feature list
        self.token_index.build(self.features)

    def search(self, query: str):
        """
        Search for features matching the given query and return them ordered by relevance.

        Matching categories (highest to lowest priority):
        1. Exact label match
        2. Exact identifier match
        3. Token match on identifier or label (via the token index)
        4. Label starts with the query
        5. Query contained anywhere in the label or identifier
        """
        q = query.lower().strip()
        if not q:
            return []

        # Candidate IDs based on token matches
        token_candidate_ids = self.token_index.ids_for_query(q)

        ranked_results = []

        for feature in self.features:

            score = self._score_feature(
                feature,
                q,
                token_candidate_ids,
            )

            if score > 0:
                # Store score, label, identifier to ensure deterministic sorting
                ranked_results.append(
                    (
                        score,
                        feature.label.lower(),
                        feature.identifier.lower(),
                        feature,
                    )
                )

        # Sort by score descending, then by label and identifier for consistent ordering
        ranked_results.sort(
            key=lambda item: (
                -item[0],
                item[1],
                item[2],
            )
        )

        return [
            item[3]
            for item in ranked_results
        ]

    def _score_feature(
        self,
        feature,
        query,
        token_candidate_ids,
    ):
        """
        Assign a numeric score to a feature for a given query.
        """
        label = feature.label.lower()
        identifier = feature.identifier.lower()

        if label == query:
            return 100

        if identifier == query:
            return 95

        if feature.feature_id in token_candidate_ids:
            return 90

        if label.startswith(query):
            return 80

        if (
            query in label
            or query in identifier
        ):
            return 60

        return 0