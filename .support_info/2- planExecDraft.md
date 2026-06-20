# Recommended Architecture

I would build these modules:

```text
core/
    feature_index.py
    token_index.py

providers/
    rna_provider.py
    operator_provider.py
    ast_provider.py
    runtime_provider.py
    keymap_provider.py

resolver/
    location_resolver.py
    breadcrumb_builder.py

cache/
    cache_manager.py

debug/
    debug_panel.py
```

Every provider returns the same structure:

```python
{
    "feature_id": "...",
    "label": "...",
    "type": "...",
}
```

No breadcrumbs yet.

---

# STAGE 1

## Goal

Acquire searchable features.

No UI locations.

No breadcrumbs.

---

## Providers

```text
RNA
Operators
```

Only.

---

## Output

```python
{
    "feature_id": "rna:View3DShading.show_cavity",
    "label": "Cavity",
    "type": "RNA"
}
```

```python
{
    "feature_id": "operator:object.delete",
    "label": "Delete",
    "type": "OPERATOR"
}
```

---

## Validation

Create debug operator:

```text
Dump Feature Index
```

Produces:

```text
Total RNA: xxxx
Total Operators: xxxx
```

Search:

```text
cavity
```

Expected:

```text
show_cavity
use_automasking_cavity
...
```

---

## Success Criteria

Search works.

No locations.

No breadcrumbs.

---

# STAGE 2

## Goal

Build token search.

Still no breadcrumbs.

---

## Build

RAM token index:

```python
token
    -> feature_ids
```

---

## Validation

Search:

```text
cavity
```

returns:

```text
N matches
```

Search speed:

```text
<50ms
```

---

## Success Criteria

Instant search.

---

# STAGE 3

## Goal

Introduce feature metadata.

---

## Add

```python
description
aliases
source
```

---

Example:

```python
{
    "feature_id": "...",
    "label": "Cavity",
    "aliases": [
        "ambient occlusion"
    ]
}
```

---

## Validation

Search:

```text
ambient occlusion
```

Finds:

```text
Cavity
```

---

# STAGE 4

## Goal

Location discovery.

NO breadcrumbs.

Important distinction.

---

Build:

```text
feature
    →
location candidates
```

Example:

```python
{
    "feature_id": "show_cavity",

    "locations": [
        {
            "container":
            "VIEW3D_PT_shading"
        }
    ]
}
```

---

## Provider

AST only.

No runtime.

---

## Validation Tool

New debug panel:

```text
Feature Inspector
```

Search:

```text
show_cavity
```

Output:

```text
Container:
VIEW3D_PT_shading
```

Nothing else.

---

## Success Criteria

Location references discovered.

---

# STAGE 5

## Goal

Container database.

---

Index:

```text
Panels
Menus
Headers
Popovers
Pie Menus
```

Example:

```python
{
    "container_id":
    "VIEW3D_PT_shading",

    "space_type":
    "VIEW_3D",

    "region_type":
    "HEADER",

    "container_type":
    "PANEL"
}
```

---

## Validation

Debug:

```text
Container Inspector
```

Query:

```text
VIEW3D_PT_shading
```

Output:

```text
Panel
3D Viewport
Header
```

---

# STAGE 6

## Goal

Location Resolver

First major milestone.

---

Input:

```text
Feature
+
Container
```

Output:

```python
{
    "feature":
    "show_cavity",

    "resolved_location":
    {
        "editor":
        "VIEW_3D",

        "container":
        "VIEW3D_PT_shading"
    }
}
```

---

## Validation

Debug:

```text
Resolve Feature
```

```text
show_cavity
```

Expected:

```text
Resolved:
VIEW3D_PT_shading
```

---

# STAGE 7

## Goal

Mode detection.

---

Provider:

```text
poll()
draw conditions
keymaps
```

Store:

```python
mode_candidates
```

---

Example:

```python
{
    "mode":
    "OBJECT"
}
```

---

## Validation

Inspector:

```text
show_cavity
```

Output:

```text
OBJECT
```

or

```text
UNKNOWN
```

Never guess.

---

# STAGE 8

## Goal

Breadcrumb generation.

Only now.

---

Input:

```text
Feature
Container
Editor
Mode
```

Output:

```text
Object Mode
>
3D Viewport
>
Shading Panel
>
Cavity
```

---

## Validation

Generate breadcrumb preview.

No search yet.

Just:

```text
show_cavity
```

→ breadcrumb

---

# STAGE 9

## Goal

Keymap integration.

---

For pie menus:

```text
Shortcut
```

Example:

```text
Object Mode
>
3D Viewport
>
Shading Pie Menu
>
(Z)
>
Cavity
```

---

Validation:

```text
VIEW3D_MT_shading_pie
```

returns:

```text
Shortcut: Z
```

---

# STAGE 10

## Goal

Runtime verification layer.

Not discovery.

Verification.

Important difference.

---

Runtime layer should NOT be the primary source.

Use it to verify AST results.

Example:

```text
AST:
show_cavity
→ VIEW3D_PT_shading
```

Runtime confirms:

```text
YES
```

Confidence:

```text
100
```

---

# STAGE 11

## Goal

Cache system.

Only after everything works.

Many developers do this too early.

---

Store:

```text
Features
Containers
Locations
Aliases
```

in:

```text
index.json
```

---

Validation:

```text
Build cache
Delete RAM
Reload cache
Compare counts
```

Must match.

---

# STAGE 12

## Goal

Production Search Pipeline

Final flow:

```text
Query
    ↓
Token Index
    ↓
Feature IDs
    ↓
Location Resolver
    ↓
Breadcrumb Builder
    ↓
Result Ranking
    ↓
UI
```

---

# What I Would Change in Your Suggestion

One thing only:

I would **delay breadcrumb generation much longer than you currently envision**.

Your instinct is:

```text
Acquire data
→ Build breadcrumb
→ Improve
```

I would instead do:

```text
Acquire features
→ Validate features

Acquire locations
→ Validate locations

Acquire contexts
→ Validate contexts

Only then:
→ Build breadcrumb
```

Because a breadcrumb is merely a presentation of several underlying facts.

If:

```text
feature = wrong
location = wrong
mode = wrong
```

then:

```text
breadcrumb = wrong
```

but debugging becomes difficult because you no longer know which layer failed.

The staged plan above keeps every layer independently testable and gives you clear pass/fail checkpoints before moving to the next stage.
