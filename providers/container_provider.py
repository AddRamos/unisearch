from ..core.models import FeatureRecord

def collect_container_features(features):
    """
    Build a reduced container index from existing feature records.

    Only one container is generated per unique operator module. RNA owners
    are deliberately omitted to keep the number of containers manageable.
    Modules are normalised to lower case to avoid duplicate entries like
    'Object' and 'object'.
    """
    containers = []
    seen_modules = set()

    for feature in features:
        if feature.feature_type == "OPERATOR":
            # normalise the module name (prefix before the first dot) to lower case
            module = feature.identifier.split(".", 1)[0].lower()
            if module not in seen_modules:
                seen_modules.add(module)
                container_id = f"container:module:{module}"
                label = module.replace("_", " ").title()
                containers.append(
                    FeatureRecord(
                        feature_id=container_id,
                        label=label,
                        identifier=module,
                        feature_type="CONTAINER",
                        description=f"Operator module: {module}",
                        source="CONTAINER",
                    )
                )
    return containers