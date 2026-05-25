"""
Dataset schemas and provenance metadata for the Urban Company embedded-finance
synthetic data project.

The schema objects below are intentionally plain Python dictionaries so they can
be imported by generation, validation, and documentation scripts without adding
dependencies beyond the approved project libraries.
"""

SCHEMAS = {
    "merchants.csv": {
        "description": "One row per Urban Company-style service provider.",
        "columns": [
            {
                "name": "merchant_id",
                "dtype": "string",
                "comment": "Stable synthetic provider identifier.",
            },
            {
                "name": "region",
                "dtype": "category",
                "comment": "Indian macro-region used for geographic calibration.",
            },
            {
                "name": "city",
                "dtype": "category",
                "comment": "Provider operating city.",
            },
            {
                "name": "category",
                "dtype": "category",
                "comment": "Service category such as beauty, repairs, cleaning, or appliance services.",
            },
            {
                "name": "tenure_days",
                "dtype": "int64",
                "comment": "Days since provider joined the platform at the start of the panel.",
            },
            {
                "name": "avg_ticket",
                "dtype": "float64",
                "comment": "Typical customer order value in Indian rupees.",
            },
            {
                "name": "monthly_income",
                "dtype": "float64",
                "comment": "Baseline monthly gross provider income in Indian rupees.",
            },
            {
                "name": "repeat_customer_rate",
                "dtype": "float64",
                "comment": "Share of customers expected to return, bounded between 0 and 1.",
            },
            {
                "name": "platform_commission_pct",
                "dtype": "float64",
                "comment": "Platform commission rate charged to the provider, expressed as 0 to 1.",
            },
            {
                "name": "kyc_flag",
                "dtype": "bool",
                "comment": "Whether provider passed KYC checks required for embedded finance.",
            },
            {
                "name": "treatment_flag",
                "dtype": "bool",
                "comment": "Whether provider is assigned to embedded finance access.",
            },
            {
                "name": "treatment_start_month",
                "dtype": "int64",
                "comment": "First panel month with embedded finance access; 0 indicates never treated.",
            },
            {
                "name": "intervention_timestamp",
                "dtype": "datetime64[ns]",
                "comment": "Calendar timestamp when embedded finance access begins; blank for never-treated providers.",
            },
            {
                "name": "payment_success_rate",
                "dtype": "float64",
                "comment": "Provider-level expected digital payment success rate, bounded between 0 and 1.",
            },
            {
                "name": "transaction_velocity",
                "dtype": "float64",
                "comment": "Expected monthly transaction throughput for the provider.",
            },
            {
                "name": "multi_product_adoption",
                "dtype": "int64",
                "comment": "Count of embedded-finance and digital products adopted by the provider.",
            },
            {
                "name": "digital_tool_usage",
                "dtype": "float64",
                "comment": "Provider use of platform digital tools, bounded between 0 and 1.",
            },
            {
                "name": "ai_adoption_score",
                "dtype": "float64",
                "comment": "Provider adoption of AI-assisted workflows, bounded between 0 and 1.",
            },
            {
                "name": "agent_usage_flag",
                "dtype": "bool",
                "comment": "Whether provider uses agentic AI assistance for planning, support, or forecasts.",
            },
        ],
    },
    "transactions.csv": {
        "description": "Synthetic customer payment transactions linked to providers.",
        "columns": [
            {
                "name": "transaction_id",
                "dtype": "string",
                "comment": "Stable synthetic transaction identifier.",
            },
            {
                "name": "merchant_id",
                "dtype": "string",
                "comment": "Foreign key to merchants.csv.",
            },
            {
                "name": "timestamp",
                "dtype": "datetime64[ns]",
                "comment": "Transaction timestamp within the simulated study window.",
            },
            {
                "name": "amount",
                "dtype": "float64",
                "comment": "Customer payment amount in Indian rupees.",
            },
            {
                "name": "customer_rating",
                "dtype": "float64",
                "comment": "Post-service customer rating on a 1 to 5 scale.",
            },
            {
                "name": "payment_method",
                "dtype": "category",
                "comment": "Payment rail such as UPI, card, wallet, netbanking, or cash.",
            },
            {
                "name": "cancellation_flag",
                "dtype": "bool",
                "comment": "Whether the booking was cancelled after being created.",
            },
            {
                "name": "tip_amount",
                "dtype": "float64",
                "comment": "Customer tip amount in Indian rupees.",
            },
            {
                "name": "treatment_active",
                "dtype": "bool",
                "comment": "Whether embedded finance was active for the provider at transaction time.",
            },
            {
                "name": "settlement_delay",
                "dtype": "float64",
                "comment": "Estimated transaction settlement delay in days.",
            },
            {
                "name": "service_completion_rate",
                "dtype": "float64",
                "comment": "Transaction-level expected service completion probability, bounded between 0 and 1.",
            },
        ],
    },
    "payouts_loans.csv": {
        "description": "Monthly payout and working-capital loan outcomes by provider.",
        "columns": [
            {
                "name": "merchant_id",
                "dtype": "string",
                "comment": "Foreign key to merchants.csv.",
            },
            {
                "name": "month",
                "dtype": "period[M]",
                "comment": "Provider panel month.",
            },
            {
                "name": "payout_amount",
                "dtype": "float64",
                "comment": "Provider payout amount after commission and cancellations.",
            },
            {
                "name": "payout_delay_days",
                "dtype": "float64",
                "comment": "Estimated delay between service completion and provider payout; NaN when provider-month is inactive after churn.",
            },
            {
                "name": "active_provider_month_flag",
                "dtype": "bool",
                "comment": "Whether provider was active and eligible for payout activity in the provider-month.",
            },
            {
                "name": "loan_offer_flag",
                "dtype": "bool",
                "comment": "Whether the provider received a working-capital loan offer.",
            },
            {
                "name": "loan_amount",
                "dtype": "float64",
                "comment": "Working-capital principal offered or disbursed in Indian rupees.",
            },
            {
                "name": "loan_status",
                "dtype": "category",
                "comment": "Loan state: not_offered, declined, active, repaid, or defaulted.",
            },
            {
                "name": "repayment_amount",
                "dtype": "float64",
                "comment": "Loan repayment amount collected in Indian rupees.",
            },
            {
                "name": "working_capital_gap",
                "dtype": "float64",
                "comment": "Estimated monthly liquidity shortfall before financing in Indian rupees.",
            },
            {
                "name": "loan_disbursal_time",
                "dtype": "float64",
                "comment": "Estimated loan disbursal time in days; zero when no loan is accepted.",
            },
            {
                "name": "default_flag",
                "dtype": "bool",
                "comment": "Whether the monthly loan outcome defaulted.",
            },
        ],
    },
    "provider_kpis.csv": {
        "description": "Provider-month outcomes for dissertation analysis.",
        "columns": [
            {
                "name": "merchant_id",
                "dtype": "string",
                "comment": "Foreign key to merchants.csv.",
            },
            {
                "name": "month",
                "dtype": "period[M]",
                "comment": "Provider panel month.",
            },
            {
                "name": "income_growth_pct",
                "dtype": "float64",
                "comment": "Monthly income growth relative to baseline income.",
            },
            {
                "name": "monthly_profit",
                "dtype": "float64",
                "comment": "Estimated monthly provider profit after commission, financing, and operating costs.",
            },
            {
                "name": "retention_flag",
                "dtype": "bool",
                "comment": "Whether the provider remains active in the month.",
            },
            {
                "name": "churn_probability",
                "dtype": "float64",
                "comment": "Model-implied provider churn probability, bounded between 0 and 1.",
            },
            {
                "name": "treatment_flag",
                "dtype": "bool",
                "comment": "Whether provider is assigned to embedded finance access.",
            },
            {
                "name": "post_treatment_flag",
                "dtype": "bool",
                "comment": "Whether provider-month occurs after embedded finance access begins.",
            },
            {
                "name": "lock_in_score",
                "dtype": "float64",
                "comment": "Provider platform lock-in score based on retention, repeat customers, and product adoption.",
            },
            {
                "name": "technology_adoption_score",
                "dtype": "float64",
                "comment": "Provider technology adoption score based on digital tools and payment success.",
            },
            {
                "name": "advancement_score",
                "dtype": "float64",
                "comment": "Provider advancement score based on income growth, profit, and retention.",
            },
            {
                "name": "agentic_intelligence_score",
                "dtype": "float64",
                "comment": "Provider score for AI and agentic workflow adoption.",
            },
            {
                "name": "forecast_usage",
                "dtype": "bool",
                "comment": "Whether provider uses AI forecasts for demand, cash flow, or loan planning.",
            },
        ],
    },
    "provenance.csv": {
        "description": "Column-level provenance and DELTA framework mapping for generated datasets.",
        "columns": [
            {
                "name": "dataset",
                "dtype": "string",
                "comment": "Generated CSV file name.",
            },
            {
                "name": "column_name",
                "dtype": "string",
                "comment": "Column name in the generated dataset.",
            },
            {
                "name": "delta_dimension",
                "dtype": "category",
                "comment": "DELTA framework dimension represented by the column.",
            },
            {
                "name": "source_type",
                "dtype": "category",
                "comment": "Whether the value is synthetic, derived, assigned, or metadata.",
            },
            {
                "name": "description",
                "dtype": "string",
                "comment": "Research interpretation of the column.",
            },
        ],
    },
}


PUBLIC_DATA_PRIORS = {
    "payment_methods": (
        "Digital payment adoption in India is led by UPI, with cards, wallets, "
        "netbanking, and cash retained for realism."
    ),
    "embedded_finance_mechanism": (
        "Payments, faster payouts, and working-capital access are modeled as "
        "improving liquidity, reducing churn, and increasing provider income."
    ),
    "study_design": (
        "Treatment assignment and phased rollout fields support quasi-experimental "
        "MBA analyses such as balance checks and Difference-in-Differences."
    ),
    "delta_framework": (
        "The DELTA framework maps Data, Embedded Finance, Lock-in, Technology, "
        "Advancement, and Agentic Intelligence into measurable synthetic variables."
    ),
}


DELTA_COLUMN_MAP = {
    "merchant_id": "Data",
    "transaction_id": "Data",
    "timestamp": "Data",
    "month": "Data",
    "region": "Data",
    "city": "Data",
    "category": "Data",
    "tenure_days": "Data",
    "avg_ticket": "Data",
    "monthly_income": "Data",
    "repeat_customer_rate": "Lock-in",
    "platform_commission_pct": "Embedded Finance",
    "kyc_flag": "Embedded Finance",
    "treatment_flag": "Embedded Finance",
    "treatment_start_month": "Embedded Finance",
    "intervention_timestamp": "Embedded Finance",
    "payment_success_rate": "Data",
    "transaction_velocity": "Data",
    "multi_product_adoption": "Embedded Finance",
    "digital_tool_usage": "Technology",
    "ai_adoption_score": "Agentic Intelligence",
    "agent_usage_flag": "Agentic Intelligence",
    "amount": "Data",
    "customer_rating": "Data",
    "payment_method": "Embedded Finance",
    "cancellation_flag": "Data",
    "tip_amount": "Data",
    "treatment_active": "Embedded Finance",
    "settlement_delay": "Embedded Finance",
    "service_completion_rate": "Advancement",
    "payout_amount": "Embedded Finance",
    "payout_delay_days": "Embedded Finance",
    "active_provider_month_flag": "Data",
    "loan_offer_flag": "Embedded Finance",
    "loan_amount": "Embedded Finance",
    "loan_status": "Embedded Finance",
    "repayment_amount": "Embedded Finance",
    "working_capital_gap": "Embedded Finance",
    "loan_disbursal_time": "Embedded Finance",
    "default_flag": "Embedded Finance",
    "income_growth_pct": "Advancement",
    "monthly_profit": "Advancement",
    "retention_flag": "Lock-in",
    "churn_probability": "Lock-in",
    "post_treatment_flag": "Embedded Finance",
    "lock_in_score": "Lock-in",
    "technology_adoption_score": "Technology",
    "advancement_score": "Advancement",
    "agentic_intelligence_score": "Agentic Intelligence",
    "forecast_usage": "Agentic Intelligence",
    "dataset": "Data",
    "column_name": "Data",
    "delta_dimension": "Data",
    "source_type": "Data",
    "description": "Data",
}


def get_schema(file_name):
    """Return the schema dictionary for a generated CSV file."""
    return SCHEMAS[file_name]


def schema_columns(file_name):
    """Return ordered column names for a generated CSV file."""
    return [column["name"] for column in get_schema(file_name)["columns"]]


def schema_dtypes(file_name):
    """Return a name-to-dtype mapping for a generated CSV file."""
    return {column["name"]: column["dtype"] for column in get_schema(file_name)["columns"]}
