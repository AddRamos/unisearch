from ..providers.rna_provider import collect_rna_features
from ..providers.operator_provider import collect_operator_features
from ..providers.container_provider import collect_container_features
from .token_index import TokenIndex


ALIASES = {
    "delete": ["remove", "erase"],
    "save": ["write file", "store"],
    "cavity": ["ambient occlusion", "viewport cavity"],
}


SYNONYM_TO_CANONICAL = {}

for canonical, synonyms in ALIASES.items():
    for phrase in synonyms:
        tokens = (
            phrase.lower()
            .replace(".", " ")
            .replace("_", " ")
            .split()
        )

        for token in tokens:
            SYNONYM_TO_CANONICAL.setdefault(
                token,
                canonical,
            )


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

        base_features = []

        base_features.extend(rna_features)

        base_features.extend(operator_features)

        container_features = collect_container_features(
            base_features
        )

        all_features = []

        all_features.extend(base_features)

        all_features.extend(container_features)

        print("\n")
        print("=" * 60)
        print("UNISEARCH FEATURE BUILD")
        print("=" * 60)
        print("NORMALIZED RNA FEATURES:", len(rna_features))
        print("OPERATOR FEATURES:", len(operator_features))
        print("CONTAINER FEATURES:", len(container_features))
        print("TOTAL SEARCHABLE FEATURES:", len(all_features))
        print("=" * 60)

        for feature in all_features:

            self.features.append(feature)

            self.by_id[
                feature.feature_id
            ] = feature

        self.token_index.build(self.features)

    def search(self, query):

        q = query.lower().strip()

        if not q:
            return []

        raw_tokens = (
            q.replace(".", " ")
            .replace("_", " ")
            .split()
        )

        if not raw_tokens:
            return []

        candidate_ids = None

        for token in raw_tokens:

            token_variants = self._expand_token(token)

            union_ids = set()

            for token_variant in token_variants:

                union_ids.update(
                    self.token_index.token_to_ids.get(
                        token_variant,
                        set(),
                    )
                )

            if candidate_ids is None:
                candidate_ids = union_ids
            else:
                candidate_ids &= union_ids

            if not candidate_ids:
                return []

        ranked_results = []

        for feature in self.features:

            if feature.feature_id not in candidate_ids:
                continue

            score = self._score_feature(
                feature,
                q,
                raw_tokens,
            )

            if score > 0:
                ranked_results.append(
                    (
                        score,
                        feature.label.lower(),
                        feature.identifier.lower(),
                        feature,
                    )
                )

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

    def _expand_token(self, token):

        expanded = [token]

        canonical = SYNONYM_TO_CANONICAL.get(token)

        if canonical:
            expanded.append(canonical)

        return expanded

    def _score_feature(
        self,
        feature,
        query,
        raw_tokens,
    ):

        label = feature.label.lower()

        identifier = feature.identifier.lower()

        feature_tokens = (
            label.replace(".", " ")
            .replace("_", " ")
            .split()
        )

        feature_tokens.extend(
            identifier.replace(".", " ")
            .replace("_", " ")
            .split()
        )

        for alias in feature.aliases:
            feature_tokens.extend(
                alias.lower()
                .replace(".", " ")
                .replace("_", " ")
                .split()
            )

        if label == query:
            return 100

        if identifier == query:
            return 95

        for token in raw_tokens:

            for expanded_token in self._expand_token(token):

                if expanded_token in feature_tokens:
                    return 90

        if label.startswith(query):
            return 80

        if (
            query in label
            or query in identifier
        ):
            return 60

        return 0