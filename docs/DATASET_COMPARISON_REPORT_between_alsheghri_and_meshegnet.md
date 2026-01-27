# Dataset Comparison: MeshSegNet vs. Semi-Supervised Teeth Segmentation

## Executive Summary

This report compares the datasets used in two dental segmentation research projects:
1. **MeshSegNet** (Tai-Hsien/MeshSegNet) - Original supervised learning approach
2. **Semi-Supervised Teeth Segmentation** (Alsheghri/Teeth-Segmentation) - Extended semi-supervised approach

Both projects work with 3D dental surface scans but differ significantly in dataset size, availability, and labeling strategies.

---

## 📊 Dataset Overview Comparison

| Aspect | MeshSegNet (2019) | Semi-Supervised (2022) |
|--------|-------------------|------------------------|
| **Total Scans** | 36 intraoral scans | Not explicitly stated (estimated 30-40+) |
| **Data Availability** | ❌ **NOT publicly available** | ✅ **Publicly available** |
| **Download Link** | Not provided | [Google Drive Link](https://drive.google.com/drive/folders/1YRCakTTTyr8Sqp3pBBqvgMgZKb59ktES) |
| **Training Scans** | 24 scans | Labeled: Similar range, Unlabeled: Additional clustered data |
| **Validation Scans** | 6 scans | Similar proportion (3-fold CV) |
| **Test Scans** | 6 scans | Separate test set |
| **Data Format** | VTP (VTK PolyData) | VTP (VTK PolyData) |
| **Pre-processing** | Pre-downsampled | High-resolution available |
| **Labeled Data Split** | 100% labeled | Partial labeled + unlabeled |

---

## 🔍 Dataset Content & Structure

### MeshSegNet Dataset

#### **Data Source:**
- 36 intraoral scans from clinical sources
- **Not publicly available** - researchers must use their own data
- Scans acquired using intraoral scanners (IOSs)
- Pre-downsampled before distribution

#### **What Each Scan Contains:**

**1. Mesh Structure:**
- 3D triangular mesh of dental surface
- VTP (VTK Polygonal Data) format
- Variable number of cells (triangles) per scan
- Both upper and lower dental arches
- Each scan includes "flipped" version (left-right mirror)

**2. Anatomical Coverage:**
- Complete dental arch (gingiva + teeth)
- From 2nd molar to 2nd molar (14 teeth max)
- Includes gingival tissue (gums)

**3. Annotations:**
- **Ground Truth Labels:** Per-cell (triangle) labels
- **15 Classes Total:**
  - Class 0: Gingiva (gums)
  - Classes 1-14: Individual teeth (2nd molar → 2nd molar)
- Labels stored as cell attributes in VTP files
- Field name: `'Label'`

**4. Mesh Properties:**
- Cell vertices (3 triangle points × 3 coordinates = 9 values)
- Normal vectors computed from mesh geometry
- Barycenter positions (cell centers)
- Pre-downsampled to manageable resolution

#### **Dataset Organization:**
```
Original Data/
├── Sample_01_d.vtp          (Upper arch, patient 1)
├── Sample_01001_d.vtp       (Lower arch flipped, patient 1)
├── Sample_02_d.vtp          (Upper arch, patient 2)
├── Sample_02001_d.vtp       (Lower arch flipped, patient 2)
...
├── Sample_36_d.vtp
└── Sample_36001_d.vtp

Split:
- Training: Sample_01 to Sample_24 (+ flipped versions)
- Validation: Sample_25 to Sample_30 (+ flipped versions)
- Testing: Sample_31 to Sample_36 (+ flipped versions)
```

#### **Quality Characteristics:**
- ✅ Clinically acquired scans
- ✅ Expert-annotated labels
- ✅ Includes anatomical variations
- ❌ Small dataset size (36 scans)
- ❌ Limited diversity
- ❌ Not publicly available

---

### Semi-Supervised Teeth Segmentation Dataset

#### **Data Source:**
- **Publicly available dataset**
- Download: [Google Drive Link](https://drive.google.com/drive/folders/1YRCakTTTyr8Sqp3pBBqvgMgZKb59ktES)
- Original high-resolution scans provided
- Multiple data subsets for different learning strategies

#### **What the Dataset Contains:**

**1. Supervised Labeled Train Data:**

**Location:** `SemiSupervised/Supervised Labeled Train Data/`

- Fully annotated 3D dental scans
- Similar structure to MeshSegNet
- VTP format with per-cell labels
- 15 classes (0-14: gingiva + 14 teeth)
- Each scan includes:
  - Triangle mesh geometry
  - Cell label annotations
  - Normal vectors
  - Coordinate information
  
**Sample Naming:** `A{arch}_Sample_{id}_d.vtp`
- `arch`: Upper (A) or Lower (B) jaw indicator
- `id`: Patient/sample identifier

**2. Self-Supervised Clustered Train Data:**

**Location:** `SemiSupervised/Selfsupervised Clustered Train Data/`

- **Unlabeled mesh data** for self-supervised learning
- Pre-clustered into pseudo-categories
- **60 clusters** for contrastive learning
- VTP files without ground truth labels
- Used with k-shot learning (k=14)
- Larger volume than labeled data

**Structure:**
```
Selfsupervised Clustered Train Data/
├── cluster_01/
│   ├── mesh_001.vtp
│   ├── mesh_002.vtp
│   └── ...
├── cluster_02/
│   └── ...
...
└── cluster_60/
    └── ...
```

**3. Labeled Test Data:**

**Location:** `SemiSupervised/Labeled Test Data/`

- Hold-out test set with ground truth
- Similar format to labeled training data
- Used for final evaluation
- Metrics: DSC, SEN, PPV

**4. Original High-Resolution Data:**

**Available:** Google Drive (separate from processed data)
- Original resolution scans before downsampling
- Suitable for high-fidelity applications
- Full clinical detail preserved

#### **Dataset Organization:**
```
Teeth-Segmentation Dataset/
│
├── Supervised Labeled Train Data/
│   ├── A_Sample_01_d.vtp     (Labeled, upper arch)
│   ├── A_Sample_02_d.vtp
│   ├── B_Sample_01_d.vtp     (Labeled, lower arch)
│   └── ...
│
├── Selfsupervised Clustered Train Data/
│   ├── mesh_0001.vtp         (Unlabeled, cluster 1)
│   ├── mesh_0002.vtp         (Unlabeled, cluster 2)
│   ├── ...
│   └── mesh_NNNN.vtp         (60 clusters total)
│
└── Labeled Test Data/
    ├── Sample_Test01_d.vtp   (Ground truth for testing)
    ├── Sample_Test02_d.vtp
    └── ...

Original High-Resolution Data/
├── (Available via Google Drive)
└── Full resolution clinical scans
```

#### **Quality Characteristics:**
- ✅ **Publicly available** (major advantage)
- ✅ Original high-resolution scans included
- ✅ Dual dataset (labeled + unlabeled)
- ✅ Larger effective training data via clustering
- ✅ Supports semi-supervised research
- ✅ Pre-clustered for convenience
- ✅ Suitable for few-shot learning experiments

---

## 📐 Data Specifications Comparison

### Mesh Geometry

| Property | MeshSegNet | Semi-Supervised |
|----------|------------|-----------------|
| **Format** | VTP (VTK PolyData) | VTP (VTK PolyData) |
| **Mesh Type** | Triangle mesh | Triangle mesh |
| **Cells per Scan** | Variable (pre-downsampled) | Variable (original resolution available) |
| **Patch Size (Training)** | 6,000 cells | 9,000 cells (supervised), varies (self-supervised) |
| **Coordinate System** | Centered at origin | Centered at origin |
| **Geometric Features** | 15 channels | 15 channels |

### Feature Channels (15 total)

Both datasets use identical feature representation:

| Channels | Description | Dimension |
|----------|-------------|-----------|
| 1-9 | **Cell Vertices** | 3 triangle points × 3 coords |
| 10-12 | **Normal Vectors** | Face normal direction (x, y, z) |
| 13-15 | **Relative Position** | Barycenter coordinates (x, y, z) |

### Label Structure

| Property | MeshSegNet | Semi-Supervised |
|----------|------------|-----------------|
| **Number of Classes** | 15 | 15 |
| **Gingiva Class** | 0 | 0 |
| **Tooth Classes** | 1-14 | 1-14 |
| **Tooth Coverage** | 2nd molar to 2nd molar | 2nd molar to 2nd molar |
| **Label Granularity** | Per-cell (triangle) | Per-cell (triangle) |
| **Label Field Name** | `'Label'` | `'Label'` |
| **FDI Notation Support** | Via conversion | Via conversion |

### Dental Nomenclature

Both use simplified 15-class labeling (0-14) which maps to FDI notation:

```
Upper Arch (Maxilla):
17 (Class 1) → 11 (Class 7) → 27 (Class 14)

Lower Arch (Mandible):  
47 (Class 1) → 41 (Class 7) → 37 (Class 14)

Class 0: Gingiva (gums)
```

---

## 🔬 Dataset Acquisition & Preprocessing

### MeshSegNet

**Acquisition:**
- Clinical intraoral scanners (IOSs)
- Manufacturer/model not specified
- Real patient data (anonymized)

**Preprocessing:**
1. **Downsampling:** Pre-applied before dataset creation
   - Reduces computational load
   - Fixed resolution across all samples
   
2. **Annotation:** Manual expert labeling
   - Per-triangle classification
   - 15-class taxonomy
   - Clinical validation

3. **Data Format:** Converted to VTP for VTK compatibility

**Challenges:**
- ❌ No access to original high-resolution scans
- ❌ Downsampling artifacts may exist
- ❌ Cannot regenerate at different resolutions

---

### Semi-Supervised Teeth Segmentation

**Acquisition:**
- Multiple intraoral scanner sources
- Original high-resolution data preserved
- Diverse patient population

**Preprocessing:**

**1. Labeled Data:**
- Manual annotation by experts
- Per-triangle labels (15 classes)
- Clinical validation
- Both original and processed versions available

**2. Unlabeled Data (Self-Supervised):**
- **Clustering:** Pre-clustered into 60 pseudo-categories
- **Purpose:** Contrastive learning without ground truth
- **Method:** Likely based on geometric/anatomical similarity
- **Organization:** Grouped by cluster ID in separate folders

**3. Data Availability:**
- ✅ Original resolution scans: Google Drive
- ✅ Processed training data: Included in repository
- ✅ Augmented versions: Generated via scripts

**Advantages:**
- ✅ Multiple resolution options
- ✅ Flexibility for different applications
- ✅ Supports semi-supervised experiments out-of-the-box
- ✅ Pre-clustered unlabeled data saves computation

---

## 📈 Data Augmentation Strategies

### MeshSegNet Augmentation

Applied to 24 training + 6 validation scans (30 total):

**Per Scan Augmentation (20× each):**
1. **Random Rotation** - Full 3D rotation in reasonable ranges
2. **Random Translation** - Spatial shifts
3. **Random Rescaling** - Size variations

**Resulting Dataset:**
- Training: 24 scans × 2 (original + flipped) × 20 augmentations = **960 samples**
- Validation: 6 scans × 2 × 20 = **240 samples**
- Test: 6 scans (no augmentation) = **6 samples**

**Total Augmented:** 1,200 samples

---

### Semi-Supervised Augmentation

**Supervised Data Augmentation (20× each):**
- Same strategy as MeshSegNet
- Applied to labeled scans only

**Augmentation Parameters:**
- **Rotation:** ±10° on X, Y, Z axes (more conservative)
- **Translation:** ±1 unit
- **Scaling:** 0.9-1.1 scale factors

**Self-Supervised Data:**
- Already pre-clustered (60 clusters)
- Additional on-the-fly augmentation during training
- Dynamic transformations via `provider.py`

**Online Augmentation (During Training):**
- Random point cloud rotations
- Point shuffling
- Normalization

**Resulting Effective Dataset:**
- Supervised: Similar to MeshSegNet (~900-1000 labeled samples)
- Self-supervised: Large pool of clustered unlabeled data
- **Combined advantage:** More diverse training signal

---

## 🆚 Key Differences

### 1. **Data Availability** ⭐ MOST IMPORTANT

| Aspect | MeshSegNet | Semi-Supervised |
|--------|------------|-----------------|
| **Public Access** | ❌ NO | ✅ YES |
| **Download Link** | None | [Google Drive](https://drive.google.com/drive/folders/1YRCakTTTyr8Sqp3pBBqvgMgZKb59ktES) |
| **Reproducibility** | ❌ Limited - need own data | ✅ Full - data provided |
| **Research Impact** | Requires data collection | Ready to use |

**Winner:** 🏆 **Semi-Supervised** - Public availability is a game-changer

---

### 2. **Dataset Composition**

| Component | MeshSegNet | Semi-Supervised |
|-----------|------------|-----------------|
| **Labeled Data** | 100% (all 36 scans) | Partial (similar quantity) |
| **Unlabeled Data** | None | ✅ Pre-clustered (60 clusters) |
| **Learning Paradigm** | Fully supervised | Semi-supervised |
| **Data Efficiency** | Requires all labels | Works with fewer labels |

**Winner:** 🏆 **Semi-Supervised** - Better for limited annotation scenarios

---

### 3. **Data Resolution**

| Aspect | MeshSegNet | Semi-Supervised |
|--------|------------|-----------------|
| **Original Scans** | ❌ Not available | ✅ Available (Google Drive) |
| **Processed Scans** | Pre-downsampled | Multiple resolutions |
| **Flexibility** | Fixed resolution | User choice |
| **Detail Preservation** | Some loss from downsampling | Full detail preserved |

**Winner:** 🏆 **Semi-Supervised** - More flexibility

---

### 4. **Training Data Volume**

| Type | MeshSegNet | Semi-Supervised |
|------|------------|-----------------|
| **Base Scans** | 36 | ~30-40 (estimated) |
| **After Augmentation** | 1,200 samples | ~900-1,000 labeled + unlabeled pool |
| **Effective Training Data** | 960 labeled | 900 labeled + large unlabeled corpus |
| **Data Diversity** | Augmentation only | Augmentation + clustering |

**Winner:** 🏆 **Semi-Supervised** - More diverse learning signals

---

### 5. **Annotation Burden**

| Aspect | MeshSegNet | Semi-Supervised |
|--------|------------|-----------------|
| **Labeled Samples Required** | All 36 scans (100%) | Fewer labeled + unlabeled |
| **Annotation Time** | High (45 min/scan × 36) | Lower (fewer labeled needed) |
| **Scalability** | Limited by annotation cost | Can leverage unlabeled data |
| **Clinical Feasibility** | Requires expert time | More practical for clinics |

**Winner:** 🏆 **Semi-Supervised** - Reduced annotation burden

---

### 6. **Data Organization**

| Aspect | MeshSegNet | Semi-Supervised |
|--------|------------|-----------------|
| **Structure** | Single flat dataset | Multi-folder (labeled/unlabeled/test) |
| **Clustering** | None | 60 pre-computed clusters |
| **Ready for Research** | Requires preprocessing | Multiple experiments ready |
| **Documentation** | Basic | Clear folder structure |

**Winner:** 🏆 **Semi-Supervised** - Better organization

---

## 🎯 Use Case Recommendations

### Use MeshSegNet Dataset When:
- ❌ **Problem:** Dataset not publicly available
- You already have proprietary dental scan data
- You need a proven supervised learning baseline
- You want to replicate published results with your data

### Use Semi-Supervised Dataset When:
- ✅ You need a publicly available dental dataset
- ✅ You want to research semi-supervised learning
- ✅ You have limited annotation budget
- ✅ You need original high-resolution scans
- ✅ You want to benchmark on public data
- ✅ You're exploring few-shot learning
- ✅ You need pre-clustered unlabeled data

---

## 🔗 Dataset Access

### MeshSegNet Dataset
- **Availability:** ❌ Not publicly available
- **Access Method:** Must collect your own dental scans
- **Alternative:** Use 3DTeethSeg public benchmark (separate dataset)
- **Citation:** Cite the paper but provide your own data

### Semi-Supervised Teeth Segmentation Dataset
- **Availability:** ✅ Publicly available
- **Download Link:** [Google Drive](https://drive.google.com/drive/folders/1YRCakTTTyr8Sqp3pBBqvgMgZKb59ktES)
- **Contents:**
  - Supervised labeled training data
  - Self-supervised clustered data
  - Labeled test data
  - Original high-resolution scans
- **License:** Check dataset documentation (likely academic use)

---

## 🌐 Alternative Public Datasets

If you need public dental datasets, consider:

### **3DTeethSeg Dataset** (Recommended Alternative)

- **Scale:** 1,800 3D intra-oral scans (900 patients)
- **Coverage:** 23,999 annotated teeth
- **Format:** High-resolution mesh (30-80 points/mm²)
- **Annotations:** Per-vertex labels with FDI notation
- **Diversity:** Children, adults, orthodontic, prosthetic cases
- **Scanners:** 3Shape Trios3, Dentsply Primescan, iTero Element 2 Plus
- **Validation:** Clinical expert verification
- **Access:** [3DTeethSeg Challenge](https://3dteethseg.grand-challenge.org/)
- **Papers:** 
  - [3DTeethSeg'22 ArXiv](https://arxiv.org/abs/2305.18277)
  - [Teeth3DS+ Benchmark](https://crns-smartvision.github.io/teeth3ds/)

**Advantages over both MeshSegNet and Semi-Supervised:**
- ✅ Much larger scale (1,800 vs 36-40 scans)
- ✅ Greater diversity (multiple scanners, conditions)
- ✅ Per-vertex annotations (finer than per-cell)
- ✅ Established benchmark with leaderboards
- ✅ Active research community

---

## 📊 Summary Table: Dataset Comparison

| Feature | MeshSegNet | Semi-Supervised | 3DTeethSeg (Alternative) |
|---------|------------|-----------------|--------------------------|
| **Public Availability** | ❌ No | ✅ Yes | ✅ Yes |
| **Number of Scans** | 36 | ~30-40 | 1,800 |
| **Labeled Scans** | 36 (100%) | Partial | 1,800 (100%) |
| **Unlabeled Data** | None | Yes (60 clusters) | No |
| **Annotation Level** | Per-cell | Per-cell | Per-vertex |
| **Original Resolution** | ❌ No | ✅ Yes | ✅ Yes |
| **Learning Paradigm** | Supervised | Semi-supervised | Supervised |
| **Clinical Validation** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Diversity** | Limited | Moderate | High |
| **Research Community** | Established | Growing | Very Active |
| **Best For** | Own data | Semi-supervised | Benchmarking |

---

## 🎓 Research Impact

### MeshSegNet Dataset (2019)
- **Impact:** Foundation work, widely cited
- **Limitation:** No public data limits reproduction
- **Legacy:** Inspired many follow-up works
- **Citations:** High (foundational paper)

### Semi-Supervised Dataset (2022)
- **Impact:** Enables semi-supervised research
- **Advantage:** Public data accelerates research
- **Innovation:** Demonstrates 13% improvement with less labeled data
- **Accessibility:** Lower barrier to entry

### Recommendation for New Researchers:
1. **Start with:** Semi-Supervised dataset (publicly available)
2. **Benchmark on:** 3DTeethSeg (large-scale public dataset)
3. **Compare to:** MeshSegNet methodology (if you have own data)

---

## 🔍 What's Actually Inside the Scans?

### Anatomical Content (Both Datasets)

**Each 3D scan contains:**

1. **Gingiva (Gums):**
   - Soft tissue surrounding teeth
   - Labeled as Class 0
   - Occupies largest surface area
   - Variable topology

2. **Teeth (Classes 1-14):**
   - **Incisors (front teeth):** 4 per arch
   - **Canines (cuspids):** 2 per arch
   - **Premolars (bicuspids):** 4 per arch
   - **Molars (back teeth):** 4 per arch (2nd molar to 2nd molar)
   - Each tooth is a separate 3D object within the mesh

3. **Geometric Complexity:**
   - Sharp edges (tooth boundaries)
   - Smooth surfaces (tooth crowns)
   - Complex curvatures (gingival sulcus)
   - Occlusal surfaces (biting surfaces with grooves)
   - Interdental spaces (gaps between teeth)

4. **Variations Present:**
   - Missing teeth
   - Crowded teeth (overlapping)
   - Rotated/misaligned teeth
   - Dental restorations (fillings, crowns)
   - Orthodontic appliances (in some cases)
   - Anatomical abnormalities

---

## 📝 Conclusion

### Key Takeaways:

1. **MeshSegNet Dataset:**
   - ❌ Not publicly available (major limitation)
   - ✅ Well-established methodology
   - ✅ 36 clinically validated scans
   - ❌ Requires researchers to collect own data

2. **Semi-Supervised Dataset:**
   - ✅ **Publicly available** (huge advantage)
   - ✅ Supports semi-supervised research
   - ✅ Original high-resolution scans included
   - ✅ Pre-clustered unlabeled data provided
   - ✅ Lower annotation burden

3. **3DTeethSeg (Recommended Alternative):**
   - ✅ Largest public dataset (1,800 scans)
   - ✅ Active benchmark with leaderboards
   - ✅ Highest diversity and clinical validation
   - ✅ State-of-the-art baseline comparisons

### Final Recommendation:

**For Most Researchers:** Start with the **Semi-Supervised Teeth Segmentation dataset** due to public availability and support for modern semi-supervised methods.

**For Benchmarking:** Use **3DTeethSeg** for comparison with latest research.

**For MeshSegNet Methodology:** Apply to your own data or publicly available alternatives.

---

## 📚 References & Links

### MeshSegNet
- Paper: [IEEE TMI 2020](https://ieeexplore.ieee.org/abstract/document/8984309)
- Code: [GitHub](https://github.com/Tai-Hsien/MeshSegNet)
- Dataset: ❌ Not available

### Semi-Supervised Teeth Segmentation
- Paper: [arXiv](https://arxiv.org/abs/2208.05539)
- Code: [GitHub](https://github.com/Alsheghri/Teeth-Segmentation)
- Dataset: ✅ [Google Drive](https://drive.google.com/drive/folders/1YRCakTTTyr8Sqp3pBBqvgMgZKb59ktES)

### 3DTeethSeg Benchmark
- Challenge: [Website](https://3dteethseg.grand-challenge.org/)
- Paper: [arXiv](https://arxiv.org/abs/2305.18277)
- Code: [GitHub](https://github.com/abenhamadou/3DTeethSeg_MICCAI_Challenges)

---

*Report compiled based on repository analysis and web research. Dataset specifications reflect publicly available information as of 2024.*