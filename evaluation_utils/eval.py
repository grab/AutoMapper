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

def _normalize_st_abbreviation(word, position, total_words):
    """
    Contextually normalize "St" abbreviation:
    - At the beginning of a name: "St" -> "saint" (e.g., "St James Place")
    - Otherwise: "St" -> "street" (e.g., "Main St")
    """
    if word == 'st' and position == 0:
        return 'saint'
    elif word == 'st':
        return 'street'
    return None


def preprocess(string):
    """
    Normalize street names for comparison by:
    - Converting to lowercase
    - Removing punctuation and question marks
    - Normalizing common street name abbreviations
    - Removing extra whitespace
    """
    if pd.isna(string) or string is None:
        return ''
    
    string = str(string)
    
    # Convert to lowercase
    string = string.lower()
    
    # Remove question marks and other uncertainty markers (common in OCR/predictions)
    string = string.replace('?', '').replace('¿', '')
    
    # Normalize common street name abbreviations
    # Dictionary mapping abbreviations to full words
    abbreviations = {
        'st': 'street',  # Default, but will be overridden by _normalize_st_abbreviation for contextual cases
        'st.': 'street',
        'str': 'street',
        'str.': 'street',
        'pl': 'place',
        'pl.': 'place',
        'ave': 'avenue',
        'ave.': 'avenue',
        'av': 'avenue',
        'av.': 'avenue',
        'rd': 'road',
        'rd.': 'road',
        'dr': 'drive',
        'dr.': 'drive',
        'ln': 'lane',
        'ln.': 'lane',
        'blvd': 'boulevard',
        'blvd.': 'boulevard',
        'ct': 'court',
        'ct.': 'court',
        'cir': 'circle',
        'cir.': 'circle',
        'pkwy': 'parkway',
        'pkwy.': 'parkway',
        'e': 'east',
        'e.': 'east',
        'w': 'west',
        'w.': 'west',
        'n': 'north',
        'n.': 'north',
        's': 'south',
        's.': 'south',
    }
    
    # Split into words and normalize
    words = string.split()
    normalized_words = []
    for i, word in enumerate(words):
        # Remove punctuation (periods, commas)
        word = word.strip().replace('.', '').replace(',', '')
        
        # Handle "St" contextually first (special case)
        st_normalized = _normalize_st_abbreviation(word, i, len(words))
        if st_normalized is not None:
            word = st_normalized
        elif word in abbreviations:
            word = abbreviations[word]
        
        normalized_words.append(word)
    
    # Join and remove extra whitespace
    result = ' '.join(normalized_words)
    # Remove any remaining extra spaces
    result = ' '.join(result.split())
    
    return result


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
    # Both exist - check if they match
    elif equals(gt_value, pred_value, map_feature):
        return 'tp'
    else:
        # Mismatch: both values exist but don't match
        # This will be counted as both FP (wrong positive prediction) and FN (missed correct answer)
        # in the evaluation logic below
        return 'fp'


def update_metrics(final_metrics, osm_tag, occurrences, tp, fp, fn, precision, recall, f1):
    final_metrics['osm_tag'].append(osm_tag)
    final_metrics['occurrences'].append(occurrences)
    final_metrics['tp'].append(tp)
    final_metrics['fp'].append(fp)
    final_metrics['fn'].append(fn)
    final_metrics['precision'].append(precision)
    final_metrics['recall'].append(recall)
    final_metrics['f1'].append(f1)
    return final_metrics


def eval_map_feature_pred(pred_df_path, uid=None, gt_df_path=None, test_mode=False):
    pred_df = pd.read_csv(pred_df_path, index_col=False)
    # Get the script directory and construct paths relative to it
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    if gt_df_path is None:
        gt_path = os.path.join(repo_root, 'metadata', 'ground_truth.csv')
    else:
        gt_path = gt_df_path
    gt_df = pd.read_csv(gt_path, index_col=False)
    final_metrics = {'osm_tag': [], 'occurrences': [], 'tp': [], 'fp': [], 'fn': [], 'precision': [], 'recall': [], 'f1': []}
    
    # Store detailed metrics for test assertions
    detailed_metrics = {}
    
    # Store detailed issues for each tag (for issues file generation)
    all_issues = []

    osm_tags = sorted(list(pred_df.columns))
    osm_tags = [tag for tag in osm_tags if tag != 'osmid']
    
    # Variables to store overall metrics
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    for osm_tag in osm_tags:

        assert osm_tag in OSM_TAGS.keys(), f"Invalid map feature: {osm_tag}"
        if osm_tag not in gt_df.columns:
            print(f"OSM tag '{osm_tag}' not found in ground truth dataframe.")
            final_metrics = update_metrics(final_metrics, osm_tag, 0, 0, 0, 0, None, None, None)
            continue

        map_feature_gt_df = gt_df[['osmid', osm_tag]]
        map_feature_pred_df = pred_df[['osmid', osm_tag]]
        # Use outer merge to capture FPs (osmid in pred but not in GT) and FNs (osmid in GT but not in pred)
        map_feature_gt_df = map_feature_gt_df.merge(map_feature_pred_df, on='osmid', how='outer', suffixes=('_gt', '_pred'))

        # Count occurrences (non-null values in ground truth) - use original GT df before merge
        occurrences = gt_df[osm_tag].notna().sum()

        map_feature_gt_df['pred_status'] = map_feature_gt_df.apply(lambda x: get_pred_status(
            x[osm_tag + '_gt'], x[osm_tag + '_pred'], osm_tag), axis=1)

        # For mismatches (both exist but don't match), we need to count as both FP and FN
        # Create separate columns for precision and recall counting
        map_feature_gt_df['is_fp'] = map_feature_gt_df['pred_status'].isin(['fp'])
        map_feature_gt_df['is_fn'] = map_feature_gt_df['pred_status'].isin(['fn'])
        # Mismatches (wrong predictions when GT exists) count as both FP and FN
        # A mismatch is when: pred_status is 'fp' AND both GT and pred have values (notna)
        # This means it's a wrong prediction (FP) that also missed the correct answer (FN)
        mismatch_mask = (map_feature_gt_df['pred_status'] == 'fp') & \
                        map_feature_gt_df[osm_tag + '_gt'].notna() & \
                        map_feature_gt_df[osm_tag + '_pred'].notna()
        map_feature_gt_df.loc[mismatch_mask, 'is_fp'] = True
        map_feature_gt_df.loc[mismatch_mask, 'is_fn'] = True

        tp_samples = map_feature_gt_df[map_feature_gt_df['pred_status'] == 'tp']
        fp_samples = map_feature_gt_df[map_feature_gt_df['is_fp'] == True]
        fn_samples = map_feature_gt_df[map_feature_gt_df['is_fn'] == True]

        tp_count = len(tp_samples)
        fp_count = len(fp_samples)
        fn_count = len(fn_samples)
        
        # Store issues for this tag
        # True Positives
        for _, row in tp_samples.iterrows():
            all_issues.append({
                'osmid': row['osmid'],
                'tag': osm_tag,
                'issue_type': 'TP',
                'ground_truth': row[osm_tag + '_gt'] if pd.notna(row[osm_tag + '_gt']) else '',
                'prediction': row[osm_tag + '_pred'] if pd.notna(row[osm_tag + '_pred']) else ''
            })
        
        # False Positives (including mismatches)
        for _, row in fp_samples.iterrows():
            is_mismatch = (pd.notna(row[osm_tag + '_gt']) and 
                          pd.notna(row[osm_tag + '_pred']) and 
                          row['pred_status'] == 'fp')
            issue_type = 'Mismatch' if is_mismatch else 'FP'
            all_issues.append({
                'osmid': row['osmid'],
                'tag': osm_tag,
                'issue_type': issue_type,
                'ground_truth': row[osm_tag + '_gt'] if pd.notna(row[osm_tag + '_gt']) else '(empty)',
                'prediction': row[osm_tag + '_pred'] if pd.notna(row[osm_tag + '_pred']) else '(empty)'
            })
        
        # False Negatives (including mismatches, as they count as both FP and FN)
        for _, row in fn_samples.iterrows():
            is_mismatch = (pd.notna(row[osm_tag + '_gt']) and 
                          pd.notna(row[osm_tag + '_pred']) and 
                          row['pred_status'] == 'fp')
            issue_type = 'Mismatch' if is_mismatch else 'FN'
            all_issues.append({
                'osmid': row['osmid'],
                'tag': osm_tag,
                'issue_type': issue_type,
                'ground_truth': row[osm_tag + '_gt'] if pd.notna(row[osm_tag + '_gt']) else '(empty)',
                'prediction': row[osm_tag + '_pred'] if pd.notna(row[osm_tag + '_pred']) else '(empty)'
            })

        # Update total counts for overall metrics
        total_tp += tp_count
        total_fp += fp_count
        total_fn += fn_count

        precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) > 0 else 0
        recall = tp_count / (tp_count + fn_count) if (tp_count + fn_count) > 0 else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Store detailed metrics for test assertions
        detailed_metrics[osm_tag] = {
            'tp': tp_count,
            'fp': fp_count,
            'fn': fn_count,
            'occurrences': occurrences,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        final_metrics = update_metrics(final_metrics, osm_tag, occurrences, tp_count, fp_count, fn_count, round(precision, 4), round(recall, 4), round(f1, 4))

    final_metrics_df = pd.DataFrame(final_metrics)
    
    # Compute overall precision, recall, and F1
    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    overall_f1 = (2 * overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0
    
    # Add separator row and overall metrics
    final_metrics_df.loc[-1] = ['-' for _ in range(len(final_metrics_df.columns))]
    final_metrics_df.index = final_metrics_df.index + 1  # Shift index to make space for the new row
    final_metrics_df.loc[-1] = ['overall', '-', total_tp, total_fp, total_fn,
                               round(overall_precision, 4), round(overall_recall, 4), round(overall_f1, 4)]

    pred_dir = os.path.join(repo_root, 'evaluation_results')
    os.makedirs(pred_dir, exist_ok=True)
    if uid is None:
        uid = datetime.now().strftime('%Y%m%d%H%M%S')
    
    pred_csv = os.path.join(pred_dir, f'metrics_{uid}.csv')
    pred_md = os.path.join(pred_dir, f'metrics_{uid}.md')

    final_metrics_df.to_markdown(pred_md, index=False)
    final_metrics_df.to_csv(pred_csv, index=False)

    # Generate detailed issues file in human-readable format
    if all_issues:
        issues_df = pd.DataFrame(all_issues)
        # Sort by tag, then by issue_type, then by osmid
        issues_df = issues_df.sort_values(['tag', 'issue_type', 'osmid'])
        
        # Generate CSV file
        issues_csv = os.path.join(pred_dir, f'issues_{uid}.csv')
        issues_df.to_csv(issues_csv, index=False)
        
        # Generate human-readable text file
        issues_txt = os.path.join(pred_dir, f'issues_{uid}.txt')
        with open(issues_txt, 'w') as f:
            # Group by tag
            for tag in sorted(issues_df['tag'].unique()):
                tag_issues = issues_df[issues_df['tag'] == tag]
                
                f.write(f"{tag.upper()}\n")
                f.write("=" * 80 + "\n\n")
                
                # True Positives
                tp_issues = tag_issues[tag_issues['issue_type'] == 'TP']
                if len(tp_issues) > 0:
                    f.write("True Positives:\n\n")
                    for _, row in tp_issues.iterrows():
                        gt_val = row['ground_truth'] if row['ground_truth'] != '' else 'None'
                        pred_val = row['prediction'] if row['prediction'] != '' else 'None'
                        f.write(f"  id: {row['osmid']}  gt: {gt_val}  pred: {pred_val}\n")
                    f.write("\n")
                
                # False Positives (excluding mismatches, as they'll be in Mismatched section)
                fp_issues = tag_issues[(tag_issues['issue_type'] == 'FP')]
                if len(fp_issues) > 0:
                    f.write("False Positives:\n\n")
                    for _, row in fp_issues.iterrows():
                        gt_val = row['ground_truth'] if row['ground_truth'] != '(empty)' else 'None'
                        pred_val = row['prediction'] if row['prediction'] != '(empty)' else 'None'
                        f.write(f"  id: {row['osmid']}  gt: {gt_val}  pred: {pred_val}\n")
                    f.write("\n")
                
                # False Negatives (excluding mismatches)
                fn_issues = tag_issues[(tag_issues['issue_type'] == 'FN')]
                if len(fn_issues) > 0:
                    f.write("False Negatives:\n\n")
                    for _, row in fn_issues.iterrows():
                        gt_val = row['ground_truth'] if row['ground_truth'] != '(empty)' else 'None'
                        pred_val = row['prediction'] if row['prediction'] != '(empty)' else 'None'
                        f.write(f"  id: {row['osmid']}  gt: {gt_val}  pred: {pred_val}\n")
                    f.write("\n")
                
                # Mismatches (only show once, not duplicated)
                mismatch_issues = tag_issues[tag_issues['issue_type'] == 'Mismatch']
                # Remove duplicates (mismatches appear twice - once as FP, once as FN)
                mismatch_issues = mismatch_issues.drop_duplicates(subset=['osmid', 'tag'])
                if len(mismatch_issues) > 0:
                    f.write("Mismatched:\n\n")
                    for _, row in mismatch_issues.iterrows():
                        gt_val = row['ground_truth'] if row['ground_truth'] != '(empty)' else 'None'
                        pred_val = row['prediction'] if row['prediction'] != '(empty)' else 'None'
                        f.write(f"  id: {row['osmid']}  gt: {gt_val}  pred: {pred_val}\n")
                    f.write("\n")
                
                f.write("\n")
        
        print(f"Detailed issues saved to {pred_dir}/issues_{uid}.txt (and {pred_dir}/issues_{uid}.csv)")
    
    print(f"Evaluation completed. Metrics saved to {pred_dir}/metrics_{uid}")
    
    # Run test assertions if in test mode
    if test_mode:
        from test_eval import run_test_assertions
        run_test_assertions(detailed_metrics, total_tp, total_fp, total_fn, overall_precision, overall_recall, overall_f1)
    
    return detailed_metrics, final_metrics_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate map feature predictions.")
    parser.add_argument("pred_df_path", type=str, help="Path to the predictions dataframe (csv file).")
    parser.add_argument("uid", type=str, help="uid for the evaluation run (optional).", default=None, nargs='?')
    parser.add_argument("--gt-path", type=str, help="Path to ground truth CSV (optional, defaults to metadata/ground_truth.csv).", default=None)
    parser.add_argument("--test", action="store_true", help="Enable test mode with assertions (for test cases).")
    args = parser.parse_args()

    eval_map_feature_pred(args.pred_df_path, args.uid, args.gt_path, test_mode=args.test)
    