import ast
from dataclasses import dataclass
from pathlib import Path

import addon_utils
import bpy


UI_CALL_NAMES = {
    "menu",
    "menu_pie",
    "operator",
    "operator_enum",
    "operator_menu_enum",
    "popover",
    "prop",
    "prop_enum",
    "prop_menu_enum",
    "template_ID",
    "template_list",
}


@dataclass
class StaticUIContainer:

    container_id: str

    container_type: str

    source_file: str

    source_kind: str

    addon_module: str = ""

    bl_label: str = ""

    bl_space_type: str = ""

    bl_region_type: str = ""

    bl_category: str = ""


@dataclass
class StaticUICall:

    identifier: str

    ui_call: str

    container_id: str

    container_type: str

    source_file: str

    line_number: int

    source_kind: str

    addon_module: str = ""

    container_label: str = ""

    bl_space_type: str = ""

    bl_region_type: str = ""

    bl_category: str = ""


@dataclass
class StaticUIScanResult:

    calls: list[StaticUICall]

    containers: dict[str, StaticUIContainer]

    files_scanned: int = 0

    core_files_scanned: int = 0

    addon_files_scanned: int = 0

    containers_discovered: int = 0

    call_counts: dict[str, int] = None

    def __post_init__(self):

        if self.call_counts is None:
            self.call_counts = {}


def collect_static_ui_calls():

    result = StaticUIScanResult(
        calls=[],
        containers={},
    )

    for source_root, source_kind, addon_module in _iter_ui_source_roots():

        if not source_root.exists():
            continue

        for path in _iter_python_files(source_root):

            _scan_file(
                path,
                source_kind,
                addon_module,
                result,
            )

    return result


def _iter_ui_source_roots():

    seen = set()

    for resource_kind in (
        "LOCAL",
        "SYSTEM",
        "USER",
    ):

        try:
            resource_path = bpy.utils.resource_path(
                resource_kind
            )
        except Exception:
            continue

        if not resource_path:
            continue

        source_root = (
            Path(resource_path)
            / "scripts"
            / "startup"
            / "bl_ui"
        )

        yield from _dedupe_root(
            source_root,
            "CORE",
            "",
            seen,
        )

    for module in addon_utils.modules():

        if not _is_addon_enabled(module):
            continue

        module_file = getattr(
            module,
            "__file__",
            "",
        )

        if not module_file:
            continue

        module_name = getattr(
            module,
            "__name__",
            "",
        )

        module_path = Path(module_file)

        if module_path.name == "__init__.py":
            source_root = module_path.parent
        else:
            source_root = module_path

        yield from _dedupe_root(
            source_root,
            "ADDON",
            module_name,
            seen,
        )


def _dedupe_root(path, source_kind, addon_module, seen):

    try:
        normalized = str(path.resolve())
    except OSError:
        normalized = str(path)

    if normalized in seen:
        return

    seen.add(normalized)

    yield path, source_kind, addon_module


def _is_addon_enabled(module):

    module_name = getattr(
        module,
        "__name__",
        "",
    )

    if not module_name:
        return False

    try:
        return bool(
            addon_utils.check(module_name)[1]
        )
    except Exception:
        return False


def _iter_python_files(source_root):

    if source_root.is_file():

        if source_root.suffix == ".py":
            yield source_root

        return

    yield from sorted(source_root.rglob("*.py"))


def _scan_file(
    path,
    source_kind,
    addon_module,
    result,
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

    if source_kind == "CORE":
        result.core_files_scanned += 1
    elif source_kind == "ADDON":
        result.addon_files_scanned += 1

    for node in tree.body:

        if not isinstance(node, ast.ClassDef):
            continue

        container = _container_from_class(
            node,
            str(path),
            source_kind,
            addon_module,
        )

        if not container:
            continue

        result.containers_discovered += 1

        result.containers[
            container.container_id
        ] = container

        for item in node.body:

            if (
                isinstance(item, ast.FunctionDef)
                and item.name == "draw"
            ):
                _scan_draw_function(
                    item,
                    container,
                    result,
                )


def _container_from_class(
    node,
    source_file,
    source_kind,
    addon_module,
):

    container_type = _container_type_from_class(node)

    if not container_type:
        return None

    class_values = _class_string_values(node)

    return StaticUIContainer(
        container_id=node.name,
        container_type=container_type,
        source_file=source_file,
        source_kind=source_kind,
        addon_module=addon_module,
        bl_label=class_values.get(
            "bl_label",
            "",
        ),
        bl_space_type=class_values.get(
            "bl_space_type",
            "",
        ),
        bl_region_type=class_values.get(
            "bl_region_type",
            "",
        ),
        bl_category=class_values.get(
            "bl_category",
            "",
        ),
    )


def _container_type_from_class(node):

    for base in node.bases:

        name = _node_name(base)

        if name in {
            "Panel",
            "bpy.types.Panel",
        }:
            return "PANEL"

        if name in {
            "Menu",
            "bpy.types.Menu",
        }:
            return "MENU"

        if name in {
            "Header",
            "bpy.types.Header",
        }:
            return "HEADER"

        if name in {
            "UIList",
            "bpy.types.UIList",
        }:
            return "UILIST"

    return ""


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


def _scan_draw_function(
    function_node,
    container,
    result,
):

    for node in ast.walk(function_node):

        if not isinstance(node, ast.Call):
            continue

        call_name = _call_name(node.func)

        if call_name not in UI_CALL_NAMES:
            continue

        identifier = _identifier_from_call(
            call_name,
            node,
        )

        _count_call(
            call_name,
            result,
        )

        if not identifier:
            continue

        result.calls.append(
            StaticUICall(
                identifier=identifier,
                ui_call=call_name,
                container_id=container.container_id,
                container_type=container.container_type,
                source_file=container.source_file,
                line_number=getattr(
                    node,
                    "lineno",
                    0,
                ),
                source_kind=container.source_kind,
                addon_module=container.addon_module,
                container_label=container.bl_label,
                bl_space_type=container.bl_space_type,
                bl_region_type=container.bl_region_type,
                bl_category=container.bl_category,
            )
        )


def _identifier_from_call(call_name, node):

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

    if call_name in {
        "operator",
        "operator_enum",
        "operator_menu_enum",
        "menu",
    }:
        return _string_arg(
            node,
            0,
        )

    if call_name == "popover":
        return _string_keyword(
            node,
            "panel",
        ) or _string_arg(
            node,
            0,
        )

    if call_name == "template_list":
        return _string_arg(
            node,
            0,
        )

    if call_name == "menu_pie":
        return "menu_pie"

    return ""


def _count_call(call_name, result):

    result.call_counts[call_name] = (
        result.call_counts.get(
            call_name,
            0,
        )
        + 1
    )


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
