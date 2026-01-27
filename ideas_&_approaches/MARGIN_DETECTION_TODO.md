# Margin Detection: TODO Lists

---

## ✅ Ready to Start Now

- [ ] **Data Preprocessing Pipeline**
  - [ ] Load mesh + GT margin points from Exocad exports
  - [ ] Apply coordinate transformations (Scanner ↔ Design space)
  - [ ] Compute curvature features (Gaussian + point curvature)
  - [ ] Save merged data as training-ready format (`.npz`)

- [ ] **Baseline Model Architecture**
  - [ ] Input: per-vertex features `[x, y, z, nx, ny, nz, curvature]`
  - [ ] Backbone: EdgeConv for local features
  - [ ] Global context: Transformer encoder or Dilated EdgeConv
  - [ ] Output head: per-vertex prediction

- [ ] **Training Infrastructure**
  - [ ] PyTorch/PyG setup for mesh processing
  - [ ] Training loop with basic segmentation loss
  - [ ] Validation split from available cases

---

## ⚠️ Needs Definition Before Training

- [ ] **Ground Truth Representation**
  - How to encode GT margin for training?
  - Options: binary mask (near-margin vertices), distance field, heatmap
  - Decision needed: which format works best?

- [ ] **Curve Extraction Method**
  - How to convert model output → ordered 3D margin curve?
  - Options: threshold + contour tracing, peak detection, level-set extraction
  - Need to research/prototype

- [ ] **Evaluation Metrics**
  - How to measure prediction quality?
  - Options: Chamfer distance, Hausdorff distance, point-to-curve error
  - Define "acceptable" clinical threshold (e.g., <0.1mm)

---

## 📋 Research Needed

- [ ] Literature on **3D curve extraction** from heatmaps/distance fields
- [ ] Literature on **margin-specific metrics** in dental CAD/CAM
- [ ] Decide GT format based on what works for curve extraction
