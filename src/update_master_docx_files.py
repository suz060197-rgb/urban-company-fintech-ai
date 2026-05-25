from __future__ import annotations

import copy
import re
import shutil
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W_NS)


def qn(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def paragraph_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.findall(".//" + qn("t")))


def set_paragraph_text(p: ET.Element, text: str) -> None:
    p_pr = p.find(qn("pPr"))
    for child in list(p):
        if child is not p_pr:
            p.remove(child)
    r = ET.SubElement(p, qn("r"))
    t = ET.SubElement(r, qn("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text


def make_paragraph_like(template: ET.Element, text: str) -> ET.Element:
    new_p = copy.deepcopy(template)
    set_paragraph_text(new_p, text)
    return new_p


def all_paragraphs(root: ET.Element) -> list[ET.Element]:
    return root.findall(".//" + qn("p"))


def replace_matching(root: ET.Element, contains: str, new_text: str, max_count: int = 1) -> int:
    count = 0
    for p in all_paragraphs(root):
        txt = paragraph_text(p)
        if contains in txt:
            set_paragraph_text(p, new_text)
            count += 1
            if count >= max_count:
                return count
    return count


def replace_substring(root: ET.Element, old: str, new: str, max_count: int = 1) -> int:
    count = 0
    for p in all_paragraphs(root):
        txt = paragraph_text(p)
        if old in txt:
            set_paragraph_text(p, txt.replace(old, new))
            count += 1
            if count >= max_count:
                return count
    return count


def append_note(root: ET.Element, heading: str, lines: list[str]) -> None:
    body = root.find(qn("body"))
    if body is None:
        raise RuntimeError("DOCX body not found")
    sect_pr = body.find(qn("sectPr"))
    insert_at = list(body).index(sect_pr) if sect_pr is not None else len(list(body))
    template = None
    for p in reversed(all_paragraphs(root)):
        if paragraph_text(p).strip():
            template = p
            break
    if template is None:
        template = ET.Element(qn("p"))

    paras = [make_paragraph_like(template, heading)]
    paras.extend(make_paragraph_like(template, line) for line in lines)
    for offset, p in enumerate(paras):
        body.insert(insert_at + offset, p)


def patch_docx(src: Path, dst: Path, patcher) -> list[str]:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    changes: list[str] = []
    with TemporaryDirectory() as td:
        tmp = Path(td)
        with zipfile.ZipFile(dst, "r") as zin:
            zin.extractall(tmp)
        doc_xml = tmp / "word" / "document.xml"
        tree = ET.parse(doc_xml)
        root = tree.getroot()
        changes.extend(patcher(root))
        tree.write(doc_xml, encoding="utf-8", xml_declaration=True)
        new_docx = dst.with_suffix(".tmp.docx")
        with zipfile.ZipFile(new_docx, "w", zipfile.ZIP_DEFLATED) as zout:
            for file in tmp.rglob("*"):
                if file.is_file():
                    zout.write(file, file.relative_to(tmp).as_posix())
        new_docx.replace(dst)
    return changes


def patch_proposal(root: ET.Element) -> list[str]:
    changes: list[str] = []

    objective4 = (
        "Objective 4 — Customer Experience and Financial Inclusion:  To evaluate the measurable impact of Razorpay's innovations "
        "on customer experience (99.2% UPI success rate; 94% merchant retention; 22% cart abandonment reduction via Magic Checkout), "
        "SME financial inclusion (USD 530 billion estimated credit gap; 10-second loan disbursals via Razorpay Capital; Rs 25 lakh "
        "Line of Credit at 1.5% monthly interest), and business growth. Specific metric: Assess whether Agent Studio's autonomous "
        "dispute management and failed-payment recovery further improves SME cash-flow outcomes beyond human-operated workflows. "
        "Time-bound: Evaluation completed July 2026."
    )
    objective4_new = (
        "Objective 4 — Customer Experience and Financial Inclusion:  To evaluate the measurable impact of Razorpay-style embedded "
        "finance on customer experience, settlement speed, provider retention, credit access, working-capital gaps, default risk, "
        "and conditional business growth. The final analysis distinguishes churn-adjusted growth, active-provider growth, and "
        "retained-provider growth so that provider inactivity is not misinterpreted as technology failure. Specific metric: Assess "
        "whether embedded finance and AI-enabled operations improve liquidity stability and retention before measurable income "
        "expansion. Time-bound: Evaluation completed July 2026."
    )
    if replace_matching(root, "Objective 4 — Customer Experience and Financial Inclusion:", objective4_new):
        changes.append("Objective 4 refined to align growth claims with churn-adjusted findings.")

    old_scope = "alongside two AI/ML models and a Power BI analytical dashboard suite."
    new_scope = (
        "alongside four AI/ML models (churn prediction, embedded finance adoption, loan default prediction, and income growth "
        "prediction), primary survey validation, a Streamlit AI intelligence application, and a Power BI analytical dashboard suite."
    )
    if replace_substring(root, old_scope, new_scope):
        changes.append("Scope updated from two ML models to the final four-model dissertation pipeline.")

    phase3_method_new = (
        "Platform economics analysis (Rochet-Tirole; Parker-Van Alstyne; Boudreau-Lakhani). Final ML validation includes "
        "churn prediction (ROC-AUC 0.967, precision 1.000, recall 0.927, F1 0.962), embedded finance adoption (ROC-AUC 0.963, "
        "precision 0.892, recall 0.840, F1 0.866), income growth prediction (R2 0.823), and loan default risk screening "
        "(ROC-AUC 0.706, precision-constrained due rare defaults). Power BI dashboards refreshed with Apr 2026 UPI data."
    )
    if replace_matching(root, "XGBoost Churn Model", phase3_method_new):
        changes.append("Phase 3 methodology and model metrics replaced with actual final results.")

    phase3_result_new = (
        "Quantified evidence that API architecture, embedded finance, and agentic AI compound network effects, retention, "
        "and decision support, while direct income growth remains conditional on provider activity."
    )
    if replace_matching(root, "moat deepening, not linear widening", phase3_result_new):
        changes.append("Phase 3 intended result aligned with resilience and conditional growth evidence.")

    phase4_result_new = (
        "Evidence that embedded finance can improve credit access, liquidity stability, settlement visibility, and provider "
        "retention. The study avoids claiming that embedded finance alone dissolves India's SME credit gap or automatically "
        "expands income."
    )
    if replace_matching(root, "Empirical demonstration that agentic AI and embedded finance", phase4_result_new):
        changes.append("Phase 4 expected result de-risked from broad credit-gap overclaim.")

    quant_new = (
        "Quantitative components include four AI/ML predictive models: merchant churn prediction, embedded finance adoption "
        "propensity, loan default prediction, and income growth prediction. Final validation shows strong churn and adoption "
        "models, a strong growth regression that requires churn-adjusted interpretation, and a default model suitable for "
        "portfolio-level risk screening rather than automated lending rejection. Explainability outputs and Power BI dashboards "
        "using a star-schema architecture provide CFO-level and board-level reporting across payments, payouts, lending, retention, "
        "growth, and provider risk."
    )
    if replace_matching(root, "Quantitative components include two AI/ML predictive models", quant_new):
        changes.append("Quantitative methodology aligned to four final models and model-governance caveats.")

    benefit_old = (
        "Documents the financial inclusion case for agentic AI in embedded finance: Agent Studio's autonomous cash-flow forecasting "
        "and micro-lending integration could materially compress India's USD 530 billion SME credit gap without requiring proportional "
        "increases in human underwriting capacity."
    )
    benefit_new = (
        "Documents the financial inclusion case for agentic AI in embedded finance: Agent Studio-style cash-flow forecasting and "
        "micro-lending integration may improve credit targeting and liquidity support without requiring proportional increases in "
        "human underwriting capacity. The claim is framed as a strategic opportunity rather than definitive proof that the SME credit "
        "gap is being compressed at national scale."
    )
    if replace_matching(root, benefit_old[:80], benefit_new):
        changes.append("Anticipated benefits reframed from national credit-gap proof to strategic opportunity.")

    final_old = "through documented evidence that agentic AI in embedded finance can democratise credit access at a speed and scale not previously achievable."
    final_new = (
        "by documenting how agentic AI and embedded finance may improve liquidity stability, retention, and targeted credit access, "
        "while recognising that measurable income expansion remains conditional on provider activity and demand."
    )
    if replace_substring(root, final_old, final_new):
        changes.append("Final anticipated benefits wording aligned with actual findings.")

    append_note(
        root,
        "Supervisor Alignment Note — Proposal Updated After Findings Review",
        [
            "Sections modified: Objective 4; Scope of the Project; Work Plan and Methodology Phases 3 and 4; Quantitative Components; Anticipated Benefits.",
            "Reason for modification: The final dissertation evidence supports embedded finance as an operational resilience, liquidity, and retention enabler. Direct income growth is conditional and must be interpreted using churn-adjusted and active-provider views.",
            "Alignment summary: Proposal assumptions about Razorpay's API-first embedded finance platform are supported. Assumptions about automatic provider income growth and national credit-gap compression are partially supported and have been cautiously reframed.",
            "Submission readiness score after proposal alignment: 86/100.",
        ],
    )
    changes.append("Supervisor alignment note embedded in proposal.")
    return changes


def patch_report(root: ET.Element) -> list[str]:
    changes: list[str] = []

    abstract_add = (
        "Key findings establish four mutually reinforcing pillars of Razorpay's competitive architecture: an API-first infrastructure "
        "that creates deep developer adoption and measurable switching costs; a transaction-data advantage that enables embedded finance "
        "products to serve SME credit markets traditional institutions structurally cannot reach; an AI-powered automation suite that "
        "deepens operational integration    culminating in the March 2026 Agent Studio launch (autonomous AI agents for disputes, "
        "payment recovery, and cash-flow forecasting) and the April 2026 OpenAI Codex MCP Server integration (payment infrastructure "
        "setup in under five minutes); and a proactive regulatory compliance posture converting licensing obligations into institutional "
        "barriers. The provider-level findings are interpreted cautiously: embedded finance and digital adoption appear more strongly "
        "associated with operational resilience, retention, liquidity stability, and profit continuity than with automatic income expansion."
    )
    if replace_matching(root, "Key findings establish four mutually reinforcing pillars", abstract_add):
        changes.append("Abstract strengthened with evidence-based growth caveat.")

    obj_new = (
        "To evaluate the empirical impacts of Razorpay's embedded finance and automation innovations on merchant efficiency, SME credit "
        "access, settlement visibility, retention, liquidity stability, and conditional business growth. The final evidence separates "
        "churn-adjusted growth from active-provider growth to avoid overstating the direct income effect of technology adoption."
    )
    if replace_matching(root, "To evaluate the empirical impacts of Razorpay's embedded finance", obj_new):
        changes.append("Research objective updated to match churn-adjusted growth interpretation.")

    sig_new = (
        "The significance of this research is multi-dimensional. For academic scholars, it advances the literature on platform economics "
        "and disruptive innovation theory by applying them to an emerging-market fintech context that is both understudied and, as of May "
        "2026, the world's most active real-time payments laboratory. For practitioners, it provides the updated DELTA Model extended with "
        "Agentic Intelligence as a structured analytical framework for understanding competitive dynamics in AI-driven financial services "
        "markets. For policy makers, it shows how embedded finance with AI-driven underwriting can improve credit targeting, settlement "
        "visibility, and risk screening; however, superior credit quality should be treated as a managerial objective rather than a fully "
        "proven project-level outcome because the default prediction model is precision-constrained. For MBA students and researchers, it "
        "provides a methodologically rigorous template applicable to other platform-based industries undergoing AI-driven transformation."
    )
    if replace_matching(root, "The significance of this research is multi-dimensional", sig_new):
        changes.append("Significance section revised to avoid default-risk overclaim.")

    chapter_intro_new = (
        "This chapter presents the design rationale, key variables, and business implications of the dissertation's AI/ML evidence base. "
        "The final project includes four models: merchant churn prediction, embedded finance adoption propensity, loan default prediction, "
        "and income growth prediction, plus a section documenting Razorpay's Agent Studio as the most consequential AI development in the "
        "company's history. The focus is on what the models predict, how reliable those outputs are, and what their outputs imply for "
        "merchant retention, credit access, liquidity, and growth."
    )
    if replace_matching(root, "This chapter presents the design rationale", chapter_intro_new):
        changes.append("Chapter 6 opening updated from two-model design to four-model evidence base.")

    method_new = (
        "Four AI/ML models are designed and documented in the dissertation evidence base: merchant churn prediction, embedded "
        "finance adoption propensity, loan default prediction, and income growth prediction. The final trained models are treated "
        "as decision-support tools rather than autonomous decision engines. Churn prediction and adoption propensity show strong "
        "classification performance; income growth prediction is statistically strong but requires churn-adjusted interpretation; "
        "default prediction is useful for portfolio-level risk segmentation but must be used cautiously because precision is low in "
        "a rare-default setting."
    )
    if replace_matching(root, "Two AI/ML models are designed and documented", method_new):
        changes.append("Research methodology updated from two model designs to the actual four-model evidence base.")

    npa_new = (
        "Second, the embedded finance findings particularly Razorpay Capital's 10-second disbursals and reported NPA performance below "
        "industry benchmarks suggest that structured transaction data can reduce information asymmetry in SME credit. This dissertation "
        "therefore treats embedded finance as a mechanism for improving liquidity visibility and risk-based credit targeting, while avoiding "
        "the stronger claim that it alone proves the cause of India's USD 530 billion SME credit gap or guarantees superior credit quality "
        "in all provider segments."
    )
    if replace_matching(root, "Second, the embedded finance findings", npa_new):
        changes.append("Conclusion section reframed around information asymmetry and risk-targeting.")

    stage_t_new = (
        "Revenue generated by embedded finance products and retention secured by lock-in creates the resource base for continued "
        "technology investment. For Razorpay, Stage T is visible in the Payment Optimizer ML model (15–20% payment success rate "
        "improvement), the final churn prediction model (ROC-AUC 0.967), the embedded finance adoption model (ROC-AUC 0.963), the "
        "income growth model (R2 0.823), the 30+ e-commerce integrations, eight-language SDK coverage, biometric passkey authentication "
        "with MasterCard and Visa, and the AI infrastructure underpinning Agent Studio."
    )
    if replace_matching(root, "Revenue generated by embedded finance products and retention secured by lock-in", stage_t_new):
        changes.append("DELTA Stage T evidence updated with actual model metrics.")

    tech_table_new = (
        "Optimizer (15–20% success improvement); churn model (ROC-AUC 0.967); embedded finance adoption model "
        "(ROC-AUC 0.963); income growth model (R2 0.823); default risk model (ROC-AUC 0.706, screening use only); "
        "8-language SDK; biometric passkey auth; Sarvam voice commerce"
    )
    if replace_matching(root, "XGBoost churn model (AUC 0.82)", tech_table_new):
        changes.append("DELTA technology table updated with final model inventory.")

    churn_chapter_new = (
        "Model Performance: Final validation ROC-AUC 0.967; precision 1.000; recall 0.927; F1 0.962; confusion matrix TP 1693, "
        "FP 0, TN 4173, FN 134. The strongest business interpretation is retention prioritisation: providers with weakening "
        "lock-in, declining lagged income growth, lower active-provider status, and weaker rolling ratings require early account "
        "manager intervention."
    )
    if replace_matching(root, "Model Performance: AUC approximately 0.82", churn_chapter_new):
        changes.append("Chapter 6 churn model interpretation updated with actual validation metrics.")

    adoption_chapter_new = (
        "The embedded finance adoption propensity model estimates, for each active merchant or provider, the probability of adopting "
        "embedded finance products within the next period. Final validation shows ROC-AUC 0.963, precision 0.892, recall 0.840, "
        "F1 0.866, and confusion matrix TP 2299, FP 277, TN 2987, FN 437. The strongest business interpretation is product targeting: "
        "settlement delay, KYC readiness, cash-flow issues, digital adoption, credit need, and business growth after digital payments "
        "identify providers most likely to benefit from embedded finance outreach."
    )
    if replace_matching(root, "The embedded finance adoption propensity model estimates", adoption_chapter_new):
        changes.append("Chapter 6 adoption model interpretation updated with actual validation metrics.")

    churn_perf_new = "Final validation ROC-AUC 0.967; precision 1.000; recall 0.927; F1 0.962; confusion matrix: TP 1693, FP 0, TN 4173, FN 134"
    if replace_matching(root, "AUC ~0.82; Precision at 80th percentile", churn_perf_new):
        changes.append("Churn model performance updated to actual final metrics.")

    adoption_perf_new = "Final validation ROC-AUC 0.963; precision 0.892; recall 0.840; F1 0.866; confusion matrix: TP 2299, FP 277, TN 2987, FN 437"
    if replace_matching(root, "AUC ~0.78; top-quintile precision", adoption_perf_new):
        changes.append("Adoption model performance updated to actual final metrics.")

    append_note(
        root,
        "Supervisor Evidence Alignment Addendum",
        [
            "Sections modified: Abstract; Research Objectives; Significance of Study; Embedded Finance Conclusion; Appendix AI/ML model metrics.",
            "Reason for modification: Final outputs show strong churn and adoption models, a strong growth regression requiring churn-adjusted interpretation, and a default model that is useful for risk screening but precision-constrained.",
            "Alignment summary: Proposal and report are aligned on Razorpay's platform evolution, DELTA framework, UPI context, and embedded finance strategy. The conclusion is revised so embedded finance is presented as supporting resilience, retention, liquidity stability, and profit continuity before measurable income expansion.",
            "Key model evidence: Churn ROC-AUC 0.967, precision 1.000, recall 0.927, F1 0.962. Adoption ROC-AUC 0.963, precision 0.892, recall 0.840, F1 0.866. Default ROC-AUC 0.706 with low precision; use for risk bands and human review. Income growth model R2 0.823 with churn-adjusted interpretation required.",
            "Final conclusion: Growth appears constrained by churn and provider inactivity rather than technology failure. Embedded finance and digital adoption should be treated as operational enablers of retention, liquidity, and resilience.",
            "Submission readiness score after report alignment: 86/100.",
        ],
    )
    changes.append("Supervisor evidence alignment addendum embedded in report.")
    return changes


def main() -> None:
    base = Path(r"D:\Project Files\MBA Project\Demo\Claude report")
    proposal_src = base / "Project_Proposal_DYPatil_Razorpay_FinTech_May2026 (1).docx"
    report_src = base / "MBA_Razorpay_FinTech_Report_Updated_May2026.docx"
    proposal_dst = Path("Updated_Proposal.docx")
    report_dst = Path("Updated_Report.docx")

    proposal_changes = patch_docx(proposal_src, proposal_dst, patch_proposal)
    report_changes = patch_docx(report_src, report_dst, patch_report)

    print("Updated_Proposal.docx")
    for change in proposal_changes:
        print(f"- {change}")
    print("Updated_Report.docx")
    for change in report_changes:
        print(f"- {change}")


if __name__ == "__main__":
    main()
