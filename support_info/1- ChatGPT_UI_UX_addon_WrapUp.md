## UniSearch Add-on — Current Prototype Brief

We created the first UI/UX prototype for a Blender add-on called **UniSearch**.

The goal of the add-on is to eventually become a universal search interface for Blender, able to find:

```text
commands
menus
panels
buttons
preferences
extension settings
renamed or moved features
```

The long-term search result style should use complete breadcrumb paths, for example:

```text
Object Mode > 3D Viewport > Shading Header > Cavity
Sculpt Mode > 3D Viewport > Auto Masking Header > Cavity
Texture Paint Mode > 3D Viewport > Masking Header > Cavity Mask
```

The key rule is: breadcrumbs must be exact and complete. Not generic.

Bad:

```text
3D Viewport > Header > Cavity
```

Good:

```text
Object Mode > 3D Viewport > Shading Header > Cavity
```

---

# Current implemented phase

## Version

```text
UniSearch UI Prototype
Version: 0.1.1
Target: Blender 4.2+
Designed conservatively for future Blender 5.x compatibility
```

## Scope

This phase is **UI/UX only**.

No real search functionality yet.

The add-on currently uses fixed dummy data so the panel behavior can be tested.

---

# Current UI location

The add-on creates a Sidebar/N-panel tab:

```text
3D Viewport > Sidebar / N-panel > UniSearch
```

Panel name:

```text
UniSearch
```

---

# Current panel layout

The panel follows this structure:

```text
+--------------------------------------------------+
| Search field                                     |
|                                                  |
| [SEARCH] [clear icon]                            |
|                                                  |
| occasional inline messages                       |
|                                                  |
| Pinned                                           |
| Breadcrumb...                              icon   |
| Breadcrumb...                              icon   |
|                                                  |
| Results                                          |
| Breadcrumb...                              icon   |
| Breadcrumb...                              icon   |
| Breadcrumb...                              icon   |
+--------------------------------------------------+
```

The active `PIN` and `UNPIN` buttons are now **icon-only**.

`PINNED #n` is still displayed as disabled text/status so the user knows that a result is already pinned and where it is in the pinned list.

---

# Current search behavior

The search field must contain text.

If the user presses `SEARCH` with an empty field:

```text
No results appear
Existing results are cleared
Inline message appears:
"Type something to search."
```

If the user types anything and presses `SEARCH`:

```text
The same fixed dummy results appear
```

The query text does not affect results yet.

---

# Dummy results currently used

The prototype returns fixed breadcrumbs like:

```text
DUMMY MODE > DUMMY MENU > DUMMY MENU > DUMMY DATA
DUMMY MODE > DUMMY HEADER > DUMMY DATA
DUMMY MODE > DUMMY PANEL > DUMMY BUTTON > DUMMY DATA
DUMMY MODE > DUMMY PREFERENCES > DUMMY SECTION > DUMMY SETTING
DUMMY MODE > DUMMY EDITOR > DUMMY TOOLBAR > DUMMY TOOL
DUMMY MODE > DUMMY CONTEXT MENU > DUMMY OPERATOR > DUMMY DATA
```

Internally, breadcrumbs are stored as parts, not just flat strings:

```python
["DUMMY MODE", "DUMMY PREFERENCES", "DUMMY SECTION", "DUMMY SETTING"]
```

This was intentional, so future real search can return structured breadcrumb data.

---

# Pin behavior

Each result can be pinned.

If the result is not pinned:

```text
Breadcrumb...    [pin icon]
```

If the result is already pinned:

```text
Breadcrumb...    PINNED #2
```

Duplicate pins are blocked.

If a duplicate pin attempt happens internally, the inline message says:

```text
Already in pinned list: Pin #2
```

Pinned items are displayed above results.

Pinned items have an icon-only unpin button.

---

# Pin storage

Pinned items are **session-only**.

They are stored in:

```python
bpy.types.WindowManager
```

They are not intended to be saved permanently into the `.blend` file.

Addon preferences are persistent, but pins are temporary.

---

# Add-on preferences

Current preferences:

```text
Maximum Number of Pins
Allow Pin Rollover
```

Default:

```text
Maximum Number of Pins: 5
Allow Pin Rollover: enabled
```

Range:

```text
1 to 50 pins
```

---

# Max pin behavior

If the pin list is full and rollover is enabled:

```text
Oldest pin is removed
New pin is added to the end
```

If the pin list is full and rollover is disabled:

```text
New pin is blocked
Inline warning appears:
"Your pinned list is full. Unpin some pinned elements to make space."
```

Important decision:

```text
If max pins is lowered, existing pins are not auto-deleted.
```

Example:

```text
Max pins = 5
User has 5 pins
User changes max pins to 3

Result:
The 5 existing pins stay visible.
```

Future pin attempts then follow the new limit.

With rollover enabled, only one oldest pin is removed when adding a new one. The add-on does not aggressively trim the list down to the new max.

---

# Inline panel messages

Messages now appear inside the UniSearch panel, between the search button and the pinned section.

Examples:

```text
Type something to search.
Already in pinned list: Pin #2
Your pinned list is full. Unpin some pinned elements to make space.
Result not found.
Pinned item not found.
Breadcrumb item not found.
```

We intentionally avoid relying on Blender’s bottom status bar because users often miss those messages.

---

# Responsive breadcrumb display

This was an important UX decision.

The add-on checks the N-panel width using:

```python
context.region.width
```

Then estimates how much text fits.

The behavior is:

## If breadcrumb fits

Show the full breadcrumb on one line.

```text
DUMMY MODE > DUMMY HEADER > DUMMY DATA    [pin icon]
```

No expand button is shown.

## If breadcrumb does not fit

Show a collapsed compact version:

```text
[+] DUMMY MODE > ... > DUMMY DATA    [pin icon]
```

The `[+]` button appears only for breadcrumbs that do not fit.

So this is valid:

```text
DUMMY MODE > DUMMY HEADER > DUMMY DATA
[+] DUMMY MODE > ... > DUMMY DATA
```

## If user expands

The `[+]` becomes `[-]`.

The breadcrumb shows the full path using the fewest practical number of lines.

Preferred:

```text
[-] DUMMY MODE > DUMMY PREFERENCES
    > DUMMY SECTION > DUMMY DATA
```

Not preferred:

```text
[-] DUMMY MODE > DUMMY PREFERENCES
    > DUMMY SECTION
    > DUMMY DATA
```

The algorithm uses greedy wrapping: it packs as many breadcrumb parts into each line as possible.

## If panel width changes

The UI recalculates.

If a breadcrumb now fits, the `[+]` or `[-]` disappears and the full breadcrumb is shown in one line.

The add-on still remembers the expanded state internally. If the user narrows the panel again, the breadcrumb can return to expanded form.

---

# Current architecture

The code is structured around these parts:

```text
AddonPreferences
BreadcrumbItem PropertyGroup
State PropertyGroup
Dummy search provider
Search operator
Pin operator
Unpin operator
Toggle expand operator
Clear operator
Sidebar panel
Responsive breadcrumb drawing helpers
Inline message helpers
```

Important future-proofing decision:

```python
get_dummy_results(query)
```

is isolated.

Later it can be replaced by:

```python
search_blender_ui(query)
```

without rewriting the panel UI.

---

# Not implemented yet

These were intentionally deferred:

```text
Real command/menu/button/panel/preference search
Floating search window
Ctrl + Shift + RMB invocation
Configurable shortcut
Filters
Search ranking
Aliases
Moved/renamed feature mapping
Direct command execution
Command state feedback
Preference scanning
Extension setting scanning
Context-aware mode filtering
```

---

# Recommended next phase

The next phase should focus on implementing a real search backend without disturbing the UI.

## Phase 2 goal

Replace dummy results with a first real search provider.

Recommended first target:

```text
Search Blender operators/commands first
```

Why operators first?

Because Blender exposes many commands through Python as operators, for example:

```python
bpy.ops.object.delete
bpy.ops.mesh.primitive_cube_add
bpy.ops.wm.save_as_mainfile
```

This makes operators easier to index than arbitrary UI buttons.

A first real result could look like:

```text
Object Mode > Command > Delete
Object Mode > Command > Add Mesh > Cube
Window > File > Save As
```

Even if the breadcrumb is not perfect at first, the search backend can start producing real entries.

---

# Suggested Phase 2 roadmap

## Step 1 — Create a search result schema

Before indexing real Blender features, define a stable result object.

Recommended fields:

```python
id
label
breadcrumb_parts
result_type
operator_id
context_mode
description
aliases
source
can_execute
```

Example:

```python
{
    "id": "operator:bpy.ops.object.delete",
    "label": "Delete",
    "breadcrumb_parts": [
        "Object Mode",
        "3D Viewport",
        "Object Menu",
        "Delete"
    ],
    "result_type": "OPERATOR",
    "operator_id": "object.delete",
    "context_mode": "OBJECT",
    "description": "Delete selected objects",
    "aliases": ["remove", "erase"],
    "source": "Blender Operator",
    "can_execute": True,
}
```

The current UI only needs `breadcrumb_parts`, but future features will need the rest.

---

## Step 2 — Keep dummy provider as fallback

Do not delete the dummy provider immediately.

Use a switch internally:

```python
USE_DUMMY_RESULTS = False
```

or add a development preference:

```text
Use Dummy Results
```

This helps test the UI when the real search provider breaks.

---

## Step 3 — Implement simple operator indexing

Start by collecting available `bpy.ops` operators.

The first version does not need perfect menu breadcrumbs.

It can produce rough but structured entries like:

```text
Any Mode > Operator > object.delete
Any Mode > Operator > mesh.primitive_cube_add
Any Mode > Operator > wm.save_as_mainfile
```

Then improve breadcrumbs later.

---

## Step 4 — Add aliases

Add a simple alias dictionary.

Example:

```python
ALIASES = {
    "delete": ["remove", "erase"],
    "save": ["write file", "store"],
    "cavity": ["ambient occlusion", "viewport cavity"],
}
```

A result should match if the query hits:

```text
label
breadcrumb
operator id
aliases
description
```

---

## Step 5 — Add result types

Prepare for filters later.

Suggested result types:

```text
COMMAND
MENU
PANEL
PREFERENCE
EXTENSION_SETTING
MOVED_FEATURE
BUTTON
TOOL
```

Even if version 2 only fills `COMMAND`, the schema should already support all types.

---

## Step 6 — Add ranking

Early ranking can be simple:

```text
Exact label match
Label starts with query
Alias match
Breadcrumb match
Description match
Fuzzy/contains match
```

Do not overbuild ranking at first. The important thing is to produce useful predictable results.

---

# Final considerations before functionality work

The hardest part of the future add-on is not the panel UI. The hard part is building accurate breadcrumbs for Blender UI elements.

Blender’s Python API exposes operators and RNA properties better than it exposes “where every button is located in the UI.” So the backend should grow in layers:

```text
Layer 1: Operators / commands
Layer 2: Preferences
Layer 3: Known curated UI paths
Layer 4: Panels and menus
Layer 5: Moved/renamed feature aliases
Layer 6: Context/state feedback
Layer 7: Direct execution from UniSearch
```

For accuracy, especially for things like:

```text
Object Mode > 3D Viewport > Shading Header > Cavity
```

we will probably need a curated database plus API introspection, not only automatic discovery.

The best next move is to implement the search result schema and the first operator search provider, while keeping the UI exactly as it is.
