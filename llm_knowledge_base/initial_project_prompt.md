# Project: Automated Dental Margin Line Detection (AI Lab Technician)

## 1. Executive Summary
**Role**: Senior Data Engineer / AI Researcher
**Objective**: Automate the detection of "margin lines" on dental tooth preparations.
**Impact**: Reduce the manual design time per case by ~15 minutes (from ~40m to ~25m), increasing lab productivity.

## 2. Domain Context: The Dental Workflow
1.  **Input**: Dentist sends a physical impression or intraoral scan of the patient's teeth.
2.  **Digitization**: Lab technician scans the model (if physical) to create a 3D digital version (`Scanner Space`).
3.  **The Bottleneck (Task to Automate)**:
    - Designer opens the scan in CAD software (Exocad).
    - **Action**: Manually identifying and drawing the **Margin Line** (the precise edge between the prepared tooth and the gum).
    - *Context*: This line dictates where the future crown ends. Accuracy is critical for fit and hygiene.
4.  **Design**: A digital tooth from a library is placed and adapted.
5.  **Manufacturing**: The design is sent to a milling machine.

## 3. The Data Structure
The dataset consists of Exocad project folders. Each case contains inputs (geometry) and ground truth (human-designed metadata).

### Key Files
| File Type | Example Name | Function | Space |
| :--- | :--- | :--- | :--- |
| **Input Mesh** | `*-UpperJaw.stl` | Raw 3D scan of the prep. | **Scanner Space** |
| **Context Mesh**| `*-LowerJaw.stl` | Opposing jaw (antagonist). | **Scanner Space** |
| **Labels (GT)** | `*.constructionInfo` | XML file containing the `Margin` line coordinates. | **Design Space** |
| **Alignment** | `*.constructionInfo` | XML containing `ZRotationMatrix`. | *Bridge* |
| **Metadata** | `*.dentalProject` | Links files and contains project info. | N/A |

## 4. Technical Challenges & Solutions

### The Alignment Problem
*   **Issue**: The Input Mesh (`UpperJaw.stl`) is in **Scanner Space**, but the Label (`Margin` points) is saved in **Design Space** (local to the tooth). They do not overlap in 3D space by default.
*   **The Trap**: The `ZRotationMatrix` provided in the XML is stored using a **Row-Vector Convention** (Translation is in the bottom row), whereas standard Python libraries (numpy/trimesh) expect a Column-Vector convention.
*   **The Solution**:
    1.  Load the `ZRotationMatrix` from `<constructionInfo>`.
    2.  **Transpose** the matrix ($M^T$).
    3.  Apply $M^T$ to the `UpperJaw.stl` mesh vertices.
    4.  Result: The mesh is now perfectly aligned with the margin line points.

## 5. Current Project State
*   **Phase**: Data Engineering & Preparation.
*   **Status**:
    *   Data structure understood.
    *   Alignment transformation mathematically solved and verified (0.0195mm mean error).
    *   Next steps: implementing the training pipeline.

## 6. Instructions for Future AI Agents
If you are reading this to assist on the project:
1.  **Do not reinvent the alignment logic.** Use the transpose method described above.
2.  **Data Path**: Look in `data/` for patient case subfolders.
3.  **Target**: We are training a model (likely PointNet, DGCNN, or 3D UNet) to predict the specialized curve (margin) on the mesh surface.