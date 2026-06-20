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
