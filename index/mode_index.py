from ..core.models import ModeCandidate


UNKNOWN_MODE = "UNKNOWN"


KEYMAP_MODE_MAP = {
    "Object Mode": "OBJECT",
    "Mesh": "EDIT_MESH",
    "Curve": "EDIT_CURVE",
    "Curves": "EDIT_CURVES",
    "Armature": "EDIT_ARMATURE",
    "Metaball": "EDIT_METABALL",
    "Lattice": "EDIT_LATTICE",
    "Pose": "POSE",
    "Sculpt": "SCULPT",
    "Weight Paint": "PAINT_WEIGHT",
    "Vertex Paint": "PAINT_VERTEX",
    "Image Paint": "PAINT_TEXTURE",
    "Grease Pencil Edit Mode": "EDIT_GREASE_PENCIL",
    "Grease Pencil Paint Mode": "PAINT_GREASE_PENCIL",
    "Grease Pencil Sculpt Mode": "SCULPT_GREASE_PENCIL",
    "Grease Pencil Weight Paint": "WEIGHT_GREASE_PENCIL",
}


STATIC_MODE_HINTS = (
    ("SCULPT", ("sculpt", "automasking", "voxel_remesh")),
    ("PAINT_TEXTURE", ("texture_paint", "image_paint")),
    ("PAINT_WEIGHT", ("weight_paint",)),
    ("PAINT_VERTEX", ("vertex_paint",)),
    ("EDIT_MESH", ("edit_mesh", "mesh_edit")),
    ("EDIT_CURVE", ("edit_curve", "curve_edit")),
    ("POSE", ("pose",)),
    ("OBJECT", ("object_mode",)),
)


class ModeIndex:

    def __init__(self):

        self.candidates = []

        self.by_feature_id = {}

        self.by_identifier = {}

        self.unknown_feature_count = 0

    def build(
        self,
        features,
        location_index,
        keymap_index,
    ):

        self.candidates.clear()
        self.by_feature_id.clear()
        self.by_identifier.clear()
        self.unknown_feature_count = 0

        for feature in features:

            feature_candidates = []

            feature_candidates.extend(
                _mode_candidates_from_keymaps(
                    feature,
                    keymap_index,
                )
            )

            feature_candidates.extend(
                _mode_candidates_from_locations(
                    feature,
                    location_index,
                )
            )

            unique_candidates = _dedupe_candidates(
                feature_candidates
            )

            if not unique_candidates:
                self.unknown_feature_count += 1
                continue

            for candidate in unique_candidates:
                self._add_candidate(candidate)

        print("\n")
        print("=" * 60)
        print("UNISEARCH MODE RESOLVER")
        print("=" * 60)
        print("MODE CANDIDATES:", len(self.candidates))
        print(
            "FEATURES WITH MODE:",
            len(self.by_feature_id),
        )
        print(
            "FEATURES WITHOUT MODE:",
            self.unknown_feature_count,
        )
        print("=" * 60)

    def inspect_identifier(self, identifier):

        return self.by_identifier.get(
            identifier,
            [],
        )

    def _add_candidate(self, candidate):

        self.candidates.append(candidate)

        self.by_feature_id.setdefault(
            candidate.feature_id,
            [],
        ).append(candidate)

        self.by_identifier.setdefault(
            candidate.feature_identifier,
            [],
        ).append(candidate)


def _mode_candidates_from_keymaps(
    feature,
    keymap_index,
):

    if feature.feature_type != "OPERATOR":
        return []

    candidates = []

    for shortcut in keymap_index.inspect_target(
        feature.identifier
    ):

        mode = KEYMAP_MODE_MAP.get(
            shortcut.keymap_name,
            UNKNOWN_MODE,
        )

        if mode == UNKNOWN_MODE:
            continue

        candidates.append(
            ModeCandidate(
                feature_id=feature.feature_id,
                feature_identifier=feature.identifier,
                mode=mode,
                source="KEYMAP",
                confidence=90,
                evidence=shortcut.event,
                keymap_name=shortcut.keymap_name,
            )
        )

    return candidates


def _mode_candidates_from_locations(
    feature,
    location_index,
):

    candidates = []

    for location in location_index.inspect_identifier(
        feature.identifier
    ):

        mode = _mode_from_location(location)

        if mode == UNKNOWN_MODE:
            continue

        candidates.append(
            ModeCandidate(
                feature_id=feature.feature_id,
                feature_identifier=feature.identifier,
                mode=mode,
                source="STATIC_UI_HINT",
                confidence=70,
                evidence=_location_evidence(location),
                container_id=location.container_id,
            )
        )

    return candidates


def _mode_from_location(location):

    text = " ".join(
        (
            location.container_id,
            location.container_label,
            location.bl_category,
            location.source_file,
        )
    ).lower()

    normalized = text.replace(
        "\\",
        "/",
    )

    for mode, hints in STATIC_MODE_HINTS:

        for hint in hints:

            if hint in normalized:
                return mode

    return UNKNOWN_MODE


def _location_evidence(location):

    evidence = location.container_id

    if location.container_label:
        evidence = (
            f"{evidence} "
            f"({location.container_label})"
        )

    return evidence


def _dedupe_candidates(candidates):

    unique = []
    seen = set()

    for candidate in candidates:

        key = (
            candidate.feature_id,
            candidate.mode,
            candidate.source,
            candidate.container_id,
            candidate.keymap_name,
            candidate.evidence,
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(candidate)

    unique.sort(
        key=lambda candidate: (
            -candidate.confidence,
            candidate.mode,
            candidate.source,
            candidate.evidence,
        )
    )

    return unique
