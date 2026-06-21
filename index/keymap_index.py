from ..providers.keymap_provider import (
    collect_keymap_candidates,
)


class KeymapIndex:

    def __init__(self):

        self.shortcuts = []

        self.by_target_id = {}

        self.by_operator_id = {}

        self.by_menu_id = {}

        self.by_pie_menu_id = {}

        self.duplicates_skipped = 0

    def build(self):

        self.shortcuts.clear()
        self.by_target_id.clear()
        self.by_operator_id.clear()
        self.by_menu_id.clear()
        self.by_pie_menu_id.clear()
        self.duplicates_skipped = 0

        candidates = collect_keymap_candidates()

        seen = set()

        for candidate in candidates:

            key = _candidate_key(candidate)

            if key in seen:
                self.duplicates_skipped += 1
                continue

            seen.add(key)
            self._add_candidate(candidate)

        print("\n")
        print("=" * 60)
        print("UNISEARCH KEYMAP INDEX")
        print("=" * 60)
        print("INDEXED SHORTCUTS:", len(self.shortcuts))
        print(
            "INDEX DUPLICATES SKIPPED:",
            self.duplicates_skipped,
        )
        print("=" * 60)

    def inspect_target(self, target_id):

        shortcuts = list(
            self.by_target_id.get(
                target_id,
                [],
            )
        )

        seen = {
            id(shortcut)
            for shortcut in shortcuts
        }

        for shortcut in self.by_operator_id.get(
            target_id,
            [],
        ):

            if id(shortcut) in seen:
                continue

            seen.add(id(shortcut))
            shortcuts.append(shortcut)

        return shortcuts

    def _add_candidate(self, candidate):

        self.shortcuts.append(candidate)

        self.by_target_id.setdefault(
            candidate.target_id,
            [],
        ).append(candidate)

        self.by_operator_id.setdefault(
            candidate.operator_id,
            [],
        ).append(candidate)

        if candidate.target_type == "OPERATOR":
            self.by_operator_id.setdefault(
                candidate.target_id,
                [],
            ).append(candidate)

        elif candidate.target_type == "MENU":
            self.by_menu_id.setdefault(
                candidate.target_id,
                [],
            ).append(candidate)

        elif candidate.target_type == "PIE_MENU":
            self.by_pie_menu_id.setdefault(
                candidate.target_id,
                [],
            ).append(candidate)


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
