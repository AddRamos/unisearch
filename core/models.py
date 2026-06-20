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