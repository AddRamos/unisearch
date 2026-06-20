Perfect idea. Before opening Stage 2, we should freeze what we learned, because several assumptions from the original plan were proven wrong and the roadmap should be updated accordingly.

---

# UniSearch Backend Roadmap

# Stage 1 Final Review (Validated)

## Original Goal

Acquire searchable Blender features.

```text
RNA Properties
Operators
```

No:

```text
Locations
Containers
Breadcrumbs
Cache
AST
Keymaps
```

---

# Stage 1A — RNA Acquisition

## Result

PASS

Provider:

```text
providers/rna_provider.py
```

Successfully traverses:

```python
bpy.types.*.bl_rna.properties
```

and extracts:

```text
identifier
label
description
owner class
```

---

## Discovery #1

Original assumption:

```text
RNA Features ≈ 10k
```

Actual:

```text
RNA Property Instances = 64958
```

---

## Discovery #2

Most RNA records are duplicates.

Measurements:

```text
RNA Instances:            64958
Unique RNA Identifiers:    5796
Unique RNA Labels:         5287
```

Duplication ratio:

```text
~11.2x
```

Meaning:

```text
64958 RNA records
```

does NOT mean:

```text
64958 searchable features
```

---

## Architectural Conclusion

UniSearch must search:

```text
Feature Concepts
```

not:

```text
RNA Property Instances
```

---

# Stage 1B — Operator Acquisition

## Original Result

FAIL

First implementation discovered:

```text
77 operators
```

which was clearly incorrect.

---

## Root Cause

This detection:

```python
hasattr(value, "get_rna_type")
```

was not compatible with Blender 4.3 operator proxies.

---

## Investigation

Discovered Blender 4.3 exposes operators as:

```python
bpy.ops._BPyOpsSubModOp
```

Example:

```text
object.delete
mesh.bevel
wm.save_mainfile
```

all appeared as:

```python
<class 'bpy.ops._BPyOpsSubModOp'>
```

---

## Fixed Provider

Final provider walks:

```python
bpy.ops
    -> category
        -> operator
```

without recursive proxy detection.

---

## Final Result

PASS

```text
Operator Features: 2323
```

---

# Stage 1.5 — Feature Normalization

## Why Added

Not present in original roadmap.

Added after discovering:

```text
64958 RNA instances
5796 unique RNA identifiers
```

---

## Goal

Convert:

```text
Object.use_cavity
World.use_cavity
Material.use_cavity
```

into:

```text
Feature:
use_cavity

Owners:
Object
World
Material
```

---

## New FeatureRecord

Added:

```python
owners: list[str]
```

---

## New RNA Model

Current search indexes:

```text
5796 normalized RNA features
```

instead of:

```text
64958 RNA instances
```

---

## Final Searchable Universe

```text
Normalized RNA Features: 5796

Operators: 2323

Total Searchable Features: 8119
```

This number is considered healthy and manageable.

---

# Search Quality Findings

## Description Matching

Original search:

```python
query in description
```

caused major noise.

Example:

```text
save
```

matched:

```text
unsaved
```

inside descriptions.

---

## Decision

Stage 1 search only uses:

```python
label
identifier
```

Description matching postponed until ranking exists.

---

# Search Result Analysis

## Query: cavity

Before normalization:

```text
39 results
many duplicates
```

After normalization:

```text
16 results
```

Representative results:

```text
show_cavity
use_cavity
use_automasking_cavity
cavity_type
mask_from_cavity
```

Search quality improved dramatically.

---

## Query: save

Current result:

```text
34 results
```

Includes:

```text
image.save
image.save_as
asset.catalogs_save
use_preferences_save
save_version
```

Reasonable quality.

---

## Query: delete

Current result:

```text
67 results
```

Includes:

```text
action.delete
armature.delete
curve.delete
constraint.delete
...
```

Search working correctly.

---

# Important Discovery About Ranking

Current search order is:

```text
First match found
```

not:

```text
Best match first
```

Example:

```text
delete
```

returns:

```text
delete_in_obstacle
```

before:

```text
object.delete
curve.delete
armature.delete
```

---

## Conclusion

Stage 2 must include:

```text
Token Index
+
Ranking
```

Not token index alone.

---

# Updated Architecture

## Current Feature Model

```python
FeatureRecord

feature_id
label
identifier
feature_type
description
source
aliases
owners
```

---

## Current Feature Counts

```text
RNA Features: 5796
Operators: 2323
Total: 8119
```

These numbers become baseline validation metrics.

---

# Updated Roadmap

## Completed

```text
Stage 1A
RNA Acquisition
PASS

Stage 1B
Operator Acquisition
PASS

Stage 1.5
Feature Normalization
PASS
```

---

## Stage 2 (Next Chat)

### Goal

Build real search engine.

---

### Inputs

```text
8119 normalized features
```

---

### Deliverables

#### Token Index

```text
token
    →
feature_ids
```

Example:

```text
cavity
    →
show_cavity
use_cavity
use_automasking_cavity
```

---

#### Ranking System

Initial ranking order:

```text
Exact label match
Identifier exact match
Label startswith
Identifier startswith
Token match
Operator boost
RNA boost
```

---

#### Debug Metrics

Add:

```text
Index build time
Token count
Average query time
```

---

#### Validation Queries

Mandatory:

```text
delete
save
cavity
bevel
extrude
```

Expected:

```text
Best results first
```

---

# Final Lessons Learned From Stage 1

### Correct

✅ Normalize RNA before building search.

✅ Validate operators separately.

✅ Use owner tracking.

✅ Separate acquisition from breadcrumbs.

---

### Incorrect Assumptions

❌ RNA count equals feature count.

❌ Operator recursion based on `get_rna_type`.

❌ Description matching is safe.

❌ Build token index before data quality validation.

---

# Stage 1 Exit Criteria (Achieved)

```text
Acquire Blender Features
✓

Normalize Features
✓

Operator Discovery
✓

Search Validation
✓

Data Quality Validation
✓

Ready For Token Index
✓
```

This is the state I would carry into the next chat as the official Stage 1 completion report and updated roadmap baseline.
