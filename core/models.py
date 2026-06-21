from dataclasses import dataclass, field


@dataclass
class FeatureRecord:

    feature_id: str

    label: str

    identifier: str

    feature_type: str

    description: str = ""

    source: str = ""

    aliases: list[str] = field(
        default_factory=list
    )

    owners: list[str] = field(
        default_factory=list
    )


@dataclass
class LocationCandidate:

    feature_id: str

    feature_identifier: str

    container_id: str

    container_type: str

    source_file: str

    line_number: int

    source: str = "STATIC_UI"

    confidence: int = 80

    ui_call: str = ""

    source_kind: str = ""

    addon_module: str = ""

    container_label: str = ""

    bl_space_type: str = ""

    bl_region_type: str = ""

    bl_category: str = ""


@dataclass
class KeymapCandidate:

    target_id: str

    target_type: str

    keymap_name: str

    keymap_space_type: str

    keymap_region_type: str

    event: str

    operator_id: str

    source: str = "KEYMAP"

    is_active: bool = True


@dataclass
class ModeCandidate:

    feature_id: str

    feature_identifier: str

    mode: str

    source: str

    confidence: int

    evidence: str = ""

    container_id: str = ""

    keymap_name: str = ""


@dataclass
class ResolvedLocation:

    feature_id: str

    feature_identifier: str

    feature_label: str

    feature_type: str

    container_id: str

    container_type: str

    container_label: str

    mode: str

    editor: str

    region: str

    shortcut: str = ""

    confidence: int = 0

    source: str = "RESOLVED"

    location_source: str = ""

    mode_source: str = ""

    shortcut_source: str = ""

    shortcut_kind: str = ""

    evidence: str = ""


@dataclass
class BreadcrumbRecord:

    feature_id: str

    feature_identifier: str

    feature_label: str

    breadcrumb_parts: list[str]

    breadcrumb: str

    confidence: int

    mode: str = ""

    shortcut: str = ""

    shortcut_kind: str = ""

    source: str = "BREADCRUMB"


@dataclass
class RuntimeVerificationRecord:

    feature_id: str

    feature_identifier: str

    container_id: str

    status: str

    feature_verified: bool

    container_verified: bool

    source: str = "RUNTIME"

    detail: str = ""
