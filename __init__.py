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
    UNISEARCH_OT_test_query,
)


classes = (
    UNISEARCH_OT_build_index,
    UNISEARCH_OT_test_query,
    UNISEARCH_PT_debug,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)