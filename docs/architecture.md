# STF-WB Architecture

## Overview

STF-WB reference implementation follows the STF-Workbench v0.2.0 specification structure.

## Core Models

### Project (Section 6.1)
- Represents verification target
- Properties: id, name, target_uri, metadata

### Iteration (Section 6.2)
- Single pass through S0→S5 workflow
- State machine: created → in_progress → frozen → archived

### Artifact (Section 6.5)
Each step produces an artifact:
- **S0.A** - Source snapshot
- **S1.A** - Normalized requirements
- **S2.A** - Protocol specification (TLA+)
- **S3.A** - Model checking results
- **S4.A** - Evidence and coverage
- **S5.A** - Gate derivation

## Coverage Computation (Section 6.4.1)

Algorithm:
```
coverage = {
  "unit": "fragments" | "sections",
  "covered": number of verified items,
  "total": total number of items,
  "gaps": [list of unverified items]
}
```

Percentage = (covered / total) × 100
