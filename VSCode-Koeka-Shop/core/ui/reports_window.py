"""
Reports GUI for Tembie's Spaza Shop POS System
Daily and Monthly reports, Cash Management, and Business Analytics
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime, date, timedelta
from calendar import monthrange
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.sales.cash_management import get_cash_manager
from core.auth.authentication import get_auth_manager
from core.database.connection import get_db_manager

# Try to import optional modules
try:
    from modules.basic_reporting.daily_reports import DailyReportsManager
except ImportError:
    # Create a mock class if module not available
    class DailyReportsManager:
        def __init__(self):
            pass
        def generate_daily_report(self, date):
            return {"error": "Daily reports module not available"}
        def get_monthly_summary(self, year, month):
            return {"error": "Monthly reports module not available"}

class ReportsWindow:
    """Reports and analytics interface"""
    
    def __init__(self, parent=None, user=None):
        self.parent = parent
        self.user = user or get_auth_manager().get_current_user()
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        
        # Initialize managers
        self.cash_manager = get_cash_manager()
        self.auth_manager = get_auth_manager()
        self.db = get_db_manager()
        self.daily_reports = DailyReportsManager()
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configure window properties"""
        self.root.title("Reports & Analytics - Tembie's Spaza Shop")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Configure style
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Subheader.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Report.TLabel', font=('Courier', 10))
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1400x800+{x}+{y}")
        
    def create_widgets(self):
        """Create and layout all widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook for different report types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        # Create tabs
        self.create_daily_reports_tab()
        self.create_monthly_reports_tab()
        self.create_cash_management_tab()
        self.create_analytics_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create header with title and user info"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text=" Reports & Analytics", style='Header.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        # User info
        user_info = f" {self.user.full_name} ({self.user.role})"
        user_label = ttk.Label(header_frame, text=user_info)
        user_label.grid(row=0, column=1, sticky="e")
        
    def create_daily_reports_tab(self):
        """Create daily reports tab"""
        daily_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(daily_frame, text="Daily Reports")
        
        # Configure grid
        daily_frame.columnconfigure(1, weight=1)
        daily_frame.rowconfigure(1, weight=1)
        
        # Controls panel
        controls_frame = ttk.LabelFrame(daily_frame, text="Date Selection", padding="10")
        controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Date selection
        ttk.Label(controls_frame, text="Report Date:").pack(side=tk.LEFT)
        self.daily_date_var = tk.StringVar(value=date.today().isoformat())
        date_entry = ttk.Entry(controls_frame, textvariable=self.daily_date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(controls_frame, text="Today", 
                  command=lambda: self.daily_date_var.set(date.today().isoformat())).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Yesterday", 
                  command=lambda: self.daily_date_var.set((date.today() - timedelta(days=1)).isoformat())).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Generate Report", 
                  command=self.generate_daily_report).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(controls_frame, text="Export", 
                  command=self.export_daily_report).pack(side=tk.LEFT, padx=(0, 5))
        
        # Report display
        report_frame = ttk.LabelFrame(daily_frame, text="Daily Report", padding="10")
        report_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(0, weight=1)
        
        self.daily_report_text = tk.Text(report_frame, font=('Courier', 10), wrap=tk.WORD)
        daily_scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.daily_report_text.yview)
        self.daily_report_text.configure(yscrollcommand=daily_scrollbar.set)
        
        self.daily_report_text.grid(row=0, column=0, sticky="nsew")
        daily_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Generate today's report by default
        self.generate_daily_report()
        
    def create_monthly_reports_tab(self):
        """Create monthly reports tab"""
        monthly_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(monthly_frame, text="Monthly Reports")
        
        # Configure grid
        monthly_frame.columnconfigure(1, weight=1)
        monthly_frame.rowconfigure(1, weight=1)
        
        # Controls panel
        controls_frame = ttk.LabelFrame(monthly_frame, text="Month Selection", padding="10")
        controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Month/Year selection
        ttk.Label(controls_frame, text="Month:").pack(side=tk.LEFT)
        self.month_var = tk.StringVar(value=str(date.today().month))
        month_combo = ttk.Combobox(controls_frame, textvariable=self.month_var, 
                                 values=[str(i) for i in range(1, 13)], 
                                 state="readonly", width=5)
        month_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(controls_frame, text="Year:").pack(side=tk.LEFT)
        self.year_var = tk.StringVar(value=str(date.today().year))
        year_combo = ttk.Combobox(controls_frame, textvariable=self.year_var,
                                values=[str(i) for i in range(2020, 2030)],
                                state="readonly", width=8)
        year_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(controls_frame, text="This Month", 
                  command=self.set_current_month).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(controls_frame, text="Last Month", 
                  command=self.set_last_month).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Generate Report", 
                  command=self.generate_monthly_report).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(controls_frame, text="Export", 
                  command=self.export_monthly_report).pack(side=tk.LEFT, padx=(0, 5))
        
        # Report type selection
        report_type_frame = ttk.Frame(controls_frame)
        report_type_frame.pack(side=tk.RIGHT)
        
        ttk.Label(report_type_frame, text="Report Type:").pack(side=tk.LEFT)
        self.monthly_report_type = tk.StringVar(value="summary")
        type_combo = ttk.Combobox(report_type_frame, textvariable=self.monthly_report_type,
                                values=["summary", "detailed", "financial", "vat"], 
                                state="readonly", width=12)
        type_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Report display
        report_frame = ttk.LabelFrame(monthly_frame, text="Monthly Report", padding="10")
        report_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(0, weight=1)
        
        self.monthly_report_text = tk.Text(report_frame, font=('Courier', 10), wrap=tk.WORD)
        monthly_scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.monthly_report_text.yview)
        self.monthly_report_text.configure(yscrollcommand=monthly_scrollbar.set)
        
        self.monthly_report_text.grid(row=0, column=0, sticky="nsew")
        monthly_scrollbar.grid(row=0, column=1, sticky="ns")
        
    def create_cash_management_tab(self):
        """Create cash management tab"""
        cash_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(cash_frame, text="Cash Management")
        
        # Configure grid
        cash_frame.columnconfigure(1, weight=1)
        cash_frame.rowconfigure(1, weight=1)
        
        # Controls and status panel
        controls_frame = ttk.LabelFrame(cash_frame, text="Till Management", padding="10")
        controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        controls_frame.columnconfigure(2, weight=1)
        
        # Today's status
        today_status = self.cash_manager.get_cash_summary()
        status_text = "Day Started" if today_status['day_started'] else "Day Not Started"
        status_color = "green" if today_status['day_started'] else "red"
        
        ttk.Label(controls_frame, text="Today's Status:").grid(row=0, column=0, sticky="w")
        self.cash_status_label = ttk.Label(controls_frame, text=status_text, foreground=status_color)
        self.cash_status_label.grid(row=0, column=1, sticky="w", padx=(10, 20))
        
        # Actions
        actions_frame = ttk.Frame(controls_frame)
        actions_frame.grid(row=0, column=2, sticky="e")
        
        if not today_status['day_started']:
            ttk.Button(actions_frame, text="Start Day", 
                      command=self.start_day_dialog).pack(side=tk.LEFT, padx=(0, 5))
        else:
            ttk.Button(actions_frame, text="Record Withdrawal", 
                      command=self.record_withdrawal_dialog).pack(side=tk.LEFT, padx=(0, 5))
            if not today_status['reconciled']:
                ttk.Button(actions_frame, text="Reconcile Till", 
                          command=self.reconcile_till_dialog).pack(side=tk.LEFT, padx=(0, 5))
                          
        ttk.Button(actions_frame, text="Refresh", 
                  command=self.refresh_cash_management).pack(side=tk.LEFT)
        
        # Cash summary and history
        summary_frame = ttk.LabelFrame(cash_frame, text="Cash Summary & History", padding="10")
        summary_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.rowconfigure(0, weight=1)
        
        self.cash_text = tk.Text(summary_frame, font=('Courier', 10), wrap=tk.WORD)
        cash_scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=self.cash_text.yview)
        self.cash_text.configure(yscrollcommand=cash_scrollbar.set)
        
        self.cash_text.grid(row=0, column=0, sticky="nsew")
        cash_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load initial cash data
        self.refresh_cash_management()
        
    def create_analytics_tab(self):
        """Create analytics tab"""
        analytics_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(analytics_frame, text="Analytics")
        
        # Configure grid
        analytics_frame.columnconfigure(1, weight=1)
        analytics_frame.rowconfigure(1, weight=1)
        
        # Controls panel
        controls_frame = ttk.LabelFrame(analytics_frame, text="Analysis Period", padding="10")
        controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Period selection
        ttk.Label(controls_frame, text="Period:").pack(side=tk.LEFT)
        self.analytics_period = tk.StringVar(value="last_7_days")
        period_combo = ttk.Combobox(controls_frame, textvariable=self.analytics_period,
                                  values=["last_7_days", "last_30_days", "current_month", "last_month"],
                                  state="readonly", width=15)
        period_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(controls_frame, text="Generate Analytics", 
                  command=self.generate_analytics).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(controls_frame, text="Export", 
                  command=self.export_analytics).pack(side=tk.LEFT, padx=(0, 5))
        
        # Analytics display
        analytics_display_frame = ttk.LabelFrame(analytics_frame, text="Business Analytics", padding="10")
        analytics_display_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        analytics_display_frame.columnconfigure(0, weight=1)
        analytics_display_frame.rowconfigure(0, weight=1)
        
        self.analytics_text = tk.Text(analytics_display_frame, font=('Courier', 10), wrap=tk.WORD)
        analytics_scrollbar = ttk.Scrollbar(analytics_display_frame, orient="vertical", command=self.analytics_text.yview)
        self.analytics_text.configure(yscrollcommand=analytics_scrollbar.set)
        
        self.analytics_text.grid(row=0, column=0, sticky="nsew")
        analytics_scrollbar.grid(row=0, column=1, sticky="ns")
        
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        time_label = ttk.Label(status_frame, text=datetime.now().strftime("%Y-%m-%d %H:%M"))
        time_label.grid(row=0, column=1, sticky="e")
        
    def generate_daily_report(self):
        """Generate daily report"""
        try:
            report_date = datetime.strptime(self.daily_date_var.get(), '%Y-%m-%d').date()
            
            # Generate cash management report
            cash_report = self.cash_manager.generate_daily_report(report_date)
            
            # Generate sales summary
            sales_summary = self.daily_reports.generate_daily_sales_summary(report_date)
            
            # Combine reports
            full_report = f"{cash_report}\n\n{sales_summary}"
            
            # Display report
            self.daily_report_text.delete(1.0, tk.END)
            self.daily_report_text.insert(1.0, full_report)
            
            self.status_label.config(text=f"Daily report generated for {report_date}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date (YYYY-MM-DD)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate daily report: {str(e)}")
            self.status_label.config(text="Failed to generate daily report")
            
    def generate_monthly_report(self):
        """Generate monthly report"""
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            report_type = self.monthly_report_type.get()
            
            report = self.generate_monthly_report_content(year, month, report_type)
            
            # Display report
            self.monthly_report_text.delete(1.0, tk.END)
            self.monthly_report_text.insert(1.0, report)
            
            self.status_label.config(text=f"Monthly report generated for {year}-{month:02d}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate monthly report: {str(e)}")
            self.status_label.config(text="Failed to generate monthly report")
            
    def generate_monthly_report_content(self, year, month, report_type):
        """Generate monthly report content"""
        # Get month date range
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        # Month name
        month_name = start_date.strftime("%B %Y")
        
        if report_type == "summary":
            return self.generate_monthly_summary(start_date, end_date, month_name)
        elif report_type == "detailed":
            return self.generate_monthly_detailed(start_date, end_date, month_name)
        elif report_type == "financial":
            return self.generate_monthly_financial(start_date, end_date, month_name)
        elif report_type == "vat":
            return self.generate_monthly_vat(start_date, end_date, month_name)
        else:
            return "Unknown report type"
            
    def generate_monthly_summary(self, start_date, end_date, month_name):
        """Generate monthly summary report"""
        try:
            # Sales summary
            sales_query = """
                SELECT 
                    COUNT(*) as total_transactions,
                    COALESCE(SUM(total_amount), 0) as total_sales,
                    COALESCE(SUM(vat_amount), 0) as total_vat,
                    COALESCE(SUM(CASE WHEN payment_method = 'cash' THEN total_amount ELSE 0 END), 0) as cash_sales,
                    COALESCE(SUM(CASE WHEN payment_method = 'card' THEN total_amount ELSE 0 END), 0) as card_sales,
                    COALESCE(SUM(CASE WHEN payment_method = 'mixed' THEN cash_amount ELSE 0 END), 0) as mixed_cash,
                    COALESCE(SUM(CASE WHEN payment_method = 'mixed' THEN card_amount ELSE 0 END), 0) as mixed_card,
                    COALESCE(AVG(total_amount), 0) as avg_transaction
                FROM sales 
                WHERE DATE(date_time) BETWEEN ? AND ? AND voided = 0
            """
            
            sales_result = self.db.execute_query(sales_query, (start_date.isoformat(), end_date.isoformat()))
            sales_data = sales_result[0] if sales_result else {}
            
            # Daily breakdown
            daily_query = """
                SELECT 
                    DATE(date_time) as sale_date,
                    COUNT(*) as transactions,
                    COALESCE(SUM(total_amount), 0) as daily_total
                FROM sales 
                WHERE DATE(date_time) BETWEEN ? AND ? AND voided = 0
                GROUP BY DATE(date_time)
                ORDER BY sale_date
            """
            
            daily_result = self.db.execute_query(daily_query, (start_date.isoformat(), end_date.isoformat()))
            
            # Product performance
            product_query = """
                SELECT 
                    p.name,
                    p.category,
                    SUM(si.quantity) as total_sold,
                    COALESCE(SUM(si.total_price), 0) as revenue
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.date_time) BETWEEN ? AND ? AND s.voided = 0
                GROUP BY p.id, p.name, p.category
                ORDER BY revenue DESC
                LIMIT 10
            """
            
            product_result = self.db.execute_query(product_query, (start_date.isoformat(), end_date.isoformat()))
            
            # Build report
            total_cash = float(sales_data.get('cash_sales', 0)) + float(sales_data.get('mixed_cash', 0))
            total_card = float(sales_data.get('card_sales', 0)) + float(sales_data.get('mixed_card', 0))
            
            report = f"""
============================================================
                 MONTHLY SUMMARY REPORT
                     {month_name}
============================================================

SALES OVERVIEW:
  Total Transactions:      {sales_data.get('total_transactions', 0):>10}
  Total Sales Revenue:     R{sales_data.get('total_sales', 0):>10.2f}
  Average Transaction:     R{sales_data.get('avg_transaction', 0):>10.2f}
  Total VAT Collected:     R{sales_data.get('total_vat', 0):>10.2f}

PAYMENT BREAKDOWN:
  Cash Payments:           R{total_cash:>10.2f} ({(total_cash/float(sales_data.get('total_sales', 1))*100):>5.1f}%)
  Card Payments:           R{total_card:>10.2f} ({(total_card/float(sales_data.get('total_sales', 1))*100):>5.1f}%)

DAILY PERFORMANCE:
"""
            
            for day in daily_result:
                day_name = datetime.strptime(day['sale_date'], '%Y-%m-%d').strftime('%a')
                report += f"  {day['sale_date']} ({day_name}): {day['transactions']:>3} transactions, R{day['daily_total']:>8.2f}\n"
                
            report += f"""
TOP SELLING PRODUCTS:
"""
            
            for i, product in enumerate(product_result, 1):
                report += f"  {i:>2}. {product['name']:<30} {product['total_sold']:>4} units  R{product['revenue']:>8.2f}\n"
                
            # Business insights
            working_days = len(daily_result)
            if working_days > 0:
                avg_daily_sales = float(sales_data.get('total_sales', 0)) / working_days
                avg_daily_transactions = float(sales_data.get('total_transactions', 0)) / working_days
                
                report += f"""
BUSINESS INSIGHTS:
  Working Days:            {working_days:>10}
  Average Daily Sales:     R{avg_daily_sales:>10.2f}
  Average Daily Trans:     {avg_daily_transactions:>10.1f}
  
============================================================
Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
============================================================
"""
            
            return report
            
        except Exception as e:
            return f"Error generating monthly summary: {str(e)}"
            
    def generate_monthly_detailed(self, start_date, end_date, month_name):
        """Generate detailed monthly report"""
        # This would include day-by-day breakdown, all products, etc.
        return f"Detailed Monthly Report for {month_name}\n(Feature coming soon)"
        
    def generate_monthly_financial(self, start_date, end_date, month_name):
        """Generate financial monthly report (P&L style)"""
        try:
            # Revenue
            revenue_query = """
                SELECT 
                    COALESCE(SUM(total_amount), 0) as total_revenue,
                    COALESCE(SUM(vat_amount), 0) as vat_collected
                FROM sales 
                WHERE DATE(date_time) BETWEEN ? AND ? AND voided = 0
            """
            
            revenue_result = self.db.execute_query(revenue_query, (start_date.isoformat(), end_date.isoformat()))
            revenue_data = revenue_result[0] if revenue_result else {}
            
            # Cost of goods sold
            cogs_query = """
                SELECT 
                    COALESCE(SUM(si.quantity * p.cost_price), 0) as total_cogs
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.date_time) BETWEEN ? AND ? AND s.voided = 0
            """
            
            cogs_result = self.db.execute_query(cogs_query, (start_date.isoformat(), end_date.isoformat()))
            cogs_data = cogs_result[0] if cogs_result else {}
            
            total_revenue = float(revenue_data.get('total_revenue', 0))
            total_cogs = float(cogs_data.get('total_cogs', 0))
            gross_profit = total_revenue - total_cogs
            gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            report = f"""
============================================================
                 FINANCIAL REPORT (P&L)
                     {month_name}
============================================================

REVENUE:
  Total Sales Revenue:     R{total_revenue:>10.2f}
  VAT Collected:           R{revenue_data.get('vat_collected', 0):>10.2f}

COST OF GOODS SOLD:
  Total COGS:              R{total_cogs:>10.2f}

GROSS PROFIT:
  Gross Profit:            R{gross_profit:>10.2f}
  Gross Margin:            {gross_margin:>9.1f}%

NOTES:
- This report shows gross profit only
- Operating expenses not included
- Based on product cost prices in system

============================================================
Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
============================================================
"""
            
            return report
            
        except Exception as e:
            return f"Error generating financial report: {str(e)}"
            
    def generate_monthly_vat(self, start_date, end_date, month_name):
        """Generate VAT report"""
        try:
            vat_query = """
                SELECT 
                    COALESCE(SUM(total_amount), 0) as total_sales_incl_vat,
                    COALESCE(SUM(vat_amount), 0) as total_vat,
                    COALESCE(SUM(total_amount - vat_amount), 0) as total_sales_excl_vat,
                    COUNT(*) as vat_transactions
                FROM sales 
                WHERE DATE(date_time) BETWEEN ? AND ? AND voided = 0
            """
            
            vat_result = self.db.execute_query(vat_query, (start_date.isoformat(), end_date.isoformat()))
            vat_data = vat_result[0] if vat_result else {}
            
            report = f"""
============================================================
                     VAT REPORT
                   {month_name}
============================================================

VAT SUMMARY:
  Total Sales (Inc VAT):   R{vat_data.get('total_sales_incl_vat', 0):>10.2f}
  Total Sales (Exc VAT):   R{vat_data.get('total_sales_excl_vat', 0):>10.2f}
  Total VAT Collected:     R{vat_data.get('total_vat', 0):>10.2f}
  VAT Transactions:        {vat_data.get('vat_transactions', 0):>10}

VAT RATE: 15% (Standard Rate)

This report is ready for SARS submission when required.

============================================================
Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
============================================================
"""
            
            return report
            
        except Exception as e:
            return f"Error generating VAT report: {str(e)}"
            
    def generate_analytics(self):
        """Generate business analytics"""
        try:
            period = self.analytics_period.get()
            
            # Determine date range
            if period == "last_7_days":
                end_date = date.today()
                start_date = end_date - timedelta(days=7)
                period_name = "Last 7 Days"
            elif period == "last_30_days":
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
                period_name = "Last 30 Days"
            elif period == "current_month":
                today = date.today()
                start_date = date(today.year, today.month, 1)
                end_date = today
                period_name = f"Current Month ({start_date.strftime('%B %Y')})"
            elif period == "last_month":
                today = date.today()
                if today.month == 1:
                    start_date = date(today.year - 1, 12, 1)
                    end_date = date(today.year - 1, 12, 31)
                else:
                    start_date = date(today.year, today.month - 1, 1)
                    _, last_day = monthrange(today.year, today.month - 1)
                    end_date = date(today.year, today.month - 1, last_day)
                period_name = f"Last Month ({start_date.strftime('%B %Y')})"
                
            analytics_report = self.generate_analytics_content(start_date, end_date, period_name)
            
            # Display analytics
            self.analytics_text.delete(1.0, tk.END)
            self.analytics_text.insert(1.0, analytics_report)
            
            self.status_label.config(text=f"Analytics generated for {period_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate analytics: {str(e)}")
            self.status_label.config(text="Failed to generate analytics")
            
    def generate_analytics_content(self, start_date, end_date, period_name):
        """Generate analytics content"""
        try:
            # Sales trends
            trends_query = """
                SELECT 
                    DATE(date_time) as sale_date,
                    COUNT(*) as transactions,
                    COALESCE(SUM(total_amount), 0) as daily_sales,
                    COALESCE(AVG(total_amount), 0) as avg_transaction
                FROM sales 
                WHERE DATE(date_time) BETWEEN ? AND ? AND voided = 0
                GROUP BY DATE(date_time)
                ORDER BY sale_date
            """
            
            trends_result = self.db.execute_query(trends_query, (start_date.isoformat(), end_date.isoformat()))
            
            # Category performance
            category_query = """
                SELECT 
                    p.category,
                    COUNT(*) as items_sold,
                    COALESCE(SUM(si.total_price), 0) as category_revenue,
                    COALESCE(AVG(si.total_price), 0) as avg_item_price
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.date_time) BETWEEN ? AND ? AND s.voided = 0
                GROUP BY p.category
                ORDER BY category_revenue DESC
            """
            
            category_result = self.db.execute_query(category_query, (start_date.isoformat(), end_date.isoformat()))
            
            # Peak hours
            hours_query = """
                SELECT 
                    CAST(strftime('%H', date_time) AS INTEGER) as hour,
                    COUNT(*) as transactions,
                    COALESCE(SUM(total_amount), 0) as hourly_sales
                FROM sales 
                WHERE DATE(date_time) BETWEEN ? AND ? AND voided = 0
                GROUP BY hour
                ORDER BY transactions DESC
                LIMIT 5
            """
            
            hours_result = self.db.execute_query(hours_query, (start_date.isoformat(), end_date.isoformat()))
            
            # Calculate totals and averages
            total_sales = sum(row['daily_sales'] for row in trends_result)
            total_transactions = sum(row['transactions'] for row in trends_result)
            working_days = len(trends_result)
            
            avg_daily_sales = total_sales / working_days if working_days > 0 else 0
            avg_daily_transactions = total_transactions / working_days if working_days > 0 else 0
            
            report = f"""
============================================================
                  BUSINESS ANALYTICS
                   {period_name}
============================================================

OVERVIEW:
  Period:                  {start_date} to {end_date}
  Working Days:            {working_days:>10}
  Total Sales:             R{total_sales:>10.2f}
  Total Transactions:      {total_transactions:>10}
  Average Daily Sales:     R{avg_daily_sales:>10.2f}
  Average Daily Trans:     {avg_daily_transactions:>10.1f}

CATEGORY PERFORMANCE:
"""
            
            for cat in category_result:
                cat_percentage = (float(cat['category_revenue']) / total_sales * 100) if total_sales > 0 else 0
                report += f"  {cat['category']:<15} {cat['items_sold']:>4} items  R{cat['category_revenue']:>8.2f} ({cat_percentage:>5.1f}%)\n"
                
            report += f"""
PEAK HOURS (by transaction count):
"""
            
            for hour_data in hours_result:
                hour = hour_data['hour']
                time_range = f"{hour:02d}:00-{hour:02d}:59"
                report += f"  {time_range}  {hour_data['transactions']:>4} trans  R{hour_data['hourly_sales']:>8.2f}\n"
                
            # Daily trend analysis
            if len(trends_result) > 1:
                sales_values = [row['daily_sales'] for row in trends_result]
                avg_sales = sum(sales_values) / len(sales_values)
                best_day = max(trends_result, key=lambda x: x['daily_sales'])
                worst_day = min(trends_result, key=lambda x: x['daily_sales'])
                
                report += f"""
DAILY TRENDS:
  Best Day:                {best_day['sale_date']} (R{best_day['daily_sales']:.2f})
  Worst Day:               {worst_day['sale_date']} (R{worst_day['daily_sales']:.2f})
  Average Daily:           R{avg_sales:.2f}
"""
            
            report += f"""
============================================================
Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
============================================================
"""
            
            return report
            
        except Exception as e:
            return f"Error generating analytics: {str(e)}"
            
    def refresh_cash_management(self):
        """Refresh cash management display"""
        try:
            # Get today's status
            today_summary = self.cash_manager.get_cash_summary()
            
            # Get recent history
            history = self.cash_manager.get_cash_history(7)
            
            # Build display
            cash_display = f"""
TODAY'S CASH SUMMARY ({date.today()}):
{'='*60}

Status: {'Day Started' if today_summary['day_started'] else 'Day Not Started'}
Opening Amount:     R{today_summary['opening_amount']:>10.2f}
Cash Sales:         R{today_summary['cash_sales']:>10.2f}
Card Sales:         R{today_summary['card_sales']:>10.2f}
Withdrawals:        R{today_summary['withdrawals']:>10.2f}
Expected Closing:   R{today_summary['expected_closing']:>10.2f}
"""
            
            if today_summary['reconciled']:
                cash_display += f"Actual Closing:     R{today_summary['actual_closing']:>10.2f}\n"
                cash_display += f"Variance:           R{today_summary['variance']:>10.2f}\n"
                cash_display += f"Status:             {'BALANCED' if abs(today_summary['variance']) < 0.01 else 'VARIANCE'}\n"
            else:
                cash_display += "Reconciliation:     PENDING\n"
                
            cash_display += f"\n\nCASH HISTORY (Last 7 Days):\n{'='*60}\n"
            
            for day_record in history:
                status = " Reconciled" if day_record.reconciled else "⏳ Pending"
                variance_text = ""
                if day_record.reconciled and day_record.variance is not None:
                    if abs(day_record.variance) < 0.01:
                        variance_text = " (Balanced)"
                    else:
                        variance_text = f" (Var: R{day_record.variance:+.2f})"
                        
                cash_display += f"{day_record.date}  Opening: R{day_record.opening_amount:>7.2f}  "
                cash_display += f"Sales: R{day_record.cash_sales:>7.2f}  {status}{variance_text}\n"
                
            # Update display
            self.cash_text.delete(1.0, tk.END)
            self.cash_text.insert(1.0, cash_display)
            
            # Update status
            today_status = self.cash_manager.get_cash_summary()
            status_text = "Day Started" if today_status['day_started'] else "Day Not Started"
            status_color = "green" if today_status['day_started'] else "red"
            self.cash_status_label.config(text=status_text, foreground=status_color)
            
            self.status_label.config(text="Cash management refreshed")
            
        except Exception as e:
            self.status_label.config(text=f"Error refreshing cash data: {str(e)}")
            
    def start_day_dialog(self):
        """Dialog to start the business day"""
        dialog = StartDayDialog(self.root, self.cash_manager, self.user)
        if dialog.result:
            self.refresh_cash_management()
            
    def record_withdrawal_dialog(self):
        """Dialog to record cash withdrawal"""
        dialog = WithdrawalDialog(self.root, self.cash_manager, self.user)
        if dialog.result:
            self.refresh_cash_management()
            
    def reconcile_till_dialog(self):
        """Dialog to reconcile till"""
        dialog = ReconciliationDialog(self.root, self.cash_manager, self.user)
        if dialog.result:
            self.refresh_cash_management()
            
    def set_current_month(self):
        """Set month/year to current month"""
        today = date.today()
        self.month_var.set(str(today.month))
        self.year_var.set(str(today.year))
        
    def set_last_month(self):
        """Set month/year to last month"""
        today = date.today()
        if today.month == 1:
            self.month_var.set("12")
            self.year_var.set(str(today.year - 1))
        else:
            self.month_var.set(str(today.month - 1))
            self.year_var.set(str(today.year))
            
    def export_daily_report(self):
        """Export daily report to file"""
        try:
            content = self.daily_report_text.get(1.0, tk.END)
            if not content.strip():
                messagebox.showwarning("Warning", "No report to export. Generate a report first.")
                return
                
            filename = f"daily_report_{self.daily_date_var.get()}.txt"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=filename
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.config(text=f"Report exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
            
    def export_monthly_report(self):
        """Export monthly report to file"""
        try:
            content = self.monthly_report_text.get(1.0, tk.END)
            if not content.strip():
                messagebox.showwarning("Warning", "No report to export. Generate a report first.")
                return
                
            filename = f"monthly_report_{self.year_var.get()}_{self.month_var.get():0>2}.txt"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=filename
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.config(text=f"Report exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
            
    def export_analytics(self):
        """Export analytics to file"""
        try:
            content = self.analytics_text.get(1.0, tk.END)
            if not content.strip():
                messagebox.showwarning("Warning", "No analytics to export. Generate analytics first.")
                return
                
            filename = f"analytics_{self.analytics_period.get()}_{date.today().isoformat()}.txt"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=filename
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.config(text=f"Analytics exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export analytics: {str(e)}")

# Dialog classes for cash management

class StartDayDialog:
    """Dialog for starting the business day"""
    
    def __init__(self, parent, cash_manager, user):
        self.parent = parent
        self.cash_manager = cash_manager
        self.user = user
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def setup_dialog(self):
        """Configure dialog window"""
        self.dialog.title("Start Business Day")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"350x200+{x}+{y}")
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Start Business Day", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Date info
        date_label = ttk.Label(main_frame, text=f"Date: {date.today()}")
        date_label.pack(pady=(0, 10))
        
        # Opening amount
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(amount_frame, text="Opening Till Amount (R):").pack(anchor='w')
        self.amount_var = tk.StringVar(value="100.00")
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var)
        amount_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Start Day", command=self.start_day).pack(side=tk.RIGHT)
        
        # Focus on amount entry
        amount_entry.focus()
        amount_entry.select_range(0, tk.END)
        
    def start_day(self):
        """Start the business day"""
        try:
            amount = float(self.amount_var.get())
            if amount < 0:
                messagebox.showerror("Error", "Opening amount must be positive")
                return
                
            success = self.cash_manager.start_day(amount, self.user.id)
            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to start day")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start day: {str(e)}")
            
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()

class WithdrawalDialog:
    """Dialog for recording cash withdrawal"""
    
    def __init__(self, parent, cash_manager, user):
        self.parent = parent
        self.cash_manager = cash_manager
        self.user = user
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def setup_dialog(self):
        """Configure dialog window"""
        self.dialog.title("Record Cash Withdrawal")
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"350x250+{x}+{y}")
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Record Cash Withdrawal", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Amount
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(amount_frame, text="Withdrawal Amount (R):").pack(anchor='w')
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var)
        amount_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Reason
        reason_frame = ttk.Frame(main_frame)
        reason_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(reason_frame, text="Reason:").pack(anchor='w')
        self.reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(reason_frame, textvariable=self.reason_var,
                                  values=["Personal use", "Business expense", "Bank deposit", "Other"])
        reason_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Record", command=self.record_withdrawal).pack(side=tk.RIGHT)
        
        # Focus on amount entry
        amount_entry.focus()
        
    def record_withdrawal(self):
        """Record the withdrawal"""
        try:
            amount = float(self.amount_var.get())
            reason = self.reason_var.get().strip()
            
            if amount <= 0:
                messagebox.showerror("Error", "Withdrawal amount must be positive")
                return
                
            if not reason:
                messagebox.showerror("Error", "Please provide a reason for the withdrawal")
                return
                
            success = self.cash_manager.record_withdrawal(amount, reason, self.user.id)
            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to record withdrawal")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record withdrawal: {str(e)}")
            
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()

class ReconciliationDialog:
    """Dialog for till reconciliation"""
    
    def __init__(self, parent, cash_manager, user):
        self.parent = parent
        self.cash_manager = cash_manager
        self.user = user
        self.result = None
        
        # Get current cash summary
        self.cash_summary = cash_manager.get_cash_summary()
        
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def setup_dialog(self):
        """Configure dialog window"""
        self.dialog.title("Till Reconciliation")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"400x350+{x}+{y}")
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Till Reconciliation", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Expected amounts
        expected_frame = ttk.LabelFrame(main_frame, text="Expected Amounts", padding="10")
        expected_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(expected_frame, text=f"Opening Amount: R{self.cash_summary['opening_amount']:.2f}").pack(anchor='w')
        ttk.Label(expected_frame, text=f"Cash Sales: R{self.cash_summary['cash_sales']:.2f}").pack(anchor='w')
        ttk.Label(expected_frame, text=f"Withdrawals: R{self.cash_summary['withdrawals']:.2f}").pack(anchor='w')
        ttk.Label(expected_frame, text=f"Expected Closing: R{self.cash_summary['expected_closing']:.2f}", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(5, 0))
        
        # Actual count
        actual_frame = ttk.LabelFrame(main_frame, text="Actual Till Count", padding="10")
        actual_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(actual_frame, text="Actual Cash Amount (R):").pack(anchor='w')
        self.actual_var = tk.StringVar(value=str(self.cash_summary['expected_closing']))
        actual_entry = ttk.Entry(actual_frame, textvariable=self.actual_var)
        actual_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Variance display
        self.variance_label = ttk.Label(actual_frame, text="Variance: R0.00", font=('Arial', 10, 'bold'))
        self.variance_label.pack(anchor='w')
        
        # Notes
        notes_frame = ttk.LabelFrame(main_frame, text="Notes", padding="10")
        notes_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.notes_var = tk.StringVar()
        notes_entry = ttk.Entry(notes_frame, textvariable=self.notes_var)
        notes_entry.pack(fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reconcile", command=self.reconcile).pack(side=tk.RIGHT)
        
        # Bind amount change to variance calculation
        actual_entry.bind('<KeyRelease>', self.calculate_variance)
        
        # Focus on actual amount entry
        actual_entry.focus()
        actual_entry.select_range(0, tk.END)
        
    def calculate_variance(self, event=None):
        """Calculate and display variance"""
        try:
            actual = float(self.actual_var.get())
            expected = self.cash_summary['expected_closing']
            variance = actual - expected
            
            color = "green" if abs(variance) < 0.01 else "red"
            self.variance_label.config(text=f"Variance: R{variance:+.2f}", foreground=color)
            
        except ValueError:
            self.variance_label.config(text="Variance: R0.00", foreground="black")
            
    def reconcile(self):
        """Perform till reconciliation"""
        try:
            actual = float(self.actual_var.get())
            notes = self.notes_var.get().strip()
            
            if actual < 0:
                messagebox.showerror("Error", "Actual amount cannot be negative")
                return
                
            result = self.cash_manager.reconcile_till(actual, self.user.id, notes)
            if result['success']:
                variance = result['variance']
                if abs(variance) < 0.01:
                    message = "Till balanced successfully!"
                elif variance > 0:
                    message = f"Till reconciled with R{variance:.2f} over"
                else:
                    message = f"Till reconciled with R{abs(variance):.2f} short"
                    
                messagebox.showinfo("Reconciliation Complete", message)
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to reconcile till")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reconcile till: {str(e)}")
            
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()

def main():
    """Main entry point for reports"""
    try:
        # Check if running standalone
        root = tk.Tk()
        root.withdraw()  # Hide root window
        
        # Initialize auth for testing
        from core.auth.authentication import ensure_demo_user, get_auth_manager
        ensure_demo_user()
        
        auth_manager = get_auth_manager()
        demo_user = auth_manager.authenticate_user("demo", "demo123")
        
        if demo_user:
            auth_manager.start_session(demo_user)
            app = ReportsWindow(user=demo_user)
            app.root.mainloop()
        else:
            messagebox.showerror("Error", "Failed to authenticate demo user")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start reports: {str(e)}")

if __name__ == "__main__":
    main()
