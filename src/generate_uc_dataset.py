"""
Generate synthetic Urban Company-style provider data for an MBA dissertation on
Razorpay-style embedded finance in India.

Only approved dependencies are used: pandas, numpy, faker, scipy, and tqdm.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import timedelta

import numpy as np
import pandas as pd
from scipy.special import expit
from tqdm import tqdm

try:
    from faker import Faker
except ImportError:  # pragma: no cover - exercised only when Faker is absent.
    Faker = None

try:
    from provenance import DELTA_COLUMN_MAP, SCHEMAS
except ImportError:
    from src.provenance import DELTA_COLUMN_MAP, SCHEMAS


REGION_CITY_WEIGHTS = {
    "North": [("Delhi NCR", 0.42), ("Jaipur", 0.18), ("Lucknow", 0.20), ("Chandigarh", 0.20)],
    "West": [("Mumbai", 0.34), ("Pune", 0.26), ("Ahmedabad", 0.22), ("Surat", 0.18)],
    "South": [("Bengaluru", 0.34), ("Hyderabad", 0.25), ("Chennai", 0.22), ("Kochi", 0.19)],
    "East": [("Kolkata", 0.44), ("Bhubaneswar", 0.22), ("Guwahati", 0.18), ("Patna", 0.16)],
}

CATEGORY_PRIORS = {
    "beauty_wellness": {"weight": 0.30, "ticket_mean": 1050, "ticket_sd": 230, "commission": 0.24},
    "home_cleaning": {"weight": 0.18, "ticket_mean": 1450, "ticket_sd": 320, "commission": 0.22},
    "appliance_repair": {"weight": 0.20, "ticket_mean": 850, "ticket_sd": 210, "commission": 0.20},
    "plumbing_electrical": {"weight": 0.17, "ticket_mean": 700, "ticket_sd": 180, "commission": 0.18},
    "salon_spa_premium": {"weight": 0.15, "ticket_mean": 1700, "ticket_sd": 380, "commission": 0.26},
}

PAYMENT_METHODS = ["UPI", "card", "wallet", "netbanking", "cash"]
BASE_PAYMENT_PROBS = np.array([0.68, 0.13, 0.08, 0.04, 0.07])
TREATED_PAYMENT_PROBS = np.array([0.74, 0.12, 0.07, 0.04, 0.03])


@dataclass
class MonthlyState:
    retained: bool
    current_income: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic embedded-finance provider datasets.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--n_merchants", type=int, default=1000, help="Number of providers to generate.")
    parser.add_argument("--months", type=int, default=12, help="Number of monthly panel periods.")
    parser.add_argument("--start_month", default="2024-01", help="First panel month in YYYY-MM format.")
    parser.add_argument(
        "--end_month",
        default=None,
        help="Optional final panel month in YYYY-MM format. Overrides --months when supplied.",
    )
    parser.add_argument(
        "--treatment_frac",
        type=float,
        default=0.50,
        help="Share of providers assigned embedded finance access.",
    )
    parser.add_argument(
        "--phased_rollout",
        action="store_true",
        help="If set, treatment starts in staggered months instead of month 1.",
    )
    parser.add_argument("--out_dir", default="data", help="Directory where CSVs will be saved.")
    return parser.parse_args()


def month_count(start_month: str, end_month: str | None, months: int) -> int:
    if end_month is None:
        return months
    start = pd.Period(start_month, freq="M")
    end = pd.Period(end_month, freq="M")
    if end < start:
        raise ValueError("--end_month must be greater than or equal to --start_month.")
    return (end.year - start.year) * 12 + end.month - start.month + 1


def clipped_normal(rng: np.random.Generator, mean: float, sd: float, low: float, high: float, size=None):
    values = rng.normal(mean, sd, size=size)
    return np.clip(values, low, high)


def weighted_choice(rng: np.random.Generator, labels, weights, size=None):
    probs = np.array(weights, dtype=float)
    probs = probs / probs.sum()
    return rng.choice(labels, size=size, p=probs)


def merchant_id_for(index: int, fake) -> str:
    if fake is None:
        return f"UC{index + 1:08d}"
    return f"UC{fake.unique.random_number(digits=8, fix_len=True)}"


def bounded_score(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def build_merchants(
    n_merchants: int,
    treatment_frac: float,
    phased_rollout: bool,
    months: int,
    rng,
    fake=None,
    start_month: str = "2024-01",
):
    category_names = list(CATEGORY_PRIORS)
    category_weights = [CATEGORY_PRIORS[name]["weight"] for name in category_names]
    region_names = list(REGION_CITY_WEIGHTS)
    region_weights = [0.31, 0.27, 0.30, 0.12]

    rows = []
    for i in range(n_merchants):
        region = weighted_choice(rng, region_names, region_weights)
        city_labels, city_weights = zip(*REGION_CITY_WEIGHTS[region])
        city = weighted_choice(rng, city_labels, city_weights)
        category = weighted_choice(rng, category_names, category_weights)
        priors = CATEGORY_PRIORS[category]

        tenure_days = int(np.clip(rng.gamma(shape=2.4, scale=230), 30, 2200))
        avg_ticket = float(clipped_normal(rng, priors["ticket_mean"], priors["ticket_sd"], 250, 3200))
        monthly_jobs = float(np.clip(rng.normal(34, 11), 8, 85))
        monthly_income = avg_ticket * monthly_jobs * rng.uniform(0.85, 1.18)
        repeat_rate = float(clipped_normal(rng, 0.38 + tenure_days / 9000, 0.10, 0.08, 0.78))
        commission = float(clipped_normal(rng, priors["commission"], 0.025, 0.12, 0.32))
        kyc_flag = bool(rng.random() < 0.91)
        metro_boost = 0.08 if city in {"Delhi NCR", "Mumbai", "Bengaluru", "Hyderabad", "Pune", "Chennai"} else 0.0
        digital_tool_usage = bounded_score(
            rng.normal(0.42, 0.15) + metro_boost + 0.10 * kyc_flag + 0.18 * repeat_rate
        )
        ai_adoption_score = bounded_score(rng.normal(0.16, 0.11) + 0.42 * digital_tool_usage + 0.000045 * tenure_days)
        agent_usage_flag = bool(rng.random() < bounded_score(-0.08 + 0.70 * ai_adoption_score + 0.20 * digital_tool_usage))
        payment_success_rate = bounded_score(rng.normal(0.925, 0.025) + 0.025 * digital_tool_usage + 0.015 * kyc_flag)
        transaction_velocity = float(np.clip(monthly_jobs * (0.88 + 0.25 * digital_tool_usage), 5, 120))
        multi_product_adoption = int(
            1
            + kyc_flag
            + (digital_tool_usage > 0.55)
            + (ai_adoption_score > 0.55)
            + agent_usage_flag
        )

        rows.append(
            {
                "merchant_id": merchant_id_for(i, fake),
                "region": region,
                "city": city,
                "category": category,
                "tenure_days": tenure_days,
                "avg_ticket": round(avg_ticket, 2),
                "monthly_income": round(monthly_income, 2),
                "repeat_customer_rate": round(repeat_rate, 4),
                "platform_commission_pct": round(commission, 4),
                "kyc_flag": kyc_flag,
                "payment_success_rate": round(payment_success_rate, 4),
                "transaction_velocity": round(transaction_velocity, 2),
                "multi_product_adoption": multi_product_adoption,
                "digital_tool_usage": round(digital_tool_usage, 4),
                "ai_adoption_score": round(ai_adoption_score, 4),
                "agent_usage_flag": agent_usage_flag,
            }
        )

    merchants = pd.DataFrame(rows)
    eligible = merchants.index[merchants["kyc_flag"]].to_numpy()
    n_treated = int(round(len(eligible) * np.clip(treatment_frac, 0, 1)))
    treated_idx = rng.choice(eligible, size=n_treated, replace=False) if n_treated > 0 else []

    treatment_flags = np.zeros(len(merchants), dtype=bool)
    treatment_start_months = np.zeros(len(merchants), dtype=int)
    treatment_flags[treated_idx] = True
    if phased_rollout:
        start_low = 2 if months >= 4 else 1
        start_high = max(start_low, min(months - 2, 18))
        rollout_span = start_high - start_low + 1
        region_rank = {"South": 0.10, "West": 0.28, "North": 0.50, "East": 0.72}
        category_rank = {
            "salon_spa_premium": 0.05,
            "beauty_wellness": 0.22,
            "home_cleaning": 0.42,
            "appliance_repair": 0.62,
            "plumbing_electrical": 0.82,
        }
        tenure_pct = merchants["tenure_days"].rank(method="average", pct=True)
        rollout_score = (
            0.38 * merchants["region"].map(region_rank).astype(float)
            + 0.34 * merchants["category"].map(category_rank).astype(float)
            + 0.28 * (1 - tenure_pct)
        )
        rollout_score = rollout_score + rng.normal(0, 0.055, size=len(merchants))
        treated_order = np.argsort(rollout_score.to_numpy()[treated_idx])
        ordered_treated_idx = np.asarray(treated_idx)[treated_order]
        phased_offsets = np.floor(np.arange(len(ordered_treated_idx)) * rollout_span / max(len(ordered_treated_idx), 1)).astype(int)
        treatment_start_months[ordered_treated_idx] = start_low + np.clip(phased_offsets, 0, rollout_span - 1)
    else:
        treatment_start_months[treated_idx] = 1

    treatment_columns = pd.DataFrame(
        {
            "treatment_flag": treatment_flags,
            "treatment_start_month": treatment_start_months,
            "intervention_timestamp": [
                (pd.Timestamp(f"{start_month}-01") + pd.DateOffset(months=int(month) - 1)).date().isoformat()
                if month > 0
                else ""
                for month in treatment_start_months
            ],
        },
        index=merchants.index,
    )
    merchants = pd.concat([merchants, treatment_columns], axis=1)

    return merchants


def month_seasonality(month_number: int) -> float:
    calendar_month = ((month_number - 1) % 12) + 1
    seasonal = 1.0 + 0.07 * np.sin(2 * np.pi * (calendar_month - 2) / 12)
    festival_boost = 0.06 if calendar_month in {10, 11, 12} else 0.0
    summer_softness = -0.035 if calendar_month in {5, 6} else 0.0
    return seasonal + festival_boost + summer_softness


def payment_probabilities(month_idx: int, treatment_active: bool) -> np.ndarray:
    upi_shift = min(0.16, 0.006 * (month_idx - 1))
    cash_decline = min(0.055, 0.0025 * (month_idx - 1))
    wallet_shift = min(0.020, 0.0008 * (month_idx - 1))
    probs = (TREATED_PAYMENT_PROBS if treatment_active else BASE_PAYMENT_PROBS).astype(float).copy()
    probs[0] += upi_shift + (0.025 if treatment_active else 0.0)
    probs[4] = max(0.005, probs[4] - cash_decline - (0.020 if treatment_active else 0.0))
    probs[2] += wallet_shift
    probs[1] = max(0.04, probs[1] - 0.35 * upi_shift)
    probs[3] = max(0.015, probs[3] - 0.15 * upi_shift)
    return probs / probs.sum()


def transaction_day(rng: np.random.Generator, month_start: pd.Timestamp) -> pd.Timestamp:
    day_offset = int(rng.integers(0, month_start.days_in_month))
    minute_offset = int(rng.integers(7 * 60, 21 * 60))
    return month_start + timedelta(days=day_offset, minutes=minute_offset)


def generate_panel_outputs(merchants: pd.DataFrame, months: int, rng, start_month: str = "2024-01"):
    start_month_ts = pd.Timestamp(f"{start_month}-01")
    transaction_rows = []
    payout_rows = []
    kpi_rows = []
    transaction_counter = 1

    merchant_records = merchants.to_dict("records")
    for merchant in tqdm(merchant_records, desc="Generating providers"):
        state = MonthlyState(retained=True, current_income=float(merchant["monthly_income"]))

        for month_idx in range(1, months + 1):
            month_start = start_month_ts + pd.DateOffset(months=month_idx - 1)
            month_label = month_start.strftime("%Y-%m")
            treatment_active = bool(
                merchant["treatment_flag"]
                and merchant["treatment_start_month"] > 0
                and month_idx >= merchant["treatment_start_month"]
            )

            if not state.retained:
                kpi_rows.append(
                    {
                        "merchant_id": merchant["merchant_id"],
                        "month": month_label,
                        "income_growth_pct": -1.0,
                        "monthly_profit": 0.0,
                        "retention_flag": False,
                        "churn_probability": 1.0,
                        "treatment_flag": bool(merchant["treatment_flag"]),
                        "post_treatment_flag": treatment_active,
                        "lock_in_score": 0.0,
                        "technology_adoption_score": round(
                            bounded_score(float(merchant["digital_tool_usage"]) + 0.010 * (month_idx - 1)), 4
                        ),
                        "advancement_score": 0.0,
                        "agentic_intelligence_score": round(
                            bounded_score(float(merchant["ai_adoption_score"]) + 0.012 * (month_idx - 1)), 4
                        ),
                        "forecast_usage": False,
                    }
                )
                payout_rows.append(
                    {
                        "merchant_id": merchant["merchant_id"],
                        "month": month_label,
                        "payout_amount": 0.0,
                        "payout_delay_days": np.nan,
                        "active_provider_month_flag": False,
                        "loan_offer_flag": False,
                        "loan_amount": 0.0,
                        "loan_status": "not_offered",
                        "repayment_amount": 0.0,
                        "working_capital_gap": 0.0,
                        "loan_disbursal_time": 0.0,
                        "default_flag": False,
                    }
                )
                continue

            seasonality = month_seasonality(month_idx)
            years_elapsed = (month_idx - 1) / 12.0
            inflation_factor = (1.052 ** years_elapsed)
            digital_maturity = bounded_score(float(merchant["digital_tool_usage"]) + 0.011 * (month_idx - 1) + 0.025 * treatment_active)
            ai_maturity = bounded_score(float(merchant["ai_adoption_score"]) + 0.010 * (month_idx - 1) + 0.018 * treatment_active)
            payment_success_dynamic = bounded_score(
                float(merchant["payment_success_rate"]) + 0.0028 * (month_idx - 1) + 0.010 * treatment_active
            )
            liquidity_effect = 0.048 if treatment_active else 0.0
            technology_effect = 0.030 * digital_maturity
            agentic_effect = 0.020 * ai_maturity + (0.012 if merchant["agent_usage_flag"] else 0.0)
            loan_growth_effect = 0.026 if treatment_active and rng.random() < min(0.42, 0.20 + 0.009 * month_idx) else 0.0
            category_noise = rng.normal(0, 0.045)
            target_income = (
                float(merchant["monthly_income"])
                * inflation_factor
                * seasonality
                * (1 + liquidity_effect + technology_effect + agentic_effect + loan_growth_effect + category_noise)
            )
            state.current_income = max(0.55 * state.current_income + 0.45 * target_income, 0)

            expected_jobs = max(state.current_income / float(merchant["avg_ticket"]), 1)
            n_txn = int(np.clip(rng.poisson(expected_jobs), 1, 140))
            payment_probs = TREATED_PAYMENT_PROBS if treatment_active else BASE_PAYMENT_PROBS
            gross_amount = 0.0
            tip_total = 0.0
            completed_amount = 0.0
            cancelled_count = 0
            rating_values = []

            for _ in range(n_txn):
                amount = float(rng.lognormal(mean=np.log(float(merchant["avg_ticket"]) * inflation_factor), sigma=0.23))
                amount = float(np.clip(amount, 150, 5000))
                cancellation_prob = 0.055 - (0.012 if treatment_active else 0.0)
                cancellation_prob += 0.02 * (1 - float(merchant["repeat_customer_rate"]))
                cancellation_prob -= 0.012 * digital_maturity
                cancelled = bool(rng.random() < np.clip(cancellation_prob, 0.015, 0.14))
                rating_mean = 4.18 + 0.22 * float(merchant["repeat_customer_rate"]) + (0.06 if treatment_active else 0)
                rating_mean += 0.07 * digital_maturity + 0.04 * ai_maturity
                rating = float(clipped_normal(rng, rating_mean, 0.42, 1.0, 5.0))
                tip_prob = 0.18 + 0.10 * (rating >= 4.6)
                tip = float(rng.gamma(2.0, 35.0)) if (not cancelled and rng.random() < tip_prob) else 0.0
                service_completion_rate = bounded_score(
                    1.0 - cancellation_prob + 0.015 * digital_maturity + rng.normal(0, 0.012)
                )
                settlement_improvement = min(0.35, 0.012 * (month_idx - 1))
                settlement_delay = float(
                    rng.uniform(0.03, 0.55) * (1.0 - 0.20 * settlement_improvement)
                    if treatment_active
                    else rng.uniform(0.8, 3.6) * (1.0 - 0.24 * digital_maturity - 0.35 * settlement_improvement)
                )

                transaction_rows.append(
                    {
                        "transaction_id": f"TXN{transaction_counter:010d}",
                        "merchant_id": merchant["merchant_id"],
                        "timestamp": transaction_day(rng, month_start).isoformat(),
                        "amount": round(amount, 2),
                        "customer_rating": round(rating, 2),
                        "payment_method": weighted_choice(rng, PAYMENT_METHODS, payment_probabilities(month_idx, treatment_active)),
                        "cancellation_flag": cancelled,
                        "tip_amount": round(tip, 2),
                        "treatment_active": treatment_active,
                        "settlement_delay": round(settlement_delay, 3),
                        "service_completion_rate": round(service_completion_rate, 4),
                    }
                )
                transaction_counter += 1
                gross_amount += amount
                tip_total += tip
                rating_values.append(rating)
                if cancelled:
                    cancelled_count += 1
                else:
                    completed_amount += amount

            settlement_improvement = min(0.38, 0.014 * (month_idx - 1))
            payout_delay = float(
                rng.uniform(0.35, 1.45) * (1.0 - 0.18 * settlement_improvement)
                if treatment_active
                else rng.uniform(2.4, 6.8) * (1.0 - 0.45 * settlement_improvement - 0.12 * digital_maturity)
            )
            payout_amount = completed_amount * (1 - float(merchant["platform_commission_pct"])) + tip_total
            expected_working_capital_need = float(merchant["monthly_income"]) * rng.uniform(0.18, 0.34)
            liquidity_buffer = payout_amount * (0.18 + 0.16 * treatment_active + 0.08 * float(merchant["digital_tool_usage"]))
            working_capital_gap = float(max(expected_working_capital_need - liquidity_buffer, 0.0))
            credit_uptake_trend = min(0.45, 0.018 * (month_idx - 1))
            loan_offer_prob = expit(
                -2.2
                + 1.15 * treatment_active
                + credit_uptake_trend
                + 0.55 * merchant["kyc_flag"]
                + 0.000018 * payout_amount
            )
            loan_offer = bool(rng.random() < loan_offer_prob)
            loan_amount = 0.0
            loan_status = "not_offered"
            repayment_amount = 0.0
            loan_disbursal_time = 0.0
            if loan_offer:
                accepts = bool(rng.random() < (0.62 if treatment_active else 0.35))
                if accepts:
                    loan_amount = float(np.clip(max(payout_amount * rng.uniform(0.18, 0.42), working_capital_gap * rng.uniform(0.45, 0.85)), 3000, 85000))
                    loan_disbursal_time = float(rng.uniform(0.08, 0.75) if treatment_active else rng.uniform(1.2, 4.5))
                    default_prob = float(np.clip(0.105 - 0.025 * treatment_active - 0.000001 * payout_amount, 0.025, 0.16))
                    default_prob = float(
                        np.clip(default_prob + 0.0000012 * working_capital_gap - 0.022 * ai_maturity, 0.012, 0.18)
                    )
                    if rng.random() < default_prob:
                        loan_status = "defaulted"
                        repayment_amount = loan_amount * rng.uniform(0.12, 0.65)
                    elif rng.random() < 0.45:
                        loan_status = "repaid"
                        repayment_amount = loan_amount * rng.uniform(1.015, 1.055)
                    else:
                        loan_status = "active"
                        repayment_amount = loan_amount * rng.uniform(0.04, 0.12)
                else:
                    loan_status = "declined"

            operating_cost = completed_amount * rng.uniform(0.34, 0.46)
            finance_cost = max(repayment_amount - loan_amount, 0) if loan_status == "repaid" else 0
            monthly_profit = payout_amount - operating_cost - finance_cost
            income_growth = (payout_amount - float(merchant["monthly_income"])) / max(float(merchant["monthly_income"]), 1)

            avg_rating = float(np.mean(rating_values)) if rating_values else 4.0
            cancellation_rate = cancelled_count / max(n_txn, 1)
            churn_logit = (
                -3.0
                - 0.55 * treatment_active
                - 0.45 * float(merchant["repeat_customer_rate"])
                - 0.000018 * payout_amount
                + 0.55 * cancellation_rate
                - 0.22 * (avg_rating - 4.0)
                - 0.00025 * float(merchant["tenure_days"])
                - 0.22 * digital_maturity
            )
            churn_probability = float(np.clip(expit(churn_logit), 0.005, 0.30))
            churned_after_month = bool(rng.random() < churn_probability)

            payout_rows.append(
                {
                    "merchant_id": merchant["merchant_id"],
                    "month": month_label,
                    "payout_amount": round(payout_amount, 2),
                    "payout_delay_days": round(payout_delay, 2),
                    "active_provider_month_flag": True,
                    "loan_offer_flag": loan_offer,
                    "loan_amount": round(loan_amount, 2),
                    "loan_status": loan_status,
                    "repayment_amount": round(repayment_amount, 2),
                    "working_capital_gap": round(working_capital_gap, 2),
                    "loan_disbursal_time": round(loan_disbursal_time, 3),
                    "default_flag": loan_status == "defaulted",
                }
            )
            product_score = float(merchant["multi_product_adoption"]) / 5.0
            lock_in_score = bounded_score(
                0.30 * float(merchant["repeat_customer_rate"])
                + 0.20 * product_score
                + 0.20 * (1 - churn_probability)
                + 0.15 * treatment_active
                + 0.15 * (avg_rating / 5.0)
            )
            technology_adoption_score = bounded_score(
                0.55 * digital_maturity
                + 0.25 * payment_success_dynamic
                + 0.20 * ai_maturity
            )
            normalized_profit = bounded_score(monthly_profit / max(float(merchant["monthly_income"]), 1))
            advancement_score = bounded_score(
                0.35 * bounded_score((income_growth + 0.40) / 0.90)
                + 0.30 * normalized_profit
                + 0.20 * (1 - churn_probability)
                + 0.15 * service_completion_rate
            )
            forecast_usage = bool(merchant["agent_usage_flag"] and rng.random() < bounded_score(0.35 + 0.55 * ai_maturity))
            agentic_intelligence_score = bounded_score(
                0.55 * ai_maturity
                + 0.25 * bool(merchant["agent_usage_flag"])
                + 0.20 * forecast_usage
            )
            kpi_rows.append(
                {
                    "merchant_id": merchant["merchant_id"],
                    "month": month_label,
                    "income_growth_pct": round(income_growth, 4),
                    "monthly_profit": round(monthly_profit, 2),
                    "retention_flag": not churned_after_month,
                    "churn_probability": round(churn_probability, 4),
                    "treatment_flag": bool(merchant["treatment_flag"]),
                    "post_treatment_flag": treatment_active,
                    "lock_in_score": round(lock_in_score, 4),
                    "technology_adoption_score": round(technology_adoption_score, 4),
                    "advancement_score": round(advancement_score, 4),
                    "agentic_intelligence_score": round(agentic_intelligence_score, 4),
                    "forecast_usage": forecast_usage,
                }
            )
            state.retained = not churned_after_month

    return (
        pd.DataFrame(transaction_rows),
        pd.DataFrame(payout_rows),
        pd.DataFrame(kpi_rows),
    )


def classify_source_type(dataset: str, column_name: str) -> str:
    if dataset == "provenance.csv":
        return "metadata"
    if column_name in {
        "treatment_flag",
        "treatment_start_month",
        "intervention_timestamp",
        "treatment_active",
        "post_treatment_flag",
    }:
        return "assigned"
    if column_name in {
        "payment_success_rate",
        "transaction_velocity",
        "multi_product_adoption",
        "digital_tool_usage",
        "ai_adoption_score",
        "agent_usage_flag",
        "settlement_delay",
        "service_completion_rate",
        "working_capital_gap",
        "loan_disbursal_time",
        "default_flag",
        "lock_in_score",
        "technology_adoption_score",
        "advancement_score",
        "agentic_intelligence_score",
        "forecast_usage",
        "active_provider_month_flag",
    }:
        return "derived"
    if column_name in {"region", "city", "category", "payment_method", "platform_commission_pct"}:
        return "public"
    return "synthetic"


def build_provenance() -> pd.DataFrame:
    rows = []
    for dataset, schema in SCHEMAS.items():
        for column in schema["columns"]:
            column_name = column["name"]
            rows.append(
                {
                    "dataset": dataset,
                    "column_name": column_name,
                    "delta_dimension": DELTA_COLUMN_MAP.get(column_name, "Data"),
                    "source_type": classify_source_type(dataset, column_name),
                    "description": column["comment"],
                }
            )
    return pd.DataFrame(rows)


def save_outputs(merchants, transactions, payouts_loans, provider_kpis, provenance, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    merchants.to_csv(os.path.join(out_dir, "merchants.csv"), index=False)
    transactions.to_csv(os.path.join(out_dir, "transactions.csv"), index=False)
    payouts_loans.to_csv(os.path.join(out_dir, "payouts_loans.csv"), index=False)
    provider_kpis.to_csv(os.path.join(out_dir, "provider_kpis.csv"), index=False)
    provenance.to_csv(os.path.join(out_dir, "provenance.csv"), index=False)


def main():
    args = parse_args()
    args.months = month_count(args.start_month, args.end_month, args.months)
    if args.n_merchants <= 0:
        raise ValueError("--n_merchants must be positive.")
    if args.months <= 0:
        raise ValueError("--months must be positive.")
    if not 0 <= args.treatment_frac <= 1:
        raise ValueError("--treatment_frac must be between 0 and 1.")

    rng = np.random.default_rng(args.seed)
    fake = None
    if Faker is not None:
        fake = Faker("en_IN")
        Faker.seed(args.seed)

    merchants = build_merchants(
        n_merchants=args.n_merchants,
        treatment_frac=args.treatment_frac,
        phased_rollout=args.phased_rollout,
        months=args.months,
        rng=rng,
        fake=fake,
        start_month=args.start_month,
    )
    transactions, payouts_loans, provider_kpis = generate_panel_outputs(merchants, args.months, rng, args.start_month)
    provenance = build_provenance()
    save_outputs(merchants, transactions, payouts_loans, provider_kpis, provenance, args.out_dir)

    print(f"Saved merchants: {len(merchants):,}")
    print(f"Saved transactions: {len(transactions):,}")
    print(f"Saved payouts_loans rows: {len(payouts_loans):,}")
    print(f"Saved provider_kpis rows: {len(provider_kpis):,}")
    print(f"Saved provenance rows: {len(provenance):,}")
    print(f"Output directory: {os.path.abspath(args.out_dir)}")


if __name__ == "__main__":
    main()
