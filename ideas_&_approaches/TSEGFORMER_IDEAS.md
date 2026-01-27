# TSegFormer: Key Ideas for Margin Detection

> **Paper**: TSegFormer (2023) - 3D Transformer for Tooth Segmentation  
> **Task**: Tooth-level segmentation (same as others, NOT margin detection)  
> **Dataset**: 16,000 high-res IOSs (largest dental dataset to date)

---

## Core Approach

```
Mesh → Point Cloud (face centers) → EdgeConv → Transformer Encoder → Segmentation Heads
```

**Key insight**: Combine local feature learning (EdgeConv) with global context (Transformer self-attention).

---

## 🚩 Concepts We SHOULD Use

### 1. Geometry Guided Loss (Curvature-Weighted) ⭐
Focus training on **high-curvature points** where errors are most likely:

```python
# Points with top r% curvature get extra loss weight
S(r) = points with highest curvature values
L_geo = FocalLoss(predictions[S(r)], labels[S(r)])
```

**Why critical for margins**: Margins ARE high-curvature regions! This loss naturally emphasizes the exact areas we care about.

---

### 2. Point Curvature Feature ⭐
Novel per-point feature measuring local surface bending:

```
m_i = average angle between point's normal and neighbors' normals
```

**Why useful**: Margins have distinctive curvature signatures — this feature directly encodes what we're looking for.

---

### 3. Auxiliary Segmentation Head
Two-head design:
- **Main head**: 33 classes (all teeth + gum)
- **Auxiliary head**: 2 classes (tooth vs gum binary)

**Why useful**: For margin detection, we could use:
- Main: distance-to-margin regression
- Auxiliary: prep vs gum binary classification

---

### 4. 8-Dimensional Input Features
Rich geometric features per point:
```
[x, y, z, nx, ny, nz, gaussian_curvature, point_curvature]
```

**Why useful**: These features capture exactly the geometry needed to identify margins.

---

### 5. Transformer + EdgeConv Combination
- **EdgeConv**: Local neighborhood features
- **Transformer**: Global context via self-attention

**Why useful**: Margin detection needs both local edge sharpness AND understanding of surrounding tissue type.

---

## Results (Impressive Scale)

| Metric | TSegFormer | Previous Best |
|--------|-----------|---------------|
| **Accuracy** | 97.97% | 97.81% |
| **mIoU** | 94.34% | 93.30% |
| **Clinical error rate** | 24.0% | 45.5% (DCNet) |

Trained on **16,000 cases** — much larger than Teeth3DS (1,800).

---

## ❌ Why It Doesn't Directly Apply

| Issue | Explanation |
|-------|-------------|
| Wrong task | Segments which tooth, not where margin is |
| Healthy teeth | No prepared teeth in training data |
| Per-point labels | Outputs class labels, not margin curve |

---

## Adaptation Path for Margin Detection

| TSegFormer | Margin Detection Version |
|------------|-------------------------|
| 33 classes | 3 classes: Prep / Gum / Margin-zone |
| Classification loss | Regression: distance-to-margin |
| Geometry loss on all high-curvature | Focus on prep-gum transition zone |
| Full arch input | Cropped single prep input |

---

## Bottom Line

**Best paper yet for transferable ideas!** The geometry-guided loss and point curvature features are directly relevant — margins are inherently high-curvature boundaries. The multi-head design and Transformer architecture are also strong choices.
