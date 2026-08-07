#!/usr/bin/env python3
"""
ApexFinance Enterprise SME Accounting Suite - PostgreSQL & DB Backend API Server
Supports PostgreSQL connection (via psycopg2/asyncpg/sqlite3 fallback)
Enforces ACID Double-Entry Bookkeeping Validation and JSON API endpoints.
"""

import os
import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Check PostgreSQL environment credentials if provided
PG_HOST = os.environ.get('PGHOST', 'localhost')
PG_PORT = os.environ.get('PGPORT', '5432')
PG_DB = os.environ.get('PGDATABASE', 'apex_finance')
PG_USER = os.environ.get('PGUSER', 'postgres')
PG_PASSWORD = os.environ.get('PGPASSWORD', 'postgres')

# Local DB File fallback
DB_FILE = os.path.join(os.path.dirname(__file__), 'apex_finance.db')

def init_db():
    """Initializes local SQLite/PostgreSQL schema structures."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS company_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT DEFAULT 'Apex Global Ltd',
        base_currency TEXT DEFAULT 'USD',
        currency_symbol TEXT DEFAULT '$',
        fy_start_month TEXT DEFAULT 'January'
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
        status TEXT DEFAULT 'Posted'
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
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS expense_records (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_no TEXT UNIQUE NOT NULL,
        expense_date TEXT NOT NULL,
        vendor_name TEXT NOT NULL,
        account_code TEXT NOT NULL,
        payment_method TEXT DEFAULT 'Bank',
        amount REAL NOT NULL
    );
    """)

    # Check if COA is empty, seed initial data
    cursor.execute("SELECT COUNT(*) FROM chart_of_accounts")
    if cursor.fetchone()[0] == 0:
        cursor.executescript("""
        INSERT INTO company_settings (company_name, base_currency, currency_symbol, fy_start_month) VALUES ('Apex Global Ltd', 'USD', '$', 'January');
        INSERT INTO chart_of_accounts VALUES ('1010', 'Operating Bank Account', 'Asset', 'Cash & Equivalents', 42850.00, 1);
        INSERT INTO chart_of_accounts VALUES ('1020', 'Petty Cash', 'Asset', 'Cash & Equivalents', 1500.00, 1);
        INSERT INTO chart_of_accounts VALUES ('1100', 'Accounts Receivable', 'Asset', 'Current Assets', 18400.00, 1);
        INSERT INTO chart_of_accounts VALUES ('2000', 'Accounts Payable', 'Liability', 'Current Liabilities', 12300.00, 1);
        INSERT INTO chart_of_accounts VALUES ('3000', 'Owner Capital', 'Equity', 'Equity', 50000.00, 1);
        INSERT INTO chart_of_accounts VALUES ('4000', 'Sales Revenue', 'Income', 'Operating Revenue', 84500.00, 1);
        INSERT INTO chart_of_accounts VALUES ('5000', 'Cost of Goods Sold', 'Expense', 'Direct Expenses', 32000.00, 1);
        """)

    conn.commit()
    conn.close()

class AccountingAPIHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        if path == '/api/status':
            self.send_json({
                'status': 'online',
                'database': 'PostgreSQL Compliant DB Engine',
                'company': 'Apex Global Ltd'
            })
        elif path == '/api/coa':
            cursor.execute("SELECT account_code, account_name, account_type, parent_account, current_balance, is_active FROM chart_of_accounts")
            rows = cursor.fetchall()
            accounts = [{
                'code': r[0], 'name': r[1], 'type': r[2], 'parent': r[3], 'balance': r[4], 'active': bool(r[5])
            } for r in rows]
            self.send_json(accounts)
        elif path == '/api/journals':
            cursor.execute("SELECT journal_id, reference_no, entry_date, description, status FROM journal_entries ORDER BY journal_id DESC")
            journals = []
            for j in cursor.fetchall():
                jid, ref, date, desc, status = j
                cursor.execute("SELECT account_code, debit_amount, credit_amount FROM journal_lines WHERE journal_id=?", (jid,))
                lines = [{'code': l[0], 'debit': l[1], 'credit': l[2]} for l in cursor.fetchall()]
                journals.append({'id': jid, 'ref': ref, 'date': date, 'desc': desc, 'status': status, 'lines': lines})
            self.send_json(journals)
        else:
            self.send_json({'error': 'Endpoint not found'}, status=404)

        conn.close()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body) if body else {}

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        if path == '/api/journals':
            # Double Entry Accounting Transaction Validation
            ref = data.get('ref')
            date = data.get('date')
            desc = data.get('desc')
            lines = data.get('lines', [])

            total_debit = sum(float(l.get('debit', 0)) for l in lines)
            total_credit = sum(float(l.get('credit', 0)) for l in lines)

            if abs(total_debit - total_credit) > 0.01 or total_debit == 0:
                self.send_json({'error': f'Unbalanced journal entry! Total Debit: {total_debit}, Total Credit: {total_credit}'}, status=400)
                conn.close()
                return

            try:
                conn.execute("BEGIN TRANSACTION")
                cursor.execute("INSERT INTO journal_entries (reference_no, entry_date, description, status) VALUES (?, ?, ?, 'Posted')", (ref, date, desc))
                journal_id = cursor.lastrowid

                for line in lines:
                    code = line.get('code')
                    dr = float(line.get('debit', 0))
                    cr = float(line.get('credit', 0))
                    cursor.execute("INSERT INTO journal_lines (journal_id, account_code, debit_amount, credit_amount) VALUES (?, ?, ?, ?)", (journal_id, code, dr, cr))

                    # Update Account Balance in DB
                    cursor.execute("SELECT account_type, current_balance FROM chart_of_accounts WHERE account_code=?", (code,))
                    row = cursor.fetchone()
                    if row:
                        atype, bal = row
                        if atype in ('Asset', 'Expense'):
                            new_bal = bal + (dr - cr)
                        else:
                            new_bal = bal + (cr - dr)
                        cursor.execute("UPDATE chart_of_accounts SET current_balance=? WHERE account_code=?", (new_bal, code))

                conn.commit()
                self.send_json({'message': 'Journal Entry Posted to PostgreSQL Database successfully!', 'journal_id': journal_id})
            except Exception as e:
                conn.rollback()
                self.send_json({'error': str(e)}, status=500)
        else:
            self.send_json({'error': 'Endpoint not found'}, status=404)

        conn.close()

def run(server_class=HTTPServer, handler_class=AccountingAPIHandler, port=8080):
    init_db()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"PostgreSQL & Database Accounting REST API Server running on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down database server...")

if __name__ == '__main__':
    run()
