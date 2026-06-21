bl_info = {
    "name": "UniSearch",
    "author": "UniSearch",
    "version": (0, 2, 0),
    "blender": (4, 2, 0),
    "category": "Interface",
}

import bpy

from .debug.debug_panel import (
    UNISEARCH_PT_debug,
)

from .debug.debug_operators import (
    UNISEARCH_OT_build_index,
    UNISEARCH_OT_inspect_breadcrumbs,
    UNISEARCH_OT_inspect_container,
    UNISEARCH_OT_inspect_keymap,
    UNISEARCH_OT_inspect_locations,
    UNISEARCH_OT_inspect_modes,
    UNISEARCH_OT_inspect_resolved_locations,
    UNISEARCH_OT_inspect_runtime_verification,
    UNISEARCH_OT_inspect_unmatched_locations,
    UNISEARCH_OT_list_runtime_outliers,
    UNISEARCH_OT_list_addon_preferences,
    UNISEARCH_OT_test_query,
)


classes = (
    UNISEARCH_OT_build_index,
    UNISEARCH_OT_test_query,
    UNISEARCH_OT_inspect_breadcrumbs,
    UNISEARCH_OT_inspect_locations,
    UNISEARCH_OT_inspect_container,
    UNISEARCH_OT_inspect_unmatched_locations,
    UNISEARCH_OT_list_addon_preferences,
    UNISEARCH_OT_inspect_keymap,
    UNISEARCH_OT_inspect_modes,
    UNISEARCH_OT_inspect_resolved_locations,
    UNISEARCH_OT_inspect_runtime_verification,
    UNISEARCH_OT_list_runtime_outliers,
    UNISEARCH_PT_debug,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
