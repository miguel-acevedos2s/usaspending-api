"""
Look ups for elasticsearch fields
to be displayed for the front end
"""
TRANSACTIONS_LOOKUP = {
    "Recipient Name": "recipient_name",
    "Action Date": "action_date",
    "Transaction Amount": "transaction_amount",
    "Award Type": "type_description",
    "Awarding Agency": "awarding_toptier_agency_name",
    "Awarding Sub Agency": "awarding_subtier_agency_name",
    "Funding Agency": "funding_toptier_agency_name",
    "Funding Sub Agency": "funding_subtier_agency_name",
    "Issued Date": "period_of_performance_start_date",
    "Loan Value": "face_value_loan_guarantee",
    "Subsidy Cost": "original_loan_subsidy_cost",
    "Mod": "modification_number",
    "Award ID": "display_award_id",
    "awarding_agency_id": "awarding_agency_id",
    "internal_id": "award_id",
    "Last Date to Order": "ordering_period_end_date",
}

award_categories = ["contracts", "direct_payments", "loans", "grants", "other"]


indices_to_award_types = {
    "contracts": ("A", "B", "C", "D"),
    "idvs": ("IDV_A", "IDV_B", "IDV_B_A", "IDV_B_B", "IDV_B_C", "IDV_C", "IDV_D"),
    "directpayments": ("06", "10"),
    "grants": ("02", "03", "04", "05"),
    "loans": ("07", "08"),
    "other": ("09", "11"),
}

KEYWORD_DATATYPE_FIELDS = ["recipient_name", "awarding_toptier_agency_name", "awarding_subtier_agency_name"]
