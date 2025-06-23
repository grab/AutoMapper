import os
import pandas as pd
import argparse
from datetime import datetime

OSM_TAGS = {'name': True,  # street name
            'oneway': True,  # one way + dne
            'turn:lanes': True,  # arrow markings
            'turn:lanes:forward': True,  # arrow markings
            'turn:lanes:backward': True,  # arrow markings
            'lanes': True,  # lane count
            'lanes:forward': True,  # lane count
            'lanes:backward': True,  # lane count
            'maxspeed': True,  # speed limit
            'maxspeed:forward': True,  # speed limit
            'maxspeed:backward': True,  # speed limit
            }

def preprocess(string):
    string = string.lower()
    string = string.split(' ')
    string = [s.strip().replace('.', '').replace(',', '') for s in string]
    return ' '.join(string)


def equals(gt_value, pred_value, map_feature):
    if map_feature == 'name':
        return preprocess(gt_value) == preprocess(pred_value)
    else:
        return gt_value == pred_value


def get_pred_status(gt_value, pred_value, map_feature):
    if pd.isna(gt_value) and pd.isna(pred_value):
        return 'tn'
    elif not pd.isna(gt_value) and pd.isna(pred_value):
        return 'fn'
    elif pd.isna(gt_value) and not pd.isna(pred_value):
        return 'fp'
    # treat a mismatch as a fn
    elif equals(gt_value, pred_value, map_feature):
        return 'tp'
    else:
        return 'fn'


def update_metrics(final_metrics, osm_tag, precision, recall, f1):
    final_metrics['osm_tag'].append(osm_tag)
    final_metrics['precision'].append(precision)
    final_metrics['recall'].append(recall)
    final_metrics['f1'].append(f1)
    return final_metrics


def eval_map_feature_pred(pred_df_path, uid=None):
    pred_df = pd.read_csv(pred_df_path)
    gt_df = pd.read_csv('../metadata/ground_truth.csv')
    final_metrics = {'osm_tag': [], 'precision': [], 'recall': [], 'f1': []}

    osm_tags = sorted(list(pred_df.columns))
    osm_tags = [tag for tag in osm_tags if tag != 'osmid']
    for osm_tag in osm_tags:

        assert osm_tag in OSM_TAGS.keys(), f"Invalid map feature: {osm_tag}"
        if osm_tag not in gt_df.columns:
            print(f"OSM tag '{osm_tag}' not found in predictions dataframe.")
            final_metrics = update_metrics(final_metrics, osm_tag, None, None, None)
            continue

        map_feature_gt_df = gt_df[['osmid', osm_tag]]
        map_feature_pred_df = pred_df[['osmid', osm_tag]]
        map_feature_gt_df = map_feature_gt_df.merge(map_feature_pred_df, on='osmid', suffixes=('_gt', '_pred'))

        map_feature_gt_df['pred_status'] = map_feature_gt_df.apply(lambda x: get_pred_status(
            x[osm_tag + '_gt'], x[osm_tag + '_pred'], osm_tag), axis=1)

        map_feature_gt_df = map_feature_gt_df[map_feature_gt_df['pred_status'].isin(['tp', 'fp', 'fn'])]
        tp_samples = map_feature_gt_df[map_feature_gt_df['pred_status'] == 'tp']
        fp_samples = map_feature_gt_df[map_feature_gt_df['pred_status'] == 'fp']
        fn_samples = map_feature_gt_df[map_feature_gt_df['pred_status'] == 'fn']

        precision = len(tp_samples) / (len(tp_samples) + len(fp_samples)) if (len(tp_samples) + len(fp_samples)) > 0 else 0
        recall = len(tp_samples) / (len(tp_samples) + len(fn_samples)) if (len(tp_samples) + len(fn_samples)) > 0 else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        final_metrics = update_metrics(final_metrics, osm_tag, round(precision, 4), round(recall, 4), round(f1, 4))


    final_metrics_df = pd.DataFrame(final_metrics)
    mean_precision = final_metrics_df['precision'].mean()
    mean_recall = final_metrics_df['recall'].mean()
    mean_f1 = final_metrics_df['f1'].mean()
    
    final_metrics_df.loc[-1] = ['-' for _ in range(len(final_metrics_df.columns))]
    final_metrics_df.index = final_metrics_df.index + 1  # Shift index to make space for the new row
    final_metrics_df.loc[-1] = ['average_scores', round(mean_precision, 4), round(mean_recall, 4), round(mean_f1, 4)]

    pred_dir = '../predictions'
    os.makedirs(pred_dir, exist_ok=True)
    if uid is None:
        uid = datetime.now().strftime('%Y%m%d%H%M%S')
    
    pred_csv = os.path.join(pred_dir, f'{uid}_prediction_metrics.csv')
    pred_md = os.path.join(pred_dir, f'{uid}_prediction_metrics.md')

    final_metrics_df.to_markdown(pred_md, index=False)
    pd.DataFrame(final_metrics).to_csv(pred_csv, index=False)

    print(f"Evaluation completed. Metrics saved to {pred_dir}/{uid}_prediction_metrics")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate map feature predictions.")
    parser.add_argument("pred_df_path", type=str, help="Path to the predictions dataframe (csv file).")
    parser.add_argument("uid", type=str, help="uid for the evaluation run (optional).", default=None, nargs='?')
    args = parser.parse_args()

    eval_map_feature_pred(args.pred_df_path, args.uid)
