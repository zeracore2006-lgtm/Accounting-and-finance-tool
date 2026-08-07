-- =============================================================================
-- APEXFINANCE POSTGRESQL SEED DATA SCRIPT
-- Pre-populates realistic SME financial records for Apex Global Ltd
-- =============================================================================

-- Company Settings
INSERT INTO company_settings (company_name, base_currency, currency_symbol, fy_start_month)
VALUES ('Apex Global Ltd', 'USD', '$', 'January');

-- Chart of Accounts (COA)
INSERT INTO chart_of_accounts (account_code, account_name, account_type, parent_account, current_balance, is_active) VALUES
('1010', 'Operating Bank Account', 'Asset', 'Cash & Equivalents', 42850.00, TRUE),
('1020', 'Petty Cash', 'Asset', 'Cash & Equivalents', 1500.00, TRUE),
('1100', 'Accounts Receivable', 'Asset', 'Current Assets', 18400.00, TRUE),
('1200', 'Inventory Asset', 'Asset', 'Current Assets', 24000.00, TRUE),
('1500', 'Equipment & Furniture', 'Asset', 'Fixed Assets', 35000.00, TRUE),
('1550', 'Accumulated Depreciation - Equip', 'Asset', 'Fixed Assets', -7000.00, TRUE),
('2000', 'Accounts Payable', 'Liability', 'Current Liabilities', 12300.00, TRUE),
('2100', 'Sales Tax Payable (GST/VAT)', 'Liability', 'Current Liabilities', 2450.00, TRUE),
('2200', 'Accrued Salaries Payable', 'Liability', 'Current Liabilities', 3200.00, TRUE),
('3000', 'Owner''s Capital', 'Equity', 'Equity', 50000.00, TRUE),
('3900', 'Retained Earnings', 'Equity', 'Equity', 41800.00, TRUE),
('4000', 'Sales Revenue', 'Income', 'Operating Revenue', 84500.00, TRUE),
('4100', 'Service Income', 'Income', 'Operating Revenue', 18200.00, TRUE),
('4200', 'Other Income', 'Income', 'Non-Operating Income', 1800.00, TRUE),
('5000', 'Cost of Goods Sold', 'Expense', 'Direct Expenses', 32000.00, TRUE),
('5100', 'Rent Expense', 'Expense', 'Operating Expenses', 12000.00, TRUE),
('5200', 'Salaries Expense', 'Expense', 'Operating Expenses', 18000.00, TRUE),
('5300', 'Utilities Expense', 'Expense', 'Operating Expenses', 2400.00, TRUE),
('5400', 'Depreciation Expense', 'Expense', 'Operating Expenses', 3500.00, TRUE),
('5500', 'General & Administrative', 'Expense', 'Operating Expenses', 4600.00, TRUE);

-- Journal Entries & Lines (Balanced Double Entry)
INSERT INTO journal_entries (reference_no, entry_date, description, status) VALUES
('JE-2026-001', '2026-08-01', 'Initial Capital Injection', 'Posted'),
('JE-2026-002', '2026-08-02', 'August Office Rent Payment', 'Posted'),
('JE-2026-003', '2026-08-04', 'Equipment Purchase Cash', 'Posted');

INSERT INTO journal_lines (journal_id, account_code, debit_amount, credit_amount) VALUES
(1, '1010', 50000.00, 0.00),
(1, '3000', 0.00, 50000.00),
(2, '5100', 4000.00, 0.00),
(2, '1010', 0.00, 4000.00),
(3, '1500', 5000.00, 0.00),
(3, '1010', 0.00, 5000.00);

-- Income Records
INSERT INTO income_records (reference_no, income_date, source_category, account_code, amount, deposit_account_code, notes) VALUES
('INC-101', '2026-08-02', 'Enterprise Software Sales', '4000', 12500.00, '1010', 'Client: Acme Corp'),
('INC-102', '2026-08-05', 'Implementation Support', '4100', 4800.00, '1010', 'Client: Global Logistics');

-- Expense Records
INSERT INTO expense_records (reference_no, expense_date, vendor_name, account_code, payment_method, paid_from_account, amount, receipt_filename) VALUES
('EXP-801', '2026-08-03', 'AWS Cloud Hosting', '5500', 'Bank Transfer', '1010', 1450.00, 'AWS_Inv_8832.pdf'),
('EXP-802', '2026-08-05', 'City Electric Utility', '5300', 'Petty Cash', '1020', 320.00, 'Utility_Receipt.jpg');

-- Customer Invoices (AR)
INSERT INTO customer_invoices (invoice_number, customer_name, issue_date, due_date, total_amount, balance_due, status) VALUES
('INV-2026-01', 'Starlight Retail', '2026-07-15', '2026-08-15', 8400.00, 8400.00, 'Overdue'),
('INV-2026-02', 'BlueWave Tech', '2026-08-01', '2026-08-30', 10000.00, 10000.00, 'Pending');

-- Supplier Bills (AP)
INSERT INTO supplier_bills (bill_number, supplier_name, bill_date, due_date, total_amount, status) VALUES
('BILL-2026-01', 'TechParts Supplies', '2026-07-20', '2026-08-20', 7300.00, 'Unpaid'),
('BILL-2026-02', 'Apex Landlord Co', '2026-08-01', '2026-08-15', 5000.00, 'Unpaid');

-- Bank Statements
INSERT INTO bank_statements (account_code, transaction_date, description, amount, is_reconciled) VALUES
('1010', '2026-08-02', 'Deposit - Starlight Retail', 5000.00, FALSE),
('1010', '2026-08-03', 'Direct Debit - AWS Hosting', -1450.00, TRUE),
('1010', '2026-08-05', 'Transfer - Petty Cash Topup', -500.00, FALSE);

-- Fixed Assets
INSERT INTO fixed_assets (asset_code, asset_name, category, purchase_date, purchase_cost, useful_life_years, accumulated_depreciation) VALUES
('AST-01', 'Workstation Laptops (5x)', 'IT Equipment', '2025-01-10', 15000.00, 3, 5000.00),
('AST-02', 'Executive Desk & Chairs', 'Office Furniture', '2025-06-15', 20000.00, 5, 2000.00);

-- Budgets
INSERT INTO budgets (category_name, account_code, annual_budget, actual_ytd_spend) VALUES
('5100 - Rent Expense', '5100', 48000.00, 12000.00),
('5200 - Salaries Expense', '5200', 220000.00, 18000.00),
('5300 - Utilities Expense', '5300', 15000.00, 2400.00),
('5500 - General & Administrative', '5500', 30000.00, 4600.00);

-- Period Closing
INSERT INTO period_closing (fiscal_year, month_name, month_number, is_closed) VALUES
(2026, 'January', 1, TRUE),
(2026, 'February', 2, TRUE),
(2026, 'March', 3, TRUE),
(2026, 'April', 4, TRUE),
(2026, 'May', 5, TRUE),
(2026, 'June', 6, TRUE),
(2026, 'July', 7, TRUE),
(2026, 'August', 8, FALSE),
(2026, 'September', 9, FALSE),
(2026, 'October', 10, FALSE),
(2026, 'November', 11, FALSE),
(2026, 'December', 12, FALSE);

-- Financial Documents
INSERT INTO financial_documents (file_name, doc_type, upload_date, file_size) VALUES
('AWS_August_Invoice.pdf', 'Receipt', '2026-08-03', '240 KB'),
('Office_Lease_Agreement.pdf', 'Contract', '2026-01-01', '1.4 MB');

-- Ecosystem Logs
INSERT INTO ecosystem_sync_logs (service_name, event_type, status, details) VALUES
('Invoicing App', 'Invoice Finalized', 'Synced', 'Synced INV-2026-02 to AR'),
('POS Retail Stream', 'Daily Cash Import', 'Synced', 'Synced $1,450 sales to ledger'),
('Bank Live Feed', 'Statement Import', 'Synced', 'Imported 3 statement lines');
