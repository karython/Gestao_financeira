# TODO: Fix Reports to Include Income Data in Transactions

## Steps to Complete
- [x] Modify `generate_report` function in `app/api/v1/endpoints/reports.py` to fetch VariableIncome and FixedIncome records for the user.
- [x] Add VariableIncome and FixedIncome items to the transactions list with appropriate fields (id, description, amount, type="receita", date=created_at.date(), category_id=None).
- [x] Ensure the transactions list now includes all relevant income sources alongside expenses.
- [ ] Verify that the PDF generation includes the updated transactions list.
- [ ] Test the endpoint to confirm incomes appear in reports.
