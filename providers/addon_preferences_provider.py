import ast
from dataclasses import dataclass
from pathlib import Path

import addon_utils

from ..core.models import (
    FeatureRecord,
    LocationCandidate,
)
from .static_ui_provider import StaticUIContainer


PREFERENCE_UI_CALLS = {
    "prop",
    "prop_enum",
    "prop_menu_enum",
    "template_ID",
}


@dataclass
class AddonPreferenceBuildResult:

    features: list[FeatureRecord]

    locations: list[LocationCandidate]

    containers: dict[str, StaticUIContainer]

    files_scanned: int = 0

    preference_classes: int = 0

    properties_discovered: int = 0

    drawn_properties: int = 0


@dataclass
class _AddonSource:

    module_name: str

    display_name: str

    path: Path


@dataclass
class _PreferenceProperty:

    identifier: str

    label: str

    description: str


def collect_addon_preference_data():

    result = AddonPreferenceBuildResult(
        features=[],
        locations=[],
        containers={},
    )

    seen_features = set()

    for addon_source in _iter_enabled_addon_sources():

        if not addon_source.path.exists():
            continue

        for path in _iter_python_files(addon_source.path):

            _scan_file(
                path,
                addon_source,
                result,
                seen_features,
            )

    print("\n")
    print("=" * 60)
    print("UNISEARCH ADDON PREFERENCES BUILD")
    print("=" * 60)
    print("ADDON PREFERENCE FILES SCANNED:", result.files_scanned)
    print("ADDON PREFERENCE CLASSES:", result.preference_classes)
    print("ADDON PREFERENCE PROPERTIES:", result.properties_discovered)
    print("ADDON PREFERENCE FEATURES:", len(result.features))
    print("ADDON PREFERENCE LOCATIONS:", len(result.locations))
    print("ADDON PREFERENCE DRAWN PROPERTIES:", result.drawn_properties)
    print("=" * 60)

    return result


def _iter_enabled_addon_sources():

    seen = set()

    for module in addon_utils.modules():

        module_name = getattr(
            module,
            "__name__",
            "",
        )

        if not module_name:
            continue

        try:
            is_enabled = bool(
                addon_utils.check(module_name)[1]
            )
        except Exception:
            is_enabled = False

        if not is_enabled:
            continue

        module_file = getattr(
            module,
            "__file__",
            "",
        )

        if not module_file:
            continue

        module_path = Path(module_file)

        if module_path.name == "__init__.py":
            source_path = module_path.parent
        else:
            source_path = module_path

        try:
            normalized = str(source_path.resolve())
        except OSError:
            normalized = str(source_path)

        if normalized in seen:
            continue

        seen.add(normalized)

        bl_info = getattr(
            module,
            "bl_info",
            {},
        )

        display_name = bl_info.get(
            "name",
            module_name,
        )

        yield _AddonSource(
            module_name=module_name,
            display_name=display_name,
            path=source_path,
        )


def _iter_python_files(source_path):

    if source_path.is_file():

        if source_path.suffix == ".py":
            yield source_path

        return

    yield from sorted(source_path.rglob("*.py"))


def _scan_file(
    path,
    addon_source,
    result,
    seen_features,
):

    try:
        source = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except OSError:
        return

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )
    except SyntaxError:
        return

    result.files_scanned += 1

    for node in tree.body:

        if not isinstance(node, ast.ClassDef):
            continue

        if not _is_addon_preferences_class(node):
            continue

        _scan_preference_class(
            node,
            path,
            addon_source,
            result,
            seen_features,
        )


def _is_addon_preferences_class(node):

    for base in node.bases:

        name = _node_name(base)

        if name in {
            "AddonPreferences",
            "bpy.types.AddonPreferences",
        }:
            return True

    return False


def _scan_preference_class(
    node,
    path,
    addon_source,
    result,
    seen_features,
):

    result.preference_classes += 1

    class_values = _class_string_values(node)

    bl_idname = class_values.get(
        "bl_idname",
        addon_source.module_name,
    )

    container_id = f"ADDON_PREFS:{bl_idname}"

    container = StaticUIContainer(
        container_id=container_id,
        container_type="ADDON_PREFERENCES",
        source_file=str(path),
        source_kind="ADDON_PREFERENCES",
        addon_module=addon_source.module_name,
        bl_label=addon_source.display_name,
        bl_space_type="PREFERENCES",
        bl_region_type="ADDONS",
        bl_category="Add-ons",
    )

    result.containers[container_id] = container

    properties = _preference_properties_from_class(node)

    result.properties_discovered += len(properties)

    drawn_identifiers = _drawn_preference_identifiers(node)

    result.drawn_properties += len(drawn_identifiers)

    for identifier in sorted(
        set(properties.keys()) | set(drawn_identifiers)
    ):

        prop = properties.get(
            identifier,
            _PreferenceProperty(
                identifier=identifier,
                label=_label_from_identifier(identifier),
                description="",
            ),
        )

        feature = _make_feature(
            prop,
            node.name,
            bl_idname,
            addon_source,
        )

        if feature.feature_id not in seen_features:
            seen_features.add(feature.feature_id)
            result.features.append(feature)

        line_number = drawn_identifiers.get(
            identifier,
            getattr(node, "lineno", 0),
        )

        result.locations.append(
            LocationCandidate(
                feature_id=feature.feature_id,
                feature_identifier=feature.identifier,
                container_id=container_id,
                container_type="ADDON_PREFERENCES",
                source_file=str(path),
                line_number=line_number,
                source="ADDON_PREFERENCES",
                confidence=95
                if identifier in drawn_identifiers
                else 70,
                ui_call="addon_preferences.draw"
                if identifier in drawn_identifiers
                else "addon_preferences.property",
                source_kind="ADDON_PREFERENCES",
                addon_module=addon_source.module_name,
                container_label=addon_source.display_name,
                bl_space_type="PREFERENCES",
                bl_region_type="ADDONS",
                bl_category="Add-ons",
            )
        )


def _preference_properties_from_class(node):

    properties = {}

    for item in node.body:

        target_name = ""
        value_node = None

        if isinstance(item, ast.AnnAssign):
            target_name = _assignment_target_name(
                item.target
            )
            value_node = item.value or item.annotation

        elif isinstance(item, ast.Assign):

            if len(item.targets) != 1:
                continue

            target_name = _assignment_target_name(
                item.targets[0]
            )
            value_node = item.value

        if not target_name:
            continue

        if not _is_property_call(value_node):
            continue

        properties[target_name] = _PreferenceProperty(
            identifier=target_name,
            label=_string_keyword(
                value_node,
                "name",
            )
            or _label_from_identifier(target_name),
            description=_string_keyword(
                value_node,
                "description",
            ),
        )

    return properties


def _drawn_preference_identifiers(node):

    identifiers = {}

    for item in node.body:

        if not (
            isinstance(item, ast.FunctionDef)
            and item.name == "draw"
        ):
            continue

        for call in ast.walk(item):

            if not isinstance(call, ast.Call):
                continue

            call_name = _call_name(call.func)

            if call_name not in PREFERENCE_UI_CALLS:
                continue

            identifier = _identifier_from_preference_call(
                call_name,
                call,
            )

            if not identifier:
                continue

            identifiers[identifier] = getattr(
                call,
                "lineno",
                0,
            )

    return identifiers


def _identifier_from_preference_call(call_name, node):

    if call_name in {
        "prop",
        "prop_enum",
        "prop_menu_enum",
        "template_ID",
    }:
        return _string_arg(
            node,
            1,
        )

    return ""


def _make_feature(
    prop,
    class_name,
    bl_idname,
    addon_source,
):

    return FeatureRecord(
        feature_id=(
            f"addon_pref:"
            f"{bl_idname}:"
            f"{prop.identifier}"
        ),
        label=prop.label,
        identifier=prop.identifier,
        feature_type="ADDON_PREFERENCE",
        description=prop.description,
        source="ADDON_PREFERENCES",
        aliases=[
            addon_source.display_name,
            addon_source.module_name,
            bl_idname,
        ],
        owners=[
            class_name,
        ],
    )


def _is_property_call(node):

    if not isinstance(node, ast.Call):
        return False

    name = _node_name(node.func)

    return name.endswith("Property")


def _class_string_values(node):

    values = {}

    for item in node.body:

        target_name = ""
        value_node = None

        if isinstance(item, ast.Assign):

            if len(item.targets) != 1:
                continue

            target_name = _assignment_target_name(
                item.targets[0]
            )
            value_node = item.value

        elif isinstance(item, ast.AnnAssign):
            target_name = _assignment_target_name(
                item.target
            )
            value_node = item.value

        if not target_name or value_node is None:
            continue

        value = _literal_string(value_node)

        if value:
            values[target_name] = value

    return values


def _assignment_target_name(node):

    if isinstance(node, ast.Name):
        return node.id

    return ""


def _label_from_identifier(identifier):

    return identifier.replace(
        "_",
        " ",
    ).title()


def _string_arg(node, index):

    if len(node.args) <= index:
        return ""

    return _literal_string(node.args[index])


def _string_keyword(node, name):

    for keyword in node.keywords:

        if keyword.arg == name:
            return _literal_string(keyword.value)

    return ""


def _literal_string(node):

    if isinstance(node, ast.Constant) and isinstance(
        node.value,
        str,
    ):
        return node.value

    return ""


def _call_name(node):

    if isinstance(node, ast.Attribute):
        return node.attr

    if isinstance(node, ast.Name):
        return node.id

    return ""


def _node_name(node):

    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent = _node_name(node.value)

        if parent:
            return f"{parent}.{node.attr}"

        return node.attr

    return ""
