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