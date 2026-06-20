import bpy

from ..core.models import (
    FeatureRecord,
)


def collect_rna_features():

    #
    # KEY:
    #
    # identifier -> normalized feature
    #

    normalized = {}

    for cls_name in dir(bpy.types):

        cls = getattr(
            bpy.types,
            cls_name,
        )

        rna = getattr(
            cls,
            "bl_rna",
            None,
        )

        if rna is None:
            continue

        properties = getattr(
            rna,
            "properties",
            None,
        )

        if properties is None:
            continue

        for prop in properties:

            identifier = getattr(
                prop,
                "identifier",
                "",
            )

            if not identifier:
                continue

            label = getattr(
                prop,
                "name",
                identifier,
            )

            description = getattr(
                prop,
                "description",
                "",
            )

            #
            # Create feature once
            #

            if identifier not in normalized:

                normalized[
                    identifier
                ] = FeatureRecord(
                    feature_id=(
                        f"rna:{identifier}"
                    ),
                    label=label,
                    identifier=identifier,
                    feature_type=(
                        "RNA_PROPERTY"
                    ),
                    description=description,
                    source="RNA",
                )

            #
            # Track owner class
            #

            feature = normalized[
                identifier
            ]

            if cls_name not in feature.owners:

                feature.owners.append(
                    cls_name
                )

    return list(
        normalized.values()
    )