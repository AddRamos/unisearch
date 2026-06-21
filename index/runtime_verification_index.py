import bpy

from ..core.models import RuntimeVerificationRecord


class RuntimeVerificationIndex:

    def __init__(self):

        self.records = []

        self.by_feature_id = {}

        self.by_identifier = {}

        self.confirmed = 0

        self.partial = 0

        self.unverified = 0

    def build(
        self,
        features,
        resolved_location_index,
        location_index=None,
    ):

        self.records.clear()
        self.by_feature_id.clear()
        self.by_identifier.clear()
        self.confirmed = 0
        self.partial = 0
        self.unverified = 0

        feature_by_id = {
            feature.feature_id: feature
            for feature in features
        }

        for resolved in resolved_location_index.resolved:

            feature = feature_by_id.get(
                resolved.feature_id
            )

            if not feature:
                continue

            record = _verify_resolved_location(
                feature,
                resolved,
                location_index,
            )

            self._add_record(record)

        print("\n")
        print("=" * 60)
        print("UNISEARCH RUNTIME VERIFICATION")
        print("=" * 60)
        print("RUNTIME RECORDS:", len(self.records))
        print("CONFIRMED:", self.confirmed)
        print("PARTIAL:", self.partial)
        print("UNVERIFIED:", self.unverified)
        print("=" * 60)

    def inspect_identifier(self, identifier):

        return self.by_identifier.get(
            identifier,
            [],
        )

    def inspect_status(
        self,
        status,
        limit=50,
    ):

        status = status.upper()

        return [
            record
            for record in self.records
            if record.status == status
        ][:limit]

    def _add_record(self, record):

        self.records.append(record)

        self.by_feature_id.setdefault(
            record.feature_id,
            [],
        ).append(record)

        self.by_identifier.setdefault(
            record.feature_identifier,
            [],
        ).append(record)

        if record.status == "CONFIRMED":
            self.confirmed += 1
        elif record.status == "UNVERIFIED":
            self.unverified += 1
        else:
            self.partial += 1


def _verify_resolved_location(
    feature,
    resolved,
    location_index,
):

    feature_verified, feature_detail = _verify_feature(
        feature
    )

    container_verified, container_detail = _verify_container(
        resolved,
        location_index,
    )

    status = _status(
        feature_verified,
        container_verified,
    )

    detail = "; ".join(
        part
        for part in (
            feature_detail,
            container_detail,
        )
        if part
    )

    return RuntimeVerificationRecord(
        feature_id=feature.feature_id,
        feature_identifier=feature.identifier,
        container_id=resolved.container_id,
        status=status,
        feature_verified=feature_verified,
        container_verified=container_verified,
        detail=detail,
    )


def _verify_feature(feature):

    if feature.feature_type == "OPERATOR":
        return _verify_operator(feature.identifier)

    if feature.feature_type == "RNA_PROPERTY":
        return _verify_rna_property(feature)

    if feature.feature_type == "ADDON_PREFERENCE":
        return _verify_addon_preference(feature)

    if feature.feature_type == "CONTAINER":
        return True, "container feature"

    return False, f"unsupported feature type {feature.feature_type}"


def _verify_operator(identifier):

    parts = identifier.split(
        ".",
        1,
    )

    if len(parts) != 2:
        return False, "operator id is not category.name"

    category_name, operator_name = parts

    try:
        category = getattr(
            bpy.ops,
            category_name,
        )
        getattr(
            category,
            operator_name,
        )
    except Exception:
        return False, "operator not found in bpy.ops"

    return True, "operator found in bpy.ops"


def _verify_rna_property(feature):

    for owner_name in feature.owners:

        try:
            owner = getattr(
                bpy.types,
                owner_name,
            )
        except Exception:
            continue

        rna = getattr(
            owner,
            "bl_rna",
            None,
        )

        properties = getattr(
            rna,
            "properties",
            None,
        )

        if properties is None:
            continue

        if feature.identifier in properties:
            return (
                True,
                f"RNA property found on {owner_name}",
            )

    return False, "RNA property not found on recorded owners"


def _verify_addon_preference(feature):

    parts = feature.feature_id.split(
        ":",
        2,
    )

    if len(parts) != 3:
        return False, "addon preference feature id is malformed"

    addon_id = parts[1]
    property_name = parts[2]

    addon = bpy.context.preferences.addons.get(
        addon_id
    )

    if addon is None:
        return False, f"addon {addon_id} is not enabled"

    preferences = getattr(
        addon,
        "preferences",
        None,
    )

    if preferences is None:
        return False, f"addon {addon_id} has no preferences instance"

    if hasattr(
        preferences,
        property_name,
    ):
        return True, f"addon preference {property_name} found"

    return False, f"addon preference {property_name} not found"


def _verify_container(
    resolved,
    location_index,
):

    if resolved.container_type == "COMMAND":
        return True, "command fallback container"

    if resolved.container_type == "ADDON_PREFERENCES":
        return _verify_addon_preferences_container(
            resolved.container_id
        )

    try:
        getattr(
            bpy.types,
            resolved.container_id,
        )
    except Exception:
        if _container_was_scanned(
            resolved.container_id,
            location_index,
        ):
            return (
                True,
                "UI container found in static scan registry",
            )

        return False, "UI container class not found in bpy.types"

    return True, "UI container class found in bpy.types"


def _container_was_scanned(
    container_id,
    location_index,
):

    if location_index is None:
        return False

    return container_id in location_index.containers


def _verify_addon_preferences_container(container_id):

    prefix = "ADDON_PREFS:"

    if not container_id.startswith(prefix):
        return False, "addon preferences container id is malformed"

    addon_id = container_id[len(prefix):]

    addon = bpy.context.preferences.addons.get(
        addon_id
    )

    if addon is None:
        return False, f"addon {addon_id} is not enabled"

    if getattr(
        addon,
        "preferences",
        None,
    ) is None:
        return False, f"addon {addon_id} has no preferences instance"

    return True, f"addon preferences container {addon_id} found"


def _status(
    feature_verified,
    container_verified,
):

    if feature_verified and container_verified:
        return "CONFIRMED"

    if feature_verified or container_verified:
        return "PARTIAL"

    return "UNVERIFIED"
