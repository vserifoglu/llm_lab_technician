# Designer Insights: Margin Detection Q&A

> Summary of findings from designer interviews and technical investigation.

---

## Clarified Workflow (Critical Discovery)

```
1. Dentist creates impression/prep on patient
2. Lab technician receives jaw copy from dentist
3. Technician SCANS it → gets raw STL (upper/lower jaw)
4. Technician opens in Exocad, checks prep quality:
   - Did dentist dig tiny space below gum for zircon?
5. Technician physically CARVES ridge/pathway between prep and gum
   └── This edge is where zircon crown will sit
6. Technician RESCANS the modified model → NEW STL files
7. Designer opens new scan, draws margin line along carved edge
8. Designer adds the zircon tooth design
```

**Key insight**: The "whiteness" in Exocad is just **visualization** — the real signal is the **physical ridge** carved by technician, which IS captured in STL geometry.

**Technician knowledge**: Each technician learns individual dentist preferences over time and adjusts their prep work accordingly.

---

## Key Answers from Designers

### 1. White Marking = Exocad Visualization Only
- NOT in the data, just software coloring to help designers
- The **physical ridge** carved by technician is what matters
- This ridge IS captured in STL geometry

### 2. Zircon Depth & Margin Width
- Zircon tooth must go under gum by **~hair thickness** (very tiny)
- Margin lines should be **slightly wide** — easier to fix during milling without redesign

### 3. Antagonist NOT Relevant for Margins
- Occlusion only matters for crown design, NOT margin detection

### 4. Adjacent Prep Margins Must NOT Overlap
- Each margin stays close to its own tooth center
- ~30% of cases have neighboring prepped teeth

---

## Case Statistics

| Case Type | Frequency | Notes |
|-----------|-----------|-------|
| **Zircon crowns** | ~10/day | Most frequent, our focus |
| **Implants** | Medium | Different workflow |
| **Veneers** | ~2/day | Rare, edge case |
| **Bridges (pontics)** | Occasional | Empty tooth → relaxed margins |

| Prep Pattern | Frequency |
|--------------|-----------|
| **Individual teeth** | ~70% |
| **Neighboring preps** | ~30% |

---

## Multi-Tooth Files Explained

| File Pattern | Meaning |
|--------------|---------|
| `*-25-waxup.stl` | Single tooth crown |
| `*-34-35-37-waxup.stl` | Bridge connecting 3 teeth (dentist requested connected) |

**Pontics** (filling empty spaces): Less critical margins, no prep underneath.

---

## Edge Cases to Consider

| Case | Issue |
|------|-------|
| **Veneers** | Margins starts in MIDDLE of back of the tooth, and ends at gum line of the front of the tooth |
| **Bridges** | Pontic teeth have relaxed/no margins |
| **Poor prep** | If dentist didn't prep well, technician must compensate |

---

## Technical Investigation Results

### STL Files: No Color Data
- Analyzed 15 STL files across 2 cases
- All have **uniform gray** (RGB 102,102,102)
- White coloring exists only in Exocad visualization

### DentalCAD File
- Proprietary .NET binary format
- Contains margin detection logs
- Cannot easily parse

---

## Open Questions (Resolved ✓)

| # | Question | Answer |
|---|----------|--------|
| 1 | Where does white come from? | **Exocad visualization only** |
| 2 | What's in the STL? | **Physical ridge carved by technician** |
| 3 | Color data available? | **No** — geometry only |
| 4 | Neighbor frequency? | **~30%** neighboring preps |
| 5 | Margin tolerance? | **Wide preferred** — easier to fix during milling |

---

## Impact on Solution

| Finding | Impact |
|---------|--------|
| Physical ridge in STL | **Geometry-only approach IS viable** |
| Whiteness = just viz | Don't need color data extraction |
| 70% individual teeth | Focus on single-tooth detection first |
| Wide margins preferred | Some tolerance in predictions OK |
| Pontics different | Flag bridge cases for relaxed validation |

---

## Next: Validation Plan

Before implementing, we need to validate:

1. **Is the carved ridge detectable geometrically?**
   - Measure curvature at margin vs elsewhere
   - Context: Single prep tooth (what model will see)
   
2. **How consistent is the signal?**
   - Test across different teeth and cases
   - Expect: Margin curvature > background

3. **Edge cases?**
   - Poorly carved preps
   - Veneers (mid-tooth margins)
