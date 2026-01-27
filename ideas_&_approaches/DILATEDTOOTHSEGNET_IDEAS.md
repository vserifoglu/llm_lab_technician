# DilatedToothSegNet: Key Ideas for Margin Detection

> **Paper**: DilatedToothSegNet (2024) - Graph Neural Network with Dilated Edge Convolution  
> **Task**: Tooth-level segmentation (same problem as MeshSegNet, NOT margin detection)

---

## Core Approach

```
Raw Mesh (faces + normals) → Edge Conv → Dilated Edge Conv → Per-Face Labels
```

**Key insight**: Expand receptive field efficiently using farthest point sampling (FPS).

---

## 🚩 Concepts We Could Use

### 1. Dilated Edge Convolution
Standard kNN only sees **local** neighbors. Dilated version samples from a **larger** neighborhood:

```
Standard: k=20 nearby faces → local features only
Dilated:  k=200 faces → FPS to 20 → captures distant context
```

**Why useful**: Margin detection needs BOTH local edge sharpness AND global prep-vs-gum context.

---

### 2. Direct Mesh Processing
Works directly on mesh faces + normals — no voxelization or rendering.

```
Input per face: [9 vertex coords + 3 normal values] = 12 channels
```

**Why useful**: Preserves full geometric precision, no information loss from conversion.

---

### 3. Edge Features
Combines global and local information per face:
```
feature = MLP(xi || xj - xi)
         ↑      ↑
     global  local difference
```

**Why useful**: Captures both absolute position and relative neighborhood structure.

---

### 4. FPS for Sparse Sampling
Farthest Point Sampling selects maximally spread points from a set.

**Why useful**: Efficient way to get diverse, representative samples from a region.

---

## ❌ Why It Doesn't Directly Apply

| Issue | Explanation |
|-------|-------------|
| Wrong task | Segments *which tooth*, not *where margin is* |
| Wrong teeth | Trained on healthy teeth, not preparations |
| Wrong output | Per-face labels, not a 3D curve |

---

## Potential Adaptation for Margin Detection

| DilatedToothSegNet | Margin Detection Version |
|--------------------|-------------------------|
| 17 classes (teeth + gum) | 3 classes: Prep / Gum / Other |
| Per-face classification | Per-face "margin distance" regression |
| Full arch input | Cropped single tooth input |
| Standard loss | Add boundary loss (Sobel gradients) |

---

## Architecture Reference

```
Input: Face features (coords + normals)
  ↓
Edge Conv Block (local features)
  ↓
Dilated Edge Conv Block (expanded receptive field)
  ↓
Prediction Head (per-face MLP)
  ↓
Output: Class probabilities per face
```

---

## Bottom Line

**Not directly usable** — but the dilated edge convolution pattern is a promising architecture choice for margin detection, letting the model see both local edge geometry and broader tissue context.
