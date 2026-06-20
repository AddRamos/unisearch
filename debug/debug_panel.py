import bpy

from .debug_operators import (
    FEATURE_INDEX,
)


class UNISEARCH_PT_debug(
    bpy.types.Panel
):
    bl_label = "UniSearch Debug"

    bl_idname = (
        "UNISEARCH_PT_DEBUG"
    )

    bl_space_type = "VIEW_3D"

    bl_region_type = "UI"

    bl_category = "UniSearch"

    def draw(self, context):

        layout = self.layout

        layout.operator(
            "unisearch.build_feature_index"
        )

        layout.separator()

        layout.label(
            text=(
                f"Features: "
                f"{len(FEATURE_INDEX.features)}"
            )
        )

        col = layout.column()

        for query in (
            "cavity",
            "delete",
            "save",
            "xray",
            "bevel",
            "object delete",
            "save mainfile",
            "mesh cube",
            "Save As",
            "Save as",
            "delte",
            "remove",
            "write file",
            "ambient occlusion",
            "erase",                      
        ):

            op = col.operator(
                "unisearch.test_query",
                text=query,
            )

            op.query = query