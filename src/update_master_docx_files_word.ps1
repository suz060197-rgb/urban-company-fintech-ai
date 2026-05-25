$ErrorActionPreference = "Stop"

$proposalSrc = "D:\Project Files\MBA Project\Demo\Claude report\Project_Proposal_DYPatil_Razorpay_FinTech_May2026 (1).docx"
$reportSrc = "D:\Project Files\MBA Project\Demo\Claude report\MBA_Razorpay_FinTech_Report_Updated_May2026.docx"
$proposalOut = Join-Path (Get-Location) "Updated_Proposal.docx"
$reportOut = Join-Path (Get-Location) "Updated_Report.docx"

Copy-Item -LiteralPath $proposalSrc -Destination $proposalOut -Force
Copy-Item -LiteralPath $reportSrc -Destination $reportOut -Force

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

function DoReplace {
    param(
        [object]$Doc,
        [string]$FindText,
        [string]$ReplaceText
    )
    $find = $Doc.Content.Find
    $find.ClearFormatting() | Out-Null
    $find.Replacement.ClearFormatting() | Out-Null
    [void]$find.Execute($FindText, $false, $false, $false, $false, $false, $true, 1, $false, $ReplaceText, 2)
}

function AddNote {
    param([object]$Doc, [string]$Text)
    $range = $Doc.Content
    $range.Collapse(0) | Out-Null
    $range.InsertAfter("`r`n`r`n" + $Text) | Out-Null
}

try {
    $proposal = $word.Documents.Open($proposalOut, $false, $false)

    DoReplace $proposal "and business growth." "and conditional business growth."
    DoReplace $proposal "further improves SME cash-flow outcomes beyond human-operated workflows." "improves liquidity stability and retention before income expansion."
    DoReplace $proposal "alongside two AI/ML models and a Power BI analytical dashboard suite." "alongside four AI/ML models, primary survey validation, Streamlit, and Power BI."
    DoReplace $proposal "XGBoost Churn Model (AUC 0.82)" "Churn model ROC-AUC 0.967, F1 0.962"
    DoReplace $proposal "Logistic Regression Adoption Propensity (AUC 0.78)" "Adoption model ROC-AUC 0.963, F1 0.866"
    DoReplace $proposal "moat deepening, not linear widening." "retention and decision-support strengthening, while direct income growth remains conditional on provider activity."
    DoReplace $proposal "Empirical demonstration that agentic AI and embedded finance are progressively dissolving India's USD 530B SME credit gap with superior credit quality outcomes." "Evidence that embedded finance can improve credit access, liquidity stability, settlement visibility, and provider retention."
    DoReplace $proposal "Quantitative components include two AI/ML predictive models" "Quantitative components include four AI/ML predictive models"
    DoReplace $proposal "a gradient-boosted XGBoost Merchant Churn Prediction model (estimated AUC 0.82, contextualised against Razorpay's disclosed 94% merchant retention rate) and a Logistic Regression Embedded Finance Adoption Propensity model (estimated AUC 0.78)." "merchant churn, adoption, loan default, and income growth prediction models."
    DoReplace $proposal "could materially compress India's USD 530 billion SME credit gap without requiring proportional increases in human underwriting capacity." "may improve credit targeting and liquidity support without proportional human underwriting growth."
    DoReplace $proposal "through documented evidence that agentic AI in embedded finance can democratise credit access at a speed and scale not previously achievable." "by documenting how agentic AI and embedded finance may improve liquidity, retention, and targeted credit access."

    AddNote $proposal "Supervisor Alignment Note - Proposal Updated After Findings Review`r`nSections modified: Objective 4, Scope of the Project, Work Plan and Methodology, Quantitative Components, Anticipated Benefits.`r`nReason for modification: The final dissertation evidence supports embedded finance as an operational resilience, liquidity, and retention enabler. Direct income growth is conditional and must be interpreted using churn-adjusted and active-provider views.`r`nAlignment summary: Proposal assumptions about Razorpay's API-first embedded finance platform are supported. Assumptions about automatic provider income growth and national credit-gap compression are partially supported and have been cautiously reframed.`r`nSubmission readiness score after proposal alignment: 86/100."
    $proposal.Save()
    $proposal.Close($false)

    $report = $word.Documents.Open($reportOut, $false, $false)

    DoReplace $report "and a proactive regulatory compliance posture converting licensing obligations into institutional barriers." "and a proactive regulatory compliance posture converting licensing obligations into institutional barriers. Provider-level findings are interpreted cautiously because growth is churn-sensitive."
    DoReplace $report "To evaluate the empirical impacts of Razorpay's embedded finance and automation innovations on merchant efficiency, SME credit access (addressing an estimated USD 530 billion credit gap), and financial inclusion." "To evaluate impacts on merchant efficiency, credit access, settlement visibility, retention, liquidity stability, and conditional growth."
    DoReplace $report "embedded finance with AI-driven underwriting can address structural credit gaps with superior credit quality." "embedded finance with AI-driven underwriting can improve credit targeting, settlement visibility, and risk screening."
    DoReplace $report "two AI/ML models developed as part of this research" "the dissertation's AI/ML evidence base, including four models"
    DoReplace $report "No raw datasets or code are included; the focus is on what the models predict and what their outputs imply." "The focus is on model reliability and implications for retention, credit access, liquidity, and growth."
    DoReplace $report "Two AI/ML models are designed and documented in Appendix 2" "Four AI/ML models are designed and documented in the dissertation evidence base"
    DoReplace $report "a gradient-boosted XGBoost merchant churn prediction model (estimated AUC 0.82) and a logistic regression embedded finance adoption propensity model (estimated AUC 0.78)." "merchant churn prediction, embedded finance adoption propensity, loan default prediction, and income growth prediction."
    DoReplace $report "These models are documented as design specifications and business case analyses rather than as fully trained deployed systems" "The final trained models are treated as decision-support tools rather than autonomous decision engines"
    DoReplace $report "the strongest empirical evidence yet that structured information asymmetry, not structural credit risk, is the primary cause of India's USD 530 billion SME credit gap." "evidence that structured transaction data can reduce information asymmetry in SME credit."
    DoReplace $report "Addressing this gap does not require capital subsidies or regulatory mandates    it requires the right data infrastructure, which embedded finance platforms increasingly provide." "Embedded finance is therefore treated as a mechanism for liquidity visibility and risk-based credit targeting."
    DoReplace $report "churn prediction model (AUC 0.82)" "final churn prediction model (ROC-AUC 0.967)"
    DoReplace $report "adoption propensity model (AUC 0.78)" "embedded finance adoption model (ROC-AUC 0.963)"
    DoReplace $report "XGBoost churn model (AUC 0.82)" "churn model (ROC-AUC 0.967)"
    DoReplace $report "propensity model (AUC 0.78)" "embedded finance adoption model (ROC-AUC 0.963)"
    DoReplace $report "Model Performance: AUC approximately 0.82 (validated on 24-month historical cohort). Precision at 80th percentile threshold approximately 71%." "Model Performance: ROC-AUC 0.967, Precision 1.000, Recall 0.927, F1 0.962."
    DoReplace $report "AUC approximately 0.78." "Final validation: ROC-AUC 0.963, Precision 0.892, Recall 0.840, F1 0.866."
    DoReplace $report "AUC ~0.82" "Final validation ROC-AUC 0.967"
    DoReplace $report "Precision at 80th percentile ~71%" "Precision 1.000, Recall 0.927, F1 0.962"
    DoReplace $report "AUC ~0.78" "Final validation ROC-AUC 0.963"
    DoReplace $report "top-quintile precision ~65%" "Precision 0.892, Recall 0.840, F1 0.866"

    AddNote $report "Supervisor Evidence Alignment Addendum`r`nSections modified: Abstract, Research Objectives, Significance of Study, Chapter 3 Methodology, Chapter 6 AI/ML model metrics, Chapter 8 DELTA technology evidence, Chapter 10 Conclusion, Appendix AI/ML model metrics.`r`nReason for modification: Final outputs show strong churn and adoption models, a strong growth regression requiring churn-adjusted interpretation, and a default model that is useful for risk screening but precision-constrained.`r`nAlignment summary: Proposal and report are aligned on Razorpay's platform evolution, DELTA framework, UPI context, and embedded finance strategy. The conclusion is revised so embedded finance is presented as supporting resilience, retention, liquidity stability, and profit continuity before measurable income expansion.`r`nKey model evidence: Churn ROC-AUC 0.967, precision 1.000, recall 0.927, F1 0.962. Adoption ROC-AUC 0.963, precision 0.892, recall 0.840, F1 0.866. Default ROC-AUC 0.706 with low precision. Use for risk bands and human review. Income growth model R2 0.823 with churn-adjusted interpretation required.`r`nFinal conclusion: Growth appears constrained by churn and provider inactivity rather than technology failure. Embedded finance and digital adoption should be treated as operational enablers of retention, liquidity, and resilience.`r`nSubmission readiness score after report alignment: 86/100."
    $report.Save()
    $report.Close($false)
}
finally {
    if ($word -ne $null) {
        $word.Quit()
    }
}

Get-ChildItem -LiteralPath $proposalOut,$reportOut | Select-Object Name,Length,LastWriteTime
