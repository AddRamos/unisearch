# Universal Blender Search - Project Summary and Architectural Notes

## Project Goal

Create a Blender add-on that solves one of the community's biggest discoverability problems:

> "I know the feature exists, but I don't know where it is."

The current Blender search systems are limited because they mainly find:

* Operators
* Commands
* Some preferences
* Some menu items

But they generally fail to answer:

* Where is this button?
* What mode contains it?
* Which panel contains it?
* Which menu contains it?
* Which addon contains it?
* Where did it move in the latest Blender version?

The project focuses on providing:

```text
Search Term
↓
Visual Location(s)
↓
Breadcrumb(s)
```

Example:

Search:

```text
cavity
```

Result:

```text
Object Mode
> 3D Viewport
> Header
> Shading
> Cavity

Sculpt Mode
> 3D Viewport
> Header
> Auto Masking
> Cavity

Texture Paint
> 3D Viewport
> Masking
> Cavity Mask
```

The breadcrumb is the primary value delivered to the user.

---

# Important Design Insight

The user thinks in terms of:

```text
Button
Tool
Feature
Visible Label
```

The system should think in terms of:

```text
Feature
↓
Location(s)
↓
Breadcrumb(s)
```

The user searches:

```text
cavity
```

But internally Blender contains:

```python
show_cavity
use_automasking_cavity
use_automasking_cavity_inverted
cavity_mask
```

Multiple Blender features may produce multiple visible UI entries.

---

# The Cavity Example

Observed examples:

## Object Mode

```text
Object Mode
> VIEW_3D
> Shading Header
> Cavity
```

Associated property:

```python
space_data.shading.show_cavity
```

---

## Sculpt Mode

```text
Sculpt Mode
> VIEW_3D
> Auto Masking Header
> Cavity
```

Associated property:

```python
tool_settings.sculpt.use_automasking_cavity
```

---

## Sculpt Mode

```text
Sculpt Mode
> VIEW_3D
> Auto Masking Header
> Cavity (Inverted)
```

Associated property:

```python
tool_settings.sculpt.use_automasking_cavity_inverted
```

---

## Texture Paint

```text
Texture Paint
> VIEW_3D
> Masking Header
> Cavity Mask
```

Associated property:

```python
tool_settings.image_paint.use_cavity
```

(or similar depending on Blender version)

---

# Core Discovery

The same search term may correspond to many different Blender features.

Therefore:

```text
Search Term
≠
Feature
≠
UI Location
```

These must be treated separately.

---

# Proposed Data Model

## Search Term

User input:

```text
cavity
```

---

## Feature

Internal Blender identity:

```python
show_cavity
```

or

```python
use_automasking_cavity
```

or

```python
mesh.bevel
```

This is the stable identifier.

---

## Location

Where the feature appears.

Example:

```python
Location(
    mode="OBJECT",
    area="VIEW_3D",
    region="HEADER",
    panel="Shading"
)
```

---

## Breadcrumb

User-facing output:

```text
Object Mode
> 3D Viewport
> Header
> Shading
> Cavity
```

---

# Why Not Use Labels As IDs?

Example:

```python
layout.prop(shading, "show_cavity", text="Cavity")
```

Tomorrow Blender could change:

```python
layout.prop(shading, "show_cavity", text="Cavity Shading")
```

The visible label changes.

The identifier survives.

Therefore:

```text
Label = search/display
Identifier = tracking
```

---

# Why Not Use Breadcrumbs As IDs?

Breadcrumbs are fragile.

Example:

Blender 5.1:

```text
Object Mode
> Shading
> Cavity
```

Future Blender:

```text
Object Mode
> Viewport Effects
> Cavity
```

The feature is unchanged.

Only the UI location moved.

Therefore:

```text
Feature ID = stable
Breadcrumb = generated
```

---

# Most Important Technical Challenge

Not search.

Not storage.

Not UI.

The hardest problem is:

```text
Feature
↓
Where does it appear in Blender's UI?
```

Example:

```python
show_cavity
```

Need to discover:

```text
Object Mode
> VIEW_3D
> Header
> Shading
> Cavity
```

Blender does NOT expose a simple API like:

```python
find_ui_locations("show_cavity")
```

This relationship must be built.

---

# Major Discovery About Blender

Blender knows:

```python
show_cavity
```

Blender knows:

```python
VIEW3D_PT_shading
```

But Blender does not appear to maintain a global table:

```python
show_cavity
→
VIEW3D_PT_shading
```

This relationship exists implicitly in draw() code.

Example:

```python
class VIEW3D_PT_shading(Panel):

    def draw(self, context):
        layout.prop(shading, "show_cavity")
```

The connection exists in source code and runtime UI construction.

---

# Candidate Discovery Strategies

## Strategy A - Parse Blender UI Source

Search:

```python
layout.prop(...)
layout.operator(...)
layout.menu(...)
```

Inside:

```text
scripts/startup/bl_ui/
```

Example:

```python
layout.prop(shading, "show_cavity")
```

Result:

```text
show_cavity
↓
VIEW3D_PT_shading
```

Advantages:

* Reliable for Blender Core
* Version-aware

Limitations:

* Misses some runtime-generated UI
* Harder for addons

---

## Strategy B - Runtime UI Interception

Capture:

```python
layout.prop(...)
layout.operator(...)
layout.menu(...)
layout.popover(...)
```

during draw() execution.

Record:

```text
Current Mode
Current Panel
Current Area
Current Feature
```

Advantages:

* Works with addons
* Works with extensions
* Reflects actual UI

Limitations:

* Technically more difficult

---

# Recommended Hybrid Approach

Use both.

## Source Analysis

For Blender Core.

## Runtime Discovery

For:

* Addons
* Extensions
* Dynamic UI

---

# Search Index Discussion

Question:

Should the index be fixed?

Answer:

No.

---

## Fixed Database

Bad.

Breaks whenever Blender changes.

---

## Startup Generated Index

Good.

At startup:

```text
Scan RNA
Scan Operators
Scan Panels
Scan Menus
Scan Addons
```

Build search index.

---

## Preferred Solution

Hybrid cache.

```text
Startup
↓
Build index
↓
Save JSON cache
```

Later:

```text
Load cache
↓
Refresh differences
```

---

# Addons and Extensions

Critical requirement.

The system must discover:

```text
Blender Core
+
Enabled Addons
+
Enabled Extensions
```

because many workflows depend on:

```text
HardOps
BoxCutter
MACHIN3Tools
ZenUV
UVPackmaster
etc.
```

The system should eventually return:

```text
Found:

Blender Core
-----------
Object Mode > Shading > Cavity

Sculpt
-----------
Auto Masking > Cavity

Addon: MACHIN3Tools
-----------
Viewport > Cavity Preview
```

---

# Breadcrumb Philosophy

Original assumption:

Breadcrumbs are generated output.

After discussion:

Breadcrumbs are actually the primary user value.

The add-on exists to answer:

```text
Where is it?
```

not merely:

```text
What is it?
```

Every search result should ultimately produce breadcrumbs.

Examples:

Bad:

```text
show_cavity
```

Bad:

```text
mesh.bevel
```

Good:

```text
Object Mode
> 3D Viewport
> Header
> Shading
> Cavity
```

---

# UI Prototype Direction

Initial floating-window attempts were not ideal.

Current preferred direction:

```text
N-Panel
```

Location:

```text
3D Viewport
> Sidebar (N)
> Universal Search
```

Contains:

```text
Search Field
Search Button
Clear History
Search History
Results
Breadcrumbs
```

---

# Search History Decision

Chosen behavior:

Persistent during session.

Results accumulate.

Example:

```text
Search #1
cavity

Search #2
bevel

Search #3
snapping
```

instead of replacing previous searches.

This allows the search tool to act as a research workspace.

---

# Most Important Future Experiment

Before building the full search system:

Create a diagnostic tool.

Input:

```text
show_cavity
```

Output:

```text
Found:

Object Mode
> 3D Viewport
> Header
> Shading
> Cavity
```

If this Feature → Location relationship can be solved reliably, the rest of the Universal Search system becomes straightforward.

This relationship is the core research problem of the project.
