import bpy

from ..index.feature_index import (
    FeatureIndex,
)


FEATURE_INDEX = FeatureIndex()


class UNISEARCH_OT_build_index(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.build_feature_index"
    )

    bl_label = (
        "Build Feature Index"
    )

    def execute(self, context):

        FEATURE_INDEX.rebuild()

        self.report(
            {'INFO'},
            (
                f"Indexed "
                f"{len(FEATURE_INDEX.features)} "
                f"features"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_test_query(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.test_query"
    )

    bl_label = (
        "Test Query"
    )

    query: bpy.props.StringProperty()

    def execute(self, context):

        results = (
            FEATURE_INDEX.search(
                self.query
            )
        )

        print("\n")
        print("=" * 60)

        print(
            f"QUERY: {self.query}"
        )

        print(
            f"RESULTS: {len(results)}"
        )

        print("=" * 60)

        for feature in results[:20]:

            print(
                f"[{feature.feature_type}]",
                feature.label,
                "|",
                feature.identifier,
            )

            if feature.feature_type == (
                "RNA_PROPERTY"
            ):

                print(
                    "    owners:",
                    len(feature.owners)
                )

                print(
                    "    sample:",
                    feature.owners[:5]
                )

            if feature.feature_type == (
                "ADDON_PREFERENCE"
            ):

                print(
                    "    addon aliases:",
                    feature.aliases,
                )

                print(
                    "    owner:",
                    feature.owners[:1],
                )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"{len(results)} "
                f"results"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_inspect_locations(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.inspect_locations"
    )

    bl_label = (
        "Inspect Locations"
    )

    identifier: bpy.props.StringProperty()

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        locations = (
            FEATURE_INDEX
            .location_index
            .inspect_identifier(
                self.identifier
            )
        )

        print("\n")
        print("=" * 60)
        print(
            f"LOCATION INSPECT: {self.identifier}"
        )
        print(
            f"LOCATIONS: {len(locations)}"
        )
        print("=" * 60)

        for location in locations[:30]:

            print(
                f"[{location.source} {location.confidence}]",
                location.container_id,
                f"({location.container_type})",
            )

            print(
                "    feature:",
                location.feature_id,
            )

            print(
                "    call:",
                location.ui_call,
            )

            print(
                "    label:",
                location.container_label,
            )

            print(
                "    space/region/category:",
                location.bl_space_type,
                location.bl_region_type,
                location.bl_category,
            )

            print(
                "    source kind:",
                location.source_kind,
                location.addon_module,
            )

            print(
                "    file:",
                (
                    f"{location.source_file}:"
                    f"{location.line_number}"
                ),
            )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"{len(locations)} "
                f"locations for "
                f"{self.identifier}"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_inspect_container(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.inspect_container"
    )

    bl_label = (
        "Inspect Container"
    )

    container_id: bpy.props.StringProperty()

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        location_index = FEATURE_INDEX.location_index

        container = location_index.containers.get(
            self.container_id
        )

        locations = location_index.inspect_container(
            self.container_id
        )

        print("\n")
        print("=" * 60)
        print(
            f"CONTAINER INSPECT: {self.container_id}"
        )
        print("=" * 60)

        if container:
            print("type:", container.container_type)
            print("label:", container.bl_label)
            print("space:", container.bl_space_type)
            print("region:", container.bl_region_type)
            print("category:", container.bl_category)
            print("source kind:", container.source_kind)
            print("addon:", container.addon_module)
            print("file:", container.source_file)
        else:
            print("container metadata: not found")

        print("MATCHED LOCATIONS:", len(locations))
        print("=" * 60)

        for location in locations[:40]:
            print(
                f"[{location.confidence}]",
                location.feature_identifier,
                "|",
                location.feature_id,
                "|",
                location.ui_call,
                "|",
                f"{location.source_file}:"
                f"{location.line_number}",
            )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"{len(locations)} "
                f"locations in "
                f"{self.container_id}"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_inspect_unmatched_locations(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.inspect_unmatched_locations"
    )

    bl_label = (
        "Inspect Unmatched UI Calls"
    )

    limit: bpy.props.IntProperty(
        default=40,
        min=1,
        max=200,
    )

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        unmatched = (
            FEATURE_INDEX
            .location_index
            .inspect_unmatched(
                self.limit
            )
        )

        print("\n")
        print("=" * 60)
        print("UNMATCHED STATIC UI CALLS")
        print(
            "TOTAL:",
            FEATURE_INDEX.location_index.unmatched_calls,
        )
        print(
            "SHOWING:",
            len(unmatched),
        )
        print("=" * 60)

        for call in unmatched:
            print(
                f"[{call.source_kind}]",
                call.ui_call,
                call.identifier,
                "in",
                call.container_id,
                f"({call.container_type})",
            )

            print(
                "    label:",
                call.container_label,
            )

            print(
                "    addon:",
                call.addon_module,
            )

            print(
                "    file:",
                (
                    f"{call.source_file}:"
                    f"{call.line_number}"
                ),
            )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"Showing {len(unmatched)} "
                f"unmatched UI calls"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_list_addon_preferences(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.list_addon_preferences"
    )

    bl_label = (
        "List Addon Preferences"
    )

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        features = [
            feature
            for feature in FEATURE_INDEX.features
            if feature.feature_type == "ADDON_PREFERENCE"
        ]

        features.sort(
            key=lambda feature: (
                feature.aliases[0] if feature.aliases else "",
                feature.identifier,
            )
        )

        print("\n")
        print("=" * 60)
        print("ADDON PREFERENCE FEATURES")
        print("TOTAL:", len(features))
        print("=" * 60)

        for feature in features:

            locations = (
                FEATURE_INDEX
                .location_index
                .inspect_identifier(
                    feature.identifier
                )
            )

            addon_label = (
                feature.aliases[0]
                if feature.aliases
                else ""
            )

            print(
                feature.identifier,
                "|",
                feature.label,
                "|",
                addon_label,
                "|",
                feature.feature_id,
            )

            print(
                "    owner:",
                feature.owners[:1],
            )

            print(
                "    locations:",
                len(locations),
            )

            for location in locations[:5]:
                print(
                    "    -",
                    location.container_id,
                    f"[{location.confidence}]",
                    location.ui_call,
                    f"{location.source_file}:"
                    f"{location.line_number}",
                )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"Listed {len(features)} "
                f"addon preference features"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_inspect_keymap(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.inspect_keymap"
    )

    bl_label = (
        "Inspect Keymap"
    )

    target_id: bpy.props.StringProperty()

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        shortcuts = (
            FEATURE_INDEX
            .keymap_index
            .inspect_target(
                self.target_id
            )
        )

        print("\n")
        print("=" * 60)
        print(
            f"KEYMAP INSPECT: {self.target_id}"
        )
        print(
            f"SHORTCUTS: {len(shortcuts)}"
        )
        print("=" * 60)

        for shortcut in shortcuts[:40]:
            print(
                f"[{shortcut.target_type}]",
                shortcut.event,
                "|",
                shortcut.keymap_name,
                "|",
                shortcut.keymap_space_type,
                shortcut.keymap_region_type,
            )

            print(
                "    operator:",
                shortcut.operator_id,
            )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"{len(shortcuts)} "
                f"shortcuts for "
                f"{self.target_id}"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_inspect_modes(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.inspect_modes"
    )

    bl_label = (
        "Inspect Modes"
    )

    identifier: bpy.props.StringProperty()

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        candidates = (
            FEATURE_INDEX
            .mode_index
            .inspect_identifier(
                self.identifier
            )
        )

        print("\n")
        print("=" * 60)
        print(
            f"MODE INSPECT: {self.identifier}"
        )
        print(
            f"MODE CANDIDATES: {len(candidates)}"
        )
        print("=" * 60)

        if not candidates:
            print("mode: UNKNOWN")
            print("reason: no reliable mode evidence")
        else:
            for candidate in candidates[:30]:
                print(
                    f"[{candidate.source} {candidate.confidence}]",
                    candidate.mode,
                )

                print(
                    "    evidence:",
                    candidate.evidence,
                )

                if candidate.container_id:
                    print(
                        "    container:",
                        candidate.container_id,
                    )

                if candidate.keymap_name:
                    print(
                        "    keymap:",
                        candidate.keymap_name,
                    )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"{len(candidates)} "
                f"mode candidates for "
                f"{self.identifier}"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_inspect_resolved_locations(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.inspect_resolved_locations"
    )

    bl_label = (
        "Inspect Resolved Locations"
    )

    identifier: bpy.props.StringProperty()

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        resolved_locations = (
            FEATURE_INDEX
            .resolved_location_index
            .inspect_identifier(
                self.identifier
            )
        )

        print("\n")
        print("=" * 60)
        print(
            f"RESOLVED LOCATION INSPECT: {self.identifier}"
        )
        print(
            f"RESOLVED LOCATIONS: {len(resolved_locations)}"
        )
        print("=" * 60)

        if not resolved_locations:
            print("resolved location: none")
        else:
            for resolved in resolved_locations[:30]:
                print(
                    f"[{resolved.confidence}]",
                    resolved.mode,
                    "|",
                    resolved.editor,
                    resolved.region,
                    "|",
                    resolved.container_id,
                    f"({resolved.container_type})",
                )

                print(
                    "    feature:",
                    resolved.feature_id,
                    "|",
                    resolved.feature_label,
                )

                print(
                    "    container label:",
                    resolved.container_label,
                )

                print(
                    "    shortcut:",
                    resolved.shortcut or "None",
                )

                print(
                    "    shortcut kind:",
                    resolved.shortcut_kind or "None",
                )

                print(
                    "    sources:",
                    resolved.location_source,
                    resolved.mode_source,
                    resolved.shortcut_source,
                )

                print(
                    "    evidence:",
                    resolved.evidence,
                )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"{len(resolved_locations)} "
                f"resolved locations for "
                f"{self.identifier}"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_inspect_breadcrumbs(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.inspect_breadcrumbs"
    )

    bl_label = (
        "Inspect Breadcrumbs"
    )

    identifier: bpy.props.StringProperty()

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        breadcrumbs = (
            FEATURE_INDEX
            .breadcrumb_index
            .inspect_identifier(
                self.identifier
            )
        )

        print("\n")
        print("=" * 60)
        print(
            f"BREADCRUMB INSPECT: {self.identifier}"
        )
        print(
            f"BREADCRUMBS: {len(breadcrumbs)}"
        )
        print("=" * 60)

        if not breadcrumbs:
            print("breadcrumb: none")
        else:
            for breadcrumb in breadcrumbs[:30]:
                print(
                    f"[{breadcrumb.confidence}]",
                    breadcrumb.breadcrumb,
                )

                print(
                    "    parts:",
                    breadcrumb.breadcrumb_parts,
                )

                print(
                    "    shortcut:",
                    breadcrumb.shortcut or "None",
                    breadcrumb.shortcut_kind or "",
                )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"{len(breadcrumbs)} "
                f"breadcrumbs for "
                f"{self.identifier}"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_inspect_runtime_verification(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.inspect_runtime_verification"
    )

    bl_label = (
        "Inspect Runtime Verification"
    )

    identifier: bpy.props.StringProperty()

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        records = (
            FEATURE_INDEX
            .runtime_verification_index
            .inspect_identifier(
                self.identifier
            )
        )

        print("\n")
        print("=" * 60)
        print(
            f"RUNTIME VERIFY INSPECT: {self.identifier}"
        )
        print(
            f"RECORDS: {len(records)}"
        )
        print("=" * 60)

        if not records:
            print("runtime verification: none")
        else:
            for record in records[:30]:
                print(
                    f"[{record.status}]",
                    record.container_id,
                )

                print(
                    "    feature verified:",
                    record.feature_verified,
                )

                print(
                    "    container verified:",
                    record.container_verified,
                )

                print(
                    "    detail:",
                    record.detail,
                )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"{len(records)} "
                f"runtime records for "
                f"{self.identifier}"
            )
        )

        return {'FINISHED'}


class UNISEARCH_OT_list_runtime_outliers(
    bpy.types.Operator
):
    bl_idname = (
        "unisearch.list_runtime_outliers"
    )

    bl_label = (
        "List Runtime Outliers"
    )

    limit: bpy.props.IntProperty(
        default=40,
        min=1,
        max=200,
    )

    def execute(self, context):

        if not FEATURE_INDEX.features:
            FEATURE_INDEX.rebuild()

        runtime_index = FEATURE_INDEX.runtime_verification_index

        partial = runtime_index.inspect_status(
            "PARTIAL",
            self.limit,
        )

        remaining = max(
            0,
            self.limit - len(partial),
        )

        unverified = runtime_index.inspect_status(
            "UNVERIFIED",
            remaining,
        )

        records = partial + unverified

        print("\n")
        print("=" * 60)
        print("RUNTIME VERIFICATION OUTLIERS")
        print("PARTIAL TOTAL:", runtime_index.partial)
        print("UNVERIFIED TOTAL:", runtime_index.unverified)
        print("SHOWING:", len(records))
        print("=" * 60)

        if not records:
            print("No runtime verification outliers.")
        else:
            for record in records:
                print(
                    f"[{record.status}]",
                    record.feature_identifier,
                    "|",
                    record.container_id,
                )

                print(
                    "    feature:",
                    record.feature_id,
                )

                print(
                    "    feature/container verified:",
                    record.feature_verified,
                    record.container_verified,
                )

                print(
                    "    detail:",
                    record.detail,
                )

        print("=" * 60)

        self.report(
            {'INFO'},
            (
                f"Showing {len(records)} "
                f"runtime outliers"
            )
        )

        return {'FINISHED'}
