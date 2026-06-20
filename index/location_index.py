from ..core.models import LocationCandidate
from ..providers.static_ui_provider import (
    collect_static_ui_calls,
)


class LocationIndex:

    def __init__(self):

        self.locations = []

        self.by_feature_id = {}

        self.by_identifier = {}

        self.by_container_id = {}

        self.containers = {}

        self.unmatched = []

        self.scan_stats = None

        self.matched_calls = 0

        self.unmatched_calls = 0

    def build(self, features):

        self.locations.clear()
        self.by_feature_id.clear()
        self.by_identifier.clear()
        self.by_container_id.clear()
        self.containers.clear()
        self.unmatched.clear()

        self.matched_calls = 0
        self.unmatched_calls = 0

        feature_maps = _build_feature_maps(features)

        scan_result = collect_static_ui_calls()

        self.scan_stats = scan_result
        self.containers.update(scan_result.containers)

        for call in scan_result.calls:

            matched_features = _match_call(
                call,
                feature_maps,
            )

            if not matched_features:
                self.unmatched_calls += 1
                self.unmatched.append(call)
                continue

            self.matched_calls += 1

            for feature, confidence in matched_features:

                location = LocationCandidate(
                    feature_id=feature.feature_id,
                    feature_identifier=feature.identifier,
                    container_id=call.container_id,
                    container_type=call.container_type,
                    source_file=call.source_file,
                    line_number=call.line_number,
                    confidence=confidence,
                    ui_call=call.ui_call,
                    source_kind=call.source_kind,
                    addon_module=call.addon_module,
                    container_label=call.container_label,
                    bl_space_type=call.bl_space_type,
                    bl_region_type=call.bl_region_type,
                    bl_category=call.bl_category,
                )

                self._add_location(location)

        self._print_build_report(scan_result)

    def inspect_identifier(self, identifier):

        return self.by_identifier.get(
            identifier,
            [],
        )

    def inspect_container(self, container_id):

        return self.by_container_id.get(
            container_id,
            [],
        )

    def inspect_unmatched(self, limit=50):

        return self.unmatched[:limit]

    def _add_location(self, location):

        self.locations.append(location)

        self.by_feature_id.setdefault(
            location.feature_id,
            [],
        ).append(location)

        self.by_identifier.setdefault(
            location.feature_identifier,
            [],
        ).append(location)

        self.by_container_id.setdefault(
            location.container_id,
            [],
        ).append(location)

    def _print_build_report(self, scan_result):

        print("\n")
        print("=" * 60)
        print("UNISEARCH STATIC UI LOCATION BUILD")
        print("=" * 60)
        print("STATIC UI FILES SCANNED:", scan_result.files_scanned)
        print("CORE UI FILES SCANNED:", scan_result.core_files_scanned)
        print("ADDON UI FILES SCANNED:", scan_result.addon_files_scanned)
        print(
            "UI CONTAINERS DISCOVERED:",
            scan_result.containers_discovered,
        )

        for call_name in sorted(scan_result.call_counts):
            print(
                f"LAYOUT {call_name.upper()} CALLS:",
                scan_result.call_counts[call_name],
            )

        print("LOCATION CANDIDATES:", len(self.locations))
        print("MATCHED UI CALLS:", self.matched_calls)
        print("UNMATCHED UI CALLS:", self.unmatched_calls)
        print("=" * 60)


def _build_feature_maps(features):

    by_feature_id = {}
    by_identifier = {}
    by_operator_id = {}
    by_container_id = {}

    for feature in features:

        by_feature_id[feature.feature_id] = feature

        by_identifier.setdefault(
            feature.identifier,
            [],
        ).append(feature)

        if feature.feature_type == "OPERATOR":
            by_operator_id[feature.identifier] = feature

        if feature.feature_type == "CONTAINER":
            by_container_id[feature.identifier] = feature

    return {
        "by_feature_id": by_feature_id,
        "by_identifier": by_identifier,
        "by_operator_id": by_operator_id,
        "by_container_id": by_container_id,
    }


def _match_call(call, feature_maps):

    if call.ui_call in {
        "operator",
        "operator_enum",
        "operator_menu_enum",
    }:
        feature = feature_maps["by_operator_id"].get(
            call.identifier
        )

        if feature:
            return [
                (
                    feature,
                    90,
                )
            ]

        return []

    if call.ui_call in {
        "prop",
        "prop_enum",
        "prop_menu_enum",
        "template_ID",
    }:
        features = [
            feature
            for feature in feature_maps["by_identifier"].get(
                call.identifier,
                [],
            )
            if feature.feature_type == "RNA_PROPERTY"
        ]

        if not features:
            return []

        confidence = 80

        if len(features) > 1:
            confidence = 50

        if call.ui_call != "prop":
            confidence = min(
                confidence,
                70,
            )

        return [
            (
                feature,
                confidence,
            )
            for feature in features
        ]

    if call.ui_call in {
        "menu",
        "popover",
        "template_list",
    }:
        features = feature_maps["by_identifier"].get(
            call.identifier,
            [],
        )

        if features:
            return [
                (
                    feature,
                    65,
                )
                for feature in features
            ]

    return []
