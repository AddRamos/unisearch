from ..providers.rna_provider import collect_rna_features
from ..providers.operator_provider import collect_operator_features
from .token_index import TokenIndex

# ------------------------------------------------------------------------
# Alias dictionary (Stage 3)
# ------------------------------------------------------------------------
ALIASES = {
    "delete": ["remove", "erase"],
    "save": ["write file", "store"],
    "cavity": ["ambient occlusion", "viewport cavity"],
}
# Reverse lookup: each synonym token maps back to its canonical term
SYNONYM_TO_CANONICAL = {}
for canonical, synonyms in ALIASES.items():
    for phrase in synonyms:
        for token in (
            phrase.lower()
            .replace(".", " ")
            .replace("_", " ")
            .split()
        ):
            SYNONYM_TO_CANONICAL.setdefault(token, canonical)


class FeatureIndex:
    def __init__(self):
        self.features = []
        self.by_id = {}
        self.token_index = TokenIndex()

    def rebuild(self):
        self.features.clear()
        self.by_id.clear()

        rna_features = collect_rna_features()
        operator_features = collect_operator_features()

        print("\n" + "=" * 60)
        print("UNISEARCH FEATURE BUILD")
        print("=" * 60)
        print("NORMALIZED RNA FEATURES:", len(rna_features))
        print("OPERATOR FEATURES:", len(operator_features))
        print("TOTAL SEARCHABLE FEATURES:", len(rna_features) + len(operator_features))
        print("=" * 60)

        all_features = list(rna_features) + list(operator_features)
        for feature in all_features:
            self.features.append(feature)
            self.by_id[feature.feature_id] = feature

        self.token_index.build(self.features)

    def _expand_token(self, token: str) -> list[str]:
        """Return [token] + [canonical] if the token is a known synonym."""
        expanded = [token]
        canonical = SYNONYM_TO_CANONICAL.get(token)
        if canonical:
            expanded.append(canonical)
        return expanded

    def search(self, query: str):
        """
        Search for features matching the query.  Expand query tokens using aliases
        both for candidate selection and for scoring, so that synonyms like
        'remove' or 'write file' map back to their canonical terms.
        """
        q = query.lower().strip()
        if not q:
            return []

        # Break the query into raw tokens (dot/underscore separated)
        raw_tokens = q.replace(".", " ").replace("_", " ").split()
        if not raw_tokens:
            return []

        # Build candidate IDs with AND semantics, expanding each token via the alias map
        candidate_ids = None
        for token in raw_tokens:
            token_variants = self._expand_token(token)
            union_ids = set()
            for t in token_variants:
                union_ids |= self.token_index.token_to_ids.get(t, set())
            if candidate_ids is None:
                candidate_ids = union_ids
            else:
                candidate_ids &= union_ids
            if not candidate_ids:
                break

        if not candidate_ids:
            return []

        # Score candidates based on exact, identifier, token, prefix, contains
        ranked_results = []
        for feature in self.features:
            if feature.feature_id not in candidate_ids:
                continue
            score = self._score_feature(feature, q, raw_tokens)
            if score > 0:
                ranked_results.append(
                    (score, feature.label.lower(), feature.identifier.lower(), feature)
                )

        ranked_results.sort(key=lambda item: (-item[0], item[1], item[2]))
        return [item[3] for item in ranked_results]

    def _score_feature(self, feature, query_str: str, raw_tokens: list[str]) -> int:
        """
        Assign a score to a feature.  Alias matches (synonyms of the query tokens)
        are treated as token matches, ensuring that queries like 'erase' or
        'write file' hit their corresponding canonical tokens ('delete', 'save').
        """
        label = feature.label.lower()
        identifier = feature.identifier.lower()

        # Exact label or identifier match
        if label == query_str:
            return 100
        if identifier == query_str:
            return 95

        # Gather all tokens from the feature's label, identifier and aliases
        feature_tokens = (
            label.replace(".", " ").replace("_", " ").split()
            + identifier.replace(".", " ").replace("_", " ").split()
            + [a.lower() for a in feature.aliases]
        )

        # Check for token match (including synonym expansions)
        for token in raw_tokens:
            # The token itself and its canonical alias, if any
            variants = self._expand_token(token)
            for var in variants:
                if var in feature_tokens:
                    return 90

        # Prefix match on label
        if label.startswith(query_str):
            return 80

        # Substring match in label or identifier
        if query_str in label or query_str in identifier:
            return 60

        return 0