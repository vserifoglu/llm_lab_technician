# MeshSegNet Repository Overview

## 📋 Project Summary

**Repository:** Tai-Hsien/MeshSegNet

**Authors:** Chunfeng Lian, Li Wang, Tai-Hsien Wu, Fan Wang, Pew-Thian Yap, Ching-Chang Ko, and Dinggang Shen

**Publications:**
- [IEEE Transactions on Medical Imaging (2020)](https://ieeexplore.ieee.org/abstract/document/8984309)
- [MICCAI 2019](https://link.springer.com/chapter/10.1007/978-3-030-32226-7_93)

**Purpose:** Deep multi-scale mesh feature learning for automated labeling of raw dental surfaces from 3D intraoral scanners (IOSs).

---

## 🎯 Main Features

### 1. **Multi-Scale Feature Learning**
- Hierarchical feature extraction at different scales
- Combines local geometric features with global context
- Deep learning architecture specifically designed for 3D mesh data

### 2. **Graph-Constrained Learning Modules (GLM)**
- Two GLM modules that leverage mesh topology
- Uses adjacency matrices (A_S and A_L) to capture spatial relationships
- Spatial Aggregation Pooling (SAP) for neighborhood feature aggregation

### 3. **Feature Transformer Module (FTM)**
- Spatial Transformer Network for feature space alignment
- Ensures feature invariance across different mesh orientations
- Improves robustness to mesh variations

### 4. **Dense Feature Fusion**
- Multi-level feature concatenation
- Combines features from different network depths
- Preserves both fine-grained and coarse details

### 5. **Post-Processing with Graph Cuts**
- Optional multi-label graph-cut refinement
- Smooths segmentation boundaries
- Improves spatial consistency using pygco library

### 6. **Complete Training Pipeline**
- Data augmentation (rotation, translation, scaling)
- K-fold cross-validation support
- Pre-trained models for upper and lower dental arches

---

## �� Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MESHSEGNET PIPELINE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: DATA AUGMENTATION                                                     │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Input: 36 Intraoral Scans (.vtp files)                                     │
│         ├─ 24 scans → Training                                               │
│         ├─ 6 scans → Validation                                              │
│         └─ 6 scans → Testing                                                 │
│                                                                               │
│  ┌─────────────────────────────────────┐                                    │
│  │  step1_augmentation.py              │                                    │
│  │  • Random rotation                  │                                    │
│  │  • Random translation                │                                    │
│  │  • Random rescaling                  │                                    │
│  │  • Each scan + flipped → 20 augments │                                    │
│  └─────────────────────────────────────┘                                    │
│         ↓                                                                     │
│  Output: ./augmentation_vtk_data/                                           │
│         960 training samples (24 × 2 × 20)                                  │
│         240 validation samples (6 × 2 × 20)                                 │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: GENERATE TRAINING & VALIDATION LISTS                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────┐                                    │
│  │  step2_get_list.py                  │                                    │
│  │  • Parse augmented data             │                                    │
│  │  • 80/20 train/val split            │                                    │
│  │  • Generate CSV lists               │                                    │
│  └─────────────────────────────────────┘                                    │
│         ↓                                                                     │
│  Output: train_list_1.csv, val_list_1.csv                                   │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: MODEL TRAINING                                                        │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  step3_training.py                                               │        │
│  │                                                                  │        │
│  │  ┌──────────────────────────────────────────────────────────┐  │        │
│  │  │  MeshSegNet Architecture (meshsegnet.py)                 │  │        │
│  │  │                                                            │  │        │
│  │  │  Input: [batch, 15 channels, 6000 cells]                 │  │        │
│  │  │         • Cell vertices (9): 3 points × 3 coords          │  │        │
│  │  │         • Normal vectors (3)                              │  │        │
│  │  │         • Relative positions (3)                          │  │        │
│  │  │                                                            │  │        │
│  │  │  ┌──────────────────────────────────────────────┐        │  │        │
│  │  │  │  MLP-1: [64, 64]                             │        │  │        │
│  │  │  │  • Conv1d layers with BatchNorm              │        │  │        │
│  │  │  └──────────────┬───────────────────────────────┘        │  │        │
│  │  │                 ↓                                          │  │        │
│  │  │  ┌──────────────────────────────────────────────┐        │  │        │
│  │  │  │  FTM (Feature Transformer Module)            │        │  │        │
��  │  │  │  • STNkd: k=64                               │        │  │        │
│  │  │  │  • Learns 64×64 transformation matrix        │        │  │        │
│  │  │  │  • Aligns features in high-dim space         │        │  │        │
│  │  │  └──────────────┬───────────────────────────────┘        │  │        │
│  │  │                 ↓                                          │  │        │
│  │  │  ┌──────────────────────────────────────────────┐        │  │        │
│  │  │  │  GLM-1 (Graph-Constrained Learning)          │        │  │        │
│  │  │  │  • Input: x_ftm, A_S (adjacency matrix)      │        │  │        │
│  │  │  │  • SAP: Spatial Aggregation Pooling          │        │  │        │
│  │  │  │  • Conv layers: [32+32 → 64]                 │        │  │        │
│  │  │  └──────────────┬───────────────────────────────┘        │  │        │
│  │  │                 ↓                                          │  │        │
│  │  │  ┌──────────────────────────────────────────────┐        │  │        │
│  │  │  │  MLP-2: [64, 128, 512]                       │        │  │        │
│  │  │  │  • Deeper feature extraction                 │        │  │        │
│  │  │  │  • Dropout (p=0.5)                           │        │  │        │
│  │  │  └──────────────┬───────────────────────────────┘        │  │        │
│  │  │                 ↓                                          │  │        │
│  │  │  ┌──────────────────────────────────────────────┐        │  │        │
│  │  │  │  GLM-2 (Graph-Constrained Learning)          │        │  │        │
│  │  │  │  • Input: x_mlp2, A_S, A_L (2 matrices)      │        │  │        │
│  │  │  │  • SAP on both adjacency matrices            │        │  │        │
│  │  │  │  • Conv layers: [128×3 → 512]                │        │  │        │
│  │  │  └──────────────┬───────────────────────────────┘        │  │        │
│  │  │                 ↓                                          │  │        │
│  │  │  ┌─────────────────────────────────────────────���┐        │  │        │
│  │  │  │  Global Max Pooling (GMP)                    │        │  │        │
│  │  │  │  • Extract global features                   │        │  │        │
│  │  │  └──────────────┬───────────────────────────────┘        │  │        │
│  │  │                 ↓                                          │  │        │
│  │  │  ┌──────────────────────────────────────────────┐        │  │        │
│  │  │  │  Upsample + Dense Fusion                     │        │  │        │
│  │  │  │  • Concatenate: x_ftm + x_mlp2 + x_glm2      │        │  │        │
│  │  │  │  • Multi-scale feature integration           │        │  │        │
│  │  │  └────────────���─┬───────────────────────────────┘        │  │        │
│  │  │                 ↓                                          │  │        │
│  │  │  ┌──────────────────────────────────────────────┐        │  │        │
│  │  │  │  MLP-3: [256, 256, 128, 128]                 │        │  │        │
│  │  │  │  • Final refinement layers                   │        │  │        │
│  │  │  │  • Dropout before output                     │        │  │        │
│  │  │  └──────────────┬───────────────────────────────┘        │  │        │
│  │  │                 ↓                                          │  │        │
│  │  │  ┌──────────────────────────────────────────────┐        │  │        │
│  │  │  │  Output Layer: [128 → 15 classes]            │        │  │        │
│  │  │  │  • Softmax activation                        │        │  │        │
│  │  │  │  • Per-cell classification                   │        │  │        │
│  │  │  └──────────────────────────────────────────────┘        │  │        │
│  │  │                                                            │  │        │
│  │  │  Output: [batch, 6000 cells, 15 classes]                 │  │        │
│  │  ���──────────────────────────────────────────────────────────┘  │        │
│  │                                                                  │        │
│  │  Training Parameters:                                           │        │
│  │  • Epochs: 200                                                  │        │
│  │  • Batch Size: 10                                               │        │
│  │  • Optimizer: Adam (amsgrad=True)                               │        │
│  │  • Patch Size: 6000 cells per sample                            │        │
│  │  • Loss: Generalized Dice Loss                                  │        │
│  │  • Metrics: DSC, SEN, PPV (weighted)                            │        │
│  │  • Monitoring: Visdom (optional)                                │        │
│  └──────────────────────────────────────────────────────────────────┘        │
│         ↓                                                                     │
│  Output: ./models/MeshSegNet_best.tar                                       │
│         (Upper and Lower models provided)                                   │
│                                                                               │
└─────────���─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 3-1: CONTINUOUS TRAINING (Optional)                                      │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────┐                                    │
│  │  step3_1_continous_training.py      │                                    │
│  │  • Resume from checkpoint           │                                    │
│  │  • Continue training for 300 epochs │                                    │
│  └─────────────────────────────────────┘                                    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: MODEL TESTING                                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Input: Test Dataset (6 scans)                                              │
│         ↓                                                                     │
│  ┌─────────────────────────────────────┐                                    │
│  │  step4_test.py                      │                                    │
│  │  • Load trained model               │                                    │
│  │  • Predict on test meshes           │                                    │
│  │  • Compare with ground truth        │                                    │
│  │  • Calculate metrics:               │                                    │
│  │    - Weighted DSC                   │                                    │
│  │    - Weighted SEN                   │                                    │
│  │    - Weighted PPV                   │                                    │
│  └─────────────────────────────────────┘                                    │
│         ↓                                                                     │
│  Output: ./test/                                                            │
│         • Segmented meshes with predictions                                 │
│         • Performance metrics displayed                                     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: PREDICT ON UNSEEN DATA (Optional)                                     │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Input: New Intraoral Scans (.stl, .vtp)                                    │
│         ↓                                                                     │
│  ┌─────────────────────────────────────┐                                    │
│  │  step5_predict.py                   │                                    │
│  │  • Load trained model               │                                    │
│  │  • Auto-downsample if >10k cells    │                                    │
│  │  • Predict tooth labels             │                                    │
│  │  • No ground truth required         │                                    │
│  └─────────────────────────────────────┘                                    │
│         ↓                                                                     │
│  Output: ./outputs/                                                         │
│         • Labeled dental scans                                              │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: POST-PROCESSING WITH GRAPH CUTS (Optional)                            │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Input: Predicted meshes from Step 5                                        │
│         ↓                                                                     │
│  ┌─────────────────────────────────────┐                                    │
│  │  step6_predict_with_post_processing │                                    │
│  │  • Multi-label graph-cut refinement │                                    │
│  │  • Smooth segmentation boundaries   │                                    │
│  │  • Uses pygco library               │                                    │
│  └─────────────────────────────────────┘                                    │
│         ↓                                                                     │
│  Output: Refined segmentation with smoother boundaries                      │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ FINAL OUTPUT                                                                   │
├───────────────────────────────────────────────────────────────────────────────┤
│  • Fully labeled 3D dental surfaces                                           │
│  • 15 classes: 14 teeth (2nd molar to 2nd molar) + gingiva                   │
│  • High-precision automated segmentation                                      │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
MeshSegNet/
├── step1_augmentation.py              # Data augmentation
├── step2_get_list.py                  # Train/val split generation
├── step3_training.py                  # Main training script
├── step3_1_continous_training.py      # Resume training (optional)
├── step4_test.py                      # Model evaluation
├── step5_predict.py                   # Predict on unseen data
├── step6_predict_with_post_processing_pygco.py  # Graph-cut refinement
├── meshsegnet.py                      # MeshSegNet architecture
├── Mesh_dataset.py                    # Dataset loader & preprocessing
├── losses_and_metrics_for_mesh.py     # Loss functions & metrics
├── utils.py                           # Utility functions (GPU, Visdom)
├── requirements.txt                   # Python dependencies
├── meshsegnet_architecture.png        # Architecture diagram
├── losses_metrics_vs_epoch.csv        # Training curves
├── models/                            # Pre-trained models
│   ├── Upper jaw model
│   └── Lower jaw model
└── README.md
```

---

## 🔧 Core Components

### **MeshSegNet Architecture** (`meshsegnet.py`)

The network consists of several specialized modules:

#### 1. **STN3d** - Spatial Transformer Network (Input Space)
- Predicts 3×3 transformation matrix
- Aligns input meshes to canonical orientation
- Improves rotation invariance

```python
Input: [batch, channels, points]
  ↓
Conv1d: channels → 64 → 128 → 1024
  ↓
MaxPool + FC: 1024 → 512 → 256 → 9
  ↓
Output: [batch, 3, 3] transformation matrix
```

#### 2. **STNkd** - Feature Space Transformer
- Similar to STN3d but operates in feature space
- Predicts k×k transformation matrix (k=64)
- Aligns features for better discrimination

#### 3. **MLP Modules**
- **MLP-1**: Initial feature extraction [15 → 64 → 64]
- **MLP-2**: Intermediate features [64 → 64 → 128 → 512]
- **MLP-3**: Final refinement [256 → 256 → 128 → 128 → 15]

#### 4. **GLM (Graph-Constrained Learning Modules)**
Two GLM modules leverage mesh topology:

**GLM-1:**
- Uses adjacency matrix A_S (short-range connections)
- Spatial Aggregation Pooling: aggregates neighbor features
- Output: 64-dimensional features

**GLM-2:**
- Uses both A_S and A_L (short + long-range connections)
- Dual-scale spatial reasoning
- Output: 512-dimensional features

#### 5. **Dense Feature Fusion**
Concatenates features from multiple scales:
- x_ftm (64-dim): Transformed low-level features
- x_mlp2 (512-dim): Mid-level features
- x_glm2 (512-dim): High-level graph-aware features

Total: 64 + 512 + 512 = 1088 dimensions

### **Dataset Processing** (`Mesh_dataset.py`)

#### Input Features (15 channels per cell):
1. **Cell Vertices (9)**: 3 triangle vertices × 3 coordinates
2. **Normal Vectors (3)**: Face normal direction
3. **Relative Position (3)**: Barycenter coordinates

#### Data Preprocessing:
- **Centering**: Move mesh to origin using center of mass
- **Normalization**: Standardize coordinates and normals
- **Patch Sampling**: Select 6000 cells per training sample
  - All tooth cells (labels > 0)
  - Randomly sampled gingiva cells (label = 0)

#### Adjacency Matrices:
- **A_S**: Short-range spatial connections (13 nearest neighbors)
- **A_L**: Long-range spatial connections (geodesic distance-based)
- Both matrices guide the GLM modules

### **Loss Functions & Metrics** (`losses_and_metrics_for_mesh.py`)

#### **Generalized Dice Loss**
- Class-weighted to handle imbalance
- Smooth term prevents division by zero
- Encourages overlap between prediction and ground truth

#### **Evaluation Metrics (Weighted):**

1. **DSC (Dice Similarity Coefficient)**
   ```
   DSC = 2 × |Prediction ∩ Ground Truth| / (|Prediction| + |Ground Truth|)
   ```

2. **SEN (Sensitivity / Recall)**
   ```
   SEN = True Positives / (True Positives + False Negatives)
   ```

3. **PPV (Positive Predictive Value / Precision)**
   ```
   PPV = True Positives / (True Positives + False Positives)
   ```

All metrics are weighted by class frequency to account for tooth size variations.

---

## 📊 Dataset Information

- **Total Scans**: 36 intraoral scans (VTP format)
- **Train**: 24 scans (each + flipped + 20× augmentation = 960 samples)
- **Validation**: 6 scans (each + flipped + 20× augmentation = 240 samples)
- **Test**: 6 scans (original, no augmentation)
- **Number of Classes**: 15
  - Classes 1-14: Individual teeth (2nd molar to 2nd molar)
  - Class 0: Gingiva (gums)
- **Patch Size**: 6000 cells per input sample
- **Mesh Format**: VTP (VTK PolyData) files
- **Downsampling**: Pre-applied to keep meshes manageable

---

## 🚀 Usage Instructions

### **Environment Setup**

```bash
# Create conda environment
conda create --name meshsegnet --file requirements.txt

# Activate environment
conda activate meshsegnet
```

### **Step 1: Data Augmentation**

```bash
python step1_augmentation.py
```

**Configuration:**
- Set `vtk_path` to your data directory
- Generates 20 augmented versions per scan
- Output: `./augmentation_vtk_data/`

### **Step 2: Generate Train/Val Lists**

```bash
python step2_get_list.py
```

**Configuration:**
- `num_augmentation = 20`
- `num_samples = 30` (train + val)
- `train_size = 0.8`
- Output: `train_list_1.csv`, `val_list_1.csv`

### **Step 3: Train Model**

```bash
python step3_training.py
```

**Configuration:**
- `num_epochs = 200`
- `train_batch_size = 10`
- `patch_size = 6000`
- `use_visdom = True` (optional, for monitoring)
- Output: `./models/MeshSegNet_best.tar`

**Optional - Continue Training:**
```bash
python step3_1_continous_training.py
```

### **Step 4: Test Model**

```bash
python step4_test.py
```

**Configuration:**
- Set `mesh_path` to test data directory
- Specify `model_name` to load
- Output: Segmented meshes in `./test/` + metrics printed

### **Step 5: Predict on New Data**

```bash
python step5_predict.py
```

**Configuration:**
- Set `mesh_path` and `sample_filenames`
- Accepts `.stl` and `.vtp` files
- Auto-downsamples meshes > 10,000 cells
- Output: Labeled meshes in `./outputs/`

### **Step 6: Post-Processing (Optional)**

```bash
python step6_predict_with_post_processing_pygco.py
```

Applies multi-label graph-cut refinement using pygco library.

---

## 📈 Key Results & Performance

### **Architecture Highlights**
- **Multi-scale learning**: Captures both local and global features
- **Graph-aware**: Leverages mesh topology through GLM modules
- **Rotation invariant**: STN modules handle orientation variations
- **Dense fusion**: Integrates features from multiple network depths

### **Training Details**
- **Pre-trained models**: Separate models for upper/lower arches
- **Training curves**: Provided in `losses_metrics_vs_epoch.csv`
- **Regularization**: Dropout (p=0.5) prevents overfitting
- **Optimizer**: Adam with amsgrad for stable convergence

### **Applications**
- Automated tooth labeling for orthodontic treatment planning
- Reduces manual annotation time significantly
- Handles complex dental anatomies and variations
- Compatible with clinical intraoral scanners

---

## 🔗 Dependencies

Key libraries (from `requirements.txt`):

- **PyTorch** 1.13.1 - Deep learning framework
- **VTK** 9.2.4 - 3D mesh processing
- **Vedo** 2022.4.2 - VTK interface & visualization
- **NumPy** 1.23.1 - Numerical computing
- **Pandas** 1.5.2 - Data handling
- **SciPy** 1.10.0 - Scientific computing
- **scikit-learn** 1.2.0 - Machine learning utilities
- **Visdom** 0.2.3 - Training visualization
- **pygco** 0.0.16 - Graph-cut optimization
- **Python** 3.9.15

---

## 🔗 Related Tools

- **Vedo**: 3D mesh visualization - https://github.com/marcomusy/vedo
- **Mesh Labeler**: GUI tool for mesh annotation - https://github.com/Tai-Hsien/Mesh_Labeler
- **PyGCO**: Python wrapper for graph cuts - https://github.com/amueller/gco_python

---

## 📚 Citation

If you use this code, please cite:

```bibtex
@article{lian2020meshsegnet,
  title={Deep Multi-Scale Mesh Feature Learning for Automated Labeling of Raw Dental Surfaces From 3D Intraoral Scanners},
  author={Lian, Chunfeng and Wang, Li and Wu, Tai-Hsien and Wang, Fan and Yap, Pew-Thian and Ko, Ching-Chang and Shen, Dinggang},
  journal={IEEE Transactions on Medical Imaging},
  volume={39},
  number={7},
  pages={2440--2450},
  year={2020},
  publisher={IEEE}
}

@inproceedings{lian2019meshsegnet,
  title={MeshSegNet: Deep Multi-scale Mesh Feature Learning for End-to-End Tooth Labeling on 3D Dental Surfaces},
  author={Lian, Chunfeng and Wang, Li and Wu, Tai-Hsien and Liu, Mingxia and Dur{\'a}n, Francisca and Ko, Ching-Chang and Shen, Dinggang},
  booktitle={International Conference on Medical Image Computing and Computer-Assisted Intervention},
  pages={837--845},
  year={2019},
  organization={Springer}
}
```

---

## �� Technical Innovations

### **1. Mesh-Native Architecture**
- Operates directly on 3D triangle meshes (not voxels or point clouds)
- Preserves geometric details and topology
- Efficient for clinical applications

### **2. Graph-Constrained Learning**
- Novel GLM modules that respect mesh connectivity
- Spatial aggregation from neighboring cells
- Multi-scale adjacency matrices (A_S for local, A_L for global)

### **3. Multi-Scale Feature Fusion**
- Dense connections inspired by DenseNet
- Combines features from different network depths
- Balances fine details with semantic context

### **4. Adaptive Patch Sampling**
- Samples all tooth cells + random gingiva cells
- Balances class distribution during training
- Handles varying mesh sizes

### **5. Clinical Validation**
- Tested on real intraoral scanner data
- Published in top medical imaging journals
- Provides pre-trained models for immediate use

---

## 🎓 Research Context

**Problem**: Manual tooth labeling on 3D dental scans is time-consuming and requires expert knowledge.

**Solution**: End-to-end deep learning architecture that:
1. Learns multi-scale geometric features
2. Respects mesh topology through graph constraints
3. Achieves high accuracy with automatic labeling

**Impact**: Enables automated dental treatment planning and reduces clinician workload.

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

This is the foundational work that inspired many subsequent research projects, including the semi-supervised teeth segmentation approach in the Alsheghri/Teeth-Segmentation repository.

---

*Repository: https://github.com/Tai-Hsien/MeshSegNet*

*Note: Search results may be incomplete. For complete code exploration, visit the [repository](https://github.com/Tai-Hsien/MeshSegNet) directly.*