from ..core.models import FeatureRecord


def collect_container_features(features):

    containers = []

    seen_operator_modules = set()
    seen_rna_owners = set()

    for feature in features:

        if feature.feature_type == "OPERATOR":

            module = feature.identifier.split(".")[0]

            if module not in seen_operator_modules:

                seen_operator_modules.add(module)

                containers.append(
                    FeatureRecord(
                        feature_id=f"container:operator_module:{module}",
                        label=module.replace("_", " ").title(),
                        identifier=module,
                        feature_type="CONTAINER",
                        description=f"Operator category: {module}",
                        source="CONTAINER",
                    )
                )

        if feature.feature_type == "RNA_PROPERTY":

            for owner in feature.owners:

                if owner not in seen_rna_owners:

                    seen_rna_owners.add(owner)

                    containers.append(
                        FeatureRecord(
                            feature_id=f"container:rna_owner:{owner}",
                            label=owner,
                            identifier=owner,
                            feature_type="CONTAINER",
                            description=f"RNA owner type: {owner}",
                            source="CONTAINER",
                        )
                    )

    return containers