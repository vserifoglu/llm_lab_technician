# Designer Insights: Margin Detection Q&A

> Summary of findings from designer interviews and technical investigation.

---

## Key Answers from Designers

### 1. White Margin Marking Always Exists
- Designers **manually draw** a white circular shape on the physical model before scanning
- This marks the gum/prep boundary even when no obvious shoulder exists
- The margin line should be drawn **within** this white zone (inner edge, center, or outer edge all acceptable)

### 2. Antagonist NOT Relevant for Margins
- The confronting tooth (e.g., 35 for prep 25) does **not** affect margin placement
- Occlusion only matters later during crown/tooth design — NOT margin detection

### 3. Adjacent Prep Margins Must NOT Overlap
- If neighboring teeth are both prepped, their margins must be **separated**
- Each margin stays close to its own tooth center to leave gap between them
- Overlapping margins cause milling machine to break adjacent tooth edges

### 4. Margins Must Be Smooth & Cylindrical
- Manufacturing constraint: smooth curves = easier machining
- Jagged or irregular margins increase milling time and error risk

---

## Impact on Solution Approach

| Finding | Impact |
|---------|--------|
| White marking exists | Problem may be **texture detection + refinement**, not pure geometry detection |
| Antagonist irrelevant | **Simplifies preprocessing** — don't need opposing jaw for margin detection |
| Margins must separate | Need **neighbor-awareness** when multiple adjacent preps exist |
| Smoothness required | Add **smoothness constraint** to loss function or post-processing |

---

## Technical Investigation Results

### STL Files: No Color Data
- Analyzed 15 STL files across 2 cases
- All have **uniform gray** (RGB 102,102,102)
- White marking is **NOT preserved** in STL export

### DentalCAD File
- Proprietary .NET binary format
- Contains logs: `PreparationMarginProcessor`, `Margin Line Detection`
- Exocad screenshot shows white texture **visible in software**
- Cannot easily parse this format

---

## Open Questions (Must Resolve Before Proceeding)

| # | Question | Why It Matters |
|---|----------|----------------|
| 1 | **Where does white marking come from?** Physical paint vs digital addition | Determines if we can detect it from scans |
| 2 | **Does scanner output color formats?** (PLY, OBJ with colors) | STL loses color; need source files |
| 3 | **Can we get raw scanner output?** Before Exocad processing | May preserve texture data |
| 4 | **How wide is the acceptable margin zone?** Tolerance in mm | Error budget for AI predictions |
| 5 | **How often are adjacent teeth both prepped?** | Frequency of neighbor-coordination cases |
| 6 | **How do technicians isolate single teeth from arch?** Manual crop? Segmentation? | Needed for preprocessing pipeline |

---

## Next Steps

1. [ ] Get scanner output format specs (color support?)
2. [ ] Ask designer: is white marking physical or digital?
3. [ ] Request sample PLY/OBJ files if available
4. [ ] Count adjacent-prep cases in dataset
5. [ ] Define acceptable margin position tolerance (mm)
