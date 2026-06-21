import bpy

from ..core.models import KeymapCandidate


MENU_OPERATORS = {
    "wm.call_menu": "MENU",
    "wm.call_menu_pie": "PIE_MENU",
}


def collect_keymap_candidates():

    candidates = []

    wm = bpy.context.window_manager

    keyconfigs = _keyconfigs_to_scan(wm)

    keymaps_scanned = 0
    keymap_items_scanned = 0
    active_items = 0
    direct_operator_shortcuts = 0
    menu_shortcuts = 0
    pie_menu_shortcuts = 0
    duplicate_shortcuts = 0
    seen_shortcuts = set()

    for keyconfig in keyconfigs:

        for keymap in keyconfig.keymaps:

            keymaps_scanned += 1

            for item in keymap.keymap_items:

                keymap_items_scanned += 1

                if not item.active:
                    continue

                active_items += 1

                event = _event_string(item)

                if not event:
                    continue

                target_id = _menu_target_from_item(item)

                if target_id:
                    target_type = MENU_OPERATORS.get(
                        item.idname,
                        "MENU",
                    )

                    if target_type == "PIE_MENU":
                        pie_menu_shortcuts += 1
                    else:
                        menu_shortcuts += 1

                    candidate = _make_candidate(
                        target_id=target_id,
                        target_type=target_type,
                        keymap=keymap,
                        item=item,
                        event=event,
                    )

                    if _candidate_key(candidate) in seen_shortcuts:
                        duplicate_shortcuts += 1
                    else:
                        seen_shortcuts.add(
                            _candidate_key(candidate)
                        )
                        candidates.append(candidate)

                    continue

                if item.idname:
                    direct_operator_shortcuts += 1

                    candidate = _make_candidate(
                        target_id=item.idname,
                        target_type="OPERATOR",
                        keymap=keymap,
                        item=item,
                        event=event,
                    )

                    if _candidate_key(candidate) in seen_shortcuts:
                        duplicate_shortcuts += 1
                    else:
                        seen_shortcuts.add(
                            _candidate_key(candidate)
                        )
                        candidates.append(candidate)

    print("\n")
    print("=" * 60)
    print("UNISEARCH KEYMAP BUILD")
    print("=" * 60)
    print("KEYCONFIGS SCANNED:", len(keyconfigs))
    print("KEYMAPS SCANNED:", keymaps_scanned)
    print("KEYMAP ITEMS SCANNED:", keymap_items_scanned)
    print("ACTIVE KEYMAP ITEMS:", active_items)
    print("UNIQUE SHORTCUT CANDIDATES:", len(candidates))
    print("DUPLICATE SHORTCUTS SKIPPED:", duplicate_shortcuts)
    print("DIRECT OPERATOR SHORTCUTS:", direct_operator_shortcuts)
    print("MENU SHORTCUTS:", menu_shortcuts)
    print("PIE MENU SHORTCUTS:", pie_menu_shortcuts)
    print("=" * 60)

    return candidates


def _candidate_key(candidate):

    return (
        candidate.target_id,
        candidate.target_type,
        candidate.keymap_name,
        candidate.keymap_space_type,
        candidate.keymap_region_type,
        candidate.event,
        candidate.operator_id,
    )


def _keyconfigs_to_scan(wm):

    keyconfigs = []
    seen = set()

    for keyconfig in (
        wm.keyconfigs.active,
        wm.keyconfigs.user,
        wm.keyconfigs.addon,
    ):

        if keyconfig is None:
            continue

        name = getattr(
            keyconfig,
            "name",
            "",
        )

        if name in seen:
            continue

        seen.add(name)
        keyconfigs.append(keyconfig)

    return keyconfigs


def _menu_target_from_item(item):

    if item.idname not in MENU_OPERATORS:
        return ""

    properties = getattr(
        item,
        "properties",
        None,
    )

    if properties is None:
        return ""

    return getattr(
        properties,
        "name",
        "",
    )


def _make_candidate(
    target_id,
    target_type,
    keymap,
    item,
    event,
):

    return KeymapCandidate(
        target_id=target_id,
        target_type=target_type,
        keymap_name=keymap.name,
        keymap_space_type=keymap.space_type,
        keymap_region_type=keymap.region_type,
        event=event,
        operator_id=item.idname,
        is_active=item.active,
    )


def _event_string(item):

    parts = []

    if item.ctrl:
        parts.append("Ctrl")

    if item.shift:
        parts.append("Shift")

    if item.alt:
        parts.append("Alt")

    if item.oskey:
        parts.append("OSKey")

    key = _event_key(item)

    if not key:
        return ""

    parts.append(key)

    return "+".join(parts)


def _event_key(item):

    key = getattr(
        item,
        "type",
        "",
    )

    value = getattr(
        item,
        "value",
        "",
    )

    if not key or key in {
        "NONE",
    }:
        return ""

    if value and value not in {
        "PRESS",
        "NOTHING",
    }:
        return f"{key} {value.title()}"

    return key
