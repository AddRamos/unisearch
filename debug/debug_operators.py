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
