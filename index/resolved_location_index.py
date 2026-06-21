from ..core.models import ResolvedLocation


UNKNOWN_MODE = "UNKNOWN"

DIRECT_SHORTCUT = "DIRECT_FEATURE"

CONTAINER_SHORTCUT = "CONTAINER_OPEN"

KEYMAP_ONLY_SHORTCUT = "KEYMAP_ONLY"


class ResolvedLocationIndex:

    def __init__(self):

        self.resolved = []

        self.by_feature_id = {}

        self.by_identifier = {}

    def build(
        self,
        features,
        location_index,
        mode_index,
        keymap_index,
    ):

        self.resolved.clear()
        self.by_feature_id.clear()
        self.by_identifier.clear()

        for feature in features:

            resolved_locations = _resolve_feature(
                feature,
                location_index,
                mode_index,
                keymap_index,
            )

            for resolved in resolved_locations:
                self._add_resolved(resolved)

        print("\n")
        print("=" * 60)
        print("UNISEARCH LOCATION RESOLVER")
        print("=" * 60)
        print("RESOLVED LOCATIONS:", len(self.resolved))
        print(
            "FEATURES WITH RESOLVED LOCATIONS:",
            len(self.by_feature_id),
        )
        print("=" * 60)

    def inspect_identifier(self, identifier):

        return self.by_identifier.get(
            identifier,
            [],
        )

    def _add_resolved(self, resolved):

        self.resolved.append(resolved)

        self.by_feature_id.setdefault(
            resolved.feature_id,
            [],
        ).append(resolved)

        self.by_identifier.setdefault(
            resolved.feature_identifier,
            [],
        ).append(resolved)


def _resolve_feature(
    feature,
    location_index,
    mode_index,
    keymap_index,
):

    resolved = []

    locations = [
        location
        for location in location_index.inspect_identifier(
            feature.identifier
        )
        if location.feature_id == feature.feature_id
    ]

    mode_candidates = [
        mode
        for mode in mode_index.inspect_identifier(
            feature.identifier
        )
        if mode.feature_id == feature.feature_id
    ]

    direct_shortcuts = keymap_index.inspect_target(
        feature.identifier
    )

    for location in locations:

        modes = _modes_for_location(
            location,
            mode_candidates,
        )

        shortcut_refs = _shortcut_refs_for_location(
            location,
            direct_shortcuts,
            keymap_index,
        )

        if not modes:
            modes = [None]

        if not shortcut_refs:
            shortcut_refs = [
                (
                    None,
                    "",
                )
            ]

        for mode in modes:

            for shortcut, shortcut_kind in shortcut_refs:

                resolved.append(
                    _make_resolved_location(
                        feature,
                        location,
                        mode,
                        shortcut,
                        shortcut_kind,
                    )
                )

    if not resolved and direct_shortcuts:
        for shortcut in direct_shortcuts:
            mode = _mode_for_shortcut(
                shortcut,
                mode_candidates,
            )

            resolved.append(
                _make_keymap_only_location(
                    feature,
                    mode,
                    shortcut,
                )
            )

    return _dedupe_resolved(resolved)


def _modes_for_location(location, mode_candidates):

    container_modes = [
        mode
        for mode in mode_candidates
        if mode.container_id
        and mode.container_id == location.container_id
    ]

    if container_modes:
        return container_modes

    return [
        mode
        for mode in mode_candidates
        if not mode.container_id
    ]


def _shortcut_refs_for_location(
    location,
    direct_shortcuts,
    keymap_index,
):

    shortcut_refs = []

    for shortcut in direct_shortcuts:
        shortcut_refs.append(
            (
                shortcut,
                DIRECT_SHORTCUT,
            )
        )

    if not _is_context_container(location):
        for shortcut in keymap_index.inspect_target(
            location.container_id
        ):
            shortcut_refs.append(
                (
                    shortcut,
                    CONTAINER_SHORTCUT,
                )
            )

    return _dedupe_shortcut_refs(shortcut_refs)


def _is_context_container(location):

    container_id = location.container_id.lower()

    return (
        "context_menu" in container_id
        or container_id.endswith("_context")
    )


def _mode_for_shortcut(shortcut, mode_candidates):

    for mode in mode_candidates:

        if mode.keymap_name == shortcut.keymap_name:
            return mode

    return None


def _make_resolved_location(
    feature,
    location,
    mode,
    shortcut,
    shortcut_kind,
):

    mode_name = UNKNOWN_MODE
    mode_source = ""
    mode_confidence = 0

    if mode:
        mode_name = mode.mode
        mode_source = mode.source
        mode_confidence = mode.confidence

    shortcut_value = ""
    shortcut_source = ""

    if shortcut:
        shortcut_value = shortcut.event
        shortcut_source = shortcut.source

    confidence = _resolved_confidence(
        location.confidence,
        mode_confidence,
        bool(shortcut),
    )

    return ResolvedLocation(
        feature_id=feature.feature_id,
        feature_identifier=feature.identifier,
        feature_label=feature.label,
        feature_type=feature.feature_type,
        container_id=location.container_id,
        container_type=location.container_type,
        container_label=location.container_label,
        mode=mode_name,
        editor=location.bl_space_type,
        region=location.bl_region_type,
        shortcut=shortcut_value,
        confidence=confidence,
        location_source=location.source,
        mode_source=mode_source,
        shortcut_source=shortcut_source,
        shortcut_kind=shortcut_kind,
        evidence=_resolved_evidence(
            location,
            mode,
            shortcut,
            shortcut_kind,
        ),
    )


def _make_keymap_only_location(
    feature,
    mode,
    shortcut,
):

    mode_name = UNKNOWN_MODE
    mode_source = ""
    mode_confidence = 0

    if mode:
        mode_name = mode.mode
        mode_source = mode.source
        mode_confidence = mode.confidence

    confidence = _resolved_confidence(
        45,
        mode_confidence,
        True,
    )

    return ResolvedLocation(
        feature_id=feature.feature_id,
        feature_identifier=feature.identifier,
        feature_label=feature.label,
        feature_type=feature.feature_type,
        container_id="COMMAND",
        container_type="COMMAND",
        container_label="Command",
        mode=mode_name,
        editor=shortcut.keymap_space_type,
        region=shortcut.keymap_region_type,
        shortcut=shortcut.event,
        confidence=confidence,
        location_source="KEYMAP_ONLY",
        mode_source=mode_source,
        shortcut_source=shortcut.source,
        shortcut_kind=KEYMAP_ONLY_SHORTCUT,
        evidence=(
            f"{shortcut.keymap_name} "
            f"{shortcut.event}"
        ),
    )


def _resolved_confidence(
    location_confidence,
    mode_confidence,
    has_shortcut,
):

    confidence = location_confidence

    if mode_confidence:
        confidence = int(
            (confidence + mode_confidence) / 2
        )

    if has_shortcut:
        confidence = min(
            100,
            confidence + 5,
        )

    return confidence


def _resolved_evidence(
    location,
    mode,
    shortcut,
    shortcut_kind,
):

    parts = [
        location.container_id,
        location.ui_call,
    ]

    if mode:
        parts.append(
            f"mode:{mode.mode}"
        )

    if shortcut:
        parts.append(
            f"shortcut:{shortcut_kind}:{shortcut.event}"
        )

    return " | ".join(parts)


def _dedupe_shortcut_refs(shortcut_refs):

    unique = []
    seen = set()

    for shortcut, shortcut_kind in shortcut_refs:

        key = (
            shortcut.target_id,
            shortcut.target_type,
            shortcut.keymap_name,
            shortcut.keymap_space_type,
            shortcut.keymap_region_type,
            shortcut.event,
            shortcut.operator_id,
            shortcut_kind,
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(
            (
                shortcut,
                shortcut_kind,
            )
        )

    return unique


def _dedupe_resolved(resolved_locations):

    unique = []
    seen = set()

    for resolved in resolved_locations:

        key = (
            resolved.feature_id,
            resolved.container_id,
            resolved.mode,
            resolved.editor,
            resolved.region,
            resolved.shortcut,
            resolved.shortcut_kind,
            resolved.location_source,
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(resolved)

    unique.sort(
        key=lambda resolved: (
            -resolved.confidence,
            resolved.mode,
            resolved.container_id,
            resolved.shortcut_kind,
            resolved.shortcut,
        )
    )

    return unique
