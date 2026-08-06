-- =============================================================================
-- APEXFINANCE ENTERPRISE SME ACCOUNTING SUITE - POSTGRESQL DATABASE SCHEMA
-- Compatible with PostgreSQL 12+
-- Enforces ACID Double-Entry Bookkeeping Integrity across 20 Modules
-- =============================================================================

-- Enable UUID extension if available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- MODULE 19: COMPANY & SYSTEM SETTINGS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS company_settings (
    setting_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL DEFAULT 'Apex Global Ltd',
    base_currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    currency_symbol VARCHAR(5) NOT NULL DEFAULT '$',
    fy_start_month VARCHAR(20) NOT NULL DEFAULT 'January',
    invoice_prefix VARCHAR(10) DEFAULT 'INV-',
    journal_prefix VARCHAR(10) DEFAULT 'JE-',
    bill_prefix VARCHAR(10) DEFAULT 'BILL-',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MODULE 2: CHART OF ACCOUNTS (COA)
-- -----------------------------------------------------------------------------
CREATE TYPE account_type_enum AS ENUM ('Asset', 'Liability', 'Equity', 'Income', 'Expense');

CREATE TABLE IF NOT EXISTS chart_of_accounts (
    account_code VARCHAR(50) PRIMARY KEY,
    account_name VARCHAR(255) NOT NULL,
    account_type account_type_enum NOT NULL,
    parent_account VARCHAR(255),
    current_balance NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coa_type ON chart_of_accounts(account_type);

-- -----------------------------------------------------------------------------
-- MODULE 4: JOURNAL ENTRIES & DOUBLE-ENTRY BOOKKEEPING
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS journal_entries (
    journal_id SERIAL PRIMARY KEY,
    reference_no VARCHAR(100) UNIQUE NOT NULL,
    entry_date DATE NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Posted', -- 'Draft', 'Posted', 'Reversal'
    created_by VARCHAR(100) DEFAULT 'Admin',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS journal_lines (
    line_id SERIAL PRIMARY KEY,
    journal_id INT NOT NULL REFERENCES journal_entries(journal_id) ON DELETE CASCADE,
    account_code VARCHAR(50) NOT NULL REFERENCES chart_of_accounts(account_code),
    debit_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    credit_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    CONSTRAINT check_debit_credit_positive CHECK (debit_amount >= 0 AND credit_amount >= 0),
    CONSTRAINT check_not_both_zero CHECK (debit_amount > 0 OR credit_amount > 0)
);

CREATE INDEX idx_jlines_journal ON journal_lines(journal_id);
CREATE INDEX idx_jlines_account ON journal_lines(account_code);

-- -----------------------------------------------------------------------------
-- MODULE 5: INCOME RECORDS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS income_records (
    income_id SERIAL PRIMARY KEY,
    reference_no VARCHAR(100) UNIQUE NOT NULL,
    income_date DATE NOT NULL,
    source_category VARCHAR(255) NOT NULL,
    account_code VARCHAR(50) NOT NULL REFERENCES chart_of_accounts(account_code),
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    deposit_account_code VARCHAR(50) REFERENCES chart_of_accounts(account_code),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MODULE 6: EXPENSE MANAGEMENT
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expense_records (
    expense_id SERIAL PRIMARY KEY,
    reference_no VARCHAR(100) UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    account_code VARCHAR(50) NOT NULL REFERENCES chart_of_accounts(account_code),
    payment_method VARCHAR(50) NOT NULL DEFAULT 'Bank',
    paid_from_account VARCHAR(50) REFERENCES chart_of_accounts(account_code),
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    receipt_filename VARCHAR(255),
    is_recurring BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MODULE 7: ACCOUNTS RECEIVABLE (AR)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customer_invoices (
    invoice_id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount NUMERIC(15, 2) NOT NULL CHECK (total_amount >= 0),
    balance_due NUMERIC(15, 2) NOT NULL CHECK (balance_due >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Paid', 'Overdue', 'Written-Off'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MODULE 8: ACCOUNTS PAYABLE (AP)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS supplier_bills (
    bill_id SERIAL PRIMARY KEY,
    bill_number VARCHAR(100) UNIQUE NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    bill_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount NUMERIC(15, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'Unpaid', -- 'Unpaid', 'Paid', 'Overdue'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MODULE 9: BANK & CASH & RECONCILIATION
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bank_statements (
    statement_line_id SERIAL PRIMARY KEY,
    account_code VARCHAR(50) NOT NULL REFERENCES chart_of_accounts(account_code),
    transaction_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    is_reconciled BOOLEAN NOT NULL DEFAULT FALSE,
    reconciled_journal_id INT REFERENCES journal_entries(journal_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MODULE 11: FIXED ASSETS & DEPRECIATION
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fixed_assets (
    asset_id SERIAL PRIMARY KEY,
    asset_code VARCHAR(50) UNIQUE NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    purchase_date DATE NOT NULL,
    purchase_cost NUMERIC(15, 2) NOT NULL CHECK (purchase_cost > 0),
    useful_life_years INT NOT NULL CHECK (useful_life_years > 0),
    accumulated_depreciation NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    depreciation_method VARCHAR(50) DEFAULT 'Straight-Line',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MODULE 12: BUDGETING
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS budgets (
    budget_id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    account_code VARCHAR(50) REFERENCES chart_of_accounts(account_code),
    fiscal_year INT NOT NULL DEFAULT 2026,
    annual_budget NUMERIC(15, 2) NOT NULL CHECK (annual_budget >= 0),
    actual_ytd_spend NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MODULE 14: PERIOD CLOSING
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS period_closing (
    period_id SERIAL PRIMARY KEY,
    fiscal_year INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    month_number INT NOT NULL CHECK (month_number BETWEEN 1 AND 12),
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    closed_at TIMESTAMP WITH TIME ZONE,
    closed_by VARCHAR(100)
);

-- -----------------------------------------------------------------------------
-- MODULE 16: DOCUMENT REPOSITORY
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS financial_documents (
    doc_id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    doc_type VARCHAR(50) NOT NULL, -- 'Receipt', 'Bill', 'Statement', 'Contract'
    file_size VARCHAR(50),
    upload_date DATE NOT NULL DEFAULT CURRENT_DATE,
    file_url TEXT
);

-- -----------------------------------------------------------------------------
-- MODULE 20: ECOSYSTEM INTEGRATION LOG
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ecosystem_sync_logs (
    log_id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'Synced',
    details TEXT,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create double-entry validation helper view
CREATE OR REPLACE VIEW view_journal_validation AS
SELECT 
    j.journal_id,
    j.reference_no,
    j.entry_date,
    SUM(l.debit_amount) AS total_debit,
    SUM(l.credit_amount) AS total_credit,
    (SUM(l.debit_amount) - SUM(l.credit_amount)) AS balance_diff
FROM journal_entries j
JOIN journal_lines l ON j.journal_id = l.journal_id
GROUP BY j.journal_id, j.reference_no, j.entry_date;
