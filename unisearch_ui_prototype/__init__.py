bl_info = {
    "name": "UniSearch UI Prototype",
    "author": "UniSearch Prototype",
    "version": (0, 1, 1),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > UniSearch",
    "description": "UI/UX prototype for a universal Blender search panel with dummy results and session-only pins.",
    "category": "Interface",
}

import bpy

from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)


PART_SEPARATOR = "||"


# ------------------------------------------------------------------------
# Dummy search provider
# Later this function can be replaced by a real Blender UI search provider.
# ------------------------------------------------------------------------

def get_dummy_results(query):
    return [
        [
            "DUMMY MODE",
            "DUMMY MENU",
            "DUMMY MENU",
            "DUMMY DATA",
        ],
        [
            "DUMMY MODE",
            "DUMMY HEADER",
            "DUMMY DATA",
        ],
        [
            "DUMMY MODE",
            "DUMMY PANEL",
            "DUMMY BUTTON",
            "DUMMY DATA",
        ],
        [
            "DUMMY MODE",
            "DUMMY PREFERENCES",
            "DUMMY SECTION",
            "DUMMY SETTING",
        ],
        [
            "DUMMY MODE",
            "DUMMY EDITOR",
            "DUMMY TOOLBAR",
            "DUMMY TOOL",
        ],
        [
            "DUMMY MODE",
            "DUMMY CONTEXT MENU",
            "DUMMY OPERATOR",
            "DUMMY DATA",
        ],
    ]


# ------------------------------------------------------------------------
# Breadcrumb serialization helpers
# ------------------------------------------------------------------------

def parts_to_serialized(parts):
    return PART_SEPARATOR.join(parts)


def serialized_to_parts(serialized):
    if not serialized:
        return []
    return serialized.split(PART_SEPARATOR)


def parts_to_full_path(parts):
    return " > ".join(parts)


def make_item_id_from_parts(parts):
    return parts_to_full_path(parts)


# ------------------------------------------------------------------------
# Add-on Preferences
# ------------------------------------------------------------------------

class UNISEARCH_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    max_pins: IntProperty(
        name="Maximum Number of Pins",
        description="Maximum amount of session-only pinned UniSearch results",
        default=5,
        min=1,
        max=50,
    )

    allow_pin_rollover: BoolProperty(
        name="Allow Pin Rollover",
        description="When the pin list is full, remove the oldest pin and add the new one",
        default=True,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Pinned Results", icon="PINNED")
        box.prop(self, "max_pins")
        box.prop(self, "allow_pin_rollover")

        box = layout.box()
        box.label(text="Future Feature", icon="INFO")
        box.label(text="Shortcut popup search will be added later.")
        box.label(text="Version 1 is N-panel only.")


# ------------------------------------------------------------------------
# Property Groups
# ------------------------------------------------------------------------

class UNISEARCH_BreadcrumbItem(bpy.types.PropertyGroup):
    item_id: StringProperty(
        name="Item ID",
        default="",
    )

    full_path: StringProperty(
        name="Full Path",
        default="",
    )

    parts_serialized: StringProperty(
        name="Breadcrumb Parts",
        default="",
    )

    expanded: BoolProperty(
        name="Expanded",
        default=False,
    )


class UNISEARCH_State(bpy.types.PropertyGroup):
    search_query: StringProperty(
        name="Search",
        description="Type something to search",
        default="",
    )

    panel_message: StringProperty(
        name="Panel Message",
        default="",
    )

    panel_message_type: StringProperty(
        name="Panel Message Type",
        default="INFO",
    )

    results: CollectionProperty(
        type=UNISEARCH_BreadcrumbItem,
    )

    pins: CollectionProperty(
        type=UNISEARCH_BreadcrumbItem,
    )


# ------------------------------------------------------------------------
# General helpers
# ------------------------------------------------------------------------

def get_addon_prefs(context):
    return context.preferences.addons[__name__].preferences


def get_state(context):
    return context.window_manager.unisearch_state


def clear_collection(collection):
    collection.clear()


def set_panel_message(state, message, message_type="INFO"):
    state.panel_message = message
    state.panel_message_type = message_type


def clear_panel_message(state):
    state.panel_message = ""
    state.panel_message_type = "INFO"


def add_breadcrumb_item(collection, parts, expanded=False):
    full_path = parts_to_full_path(parts)

    item = collection.add()
    item.item_id = make_item_id_from_parts(parts)
    item.full_path = full_path
    item.parts_serialized = parts_to_serialized(parts)
    item.expanded = expanded

    return item


def find_pin_index(state, item_id):
    for index, pin in enumerate(state.pins):
        if pin.item_id == item_id:
            return index
    return -1


def find_result_index(state, item_id):
    for index, result in enumerate(state.results):
        if result.item_id == item_id:
            return index
    return -1


def sync_result_expanded_state_from_pin(state, item_id, expanded):
    for result in state.results:
        if result.item_id == item_id:
            result.expanded = expanded


def sync_pin_expanded_state_from_result(state, item_id, expanded):
    for pin in state.pins:
        if pin.item_id == item_id:
            pin.expanded = expanded


# ------------------------------------------------------------------------
# Responsive text helpers
# ------------------------------------------------------------------------

def estimate_available_chars(context, has_toggle, action_kind):
    """
    Conservative character estimate for Blender N-panel labels.

    Blender does not expose exact text measurement for normal Python UI panel
    drawing, so this estimates using current region width and reserved UI space.
    """

    region_width = 280

    if context.region:
        region_width = context.region.width

    ui_scale = context.preferences.system.ui_scale or 1.0

    average_char_px = 7.2 * ui_scale

    reserved_px = 42

    if has_toggle:
        reserved_px += 26

    # Icon-only PIN/UNPIN buttons are small.
    if action_kind in {"PIN", "UNPIN"}:
        reserved_px += 34

    # PINNED #n is a disabled status label, not an icon-only button.
    elif action_kind == "PINNED":
        reserved_px += 94

    available_px = max(40, region_width - reserved_px)
    available_chars = int(available_px / average_char_px)

    return max(8, available_chars)


def full_path_fits(context, full_path, action_kind):
    available_chars = estimate_available_chars(
        context=context,
        has_toggle=False,
        action_kind=action_kind,
    )
    return len(full_path) <= available_chars


def make_collapsed_path(parts, max_chars):
    if not parts:
        return ""

    if len(parts) == 1:
        value = parts[0]
        if len(value) <= max_chars:
            return value
        return value[:max(1, max_chars - 1)] + "…"

    first = parts[0]
    last = parts[-1]

    compact = f"{first} > ... > {last}"
    if len(compact) <= max_chars:
        return compact

    minimum = f"{first} > ..."

    if len(minimum) + 4 <= max_chars:
        remaining = max_chars - len(minimum) - 4
        trimmed_last = last[-remaining:] if remaining > 0 else ""
        return f"{minimum} > …{trimmed_last}"

    if len(first) <= max_chars:
        return first

    return first[:max(1, max_chars - 1)] + "…"


def wrap_breadcrumb_parts(parts, max_chars):
    """
    Greedy breadcrumb wrapping.

    The goal is to use the fewest practical number of lines.
    It does not force one breadcrumb segment per line.
    """

    lines = []
    current = ""

    for index, part in enumerate(parts):
        separator = "" if index == 0 else " > "
        candidate = current + separator + part if current else part

        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            lines.append(current)

        continued_part = part if not lines else f"> {part}"

        if len(continued_part) <= max_chars:
            current = continued_part
        else:
            chunk = continued_part

            while len(chunk) > max_chars:
                lines.append(chunk[:max_chars - 1] + "…")
                chunk = "…" + chunk[max_chars - 1:]

            current = chunk

    if current:
        lines.append(current)

    return lines


def wrap_plain_text(text, max_chars):
    if not text:
        return []

    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"

        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            lines.append(current)

        if len(word) > max_chars:
            lines.append(word[:max_chars - 1] + "…")
            current = ""
        else:
            current = word

    if current:
        lines.append(current)

    return lines


# ------------------------------------------------------------------------
# Operators
# ------------------------------------------------------------------------

class UNISEARCH_OT_search(bpy.types.Operator):
    bl_idname = "unisearch.search"
    bl_label = "Search"
    bl_description = "Run dummy UniSearch search"

    def execute(self, context):
        state = get_state(context)
        query = state.search_query.strip()

        clear_collection(state.results)

        if not query:
            set_panel_message(
                state,
                "Type something to search.",
                "WARNING",
            )
            return {"CANCELLED"}

        clear_panel_message(state)

        dummy_results = get_dummy_results(query)

        for parts in dummy_results:
            item_id = make_item_id_from_parts(parts)
            pin_index = find_pin_index(state, item_id)
            expanded = False

            if pin_index != -1:
                expanded = state.pins[pin_index].expanded

            add_breadcrumb_item(
                state.results,
                parts,
                expanded=expanded,
            )

        return {"FINISHED"}


class UNISEARCH_OT_pin_result(bpy.types.Operator):
    bl_idname = "unisearch.pin_result"
    bl_label = "Pin"
    bl_description = "Pin this UniSearch result"

    item_id: StringProperty()

    def execute(self, context):
        state = get_state(context)
        prefs = get_addon_prefs(context)

        existing_pin_index = find_pin_index(state, self.item_id)

        if existing_pin_index != -1:
            set_panel_message(
                state,
                f"Already in pinned list: Pin #{existing_pin_index + 1}",
                "INFO",
            )
            return {"CANCELLED"}

        result_index = find_result_index(state, self.item_id)

        if result_index == -1:
            set_panel_message(
                state,
                "Result not found.",
                "WARNING",
            )
            return {"CANCELLED"}

        result = state.results[result_index]
        parts = serialized_to_parts(result.parts_serialized)

        if len(state.pins) >= prefs.max_pins:
            if prefs.allow_pin_rollover:
                # Important:
                # This removes only one old pin and adds the new one.
                # It does not auto-trim all pins if the user lowered max_pins.
                state.pins.remove(0)
            else:
                set_panel_message(
                    state,
                    "Your pinned list is full. Unpin some pinned elements to make space.",
                    "WARNING",
                )
                return {"CANCELLED"}

        add_breadcrumb_item(
            state.pins,
            parts,
            expanded=result.expanded,
        )

        clear_panel_message(state)
        return {"FINISHED"}


class UNISEARCH_OT_unpin_result(bpy.types.Operator):
    bl_idname = "unisearch.unpin_result"
    bl_label = "Unpin"
    bl_description = "Remove this item from pinned results"

    item_id: StringProperty()

    def execute(self, context):
        state = get_state(context)

        pin_index = find_pin_index(state, self.item_id)

        if pin_index == -1:
            set_panel_message(
                state,
                "Pinned item not found.",
                "WARNING",
            )
            return {"CANCELLED"}

        state.pins.remove(pin_index)
        clear_panel_message(state)

        return {"FINISHED"}


class UNISEARCH_OT_toggle_expand(bpy.types.Operator):
    bl_idname = "unisearch.toggle_expand"
    bl_label = "Toggle Breadcrumb"
    bl_description = "Expand or collapse this breadcrumb"

    item_id: StringProperty()
    source: StringProperty(default="RESULTS")

    def execute(self, context):
        state = get_state(context)

        if self.source == "PINS":
            for pin in state.pins:
                if pin.item_id == self.item_id:
                    pin.expanded = not pin.expanded
                    sync_result_expanded_state_from_pin(
                        state,
                        self.item_id,
                        pin.expanded,
                    )
                    return {"FINISHED"}

        for result in state.results:
            if result.item_id == self.item_id:
                result.expanded = not result.expanded
                sync_pin_expanded_state_from_result(
                    state,
                    self.item_id,
                    result.expanded,
                )
                return {"FINISHED"}

        set_panel_message(
            state,
            "Breadcrumb item not found.",
            "WARNING",
        )
        return {"CANCELLED"}


class UNISEARCH_OT_clear_results(bpy.types.Operator):
    bl_idname = "unisearch.clear_results"
    bl_label = "Clear"
    bl_description = "Clear search results"

    def execute(self, context):
        state = get_state(context)

        clear_collection(state.results)
        state.search_query = ""
        clear_panel_message(state)

        return {"FINISHED"}


# ------------------------------------------------------------------------
# UI drawing helpers
# ------------------------------------------------------------------------

def draw_panel_message(layout, context, state):
    if not state.panel_message:
        return

    icon = "INFO"

    if state.panel_message_type == "WARNING":
        icon = "ERROR"

    box = layout.box()

    available_chars = estimate_available_chars(
        context=context,
        has_toggle=False,
        action_kind="NONE",
    )

    lines = wrap_plain_text(
        state.panel_message,
        max_chars=max(12, available_chars),
    )

    if not lines:
        return

    first = True

    for line in lines:
        row = box.row(align=True)

        if first:
            row.label(text=line, icon=icon)
            first = False
        else:
            row.label(text=line)


def draw_action_button(row, item, action_kind, pin_number=0):
    if action_kind == "PIN":
        button_row = row.row(align=True)
        button_row.alignment = "RIGHT"

        op = button_row.operator(
            UNISEARCH_OT_pin_result.bl_idname,
            text="",
            icon="PINNED",
            emboss=True,
        )
        op.item_id = item.item_id

    elif action_kind == "UNPIN":
        button_row = row.row(align=True)
        button_row.alignment = "RIGHT"

        op = button_row.operator(
            UNISEARCH_OT_unpin_result.bl_idname,
            text="",
            icon="X",
            emboss=True,
        )
        op.item_id = item.item_id

    elif action_kind == "PINNED":
        sub = row.row(align=True)
        sub.enabled = False
        sub.label(text=f"PINNED #{pin_number}", icon="PINNED")


def draw_breadcrumb_item(
    layout,
    context,
    item,
    action_kind,
    source,
    pin_number=0,
):
    parts = serialized_to_parts(item.parts_serialized)
    full_path = item.full_path

    fits = full_path_fits(
        context=context,
        full_path=full_path,
        action_kind=action_kind,
    )

    box = layout.box()

    # Case 1:
    # Full breadcrumb fits in one line.
    # No [+] or [-] is shown.
    if fits:
        row = box.row(align=True)
        row.label(text=full_path)
        draw_action_button(row, item, action_kind, pin_number)
        return

    # Case 2:
    # Breadcrumb does not fit and is collapsed.
    if not item.expanded:
        row = box.row(align=True)

        op = row.operator(
            UNISEARCH_OT_toggle_expand.bl_idname,
            text="",
            icon="TRIA_RIGHT",
            emboss=False,
        )
        op.item_id = item.item_id
        op.source = source

        available_chars = estimate_available_chars(
            context=context,
            has_toggle=True,
            action_kind=action_kind,
        )

        collapsed = make_collapsed_path(parts, available_chars)
        row.label(text=collapsed)

        draw_action_button(row, item, action_kind, pin_number)
        return

    # Case 3:
    # Breadcrumb does not fit and is expanded.
    first_row_chars = estimate_available_chars(
        context=context,
        has_toggle=True,
        action_kind=action_kind,
    )

    following_row_chars = estimate_available_chars(
        context=context,
        has_toggle=False,
        action_kind="NONE",
    )

    max_chars = max(
        8,
        min(first_row_chars, following_row_chars),
    )

    lines = wrap_breadcrumb_parts(parts, max_chars)

    if not lines:
        lines = [full_path]

    first_line = lines[0]
    remaining_lines = lines[1:]

    row = box.row(align=True)

    op = row.operator(
        UNISEARCH_OT_toggle_expand.bl_idname,
        text="",
        icon="TRIA_DOWN",
        emboss=False,
    )
    op.item_id = item.item_id
    op.source = source

    row.label(text=first_line)
    draw_action_button(row, item, action_kind, pin_number)

    for line in remaining_lines:
        subrow = box.row(align=True)
        subrow.separator(factor=1.25)
        subrow.label(text=line)


# ------------------------------------------------------------------------
# Main Sidebar Panel
# ------------------------------------------------------------------------

class UNISEARCH_PT_sidebar_panel(bpy.types.Panel):
    bl_label = "UniSearch"
    bl_idname = "UNISEARCH_PT_sidebar_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UniSearch"

    def draw(self, context):
        layout = self.layout
        state = get_state(context)

        search_col = layout.column(align=True)

        search_col.prop(
            state,
            "search_query",
            text="",
        )

        row = search_col.row(align=True)

        row.operator(
            UNISEARCH_OT_search.bl_idname,
            text="SEARCH",
            icon="VIEWZOOM",
        )

        row.operator(
            UNISEARCH_OT_clear_results.bl_idname,
            text="",
            icon="X",
        )

        draw_panel_message(layout, context, state)

        layout.separator()

        pinned_box = layout.box()
        pinned_box.label(text="Pinned", icon="PINNED")

        if len(state.pins) == 0:
            pinned_box.label(text="No pinned items.")

        for index, pin in enumerate(state.pins):
            draw_breadcrumb_item(
                layout=pinned_box,
                context=context,
                item=pin,
                action_kind="UNPIN",
                source="PINS",
                pin_number=index + 1,
            )

        layout.separator()

        results_box = layout.box()
        results_box.label(text="Results", icon="VIEWZOOM")

        if len(state.results) == 0:
            results_box.label(text="No results.")

        for result in state.results:
            pin_index = find_pin_index(state, result.item_id)

            if pin_index == -1:
                draw_breadcrumb_item(
                    layout=results_box,
                    context=context,
                    item=result,
                    action_kind="PIN",
                    source="RESULTS",
                )
            else:
                draw_breadcrumb_item(
                    layout=results_box,
                    context=context,
                    item=result,
                    action_kind="PINNED",
                    source="RESULTS",
                    pin_number=pin_index + 1,
                )


# ------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------

classes = (
    UNISEARCH_AddonPreferences,
    UNISEARCH_BreadcrumbItem,
    UNISEARCH_State,
    UNISEARCH_OT_search,
    UNISEARCH_OT_pin_result,
    UNISEARCH_OT_unpin_result,
    UNISEARCH_OT_toggle_expand,
    UNISEARCH_OT_clear_results,
    UNISEARCH_PT_sidebar_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.unisearch_state = PointerProperty(
        type=UNISEARCH_State,
    )


def unregister():
    if hasattr(bpy.types.WindowManager, "unisearch_state"):
        del bpy.types.WindowManager.unisearch_state

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()