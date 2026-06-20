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

        layout.label(
            text=(
                f"Locations: "
                f"{len(FEATURE_INDEX.location_index.locations)}"
            )
        )

        layout.label(
            text=(
                f"Unmatched UI Calls: "
                f"{FEATURE_INDEX.location_index.unmatched_calls}"
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
            "object",
            "mesh",
            "Brush",
            "Sculpt",                      
        ):

            op = col.operator(
                "unisearch.test_query",
                text=query,
            )

            op.query = query

        layout.separator()

        layout.label(
            text="Stage 5 Location Probes"
        )

        col = layout.column()

        for identifier in (
            "show_cavity",
            "use_automasking_cavity",
            "use_snap",
            "object.delete",
            "mesh.primitive_cube_add",
            "wm.save_as_mainfile",
        ):

            op = col.operator(
                "unisearch.inspect_locations",
                text=identifier,
            )

            op.identifier = identifier

        layout.separator()

        layout.label(
            text="Stage 5.1 Container Probes"
        )

        col = layout.column()

        for container_id in (
            "VIEW3D_PT_shading_options",
            "VIEW3D_MT_object",
            "VIEW3D_MT_mesh_add",
            "TOPBAR_MT_file",
        ):

            op = col.operator(
                "unisearch.inspect_container",
                text=container_id,
            )

            op.container_id = container_id

        layout.separator()

        op = layout.operator(
            "unisearch.inspect_unmatched_locations",
            text="Show Unmatched UI Calls",
        )

        op.limit = 40
