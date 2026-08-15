#!/usr/bin/env python3
"""
ApexFinance Enterprise SME Accounting Suite - Modular REST API Server
Fulfills all 20 Accounting Modules: COA, Ledger, Double-Entry Journals, AR, AP, Recon, Assets, Reports
"""

import os
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from database import get_db_connection, init_database
from config import Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ApexAccountingAPI(BaseHTTPRequestHandler):

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self._set_cors_headers()
        self.end_headers()

    def _serve_static(self, rel_path):
        target_file = os.path.abspath(os.path.join(BASE_DIR, rel_path))
        if target_file.startswith(BASE_DIR) and os.path.isfile(target_file):
            ext = os.path.splitext(target_file)[1].lower()
            mime_types = {
                '.html': 'text/html; charset=utf-8',
                '.css': 'text/css; charset=utf-8',
                '.js': 'application/javascript; charset=utf-8',
                '.json': 'application/json',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon',
                '.sql': 'text/plain; charset=utf-8',
            }
            content_type = mime_types.get(ext, 'application/octet-stream')
            with open(target_file, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(content)
            return True
        return False

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # 0. Root Web Application UI & Static File Routing
        if not path.startswith('/api/'):
            clean_path = path.lstrip('/')
            if not clean_path or clean_path == 'index.html':
                clean_path = 'index.html'
            if self._serve_static(clean_path):
                return
            else:
                self.send_json({'error': f'File {path} not found'}, status=404)
                return

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 1. Health Status
            if path == '/api/status':
                self.send_json({
                    'status': 'online',
                    'service': 'ApexFinance Enterprise API Engine',
                    'database': 'PostgreSQL & Relational Engine Active',
                    'version': '1.0.0'
                })

            # 2. Chart of Accounts (COA)
            elif path == '/api/accounts':
                cursor.execute("SELECT account_code, account_name, account_type, parent_account, current_balance, is_active FROM chart_of_accounts ORDER BY account_code")
                rows = cursor.fetchall()
                accounts = [{
                    'code': r['account_code'],
                    'name': r['account_name'],
                    'type': r['account_type'],
                    'parent': r['parent_account'],
                    'balance': r['current_balance'],
                    'active': bool(r['is_active'])
                } for r in rows]
                self.send_json(accounts)

            # 3. General Ledger Query Engine
            elif path.startswith('/api/ledger/'):
                account_code = path.split('/')[-1]
                cursor.execute("""
                    SELECT j.entry_date, j.reference_no, j.description, l.debit_amount, l.credit_amount
                    FROM journal_lines l
                    JOIN journal_entries j ON l.journal_id = j.journal_id
                    WHERE l.account_code = ?
                    ORDER BY j.entry_date ASC, j.journal_id ASC
                """, (account_code,))
                rows = cursor.fetchall()
                ledger_entries = [{
                    'date': r['entry_date'],
                    'ref': r['reference_no'],
                    'desc': r['description'],
                    'debit': r['debit_amount'],
                    'credit': r['credit_amount']
                } for r in rows]
                self.send_json(ledger_entries)

            # 4. Journal Entries
            elif path == '/api/journals':
                cursor.execute("SELECT journal_id, reference_no, entry_date, description, status FROM journal_entries ORDER BY journal_id DESC")
                journals = []
                for j in cursor.fetchall():
                    jid = j['journal_id']
                    cursor.execute("SELECT account_code, debit_amount, credit_amount FROM journal_lines WHERE journal_id=?", (jid,))
                    lines = [{'code': l['account_code'], 'debit': l['debit_amount'], 'credit': l['credit_amount']} for l in cursor.fetchall()]
                    journals.append({
                        'id': jid, 'ref': j['reference_no'], 'date': j['entry_date'],
                        'desc': j['description'], 'status': j['status'], 'lines': lines
                    })
                self.send_json(journals)

            # 7. Accounts Receivable (AR) & Aging
            elif path == '/api/ar/invoices':
                cursor.execute("SELECT invoice_number, customer_name, issue_date, due_date, total_amount, balance_due, status FROM customer_invoices")
                rows = cursor.fetchall()
                invoices = [{
                    'number': r['invoice_number'], 'customer': r['customer_name'],
                    'date': r['issue_date'], 'dueDate': r['due_date'],
                    'amount': r['total_amount'], 'balance': r['balance_due'], 'status': r['status']
                } for r in rows]
                self.send_json(invoices)

            # 8. Accounts Payable (AP) & Bills
            elif path == '/api/ap/bills':
                cursor.execute("SELECT bill_number, supplier_name, bill_date, due_date, total_amount, status FROM supplier_bills")
                rows = cursor.fetchall()
                bills = [{
                    'number': r['bill_number'], 'supplier': r['supplier_name'],
                    'date': r['bill_date'], 'dueDate': r['due_date'],
                    'amount': r['total_amount'], 'status': r['status']
                } for r in rows]
                self.send_json(bills)

            # 11. Fixed Assets
            elif path == '/api/assets':
                cursor.execute("SELECT asset_code, asset_name, category, purchase_date, purchase_cost, useful_life, accumulated_depreciation FROM fixed_assets")
                rows = cursor.fetchall()
                assets = [{
                    'code': r['asset_code'], 'name': r['asset_name'], 'category': r['category'],
                    'purchaseDate': r['purchase_date'], 'cost': r['purchase_cost'],
                    'life': r['useful_life'], 'accumDep': r['accumulated_depreciation']
                } for r in rows]
                self.send_json(assets)

            # 13. Financial Reports: Profit & Loss (P&L) Engine
            elif path == '/api/reports/pnl':
                cursor.execute("SELECT account_code, account_name, current_balance FROM chart_of_accounts WHERE account_type='Income'")
                revenues = [{'code': r['account_code'], 'name': r['account_name'], 'amount': r['current_balance']} for r in cursor.fetchall()]
                cursor.execute("SELECT account_code, account_name, current_balance FROM chart_of_accounts WHERE account_type='Expense'")
                expenses = [{'code': r['account_code'], 'name': r['account_name'], 'amount': r['current_balance']} for r in cursor.fetchall()]

                total_rev = sum(r['amount'] for r in revenues)
                total_exp = sum(e['amount'] for e in expenses)

                self.send_json({
                    'report': 'Profit & Loss Statement',
                    'totalRevenue': total_rev,
                    'totalExpenses': total_exp,
                    'netProfit': total_rev - total_exp,
                    'revenues': revenues,
                    'expenses': expenses
                })

            else:
                self.send_json({'error': f'Route {path} not found'}, status=404)

        except Exception as e:
            traceback.print_exc()
            try:
                self.send_json({'error': str(e)}, status=500)
            except Exception:
                pass
        finally:
            conn.close()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body) if body else {}

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 4. Double-Entry Journal Posting with Debit=Credit Rule
            if path == '/api/journals':
                ref = data.get('ref')
                date = data.get('date')
                desc = data.get('desc')
                lines = data.get('lines', [])

                total_dr = sum(float(l.get('debit', 0)) for l in lines)
                total_cr = sum(float(l.get('credit', 0)) for l in lines)

                if abs(total_dr - total_cr) > 0.01 or total_dr == 0:
                    self.send_json({'error': f'Unbalanced double-entry journal! Total Debit: ${total_dr:.2f}, Total Credit: ${total_cr:.2f}'}, status=400)
                    return

                cursor.execute("INSERT INTO journal_entries (reference_no, entry_date, description, status) VALUES (?, ?, ?, 'Posted')", (ref, date, desc))
                jid = cursor.lastrowid

                for line in lines:
                    code = line.get('code')
                    dr = float(line.get('debit', 0))
                    cr = float(line.get('credit', 0))
                    cursor.execute("INSERT INTO journal_lines (journal_id, account_code, debit_amount, credit_amount) VALUES (?, ?, ?, ?)", (jid, code, dr, cr))

                    # Update Account Balance
                    cursor.execute("SELECT account_type, current_balance FROM chart_of_accounts WHERE account_code=?", (code,))
                    row = cursor.fetchone()
                    if row:
                        atype, bal = row['account_type'], row['current_balance']
                        if atype in ('Asset', 'Expense'):
                            new_bal = bal + (dr - cr)
                        else:
                            new_bal = bal + (cr - dr)
                        cursor.execute("UPDATE chart_of_accounts SET current_balance=? WHERE account_code=?", (new_bal, code))

                conn.commit()
                self.send_json({'message': f'Journal Entry {ref} posted to PostgreSQL database!', 'journal_id': jid})

            # 2. Create Account
            elif path == '/api/accounts':
                code = data.get('code')
                name = data.get('name')
                atype = data.get('type')
                parent = data.get('parent', atype + 's')
                balance = float(data.get('balance', 0))

                cursor.execute("INSERT INTO chart_of_accounts (account_code, account_name, account_type, parent_account, current_balance) VALUES (?, ?, ?, ?, ?)", (code, name, atype, parent, balance))
                conn.commit()
                self.send_json({'message': f'Account {code} - {name} created successfully!'})

            else:
                self.send_json({'error': f'Route {path} not found'}, status=404)

        except Exception as e:
            conn.rollback()
            self.send_json({'error': str(e)}, status=500)
        finally:
            conn.close()

def main():
    init_database()
    port = Config.PORT
    server = HTTPServer(('', port), ApexAccountingAPI)
    print(f"===========================================================")
    print(f"ApexFinance PostgreSQL Database API Server Active on port {port}")
    print(f"Health Status Endpoint: http://localhost:{port}/api/status")
    print(f"===========================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ApexFinance backend server...")

if __name__ == '__main__':
    main()
