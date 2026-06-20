# Python Source Collection

## __init__-core.py

```python

```

## __init__-debug.py

```python

```

## __init__-index.py

```python

```

## __init__-providers.py

```python

```

## __init__-unisearch.py

```python
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
```

## debug_operators-debug.py

```python
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
```

## debug_panel-debug.py

```python
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

        col = layout.column()

        for query in (
            "cavity",
            "delete",
            "save",
            "xray",
            "bevel",
        ):

            op = col.operator(
                "unisearch.test_query",
                text=query,
            )

            op.query = query
```

## feature_index-index.py

```python
from ..providers.rna_provider import (
    collect_rna_features,
)

from ..providers.operator_provider import (
    collect_operator_features,
)


class FeatureIndex:

    def __init__(self):

        self.features = []

        self.by_id = {}

    def rebuild(self):

        self.features.clear()
        self.by_id.clear()

        rna_features = collect_rna_features()

        operator_features = collect_operator_features()

        #
        # NEW DEBUG SECTION
        #

        unique_identifiers = {
            feature.identifier
            for feature in rna_features
        }

        unique_labels = {
            feature.label
            for feature in rna_features
        }

        print("\n")
        print("=" * 60)
        print("UNISEARCH FEATURE BUILD")
        print("=" * 60)

        print(
            "NORMALIZED RNA FEATURES:",
            len(rna_features)
        )

        print(
            "OPERATOR FEATURES:",
            len(operator_features)
        )

        print(
            "TOTAL SEARCHABLE FEATURES:",
            (
                len(rna_features)
                +
                len(operator_features)
            )
        )

        print("=" * 60)

        #
        # EXISTING BUILD
        #

        all_features = []

        all_features.extend(rna_features)

        all_features.extend(operator_features)

        for feature in all_features:

            self.features.append(feature)

            self.by_id[
                feature.feature_id
            ] = feature

    def search(self, query):

        query = query.lower().strip()

        if not query:
            return []

        results = []

        for feature in self.features:

            label = feature.label.lower()

            identifier = (
                feature.identifier.lower()
            )

            description = (
                feature.description.lower()
            )

            if (
                query in label
                or query in identifier
            ):
                results.append(feature)

        return results
```

## gatherFiles-unisearch.py

```python
import shutil
from pathlib import Path


def flatten_and_rename_py_files():
    # 1. Get the directory where this script is running
    root_dir = Path(__file__).resolve().parent

    # 2. Define the target directory named 'all.py'
    target_dir = root_dir / "all.py"

    # Create the 'all.py' directory if it doesn't exist
    target_dir.mkdir(exist_ok=True)

    print(f"Scanning for .py files in: {root_dir}")
    print(f"Copying files to: {target_dir}\n")

    # 3. Find all .py files recursively using rglob
    for file_path in root_dir.rglob("*.py"):
        # Skip files that are already inside the target 'all.py' folder
        if target_dir in file_path.parents:
            continue

        # Get the immediate parent folder's name
        parent_name = file_path.parent.name

        # file_path.stem gives the filename without extension (e.g., 'models')
        # file_path.suffix gives the extension (e.g., '.py')
        new_filename = f"{file_path.stem}-{parent_name}{file_path.suffix}"
        destination_path = target_dir / new_filename

        try:
            # 4. Copy the file to the new location
            shutil.copy2(file_path, destination_path)
            print(
                f"Copied: {file_path.relative_to(root_dir)} -> {new_filename}"
            )
        except Exception as e:
            print(f"Error copying {file_path.name}: {e}")


if __name__ == "__main__":
    flatten_and_rename_py_files()
```

## joinpy.py

```python
from pathlib import Path

# Folder containing the .py files
SOURCE_DIR = Path(__file__).resolve().parent

# Output markdown file
OUTPUT_MD = "combined_python_files.md"


def combine_py_to_md(source_dir, output_file):
    source_path = Path(source_dir)

    py_files = sorted(source_path.glob("*.py"))

    if not py_files:
        print("No .py files found.")
        return

    with open(output_file, "w", encoding="utf-8") as md:

        md.write("# Python Source Collection\n\n")

        for py_file in py_files:
            print(f"Processing: {py_file.name}")

            # Use filename as title
            md.write(f"## {py_file.name}\n\n")

            # Markdown code block
            md.write("```python\n")

            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                md.write(f.read())

            md.write("\n```\n\n")

    print(f"\nDone. Output saved to: {output_file}")


if __name__ == "__main__":
    combine_py_to_md(SOURCE_DIR, OUTPUT_MD)
```

## models-core.py

```python
from dataclasses import dataclass, field


@dataclass
class FeatureRecord:

    feature_id: str

    label: str

    identifier: str

    feature_type: str

    description: str = ""

    source: str = ""

    aliases: list[str] = field(
        default_factory=list
    )

    owners: list[str] = field(
        default_factory=list
    )
```

## operator_provider-providers.py

```python
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
```

## rna_provider-providers.py

```python
import bpy

from ..core.models import (
    FeatureRecord,
)


def collect_rna_features():

    #
    # KEY:
    #
    # identifier -> normalized feature
    #

    normalized = {}

    for cls_name in dir(bpy.types):

        cls = getattr(
            bpy.types,
            cls_name,
        )

        rna = getattr(
            cls,
            "bl_rna",
            None,
        )

        if rna is None:
            continue

        properties = getattr(
            rna,
            "properties",
            None,
        )

        if properties is None:
            continue

        for prop in properties:

            identifier = getattr(
                prop,
                "identifier",
                "",
            )

            if not identifier:
                continue

            label = getattr(
                prop,
                "name",
                identifier,
            )

            description = getattr(
                prop,
                "description",
                "",
            )

            #
            # Create feature once
            #

            if identifier not in normalized:

                normalized[
                    identifier
                ] = FeatureRecord(
                    feature_id=(
                        f"rna:{identifier}"
                    ),
                    label=label,
                    identifier=identifier,
                    feature_type=(
                        "RNA_PROPERTY"
                    ),
                    description=description,
                    source="RNA",
                )

            #
            # Track owner class
            #

            feature = normalized[
                identifier
            ]

            if cls_name not in feature.owners:

                feature.owners.append(
                    cls_name
                )

    return list(
        normalized.values()
    )
```

## tokenizer-core.py

```python
import re


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text: str) -> list[str]:
    if not text:
        return []

    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
    ]
```

