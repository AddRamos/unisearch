from ..core.models import BreadcrumbRecord


MODE_LABELS = {
    "OBJECT": "Object Mode",
    "EDIT_MESH": "Edit Mesh Mode",
    "EDIT_CURVE": "Edit Curve Mode",
    "EDIT_CURVES": "Edit Curves Mode",
    "EDIT_ARMATURE": "Edit Armature Mode",
    "EDIT_METABALL": "Edit Metaball Mode",
    "EDIT_LATTICE": "Edit Lattice Mode",
    "POSE": "Pose Mode",
    "SCULPT": "Sculpt Mode",
    "PAINT_WEIGHT": "Weight Paint",
    "PAINT_VERTEX": "Vertex Paint",
    "PAINT_TEXTURE": "Texture Paint",
    "EDIT_GREASE_PENCIL": "Grease Pencil Edit Mode",
    "PAINT_GREASE_PENCIL": "Grease Pencil Paint Mode",
    "SCULPT_GREASE_PENCIL": "Grease Pencil Sculpt Mode",
    "WEIGHT_GREASE_PENCIL": "Grease Pencil Weight Paint",
    "UNKNOWN": "Unknown Mode",
}


EDITOR_LABELS = {
    "VIEW_3D": "3D Viewport",
    "PREFERENCES": "Preferences",
    "NODE_EDITOR": "Node Editor",
    "IMAGE_EDITOR": "Image Editor",
    "GRAPH_EDITOR": "Graph Editor",
    "DOPESHEET_EDITOR": "Dope Sheet",
    "NLA_EDITOR": "NLA Editor",
    "SEQUENCE_EDITOR": "Sequencer",
    "FILE_BROWSER": "File Browser",
    "OUTLINER": "Outliner",
    "CLIP_EDITOR": "Movie Clip Editor",
}


REGION_LABELS = {
    "HEADER": "Header",
    "WINDOW": "Window",
    "UI": "Sidebar",
    "TOOLS": "Toolbar",
    "ADDONS": "Add-ons",
}


class BreadcrumbIndex:

    def __init__(self):

        self.breadcrumbs = []

        self.by_feature_id = {}

        self.by_identifier = {}

    def build(self, resolved_location_index):

        self.breadcrumbs.clear()
        self.by_feature_id.clear()
        self.by_identifier.clear()

        breadcrumbs = []

        for resolved in resolved_location_index.resolved:
            breadcrumbs.append(
                _breadcrumb_from_resolved(resolved)
            )

        for breadcrumb in _dedupe_breadcrumbs(breadcrumbs):
            self._add_breadcrumb(breadcrumb)

        print("\n")
        print("=" * 60)
        print("UNISEARCH BREADCRUMB BUILD")
        print("=" * 60)
        print("BREADCRUMBS:", len(self.breadcrumbs))
        print(
            "FEATURES WITH BREADCRUMBS:",
            len(self.by_feature_id),
        )
        print("=" * 60)

    def inspect_identifier(self, identifier):

        return self.by_identifier.get(
            identifier,
            [],
        )

    def _add_breadcrumb(self, breadcrumb):

        self.breadcrumbs.append(breadcrumb)

        self.by_feature_id.setdefault(
            breadcrumb.feature_id,
            [],
        ).append(breadcrumb)

        self.by_identifier.setdefault(
            breadcrumb.feature_identifier,
            [],
        ).append(breadcrumb)

        self.by_identifier[
            breadcrumb.feature_identifier
        ].sort(
            key=_breadcrumb_sort_key
        )


def _breadcrumb_from_resolved(resolved):

    parts = _breadcrumb_parts(resolved)

    return BreadcrumbRecord(
        feature_id=resolved.feature_id,
        feature_identifier=resolved.feature_identifier,
        feature_label=resolved.feature_label,
        breadcrumb_parts=parts,
        breadcrumb=" > ".join(parts),
        confidence=resolved.confidence,
        mode=resolved.mode,
        shortcut=resolved.shortcut,
        shortcut_kind=resolved.shortcut_kind,
    )


def _breadcrumb_parts(resolved):

    if resolved.container_type == "ADDON_PREFERENCES":
        return _addon_preference_parts(resolved)

    if resolved.container_type == "COMMAND":
        return _command_parts(resolved)

    parts = []

    parts.append(
        _mode_label(resolved.mode)
    )

    editor = _editor_label(resolved.editor)

    if editor:
        parts.append(editor)

    region = _region_label(resolved.region)

    if region:
        parts.append(region)

    container = _container_label(resolved)

    if container:
        parts.append(container)

    shortcut_part = _shortcut_part(resolved)

    if shortcut_part:
        parts.append(shortcut_part)

    parts.append(resolved.feature_label)

    return _clean_parts(parts)


def _addon_preference_parts(resolved):

    parts = [
        "Preferences",
        "Add-ons",
    ]

    if resolved.container_label:
        parts.append(resolved.container_label)

    parts.append(resolved.feature_label)

    return _clean_parts(parts)


def _command_parts(resolved):

    parts = [
        _mode_label(resolved.mode),
        "Command",
    ]

    shortcut_part = _shortcut_part(resolved)

    if shortcut_part:
        parts.append(shortcut_part)

    parts.append(resolved.feature_label)

    return _clean_parts(parts)


def _mode_label(mode):

    return MODE_LABELS.get(
        mode,
        mode.replace("_", " ").title()
        if mode
        else "Unknown Mode",
    )


def _editor_label(editor):

    if not editor:
        return ""

    return EDITOR_LABELS.get(
        editor,
        editor.replace("_", " ").title(),
    )


def _region_label(region):

    if not region:
        return ""

    return REGION_LABELS.get(
        region,
        region.replace("_", " ").title(),
    )


def _container_label(resolved):

    label = resolved.container_label

    if not label:
        label = _label_from_container_id(
            resolved.container_id
        )

    if not label:
        return ""

    if _is_context_menu(resolved):
        return f"{label} Context Menu"

    container_type = resolved.container_type.replace(
        "_",
        " ",
    ).title()

    if resolved.container_type == "PANEL":
        return f"{label} Panel"

    if resolved.container_type == "MENU":
        return f"{label} Menu"

    if resolved.container_type == "HEADER":
        return f"{label} Header"

    if resolved.container_type == "UILIST":
        return f"{label} List"

    return f"{label} {container_type}"


def _is_context_menu(resolved):

    container_id = resolved.container_id.lower()

    return (
        resolved.container_type == "MENU"
        and (
            "context_menu" in container_id
            or container_id.endswith("_context")
        )
    )


def _shortcut_part(resolved):

    if not resolved.shortcut:
        return ""

    if resolved.shortcut_kind == "DIRECT_FEATURE":
        return f"Shortcut {resolved.shortcut}"

    if resolved.shortcut_kind == "CONTAINER_OPEN":
        return f"Open with {resolved.shortcut}"

    if resolved.shortcut_kind == "KEYMAP_ONLY":
        return f"Shortcut {resolved.shortcut}"

    return resolved.shortcut


def _label_from_container_id(container_id):

    if not container_id:
        return ""

    parts = container_id.split("_")

    if len(parts) <= 2:
        return container_id.replace("_", " ").title()

    return " ".join(parts[2:]).replace("_", " ").title()


def _clean_parts(parts):

    clean = []
    seen = set()

    for part in parts:

        if not part:
            continue

        if part in seen:
            continue

        seen.add(part)
        clean.append(part)

    return clean


def _dedupe_breadcrumbs(breadcrumbs):

    best_by_text = {}

    for breadcrumb in breadcrumbs:

        existing = best_by_text.get(
            breadcrumb.breadcrumb
        )

        if existing is None:
            best_by_text[
                breadcrumb.breadcrumb
            ] = breadcrumb
            continue

        if _breadcrumb_sort_key(
            breadcrumb
        ) < _breadcrumb_sort_key(
            existing
        ):
            best_by_text[
                breadcrumb.breadcrumb
            ] = breadcrumb

    unique = list(best_by_text.values())

    unique.sort(
        key=_breadcrumb_sort_key
    )

    return unique


def _breadcrumb_sort_key(breadcrumb):

    return (
        -breadcrumb.confidence,
        _unknown_mode_penalty(breadcrumb),
        _shortcut_kind_rank(breadcrumb.shortcut_kind),
        len(breadcrumb.breadcrumb_parts),
        breadcrumb.breadcrumb,
    )


def _unknown_mode_penalty(breadcrumb):

    return 1 if breadcrumb.mode == "UNKNOWN" else 0


def _shortcut_kind_rank(shortcut_kind):

    if shortcut_kind == "DIRECT_FEATURE":
        return 0

    if shortcut_kind == "CONTAINER_OPEN":
        return 1

    if shortcut_kind == "":
        return 2

    if shortcut_kind == "KEYMAP_ONLY":
        return 3

    return 4
