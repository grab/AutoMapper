# AutoMapper - MapAGI Eval

Creating OSM-compatible mappings directly from multiple sequences of street-level imagery, particularly 360-degree images, would be a groundbreaking step in simplifying geospatial data generation and enhancing mapping accuracy. This project serves as a benchmark for evaluating the performance of large language models (LLMs) in mapping tasks, specifically designed to test their ability to generate structured mappings and automate workflows efficiently using this kind of visual input.

## Contents

- **Photos**: This directory contains street-level imagery. Each image follows the naming convention `{sequence_id}_{sequence_index}.png`.
- **Metadata**: This directory includes metadata related to the photos, sequences of photos per way, and ground truth annotations at way level. We also provide our own predictions at pipeline_predictions.csv .

## Scripts

- `eval.py`: Provides a streamlined command-line evaluation method.  
  Run it using the following command:  
  ```python
  python eval.py path/to/predictions.csv [id_suffix]
  ```
- path/to/predictions.csv: Path to the predictions file in .csv format.
- id_suffix (optional): A custom identifier for the evaluation. If not provided, a default identifier will be used.

- `interactive_eval.ipynb`: Contains interactive evaluation and visualization utilities at map feature level.

## General Workflow

1. Download photos.zip from https://drive.google.com/drive/folders/1MQsGlCBf5DRVa3P5piiopbtagYVr-W8A and extract the contents into the /photos directory.
2. Load image-level metadata by combining the photos directory with the photos.csv file.
3. Iterate through ways using the ways.csv file.
4. Generate predictions at way level.
5. Assess the accuracy of your predictions.

Further details can be accesed at https://docs.google.com/document/d/1kyimv5nURA_BSqFuXfjx9psXw1qD34D5JZmCcUQodEw/edit?usp=sharing

## Setup Instructions

  ```python
conda create -n "automapper"
conda activate automapper
pip install -r requirements.txt
  ```
## Contributions

Feel free to contribute by improving the benchmarks.
