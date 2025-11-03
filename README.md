# AutoMapper - MapAGI Demo and Eval

Creating OSM-compatible mappings directly from multiple sequences of street-level imagery, particularly 360-degree images, would be a groundbreaking step in simplifying geospatial data generation and enhancing mapping accuracy. This project serves as a benchmark for evaluating the performance of large language models (LLMs) in mapping tasks, specifically designed to test their ability to generate structured mappings and automate workflows efficiently using this kind of visual input.

# Project Structure

## Data Handling and Creating Predictions

- **Photos**: This directory contains street-level imagery. Each image follows the naming convention `{sequence_id}_{sequence_index}.png`, where sequence_id is the unique identifier of a car trip and sequence_index is the numerical position of a photo in the given sequence. Together they form the unique identifier of a photo.

- **Metadata**: This directory includes metadata related to the photos, sequences of photos per way, and ground truth annotations at way level. We also provide different LLM predictions with the naming convention predictions_*.csv

- **Demo Utilities**: This directory contains a demo notebook showcasing a possible approach for creating predictions for sequences of street-level imagery.

## Evaluation

### **Evaluation Utilities**
Tools for evaluating predictions and generating metrics:

- **`eval.py`**  
  Provides a streamlined command-line evaluation method. It generates `.csv` and `.md` files in the `evaluation_results` directory containing feature-specific and general metrics.  

  **Usage**:  
  ```bash
  python eval.py path/to/predictions.csv [id_suffix]
  ```
  - **`path/to/predictions.csv`**: Path to the predictions file in `.csv` format.  
  - **`id_suffix` (optional)**: A custom identifier for the evaluation. If not provided, a default identifier will be used.

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
- We updated the repository with more data. `extra_photos.zip` from [here](https://grabautomapper.z23.web.core.windows.net/?prefix=automapper/)