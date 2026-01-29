# Project: Automated Dental Margin Line Detection (AI Lab Technician)

## 1. Executive Summary
**Role**: Senior Data Engineer / AI Researcher
**Objective**: Automate the detection of "margin lines" on dental tooth preparations.
**Impact**: Reduce the manual design time per case by ~15 minutes (from ~40m to ~25m), increasing lab productivity.

## 2. Domain Context: The Dental Workflow
1.  **Input**: Dentist sends a physical impression or intraoral scan of the patient's teeth.
2.  **Digitization**: Lab technician scans the model to create a 3D digital version (`Scanner Space`).
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

## 4. Coordinate Spaces (Context)

| Space | Description |
|-------|-------------|
| **Scanner Space** | Raw mesh coordinates from 3D scanner |
| **Design Space** | Local tooth coordinates where margin points are stored |

**Note**: The `ZRotationMatrix` in `constructionInfo` transforms between these spaces. This alignment is already implemented and verified (mean error: 0.02mm).