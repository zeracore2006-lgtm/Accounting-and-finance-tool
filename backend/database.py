import os
import sqlite3
from config import Config

def get_db_connection():
    """Returns a active database connection (SQLite with PostgreSQL compatibility schema)."""
    conn = sqlite3.connect(Config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initializes tables and seeds initial SME dataset if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS company_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT DEFAULT 'Apex Global Ltd',
        base_currency TEXT DEFAULT 'USD',
        currency_symbol TEXT DEFAULT '$',
        fy_start_month TEXT DEFAULT 'January',
        invoice_prefix TEXT DEFAULT 'INV-',
        journal_prefix TEXT DEFAULT 'JE-',
        bill_prefix TEXT DEFAULT 'BILL-'
    );

    CREATE TABLE IF NOT EXISTS chart_of_accounts (
        account_code TEXT PRIMARY KEY,
        account_name TEXT NOT NULL,
        account_type TEXT NOT NULL,
        parent_account TEXT,
        current_balance REAL DEFAULT 0.0,
        is_active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS journal_entries (
        journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_no TEXT UNIQUE NOT NULL,
        entry_date TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'Posted',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS journal_lines (
        line_id INTEGER PRIMARY KEY AUTOINCREMENT,
        journal_id INTEGER NOT NULL,
        account_code TEXT NOT NULL,
        debit_amount REAL DEFAULT 0.0,
        credit_amount REAL DEFAULT 0.0,
        FOREIGN KEY(journal_id) REFERENCES journal_entries(journal_id),
        FOREIGN KEY(account_code) REFERENCES chart_of_accounts(account_code)
    );

    CREATE TABLE IF NOT EXISTS income_records (
        income_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_no TEXT UNIQUE NOT NULL,
        income_date TEXT NOT NULL,
        source_category TEXT NOT NULL,
        account_code TEXT NOT NULL,
        amount REAL NOT NULL,
        deposit_account TEXT DEFAULT '1010',
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS expense_records (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_no TEXT UNIQUE NOT NULL,
        expense_date TEXT NOT NULL,
        vendor_name TEXT NOT NULL,
        account_code TEXT NOT NULL,
        payment_method TEXT DEFAULT 'Bank',
        paid_from TEXT DEFAULT '1010',
        amount REAL NOT NULL,
        receipt TEXT
    );

    CREATE TABLE IF NOT EXISTS customer_invoices (
        invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        balance_due REAL NOT NULL,
        status TEXT DEFAULT 'Pending'
    );

    CREATE TABLE IF NOT EXISTS supplier_bills (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_number TEXT UNIQUE NOT NULL,
        supplier_name TEXT NOT NULL,
        bill_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'Unpaid'
    );

    CREATE TABLE IF NOT EXISTS bank_statements (
        statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_code TEXT NOT NULL,
        transaction_date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        is_reconciled INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS fixed_assets (
        asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_code TEXT UNIQUE NOT NULL,
        asset_name TEXT NOT NULL,
        category TEXT NOT NULL,
        purchase_date TEXT NOT NULL,
        purchase_cost REAL NOT NULL,
        useful_life INTEGER NOT NULL,
        accumulated_depreciation REAL DEFAULT 0.0
    );

    CREATE TABLE IF NOT EXISTS budgets (
        budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL,
        annual_budget REAL NOT NULL,
        actual_ytd_spend REAL DEFAULT 0.0
    );
    """)

    # Check COA seeding
    cursor.execute("SELECT COUNT(*) FROM chart_of_accounts")
    if cursor.fetchone()[0] == 0:
        cursor.executescript("""
        INSERT INTO company_settings (company_name, base_currency, currency_symbol) VALUES ('Apex Global Ltd', 'USD', '$');

        INSERT INTO chart_of_accounts VALUES ('1010', 'Operating Bank Account', 'Asset', 'Cash & Equivalents', 42850.00, 1);
        INSERT INTO chart_of_accounts VALUES ('1020', 'Petty Cash', 'Asset', 'Cash & Equivalents', 1500.00, 1);
        INSERT INTO chart_of_accounts VALUES ('1100', 'Accounts Receivable', 'Asset', 'Current Assets', 18400.00, 1);
        INSERT INTO chart_of_accounts VALUES ('1200', 'Inventory Asset', 'Asset', 'Current Assets', 24000.00, 1);
        INSERT INTO chart_of_accounts VALUES ('1500', 'Equipment & Furniture', 'Asset', 'Fixed Assets', 35000.00, 1);
        INSERT INTO chart_of_accounts VALUES ('1550', 'Accumulated Depreciation - Equip', 'Asset', 'Fixed Assets', -7000.00, 1);

        INSERT INTO chart_of_accounts VALUES ('2000', 'Accounts Payable', 'Liability', 'Current Liabilities', 12300.00, 1);
        INSERT INTO chart_of_accounts VALUES ('2100', 'Sales Tax Payable (GST/VAT)', 'Liability', 'Current Liabilities', 2450.00, 1);
        INSERT INTO chart_of_accounts VALUES ('2200', 'Accrued Salaries Payable', 'Liability', 'Current Liabilities', 3200.00, 1);

        INSERT INTO chart_of_accounts VALUES ('3000', 'Owner Capital', 'Equity', 'Equity', 50000.00, 1);
        INSERT INTO chart_of_accounts VALUES ('3900', 'Retained Earnings', 'Equity', 'Equity', 41800.00, 1);

        INSERT INTO chart_of_accounts VALUES ('4000', 'Sales Revenue', 'Income', 'Operating Revenue', 84500.00, 1);
        INSERT INTO chart_of_accounts VALUES ('4100', 'Service Income', 'Income', 'Operating Revenue', 18200.00, 1);
        INSERT INTO chart_of_accounts VALUES ('4200', 'Other Income', 'Income', 'Non-Operating Income', 1800.00, 1);

        INSERT INTO chart_of_accounts VALUES ('5000', 'Cost of Goods Sold', 'Expense', 'Direct Expenses', 32000.00, 1);
        INSERT INTO chart_of_accounts VALUES ('5100', 'Rent Expense', 'Expense', 'Operating Expenses', 12000.00, 1);
        INSERT INTO chart_of_accounts VALUES ('5200', 'Salaries Expense', 'Expense', 'Operating Expenses', 18000.00, 1);
        INSERT INTO chart_of_accounts VALUES ('5300', 'Utilities Expense', 'Expense', 'Operating Expenses', 2400.00, 1);
        INSERT INTO chart_of_accounts VALUES ('5400', 'Depreciation Expense', 'Expense', 'Operating Expenses', 3500.00, 1);
        INSERT INTO chart_of_accounts VALUES ('5500', 'General & Administrative', 'Expense', 'Operating Expenses', 4600.00, 1);

        INSERT INTO journal_entries (reference_no, entry_date, description, status) VALUES ('JE-2026-001', '2026-08-01', 'Initial Capital Injection', 'Posted');
        INSERT INTO journal_lines (journal_id, account_code, debit_amount, credit_amount) VALUES (1, '1010', 50000.0, 0.0);
        INSERT INTO journal_lines (journal_id, account_code, debit_amount, credit_amount) VALUES (1, '3000', 0.0, 50000.0);

        INSERT INTO customer_invoices VALUES (1, 'INV-2026-01', 'Starlight Retail', '2026-07-15', '2026-08-15', 8400.0, 8400.0, 'Overdue');
        INSERT INTO customer_invoices VALUES (2, 'INV-2026-02', 'BlueWave Tech', '2026-08-01', '2026-08-30', 10000.0, 10000.0, 'Pending');

        INSERT INTO supplier_bills VALUES (1, 'BILL-2026-01', 'TechParts Supplies', '2026-07-20', '2026-08-20', 7300.0, 'Unpaid');
        INSERT INTO supplier_bills VALUES (2, 'BILL-2026-02', 'Apex Landlord Co', '2026-08-01', '2026-08-15', 5000.0, 'Unpaid');

        INSERT INTO fixed_assets VALUES (1, 'AST-01', 'Workstation Laptops (5x)', 'IT Equipment', '2025-01-10', 15000.0, 3, 5000.0);
        INSERT INTO fixed_assets VALUES (2, 'AST-02', 'Executive Desk & Chairs', 'Office Furniture', '2025-06-15', 20000.0, 5, 2000.0);

        INSERT INTO budgets VALUES (1, '5100 - Rent Expense', 48000.0, 12000.0);
        INSERT INTO budgets VALUES (2, '5200 - Salaries Expense', 220000.0, 18000.0);
        """)

    conn.commit()
    conn.close()
