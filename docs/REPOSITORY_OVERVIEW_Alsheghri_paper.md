# Teeth-Segmentation Repository Overview

## 📋 Project Summary

**Authors:** Ammar Alsheghri, Farnoosh Ghadiri, Ying Zhang, Olivier Lessard, Julia Keren, Farida Cheriet, Francois Guibault

**Publication:** Semi-supervised segmentation of tooth from 3D Scanned Dental Arches (SPIE 2022)

**Paper:** [arXiv](https://arxiv.org/abs/2208.05539)

This repository implements a **semi-supervised deep learning approach** for tooth segmentation from 3D dental arch scans. The key innovation is combining supervised and self-supervised learning to improve segmentation performance with limited labeled data, achieving a **13% improvement** over purely supervised learning.

---

## 🎯 Main Features

### 1. **Semi-Supervised Learning Architecture**
- Combines supervised learning (labeled data) with self-supervised learning (unlabeled data)
- Uses joint loss function to leverage both labeled and unlabeled datasets
- Improves generalization with limited labeled training data

### 2. **MeshSegNet-Based Architecture**
- 3D mesh segmentation network adapted for dental arches
- Based on PointNet-like architecture with spatial transformation networks (STN)
- Handles complex tooth geometries and abnormalities

### 3. **DGCNN Integration**
- Dynamic Graph CNN (DGCNN) for self-supervised learning
- K-nearest neighbor (KNN) based feature extraction
- Contrastive loss with margin for self-supervised training

### 4. **Data Augmentation Pipeline**
- Random rotations (±10° on X, Y, Z axes)
- Random translations (±1 unit)
- Random scaling (0.9-1.1 scale factors)
- Generates 20 augmented samples per input mesh

### 5. **Comprehensive Metrics**
- Dice Similarity Coefficient (DSC) - weighted
- Sensitivity (SEN) - weighted
- Positive Predictive Value (PPV) - weighted
- Class-weighted evaluation for 15 tooth classes

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TEETH SEGMENTATION PIPELINE                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: DATA PREPARATION                                                      │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Input: Raw 3D Dental Scans (.vtp files)                                    │
│         ↓                                                                     │
│  ┌─────────────────────────────────────┐                                    │
│  │  step1_data_augmentation.py         │                                    │
│  │  • Rotate: [-10°, +10°] X,Y,Z       │                                    │
│  │  • Translate: [-1, +1] units        │                                    │
│  │  • Scale: [0.9, 1.1] factors        │                                    │
│  │  • Generate 20 augmentations/mesh   │                                    │
│  └─────────────────────────────────────┘                                    │
│         ↓                                                                     │
│  Augmented Dataset (20x larger)                                              │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌─��─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: DATASET SPLITTING                                                     │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────┐                                    │
│  │ step2_get_supervised_training_list  │                                    │
│  │  • 3-Fold Cross-Validation          │                                    │
│  │  • 80% Train / 20% Validation       │                                    │
│  │  • Generate train_list.csv          │                                    │
│  │  • Generate val_list.csv            │                                    │
│  └─────────────────────────────────────┘                                    │
│         ↓                                                                     │
│  train_list_1.csv, val_list_1.csv                                           │
│  train_list_2.csv, val_list_2.csv                                           │
│  train_list_3.csv, val_list_3.csv                                           │
│                                                                               │
└─────────────────────────────────────────────────────────────────��─────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: MODEL TRAINING (Semi-Supervised)                                      │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────┐         ┌──────────────────────┐                 │
│  │  Supervised Dataset   │         │ Self-Supervised Data  │                 │
│  │  (Labeled)            │         │ (Unlabeled - KNN)     │                 │
│  │  • Label: Tooth class │         │ • Clustered data      ���                 │
│  │  • 15 classes         │         │ • 60 clusters         │                 │
│  └──────────┬───────────┘         └──────────┬───────────┘                 │
│             │                                 │                              │
│             └────────────┬────────────────────┘                              │
│                          ↓                                                    │
│  ┌───────────────────────────────────────────────────────┐                  │
│  │         step3_trainingSSKNN.py                         │                  │
│  │  ┌─────────────────────────────────────────────────┐  │                  │
│  │  │  MeshSegNet Architecture                        │  │                  │
│  │  │  • STN3d (Spatial Transformer Network)          │  │                  │
│  │  │  • Feature extraction layers                    │  │                  │
│  │  │  • Segmentation head (15 classes)               │  │                  │
│  │  └─────────────────────────────────────────────────┘  │                  │
│  │                                                         │                  │
│  │  Loss = Supervised Loss + Self-Supervised Loss         │                  │
│  │         (NLL Loss)      (Contrastive Loss)             │                  │
│  │                                                         │                  │
│  │  Training Parameters:                                  │                  │
│  │  • Epochs: 60                                          │                  │
│  │  • Batch Size: 8                                       │                  │
���  │  • Optimizer: Adam (amsgrad=True)                      │                  │
│  │  • Patch Size: 9000 cells                              │                  │
│  │  • Dropout: 0.5                                        │                  │
│  └───────────────────────────────────────────────────────┘                  │
│             ↓                                                                 │
│  Trained Model: semisupervisedTrainingModel.tar                              │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: TESTING & EVALUATION                                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Input: Test Meshes (.vtp files)                                             │
│         ↓                                                                     │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  step4_test.py                                       │                    │
│  │  • Load trained model                                │                    │
│  │  • Predict tooth segmentation                        │                    │
│  │  • Calculate metrics:                                │                    │
│  │    - Weighted DSC (Dice Coefficient)                 │                    │
│  │    - Weighted SEN (Sensitivity)                      │                    │
│  │    - Weighted PPV (Positive Predictive Value)        │                    │
│  └─────────────────────────────────────────────────────┘                    │
│         ↓                                                                     │
│  Segmented Meshes + Performance Metrics                                      │
│                                                                               │
└────────────────────────────────────────────────���──────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ OUTPUT                                                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│  • Segmented 3D dental arches with tooth labels (1-15)                        │
│  • Performance metrics per fold                                               │
│  • 13% improvement over supervised-only baseline                              │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
Teeth-Segmentation/
├── SemiSupervised/
│   ├── step1_data_augmentation.py          # Data augmentation
│   ├── step2_get_supervised_training_list.py  # Train/val split
│   ├── step3_trainingSSKNN.py              # Semi-supervised training
│   ├── step4_test.py                       # Model evaluation
│   ├── meshsegnetSSKNN.py                  # MeshSegNet architecture
│   ├── dgcnn.py                            # DGCNN for self-supervision
│   ├── Mesh_dataset.py                     # Dataset loader
│   ├── losses_and_metrics_for_mesh.py      # Metrics (DSC, SEN, PPV)
│   ├── easy_mesh_vtk.py                    # VTK mesh utilities
│   ├── provider.py                         # Data augmentation helpers
│   ├── utils.py                            # Training utilities
│   ├── requirements_pip.txt                # Dependencies
│   └── models/                             # Pre-trained models
│       ├── Supervised model
│       └── Semi-supervised model
├── Data/ (not included)
│   ├── Supervised Labeled Train Data/
│   ├── Selfsupervised Clustered Train Data/
│   └── Labeled Test Data/
└── README.md
```

---

## 🔧 Core Components

### **MeshSegNet Architecture** (`meshsegnetSSKNN.py`)

1. **STN3d** - Spatial Transformation Network
   - Aligns input meshes to canonical orientation
   - 3×3 transformation matrix prediction
   - Improves rotation invariance

2. **STNkd** - Feature-space transformation
   - Aligns features in high-dimensional space
   - k×k transformation matrix

3. **Feature Extraction**
   - Multi-layer convolutional architecture
   - 15 input channels (geometric features)
   - Global + local feature aggregation

4. **Segmentation Head**
   - Fully connected layers
   - Dropout for regularization (p=0.5)
   - 15-class output (tooth labels)

### **DGCNN Module** (`dgcnn.py`)

- **K-NN Graph Construction**: Builds local neighborhood graphs
- **Edge Convolution**: Learns from point-to-point relationships
- **Self-Supervised Loss**: Contrastive learning with margin (0.5)
  - Positive pairs: Same tooth class
  - Negative pairs: Different tooth classes

### **Loss Functions** (`losses_and_metrics_for_mesh.py`)

```python
Total Loss = Supervised Loss + Self-Supervised Loss
           = NLL(pred, labels) + Contrastive(features, pseudo_labels)
```

- **Supervised**: Negative Log-Likelihood Loss
- **Self-Supervised**: Pairwise cosine similarity loss with margin
- **Metrics**: Class-weighted DSC, SEN, PPV

---

## 📊 Dataset Information

- **Input Format**: VTP (VTK PolyData) files
- **Number of Classes**: 15 (teeth labels)
- **Features per Cell**: 15 channels
  - 3D coordinates (3)
  - Normal vectors (3)
  - Curvature features (varies)
  - Other geometric properties
- **Patch Size**: 9000 cells
- **K-nearest neighbors**: 200 points
- **Self-supervised clusters**: 60

---

## 🚀 Usage Workflow

### **Step 1: Data Augmentation**
```bash
python step1_data_augmentation.py
```
- Augments each mesh 20 times
- Saves augmented files with `_A{i}` suffix

### **Step 2: Create Train/Val Lists**
```bash
python step2_get_supervised_training_list.py
```
- Generates 3-fold cross-validation splits
- Creates CSV files: `train_list_{1-3}.csv`, `val_list_{1-3}.csv`

### **Step 3: Train Model**
```bash
python step3_trainingSSKNN.py
```
- Trains for 60 epochs
- Uses both labeled (supervised) and unlabeled (self-supervised) data
- Saves checkpoints in `./models/`

### **Step 4: Test Model**
```bash
python step4_test.py
```
- Evaluates on test set
- Calculates DSC, SEN, PPV metrics
- Outputs segmented meshes

---

## 📈 Key Results

- **13% improvement** in segmentation score vs. supervised-only learning
- Addresses challenge of limited labeled dental scan data
- Reduces manual segmentation time (baseline: 45 minutes per scan)
- Handles complex dentition and abnormalities

---

## 🔗 Dependencies

Key libraries (from `requirements_pip.txt`):
- **PyTorch** 1.10.0 - Deep learning framework
- **VTK** 9.0.1 - 3D mesh processing
- **Vedo** 2021.0.7 - 3D visualization
- **PyVista** 0.32.1 - VTK interface
- **scikit-learn** 1.0.1 - Machine learning utilities
- **NumPy**, **Pandas**, **SciPy** - Numerical computing

---

## 🙏 Acknowledgements

Inspired by:
- **MeshSegNet**: https://github.com/Tai-Hsien/MeshSegNet
- **PointCloudLearningACD**: https://github.com/matheusgadelha/PointCloudLearningACD

---

## 📚 Citation

If you use this code, please cite:
```
Alsheghri et al., "Semi-supervised segmentation of tooth from 3D Scanned 
Dental Arches," SPIE Medical Imaging 2022
arXiv: https://arxiv.org/abs/2208.05539
```

---

## 🎓 Research Context

**Problem**: Manual tooth segmentation from 3D dental scans is time-consuming (45 min/scan) and requires expertise.

**Solution**: Semi-supervised deep learning that:
1. Learns from limited labeled data (supervised)
2. Leverages abundant unlabeled data (self-supervised)
3. Combines both via joint loss function

**Impact**: Makes automated tooth segmentation more practical for dental offices with limited annotated data.

---

## 🔍 Technical Highlights

1. **Mesh-based Segmentation**: Works directly on 3D triangle meshes (not voxels)
2. **Spatial Invariance**: STN modules handle varying orientations
3. **Local + Global Features**: Captures fine details and overall context
4. **Class Weighting**: Handles class imbalance in tooth distribution
5. **K-shot Learning**: Trains with limited examples per class (k=14)

---

*Note: This repository is under active development. Check the [GitHub repository](https://github.com/Alsheghri/Teeth-Segmentation) for updates.*