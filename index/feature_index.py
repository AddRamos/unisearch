from ..providers.rna_provider import (
    collect_rna_features,
)

from ..providers.operator_provider import (
    collect_operator_features,
)


class FeatureIndex:

    def __init__(self):

        self.features = []

        self.by_id = {}

    def rebuild(self):

        self.features.clear()
        self.by_id.clear()

        rna_features = collect_rna_features()

        operator_features = collect_operator_features()

        #
        # NEW DEBUG SECTION
        #

        unique_identifiers = {
            feature.identifier
            for feature in rna_features
        }

        unique_labels = {
            feature.label
            for feature in rna_features
        }

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

        #
        # EXISTING BUILD
        #

        all_features = []

        all_features.extend(rna_features)

        all_features.extend(operator_features)

        for feature in all_features:

            self.features.append(feature)

            self.by_id[
                feature.feature_id
            ] = feature

    def search(self, query):

        query = query.lower().strip()

        if not query:
            return []

        results = []

        for feature in self.features:

            label = feature.label.lower()

            identifier = (
                feature.identifier.lower()
            )

            description = (
                feature.description.lower()
            )

            if (
                query in label
                or query in identifier
            ):
                results.append(feature)

        return results