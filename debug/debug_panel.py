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

        layout.label(
            text=(
                f"Shortcuts: "
                f"{len(FEATURE_INDEX.keymap_index.shortcuts)}"
            )
        )

        layout.label(
            text=(
                f"Mode Candidates: "
                f"{len(FEATURE_INDEX.mode_index.candidates)}"
            )
        )

        layout.label(
            text=(
                f"Resolved Locations: "
                f"{len(FEATURE_INDEX.resolved_location_index.resolved)}"
            )
        )

        layout.label(
            text=(
                f"Breadcrumbs: "
                f"{len(FEATURE_INDEX.breadcrumb_index.breadcrumbs)}"
            )
        )

        layout.label(
            text=(
                f"Runtime Verified: "
                f"{FEATURE_INDEX.runtime_verification_index.confirmed}"
            )
        )

        layout.label(
            text=(
                f"Runtime Outliers: "
                f"{FEATURE_INDEX.runtime_verification_index.partial + FEATURE_INDEX.runtime_verification_index.unverified}"
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
            "preferences",
            "addon",
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
            text="Stage 11 Runtime Probes"
        )

        op = layout.operator(
            "unisearch.list_runtime_outliers"
        )

        op.limit = 40

        col = layout.column()

        for identifier in (
            "object.delete",
            "wm.save_mainfile",
            "show_cavity",
            "use_automasking_cavity",
            "mesh.primitive_cube_add",
            "compute_device_type",
        ):

            op = col.operator(
                "unisearch.inspect_runtime_verification",
                text=identifier,
            )

            op.identifier = identifier

        layout.separator()

        layout.label(
            text="Stage 10 Breadcrumb Probes"
        )

        col = layout.column()

        for identifier in (
            "object.delete",
            "wm.save_mainfile",
            "show_cavity",
            "use_automasking_cavity",
            "mesh.primitive_cube_add",
            "compute_device_type",
        ):

            op = col.operator(
                "unisearch.inspect_breadcrumbs",
                text=identifier,
            )

            op.identifier = identifier

        layout.separator()

        layout.label(
            text="Stage 9 Resolved Location Probes"
        )

        col = layout.column()

        for identifier in (
            "object.delete",
            "wm.save_mainfile",
            "show_cavity",
            "use_automasking_cavity",
            "mesh.primitive_cube_add",
            "compute_device_type",
        ):

            op = col.operator(
                "unisearch.inspect_resolved_locations",
                text=identifier,
            )

            op.identifier = identifier

        layout.separator()

        layout.label(
            text="Stage 7 Keymap Probes"
        )

        col = layout.column()

        for target_id in (
            "VIEW3D_MT_shading_pie",
            "VIEW3D_MT_object",
            "object.delete",
            "mesh.primitive_cube_add",
            "wm.save_mainfile",
            "wm.call_menu_pie",
        ):

            op = col.operator(
                "unisearch.inspect_keymap",
                text=target_id,
            )

            op.target_id = target_id

        layout.separator()

        layout.label(
            text="Stage 8 Mode Probes"
        )

        col = layout.column()

        for identifier in (
            "object.delete",
            "wm.save_mainfile",
            "show_cavity",
            "use_automasking_cavity",
            "mesh.primitive_cube_add",
            "voxel_remesh",
        ):

            op = col.operator(
                "unisearch.inspect_modes",
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

        layout.separator()

        layout.label(
            text="Stage 6 Preference Probes"
        )

        layout.operator(
            "unisearch.list_addon_preferences"
        )

        col = layout.column()

        for identifier in (
            "maximum_pins",
            "allow_pin_rollover",
            "show_debug_panel",
            "use_preferences_save",
        ):

            op = col.operator(
                "unisearch.inspect_locations",
                text=identifier,
            )

            op.identifier = identifier
