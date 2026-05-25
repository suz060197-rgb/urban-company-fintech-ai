# Churn And Adoption Model Evaluation

Evaluation uses the saved prediction CSV test split and final feature-importance artifacts.

## Churn Prediction

- ROC-AUC: `0.967`
- Precision: `1.000`
- Recall: `0.927`
- F1 score: `0.962`
- Confusion matrix: TP `1693`, FP `0`, TN `4173`, FN `134`
- ROC curve image: `output/model_evaluation/churn_prediction_roc_curve.png`
- Feature importance chart: `output/model_evaluation/churn_prediction_feature_importance.png`
- Evaluation source: `current final model artifact`

For an MSME/Razorpay-style embedded-finance use case, the churn model is suitable for retention operations: identify service providers likely to disengage, prioritize faster settlement support, repeat-customer enablement, payout reliability, and working-capital nudges. Strong recall means the model can catch most churn-risk providers, while high precision limits wasted interventions.

## Embedded Finance Adoption

- ROC-AUC: `0.963`
- Precision: `0.892`
- Recall: `0.840`
- F1 score: `0.866`
- Confusion matrix: TP `2299`, FP `277`, TN `2987`, FN `437`
- ROC curve image: `output/model_evaluation/embedded_finance_adoption_roc_curve.png`
- Feature importance chart: `output/model_evaluation/embedded_finance_adoption_feature_importance.png`
- Evaluation source: `current final model artifact`

For Razorpay embedded-finance adoption, the prediction output supports propensity-based targeting: identify providers likely to accept digital payouts, payment tools, or working-capital products. Use this for education, onboarding, and product-fit segmentation. Treat adoption propensity as commercial decision support rather than causal proof that finance products directly expand income.

## Consistency Note

The saved final metrics file may reflect the latest model artifact, while prediction CSVs reflect the last exported prediction run. If these differ, regenerate predictions before final submission.

model,accuracy,directional_accuracy,f1,fn,fp,mae,positive_rate,precision,r2,recall,rmse,roc_auc,threshold,tn,tp
churn_prediction,0.9776666666666668,,0.9619318181818182,134.0,0.0,,0.3045,1.0,,0.926655719759168,,0.96719088791277,0.7000000000000001,4173.0,1693.0
embedded_finance_adoption,0.881,,0.8655873493975903,437.0,277.0,,0.456,0.8924689440993789,,0.8402777777777778,,0.9633885923704276,0.5999999999999999,2987.0,2299.0
