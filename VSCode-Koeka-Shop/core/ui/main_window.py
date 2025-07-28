"""
Main Dashboard Window for Tembie's Spaza Shop POS System
Provides the primary interface for accessing all system functions
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.products.management import ProductManager
from core.sales.transaction import TransactionManager
from config.settings import get_settings_manager
from config.module_registry import get_module_registry

class MainWindow:
    """Main application window and dashboard"""
    
    def __init__(self, user=None):
        self.root = tk.Tk()
        self.setup_window()
        
        # User authentication
        if user:
            self.current_user = user
            self.user = user  # Add this for compatibility
        else:
            # Fallback for backward compatibility
            self.current_user_id = 1
            from core.auth.authentication import get_auth_manager
            auth_manager = get_auth_manager()
            self.current_user = auth_manager.get_current_user()
            if not self.current_user:
                # Create dummy user object for testing
                from core.auth.authentication import User
                self.current_user = User(1, "demo", "Demo User", "admin")
            self.user = self.current_user  # Add this for compatibility
        
        # Initialize managers
        self.product_manager = ProductManager()
        self.transaction_manager = TransactionManager()
        self.settings_manager = get_settings_manager()
        self.module_registry = get_module_registry()
        
        self.create_widgets()
        self.update_dashboard()
    
    def setup_window(self):
        """Configure main window properties"""
        self.root.title("Tembie's Spaza Shop - POS System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for better visibility
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Action.TButton', font=('Arial', 11, 'bold'), padding=10)
        style.configure('Small.TButton', font=('Arial', 9), padding=5)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def create_widgets(self):
        """Create and layout all widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Quick Actions Panel
        self.create_quick_actions(main_frame)
        
        # Dashboard Content
        self.create_dashboard_content(main_frame)
        
        # Status Bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create header with shop name, current user, and current time"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Shop name
        settings = self.settings_manager.get_settings()
        shop_label = ttk.Label(header_frame, text=settings.shop_name, style='Title.TLabel')
        shop_label.grid(row=0, column=0, sticky="w")
        
        # User info
        user_info = f"👤 {self.current_user.full_name} ({self.current_user.role})"
        self.user_label = ttk.Label(header_frame, text=user_info, style='Status.TLabel')
        self.user_label.grid(row=1, column=0, sticky="w")
        
        # Current time
        self.time_label = ttk.Label(header_frame, text="", style='Status.TLabel')
        self.time_label.grid(row=0, column=1, sticky="e")
        
        # Logout button
        ttk.Button(header_frame, text="🚪 Logout", command=self.logout, 
                  style='Small.TButton').grid(row=1, column=1, sticky="e")
        
        # Update time
        self.update_time()
    
    def create_quick_actions(self, parent):
        """Create quick action buttons with role-based access"""
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding="10")
        actions_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        from core.auth.authentication import get_auth_manager
        auth_manager = get_auth_manager()
        
        # Action buttons with permission checks
        buttons = []
        
        # Sales - Available to all users
        if auth_manager.can_access_function('sales'):
            buttons.append(("🛒 New Sale", self.open_sales_screen))
        
        # Product Management - Admin and Stock Manager only
        if auth_manager.can_access_function('product_management'):
            buttons.append(("📦 Manage Products", self.open_product_management))
        
        # Reports - Admin only
        if auth_manager.can_access_function('reports'):
            buttons.append(("📊 View Reports", self.show_reports))
        
        # Settings - Admin only
        if auth_manager.can_access_function('settings'):
            buttons.append(("⚙️ Settings", self.open_settings))
        
        # Create buttons
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(actions_frame, text=text, command=command, style='Action.TButton')
            btn.grid(row=0, column=i, padx=5, sticky="ew")
            actions_frame.columnconfigure(i, weight=1)
    
    def create_dashboard_content(self, parent):
        """Create main dashboard content area"""
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 20))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Statistics
        self.create_statistics_panel(content_frame)
        
        # Right panel - Recent Activity
        self.create_activity_panel(content_frame)
    
    def create_statistics_panel(self, parent):
        """Create statistics display panel"""
        stats_frame = ttk.LabelFrame(parent, text="Today's Summary", padding="10")
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Statistics labels
        self.stats_labels = {}
        stats = [
            ("sales_count", "Transactions:", "0"),
            ("sales_total", "Total Sales:", "R 0.00"),
            ("items_sold", "Items Sold:", "0"),
            ("avg_sale", "Average Sale:", "R 0.00"),
        ]
        
        for i, (key, label, default) in enumerate(stats):
            ttk.Label(stats_frame, text=label, style='Heading.TLabel').grid(
                row=i, column=0, sticky="w", pady=2
            )
            self.stats_labels[key] = ttk.Label(stats_frame, text=default, style='Status.TLabel')
            self.stats_labels[key].grid(row=i, column=1, sticky="e", pady=2, padx=(10, 0))
        
        # Configure column weights
        stats_frame.columnconfigure(1, weight=1)
        
        # Low stock alerts
        ttk.Separator(stats_frame, orient='horizontal').grid(
            row=len(stats), column=0, columnspan=2, sticky="ew", pady=10
        )
        
        ttk.Label(stats_frame, text="Stock Alerts:", style='Heading.TLabel').grid(
            row=len(stats) + 1, column=0, columnspan=2, sticky="w", pady=(5, 2)
        )
        
        # Stock alerts listbox
        self.stock_alerts_frame = ttk.Frame(stats_frame)
        self.stock_alerts_frame.grid(row=len(stats) + 2, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        self.stock_listbox = tk.Listbox(self.stock_alerts_frame, height=6, font=('Arial', 9))
        stock_scrollbar = ttk.Scrollbar(self.stock_alerts_frame, orient="vertical", command=self.stock_listbox.yview)
        self.stock_listbox.configure(yscrollcommand=stock_scrollbar.set)
        
        self.stock_listbox.grid(row=0, column=0, sticky="nsew")
        stock_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.stock_alerts_frame.columnconfigure(0, weight=1)
        self.stock_alerts_frame.rowconfigure(0, weight=1)
    
    def create_activity_panel(self, parent):
        """Create recent activity panel"""
        activity_frame = ttk.LabelFrame(parent, text="Recent Sales", padding="10")
        activity_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        activity_frame.columnconfigure(0, weight=1)
        activity_frame.rowconfigure(1, weight=1)
        
        # Recent sales treeview
        columns = ("Time", "Transaction", "Items", "Total", "Payment")
        self.sales_tree = ttk.Treeview(activity_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.sales_tree.heading("Time", text="Time")
        self.sales_tree.heading("Transaction", text="Transaction")
        self.sales_tree.heading("Items", text="Items")
        self.sales_tree.heading("Total", text="Total")
        self.sales_tree.heading("Payment", text="Payment")
        
        self.sales_tree.column("Time", width=80)
        self.sales_tree.column("Transaction", width=120)
        self.sales_tree.column("Items", width=60)
        self.sales_tree.column("Total", width=80)
        self.sales_tree.column("Payment", width=80)
        
        # Scrollbar for treeview
        sales_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        
        self.sales_tree.grid(row=1, column=0, sticky="nsew")
        sales_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Refresh button
        refresh_btn = ttk.Button(activity_frame, text="🔄 Refresh", command=self.update_dashboard)
        refresh_btn.grid(row=2, column=0, pady=(10, 0), sticky="ew")
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        status_frame.columnconfigure(1, weight=1)
        
        # Status message
        self.status_label = ttk.Label(status_frame, text="System ready", style='Status.TLabel')
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Connection status
        self.connection_label = ttk.Label(status_frame, text="📁 Database: Connected", style='Status.TLabel')
        self.connection_label.grid(row=0, column=1, sticky="e")
    
    def update_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # Update every second
    
    def update_dashboard(self):
        """Update dashboard statistics and recent sales"""
        try:
            self.update_statistics()
            self.update_recent_sales()
            self.update_stock_alerts()
            self.status_label.config(text="Dashboard updated successfully")
        except Exception as e:
            self.status_label.config(text=f"Error updating dashboard: {str(e)}")
    
    def update_statistics(self):
        """Update today's statistics"""
        from core.database.connection import get_db_manager
        
        db = get_db_manager()
        today = datetime.now().date()
        
        # Get today's sales statistics
        query = """
            SELECT 
                COUNT(*) as transaction_count,
                COALESCE(SUM(total_amount), 0) as total_sales,
                COALESCE(SUM((SELECT SUM(quantity) FROM sale_items WHERE sale_id = sales.id)), 0) as items_sold
            FROM sales 
            WHERE DATE(date_time) = ? AND voided = 0
        """
        
        result = db.execute_query(query, (today.isoformat(),))
        
        if result:
            row = result[0]
            sales_count = row['transaction_count']
            total_sales = float(row['total_sales'])
            items_sold = row['items_sold']
            avg_sale = total_sales / sales_count if sales_count > 0 else 0
            
            self.stats_labels['sales_count'].config(text=str(sales_count))
            self.stats_labels['sales_total'].config(text=f"R {total_sales:.2f}")
            self.stats_labels['items_sold'].config(text=str(items_sold))
            self.stats_labels['avg_sale'].config(text=f"R {avg_sale:.2f}")
    
    def update_recent_sales(self):
        """Update recent sales list"""
        from core.database.connection import get_db_manager
        
        db = get_db_manager()
        today = datetime.now().date()
        
        query = """
            SELECT s.date_time, s.transaction_ref, s.total_amount, s.payment_method,
                   COUNT(si.id) as item_count
            FROM sales s
            LEFT JOIN sale_items si ON s.id = si.sale_id
            WHERE DATE(s.date_time) = ? AND s.voided = 0
            GROUP BY s.id
            ORDER BY s.date_time DESC
            LIMIT 20
        """
        
        results = db.execute_query(query, (today.isoformat(),))
        
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Add new items
        for row in results:
            time_str = row['date_time'].split(' ')[1][:5]  # Extract HH:MM
            self.sales_tree.insert("", "end", values=(
                time_str,
                row['transaction_ref'],
                row['item_count'],
                f"R{row['total_amount']:.2f}",
                row['payment_method'].upper()
            ))
    
    def update_stock_alerts(self):
        """Update stock alerts list"""
        low_stock = self.product_manager.get_low_stock_products()
        
        # Clear existing alerts
        self.stock_listbox.delete(0, tk.END)
        
        if not low_stock:
            self.stock_listbox.insert(tk.END, "✅ All products have adequate stock")
        else:
            for product in low_stock:
                status = "🔴 OUT" if product.current_stock == 0 else "⚠️ LOW"
                alert = f"{status} {product.name} ({product.current_stock}/{product.min_stock})"
                self.stock_listbox.insert(tk.END, alert)
    
    def open_sales_screen(self):
        """Open the sales screen"""
        from core.ui.sales_screen import SalesScreen
        sales_window = SalesScreen(self.root, self.current_user.id)
        
        # Refresh dashboard when sales window is closed
        def on_close():
            self.update_dashboard()
        
        sales_window.root.protocol("WM_DELETE_WINDOW", lambda: [sales_window.root.destroy(), on_close()])
    
    def logout(self):
        """Logout current user"""
        from core.auth.authentication import get_auth_manager
        
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            auth_manager = get_auth_manager()
            auth_manager.logout()
            self.root.destroy()
    
    def open_product_management(self):
        """Open product management window"""
        try:
            from .product_management import ProductManagementWindow
            ProductManagementWindow(parent=self.root, user=self.user)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Product Management: {str(e)}")
    
    def show_reports(self):
        """Show reports window"""
        try:
            from .reports_window import ReportsWindow
            ReportsWindow(parent=self.root, user=self.user)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Reports: {str(e)}")
    
    def open_settings(self):
        """Open settings window"""
        try:
            from .settings_window import SettingsWindow
            SettingsWindow(parent=self.root, user=self.user)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Settings: {str(e)}")
    
    def reconcile_cash(self):
        """Open cash reconciliation interface"""
        try:
            from .reports_window import ReportsWindow
            # Open reports window with cash reconciliation tab selected
            reports_window = ReportsWindow(parent=self.root, user=self.user)
            # Switch to cash reconciliation tab
            reports_window.notebook.select(1)  # Cash management tab
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Cash Reconciliation: {str(e)}")
    
    def show_coming_soon(self, feature):
        """Show coming soon message"""
        messagebox.showinfo(
            "Coming Soon", 
            f"{feature} interface is coming in the next development phase.\n\n"
            f"Current functionality is available through the CLI demo:\n"
            f"python demo_cli.py"
        )
    
    def run(self):
        """Start the main application loop"""
        self.root.mainloop()

def main():
    """Main entry point for GUI application"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
