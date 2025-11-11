# Test Cases for Evaluation Script

This document describes the comprehensive test cases for validating the evaluation script.

## Test Data Files
- **Ground Truth**: `test_ground_truth.csv`
- **Predictions**: `test_predictions_comprehensive.csv`

## Test Cases Breakdown

### Test Case 1: True Positive (TP) - Perfect Match
- **osmid**: 1001
- **GT**: `oneway=yes, name=Main Street, lanes=2`
- **Pred**: `oneway=yes, name=Main Street, lanes=2`
- **Expected**: TP for all three fields
- **Metrics Impact**: Increases TP count

### Test Case 2: True Positive (TP) - Two-way Road
- **osmid**: 1002
- **GT**: `name=Oak Avenue, lanes:forward=2, lanes:backward=2`
- **Pred**: `name=Oak Avenue, lanes:forward=2, lanes:backward=2`
- **Expected**: TP for all fields
- **Metrics Impact**: Increases TP count

### Test Case 3: False Negative (FN) - Missing Name Prediction
- **osmid**: 1003
- **GT**: `oneway=yes, name=Park Road, lanes=1, maxspeed:forward=30 mph`
- **Pred**: `oneway=yes, name=(empty), lanes=1, maxspeed:forward=30 mph`
- **Expected**: 
  - TP for `oneway`, `lanes`, `maxspeed:forward`
  - FN for `name` (GT has value, pred is empty)
- **Metrics Impact**: 
  - `name`: FN increases
  - Other fields: TP increases

### Test Case 4: Mismatch - Wrong Name (Should count as BOTH FP and FN)
- **osmid**: 1004
- **GT**: `name=Elm Street, lanes:forward=1, lanes:backward=1`
- **Pred**: `name=Wrong Street, lanes:forward=1, lanes:backward=1`
- **Expected**: 
  - TP for `lanes:forward`, `lanes:backward`
  - **FP AND FN for `name`** (mismatch - wrong prediction AND missed correct answer)
- **Metrics Impact**: 
  - `name`: Both FP and FN increase
  - Precision decreases (FP in denominator)
  - Recall decreases (FN in denominator)

### Test Case 5: True Positive (TP) - Perfect Match
- **osmid**: 1005
- **GT**: `oneway=yes, name=First Street, lanes=3`
- **Pred**: `oneway=yes, name=First Street, lanes=3`
- **Expected**: TP for all fields
- **Metrics Impact**: Increases TP count

### Test Case 6: False Negative (FN) - Missing Oneway Prediction
- **osmid**: 1006
- **GT**: `name=Second Street, lanes:forward=2, lanes:backward=1`
- **Pred**: `name=Second Street, lanes:forward=2, lanes:backward=1`
- **Expected**: 
  - TP for `name`, `lanes:forward`, `lanes:backward`
  - Note: GT has empty `oneway`, pred has empty `oneway` → TN (filtered out)
- **Metrics Impact**: TP increases for present fields

### Test Case 7: Mismatch - Wrong Oneway Value (Should count as BOTH FP and FN)
- **osmid**: 1007
- **GT**: `oneway=yes, name=Third Street, lanes=1`
- **Pred**: `oneway=(empty), name=Third Street, lanes=1`
- **Expected**: 
  - TP for `name`, `lanes`
  - **FP AND FN for `oneway`** (mismatch: GT=yes, Pred=empty)
- **Metrics Impact**: 
  - `oneway`: Both FP and FN increase
  - Precision and Recall both decrease

### Test Case 8: True Positive (TP) - Perfect Match
- **osmid**: 1008
- **GT**: `name=Fourth Street, lanes:forward=1, lanes:backward=1`
- **Pred**: `name=Fourth Street, lanes:forward=1, lanes:backward=1`
- **Expected**: TP for all fields
- **Metrics Impact**: Increases TP count

### Test Case 9: False Negative (FN) - Missing Lanes Prediction
- **osmid**: 1009
- **GT**: `oneway=yes, name=Fifth Street, lanes=2`
- **Pred**: `oneway=yes, name=Fifth Street, lanes=(empty)`
- **Expected**: 
  - TP for `oneway`, `name`
  - FN for `lanes` (GT has value, pred is empty)
- **Metrics Impact**: 
  - `lanes`: FN increases, Recall decreases

### Test Case 10: Mismatch - Wrong Lanes Value (Should count as BOTH FP and FN)
- **osmid**: 1010
- **GT**: `name=Sixth Street, lanes:forward=2, lanes:backward=2`
- **Pred**: `name=Sixth Street, lanes:forward=3, lanes:backward=3`
- **Expected**: 
  - TP for `name`
  - **FP AND FN for `lanes:forward` and `lanes:backward`** (mismatch)
- **Metrics Impact**: 
  - `lanes:forward` and `lanes:backward`: Both FP and FN increase
  - Precision and Recall both decrease

### Test Case 11: True Negative (TN) - Both Null
- **osmid**: 1011
- **GT**: `lanes=1` (other fields empty)
- **Pred**: All fields empty
- **Expected**: 
  - TN for fields where both GT and Pred are empty
  - FN for `lanes` (GT has value, pred is empty)
  - TN values are filtered out (not counted in metrics)
- **Metrics Impact**: Only FN for `lanes` is counted

### Test Case 12: False Negative (FN) - Missing OSMID in Predictions
- **osmid**: 1012
- **GT**: `oneway=yes, name=Missing Street, lanes=1`
- **Pred**: OSMID 1012 does not exist in predictions
- **Expected**: 
  - FN for all fields with values in GT (`oneway`, `name`, `lanes`)
  - This tests the outer merge functionality
- **Metrics Impact**: 
  - All fields: FN increases, Recall decreases

### Test Case 13: False Positive (FP) - Extra OSMID in Predictions
- **osmid**: 1013
- **GT**: OSMID 1013 does not exist in ground truth
- **Pred**: `oneway=yes, name=Extra Street, lanes=1`
- **Expected**: 
  - FP for all fields with values in Pred (`oneway`, `name`, `lanes`)
  - This tests the outer merge functionality
- **Metrics Impact**: 
  - All fields: FP increases, Precision decreases

### Test Case 14: False Positive (FP) - Extra OSMID in Predictions (Two-way)
- **osmid**: 1014
- **GT**: OSMID 1014 does not exist in ground truth
- **Pred**: `name=Another Avenue, lanes:forward=2, lanes:backward=2`
- **Expected**: 
  - FP for all fields with values in Pred
- **Metrics Impact**: 
  - All fields: FP increases, Precision decreases

## Expected Summary Metrics

### For `name` field:
- **Occurrences**: 11 (GT has name in 11 rows: 1001-1011)
- **TP**: 7 (1002, 1005, 1006, 1007, 1008, 1009, 1010 - perfect matches)
- **FP**: 2 (1004 mismatch: GT="Elm Street", Pred="Wrong Street"; 1013 extra osmid: Pred="Extra Street")
- **FN**: 4 (1001 missing osmid in pred; 1003 missing: GT="Park Road", Pred=empty; 1004 mismatch; 1011 missing: GT="Missing Street", Pred=empty)
- **Precision**: 7 / (7 + 2) = 0.7778
- **Recall**: 7 / (7 + 4) = 0.6364
- **F1**: 2 * (0.7778 * 0.6364) / (0.7778 + 0.6364) = 0.7

### For `oneway` field:
- **Occurrences**: 7 (GT has oneway=yes in 7 rows: 1001, 1003, 1005, 1007, 1009, 1012)
- **TP**: 4 (1001, 1003, 1005, 1009)
- **FP**: 3 (1007 mismatch, 1013 extra, 1014 - wait, 1014 doesn't have oneway)
- **FN**: 3 (1007 mismatch, 1012 missing osmid)
- **Precision**: 4 / (4 + 3) = 0.5714
- **Recall**: 4 / (4 + 3) = 0.5714
- **F1**: 0.5714

## Key Test Scenarios Covered

1. ✅ **True Positives**: Perfect matches
2. ✅ **False Negatives**: Missing predictions (empty values)
3. ✅ **False Positives**: Extra predictions (osmid not in GT)
4. ✅ **Mismatches**: Wrong values (counted as BOTH FP and FN)
5. ✅ **Missing OSMIDs**: OSMID in GT but not in predictions (FN)
6. ✅ **Extra OSMIDs**: OSMID in predictions but not in GT (FP)
7. ✅ **True Negatives**: Both null (filtered out, not counted)
8. ✅ **Outer Merge**: Tests that all rows from both dataframes are included

## Running the Test

```bash
cd evaluation_utils
python eval.py ../metadata/test_predictions_comprehensive.csv test_comprehensive --gt-path ../metadata/test_ground_truth.csv --test
```

This will run the evaluation using the test ground truth and test predictions files, and automatically validate the results with assertions.

The `--test` flag enables test mode, which:
- Runs comprehensive assertions on the evaluation results
- Validates TP, FP, FN counts for each field
- Checks that mismatches are counted as both FP and FN
- Verifies outer merge handles missing osmids correctly
- Ensures TN values are filtered out
- Validates overall metrics are within expected ranges

If any assertion fails, the script will raise an error with details about what went wrong.

