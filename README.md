# AutoMapper - MapAGI Demo and Eval

Creating OSM-compatible mappings directly from multiple sequences of street-level imagery, particularly 360-degree images, would be a groundbreaking step in simplifying geospatial data generation and enhancing mapping accuracy. This project serves as a benchmark for evaluating the performance of large language models (LLMs) in mapping tasks, specifically designed to test their ability to generate structured mappings and automate workflows efficiently using this kind of visual input.

# Project Structure

## Data Handling and Creating Predictions

- **Photos**: This directory contains street-level imagery. Each image follows the naming convention `{sequence_id}_{sequence_index}.png`, where sequence_id is the unique identifier of a car trip and sequence_index is the numerical position of a photo in the given sequence. Together they form the unique identifier of a photo.

- **Metadata**: This directory includes metadata related to the photos, sequences of photos per way, and ground truth annotations at way level. We also provide different LLM predictions with the naming convention predictions_*.csv

- **Demo Utilities**: This directory contains a demo notebook showcasing a possible approach for creating predictions for sequences of street-level imagery.

## Evaluation

### **Evaluation Rules**

The evaluation follows these rules for classifying predictions. **These rules apply consistently to all OSM tags** (name, oneway, lanes, maxspeed, turn:lanes, etc.):

1. **True Positive (TP)**: Both ground truth and prediction have the same non-null value
   - Example: GT="Main Street", Pred="Main Street" → TP
   - Example: GT="yes", Pred="yes" (for oneway) → TP

2. **False Positive (FP)**:
   - Prediction has a value but ground truth is null/empty
   - Example: GT=empty, Pred="Extra Street" → FP
   - **Mismatch**: Both have values but they don't match (also counts as FN)
   - Example: GT="Elm Street", Pred="Wrong Street" → FP (and FN)


3. **False Negative (FN)**:
   - Ground truth has a value but prediction is null/empty
   - Example: GT="Park Road", Pred=empty → FN
   - **Mismatch**: Both have values but they don't match (also counts as FP)
   - Example: GT="Elm Street", Pred="Wrong Street" → FN (and FP)
   - Missing OSMID: OSMID exists in ground truth but not in predictions → FN

4. **True Negative (TN)**: Both ground truth and prediction are null/empty
   - These are filtered out and not counted in metrics

5. **Outer Merge**: The evaluation uses an outer merge to ensure:
   - OSMIDs in ground truth but not in predictions are captured (FN)
   - OSMIDs in predictions but not in ground truth are captured (FP)

**Key Points:**
- **These rules apply to ALL OSM tags**: name, oneway, lanes, lanes:forward, lanes:backward, maxspeed, turn:lanes, etc.
- **Mismatches count as BOTH FP and FN**: A wrong prediction (e.g., GT="Elm Street", Pred="Wrong Street" or GT="yes", Pred=empty for oneway) is penalized in both precision (FP) and recall (FN)
- **Special handling for 'name' field**: Street names are compared with preprocessing (lowercase, remove punctuation) to handle variations like "Main St." vs "Main Street"
- **All other fields**: Direct value comparison (exact match required)
- **Precision** = TP / (TP + FP) - measures how many predictions are correct
- **Recall** = TP / (TP + FN) - measures how many ground truth values were found
- **F1** = 2 × (Precision × Recall) / (Precision + Recall)

### **Evaluation Utilities**
Tools for evaluating predictions and generating metrics:

- **`eval.py`**  
  Provides a streamlined command-line evaluation method. It generates `.csv` and `.md` files in the `evaluation_results` directory containing feature-specific and general metrics.  

  **Usage**:  
  ```bash
  python eval.py path/to/predictions.csv [id_suffix] [--gt-path path/to/ground_truth.csv] [--test]
  ```
  - **`path/to/predictions.csv`**: Path to the predictions file in `.csv` format.  
  - **`id_suffix` (optional)**: A custom identifier for the evaluation. If not provided, a default identifier will be used.
  - **`--gt-path` (optional)**: Path to ground truth CSV. Defaults to `metadata/ground_truth.csv`.
  - **`--test` (optional)**: Enable test mode with assertions for validation.

  **Output**: The script generates metrics files with the following columns:
  - `osm_tag`: The OSM tag/attribute name
  - `occurrences`: Number of non-null values in ground truth
  - `tp`: True Positives count
  - `fp`: False Positives count
  - `fn`: False Negatives count
  - `precision`: Precision score
  - `recall`: Recall score
  - `f1`: F1 score

- **`interactive_eval_notebook.ipynb`**  
  Contains interactive evaluation and visualization utilities at feature level.

### **Evaluation Results**
This directory contains metrics and reports generated after running the evaluation scripts.

# Project Setup
- Download `photos.zip` from [here](https://grabautomapper.z23.web.core.windows.net/?prefix=automapper/) and extract its contents to ./photos.
- Details about metadata files, feature specific map-making and other related information can be accesed in this [documentation](https://docs.google.com/document/d/1kyimv5nURA_BSqFuXfjx9psXw1qD34D5JZmCcUQodEw/edit?usp=sharing)

# Environment Setup

  ```python
conda create -n "automapper"
conda activate automapper
pip install -r requirements.txt
  ```
# Contributions
Feel free to contribute by improving the benchmarks.

# Updates
- We updated the repository with more data. Download `extra_photos.zip` from [here](https://grabautomapper.z23.web.core.windows.net/?prefix=automapper/)