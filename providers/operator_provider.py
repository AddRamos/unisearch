import bpy

from ..core.models import FeatureRecord


def make_label_from_operator_name(name):
    return name.replace("_", " ").title()


def collect_operator_features():

    features = []
    visited = set()

    categories_checked = 0
    operators_checked = 0
    operators_with_rna = 0
    operators_without_rna = 0

    for category_name in dir(bpy.ops):

        if category_name.startswith("_"):
            continue

        try:
            category = getattr(bpy.ops, category_name)
        except Exception:
            continue

        categories_checked += 1

        for operator_name in dir(category):

            if operator_name.startswith("_"):
                continue

            operator_id = f"{category_name}.{operator_name}"

            if operator_id in visited:
                continue

            visited.add(operator_id)
            operators_checked += 1

            try:
                operator = getattr(category, operator_name)
            except Exception:
                continue

            label = make_label_from_operator_name(operator_name)
            description = ""

            get_rna_type = getattr(operator, "get_rna_type", None)

            if callable(get_rna_type):
                try:
                    rna = get_rna_type()

                    label = getattr(
                        rna,
                        "name",
                        label,
                    )

                    description = getattr(
                        rna,
                        "description",
                        "",
                    )

                    operators_with_rna += 1

                except Exception:
                    operators_without_rna += 1
            else:
                operators_without_rna += 1

            features.append(
                FeatureRecord(
                    feature_id=f"operator:{operator_id}",
                    label=label,
                    identifier=operator_id,
                    feature_type="OPERATOR",
                    description=description,
                    source="OPERATOR",
                )
            )

    print("\n")
    print("=" * 60)
    print("OPERATOR PROVIDER")
    print("=" * 60)
    print("CATEGORIES CHECKED:", categories_checked)
    print("OPERATORS CHECKED:", operators_checked)
    print("OPERATORS WITH RNA:", operators_with_rna)
    print("OPERATORS WITHOUT RNA:", operators_without_rna)
    print("=" * 60)

    return features