"""
Product Management GUI for Tembie's Spaza Shop POS System
Interface for adding, editing, and managing product catalog
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
from datetime import datetime, date
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.products.management import ProductManager, Product
from core.auth.authentication import get_auth_manager
from utils.validation import validate_price, validate_stock_quantity

class ProductManagementWindow:
    """Product management interface"""
    
    def __init__(self, parent=None, user=None):
        self.parent = parent
        self.user = user or get_auth_manager().get_current_user()
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        
        # Initialize managers
        self.product_manager = ProductManager()
        self.auth_manager = get_auth_manager()
        
        # Current selection
        self.selected_product_id = None
        
        self.setup_window()
        self.create_widgets()
        self.refresh_product_list()
        
    def setup_window(self):
        """Configure window properties"""
        self.root.title("Product Management - Tembie's Spaza Shop")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Configure style
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10, 'bold'), padding=8)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1200x700+{x}+{y}")
        
    def create_widgets(self):
        """Create and layout all widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=2)  # Product list
        main_frame.columnconfigure(1, weight=1)  # Product details
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Product list panel
        self.create_product_list_panel(main_frame)
        
        # Product details panel
        self.create_product_details_panel(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create header with title and main actions"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text=" Product Management", style='Header.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        # User info
        user_info = f" {self.user.full_name} ({self.user.role})"
        user_label = ttk.Label(header_frame, text=user_info)
        user_label.grid(row=0, column=1, sticky="e")
        
        # Action buttons
        actions_frame = ttk.Frame(header_frame)
        actions_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(actions_frame, text=" Add Product", command=self.add_product, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="️ Edit Product", command=self.edit_product, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="️ Delete Product", command=self.delete_product, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text=" Stock Adjustment", command=self.adjust_stock, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text=" Refresh", command=self.refresh_product_list, 
                  style='Action.TButton').pack(side=tk.RIGHT)
        
    def create_product_list_panel(self, parent):
        """Create product list with search and filters"""
        list_frame = ttk.LabelFrame(parent, text="Product Catalog", padding="10")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(2, weight=1)
        
        # Search and filter
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Button(search_frame, text="", command=self.search_products).grid(row=0, column=2)
        
        # Category filter
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, 
                                    values=["All", "Food", "Household", "Sweets", "Cooldrinks", "Other"],
                                    state="readonly", width=15)
        category_combo.pack(side=tk.LEFT, padx=(5, 10))
        category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # Low stock filter
        self.show_low_stock_var = tk.BooleanVar()
        low_stock_check = ttk.Checkbutton(filter_frame, text="Show Low Stock Only", 
                                        variable=self.show_low_stock_var, 
                                        command=self.on_filter_change)
        low_stock_check.pack(side=tk.LEFT)
        
        # Product list
        columns = ("ID", "Name", "Barcode", "Category", "Stock", "Min Stock", "Sell Price", "Status")
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Name", text="Product Name")
        self.product_tree.heading("Barcode", text="Barcode")
        self.product_tree.heading("Category", text="Category")
        self.product_tree.heading("Stock", text="Stock")
        self.product_tree.heading("Min Stock", text="Min")
        self.product_tree.heading("Sell Price", text="Price")
        self.product_tree.heading("Status", text="Status")
        
        self.product_tree.column("ID", width=50)
        self.product_tree.column("Name", width=250)
        self.product_tree.column("Barcode", width=120)
        self.product_tree.column("Category", width=100)
        self.product_tree.column("Stock", width=70)
        self.product_tree.column("Min Stock", width=50)
        self.product_tree.column("Sell Price", width=80)
        self.product_tree.column("Status", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.grid(row=2, column=0, sticky="nsew")
        scrollbar.grid(row=2, column=1, sticky="ns")
        
        # Bind selection
        self.product_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        self.product_tree.bind('<Double-1>', self.on_product_double_click)
        
    def create_product_details_panel(self, parent):
        """Create product details and actions panel"""
        details_frame = ttk.LabelFrame(parent, text="Product Details", padding="10")
        details_frame.grid(row=1, column=1, sticky="nsew")
        details_frame.columnconfigure(1, weight=1)
        
        # Product details display
        self.details_text = tk.Text(details_frame, height=15, width=40, wrap=tk.WORD, 
                                  state=tk.DISABLED, font=('Arial', 10))
        details_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        details_scrollbar.grid(row=0, column=2, sticky="ns", pady=(0, 10))
        
        # Quick actions
        actions_label = ttk.Label(details_frame, text="Quick Actions:", font=('Arial', 11, 'bold'))
        actions_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        # Stock adjustment section
        stock_frame = ttk.LabelFrame(details_frame, text="Stock Adjustment", padding="5")
        stock_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        stock_frame.columnconfigure(1, weight=1)
        
        ttk.Label(stock_frame, text="Quantity:").grid(row=0, column=0, sticky="w")
        self.stock_adjust_var = tk.StringVar()
        stock_entry = ttk.Entry(stock_frame, textvariable=self.stock_adjust_var, width=10)
        stock_entry.grid(row=0, column=1, sticky="w", padx=(5, 5))
        
        ttk.Label(stock_frame, text="Reason:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.stock_reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(stock_frame, textvariable=self.stock_reason_var,
                                  values=["Stock addition", "Damage", "Theft", "Spoilage", "Count correction"],
                                  width=15)
        reason_combo.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
        
        ttk.Button(stock_frame, text="Apply", command=self.quick_stock_adjust).grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Stock movements history
        history_label = ttk.Label(details_frame, text="Recent Stock Movements:", font=('Arial', 11, 'bold'))
        history_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        # Stock movements list
        move_columns = ("Date", "Type", "Qty", "User")
        self.movements_tree = ttk.Treeview(details_frame, columns=move_columns, show="headings", height=8)
        
        for col in move_columns:
            self.movements_tree.heading(col, text=col)
            self.movements_tree.column(col, width=80)
        
        move_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.movements_tree.yview)
        self.movements_tree.configure(yscrollcommand=move_scrollbar.set)
        
        self.movements_tree.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        move_scrollbar.grid(row=4, column=2, sticky="ns", pady=(0, 10))
        
        details_frame.rowconfigure(4, weight=1)
        
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.product_count_label = ttk.Label(status_frame, text="")
        self.product_count_label.grid(row=0, column=1, sticky="e")
        
    def on_search_change(self, event=None):
        """Handle search text change"""
        # Auto-search after 500ms delay
        self.root.after_cancel(getattr(self, '_search_timer', None))
        self._search_timer = self.root.after(500, self.search_products)
        
    def on_category_change(self, event=None):
        """Handle category filter change"""
        self.search_products()
        
    def on_filter_change(self):
        """Handle filter checkbox change"""
        self.search_products()
        
    def search_products(self):
        """Search and filter products"""
        try:
            search_term = self.search_var.get().strip()
            category = self.category_var.get()
            show_low_stock = self.show_low_stock_var.get()
            
            if show_low_stock:
                products = self.product_manager.get_low_stock_products()
            else:
                products = self.product_manager.search_products(search_term) if search_term else self.product_manager.get_all_products()
            
            # Apply category filter
            if category != "All":
                products = [p for p in products if p.category == category]
            
            self.update_product_list(products)
            self.status_label.config(text=f"Found {len(products)} products")
            
        except Exception as e:
            self.status_label.config(text=f"Search error: {str(e)}")
            
    def refresh_product_list(self):
        """Refresh the complete product list"""
        try:
            products = self.product_manager.get_all_products()
            self.update_product_list(products)
            self.status_label.config(text="Product list refreshed")
            
        except Exception as e:
            self.status_label.config(text=f"Refresh error: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh product list: {str(e)}")
            
    def update_product_list(self, products):
        """Update the product list display"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
            
        # Add products
        for product in products:
            # Determine status
            if product.current_stock == 0:
                status = "OUT"
                tags = ('out_of_stock',)
            elif product.current_stock <= product.min_stock:
                status = "LOW"
                tags = ('low_stock',)
            else:
                status = "OK"
                tags = ('normal',)
                
            self.product_tree.insert("", "end", values=(
                product.id,
                product.name,
                product.barcode or "",
                product.category,
                product.current_stock,
                product.min_stock,
                f"R{product.sell_price:.2f}",
                status
            ), tags=tags)
            
        # Configure row colors
        self.product_tree.tag_configure('out_of_stock', background='#ffebee')
        self.product_tree.tag_configure('low_stock', background='#fff3e0')
        self.product_tree.tag_configure('normal', background='white')
        
        # Update count
        self.product_count_label.config(text=f"{len(products)} products")
        
    def on_product_select(self, event=None):
        """Handle product selection"""
        selection = self.product_tree.selection()
        if selection:
            item = self.product_tree.item(selection[0])
            self.selected_product_id = int(item['values'][0])
            self.show_product_details(self.selected_product_id)
        else:
            self.selected_product_id = None
            self.clear_product_details()
            
    def on_product_double_click(self, event=None):
        """Handle double-click on product"""
        if self.selected_product_id:
            self.edit_product()
            
    def show_product_details(self, product_id):
        """Show detailed information for selected product"""
        try:
            product = self.product_manager.get_product_by_id(product_id)
            if not product:
                self.clear_product_details()
                return
                
            # Format product details
            details = f"""Product Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: {product.name}
Barcode: {product.barcode or 'Not set'}
Category: {product.category}

Pricing:
  Cost Price: R{product.cost_price:.2f}
  Sell Price: R{product.sell_price:.2f}
  Margin: R{product.sell_price - product.cost_price:.2f} ({((product.sell_price - product.cost_price) / product.cost_price * 100):.1f}%)

Stock Levels:
  Current Stock: {product.current_stock}
  Monthly Target: {product.monthly_stock}
  Minimum Level: {product.min_stock}
  Status: {'OUT OF STOCK' if product.current_stock == 0 else 'LOW STOCK' if product.current_stock <= product.min_stock else 'ADEQUATE'}

VAT Information:
  VAT Rate: {product.vat_rate}%
  VAT Inclusive: {'Yes' if product.vat_inclusive else 'No'}

Dates:
  Created: {product.created_at.strftime('%Y-%m-%d %H:%M') if product.created_at else 'Unknown'}
  Updated: {product.updated_at.strftime('%Y-%m-%d %H:%M') if product.updated_at else 'Never'}"""

            if product.expiry_date:
                days_to_expiry = (product.expiry_date - date.today()).days
                expiry_status = "EXPIRED" if days_to_expiry < 0 else f"{days_to_expiry} days" if days_to_expiry < 30 else "OK"
                details += f"\n  Expiry Date: {product.expiry_date} ({expiry_status})"
                
            # Update details display
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, details)
            self.details_text.config(state=tk.DISABLED)
            
            # Load stock movements
            self.load_stock_movements(product_id)
            
        except Exception as e:
            self.status_label.config(text=f"Error loading details: {str(e)}")
            
    def clear_product_details(self):
        """Clear product details display"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, "Select a product to view details")
        self.details_text.config(state=tk.DISABLED)
        
        # Clear movements
        for item in self.movements_tree.get_children():
            self.movements_tree.delete(item)
            
    def load_stock_movements(self, product_id):
        """Load recent stock movements for product"""
        try:
            movements = self.product_manager.get_stock_movements(product_id, limit=10)
            
            # Clear existing movements
            for item in self.movements_tree.get_children():
                self.movements_tree.delete(item)
                
            # Add movements
            for movement in movements:
                date_str = movement.get('date_time', '').split(' ')[0]  # Extract date part
                move_type = movement.get('movement_type', '')
                quantity = movement.get('quantity_change', 0)
                user_name = movement.get('user_name', 'Unknown')
                
                self.movements_tree.insert("", "end", values=(
                    date_str,
                    move_type.title(),
                    f"{quantity:+}",
                    user_name
                ))
                
        except Exception as e:
            self.status_label.config(text=f"Error loading movements: {str(e)}")
            
    def add_product(self):
        """Open add product dialog"""
        dialog = ProductEditDialog(self.root, self.product_manager, self.user)
        if dialog.result:
            self.refresh_product_list()
            self.status_label.config(text="Product added successfully")
            
    def edit_product(self):
        """Open edit product dialog"""
        if not self.selected_product_id:
            messagebox.showwarning("No Selection", "Please select a product to edit")
            return
            
        product = self.product_manager.get_product_by_id(self.selected_product_id)
        if product:
            dialog = ProductEditDialog(self.root, self.product_manager, self.user, product)
            if dialog.result:
                self.refresh_product_list()
                self.show_product_details(self.selected_product_id)
                self.status_label.config(text="Product updated successfully")
                
    def delete_product(self):
        """Delete selected product"""
        if not self.selected_product_id:
            messagebox.showwarning("No Selection", "Please select a product to delete")
            return
            
        product = self.product_manager.get_product_by_id(self.selected_product_id)
        if not product:
            return
            
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete '{product.name}'?\n\n"
                             f"This action cannot be undone."):
            try:
                success = self.product_manager.delete_product(self.selected_product_id, self.user.id)
                if success:
                    self.refresh_product_list()
                    self.clear_product_details()
                    self.status_label.config(text="Product deleted successfully")
                else:
                    messagebox.showerror("Error", "Failed to delete product")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
                
    def adjust_stock(self):
        """Open stock adjustment dialog"""
        if not self.selected_product_id:
            messagebox.showwarning("No Selection", "Please select a product for stock adjustment")
            return
            
        dialog = StockAdjustmentDialog(self.root, self.product_manager, self.user, self.selected_product_id)
        if dialog.result:
            self.refresh_product_list()
            self.show_product_details(self.selected_product_id)
            self.status_label.config(text="Stock adjusted successfully")
            
    def quick_stock_adjust(self):
        """Quick stock adjustment from details panel"""
        if not self.selected_product_id:
            return
            
        try:
            quantity_str = self.stock_adjust_var.get().strip()
            reason = self.stock_reason_var.get().strip()
            
            if not quantity_str or not reason:
                messagebox.showwarning("Missing Information", "Please enter quantity and reason")
                return
                
            quantity = int(quantity_str)
            movement_type = "addition" if quantity > 0 else "adjustment"
            
            success = self.product_manager.adjust_stock(
                self.selected_product_id, quantity, movement_type, self.user.id, reason
            )
            
            if success:
                # Clear form
                self.stock_adjust_var.set("")
                self.stock_reason_var.set("")
                
                # Refresh displays
                self.refresh_product_list()
                self.show_product_details(self.selected_product_id)
                self.status_label.config(text=f"Stock adjusted by {quantity:+}")
            else:
                messagebox.showerror("Error", "Failed to adjust stock")
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity number")
        except Exception as e:
            messagebox.showerror("Error", f"Stock adjustment failed: {str(e)}")

class ProductEditDialog:
    """Dialog for adding/editing products"""
    
    def __init__(self, parent, product_manager, user, product=None):
        self.parent = parent
        self.product_manager = product_manager
        self.user = user
        self.product = product  # None for new product
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        
        if product:
            self.load_product_data()
            
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def setup_dialog(self):
        """Configure dialog window"""
        title = "Edit Product" if self.product else "Add Product"
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = "Edit Product" if self.product else "Add New Product"
        title_label = ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Product form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        form_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Product name
        ttk.Label(form_frame, text="Product Name *:").grid(row=row, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Barcode
        ttk.Label(form_frame, text="Barcode:").grid(row=row, column=0, sticky="w", pady=5)
        self.barcode_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.barcode_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Category
        ttk.Label(form_frame, text="Category *:").grid(row=row, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var,
                                    values=["Food", "Household", "Sweets", "Cooldrinks", "Other"],
                                    state="readonly", width=38)
        category_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Cost price
        ttk.Label(form_frame, text="Cost Price (R) *:").grid(row=row, column=0, sticky="w", pady=5)
        self.cost_price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.cost_price_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Sell price
        ttk.Label(form_frame, text="Sell Price (R) *:").grid(row=row, column=0, sticky="w", pady=5)
        self.sell_price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.sell_price_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Current stock
        ttk.Label(form_frame, text="Current Stock *:").grid(row=row, column=0, sticky="w", pady=5)
        self.current_stock_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.current_stock_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Monthly stock
        ttk.Label(form_frame, text="Monthly Target Stock:").grid(row=row, column=0, sticky="w", pady=5)
        self.monthly_stock_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.monthly_stock_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Minimum stock
        ttk.Label(form_frame, text="Minimum Stock Level *:").grid(row=row, column=0, sticky="w", pady=5)
        self.min_stock_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.min_stock_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # VAT rate
        ttk.Label(form_frame, text="VAT Rate (%):").grid(row=row, column=0, sticky="w", pady=5)
        self.vat_rate_var = tk.StringVar(value="15.0")
        ttk.Entry(form_frame, textvariable=self.vat_rate_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # VAT inclusive
        ttk.Label(form_frame, text="VAT Inclusive:").grid(row=row, column=0, sticky="w", pady=5)
        self.vat_inclusive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, variable=self.vat_inclusive_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Expiry date (optional)
        ttk.Label(form_frame, text="Expiry Date (YYYY-MM-DD):").grid(row=row, column=0, sticky="w", pady=5)
        self.expiry_date_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.expiry_date_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Required fields note
        note_label = ttk.Label(form_frame, text="* Required fields", font=('Arial', 9), foreground='red')
        note_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        save_text = "Update" if self.product else "Create"
        ttk.Button(button_frame, text=save_text, command=self.save).pack(side=tk.RIGHT)
        
        # Focus on name field
        name_entry.focus()
        
    def load_product_data(self):
        """Load existing product data into form"""
        if not self.product:
            return
            
        self.name_var.set(self.product.name)
        self.barcode_var.set(self.product.barcode or "")
        self.category_var.set(self.product.category)
        self.cost_price_var.set(str(self.product.cost_price))
        self.sell_price_var.set(str(self.product.sell_price))
        self.current_stock_var.set(str(self.product.current_stock))
        self.monthly_stock_var.set(str(self.product.monthly_stock))
        self.min_stock_var.set(str(self.product.min_stock))
        self.vat_rate_var.set(str(self.product.vat_rate))
        self.vat_inclusive_var.set(self.product.vat_inclusive)
        
        if self.product.expiry_date:
            self.expiry_date_var.set(str(self.product.expiry_date))
            
    def validate_form(self):
        """Validate form data"""
        errors = []
        
        # Required fields
        if not self.name_var.get().strip():
            errors.append("Product name is required")
            
        if not self.category_var.get():
            errors.append("Category is required")
            
        # Numeric validations
        try:
            cost_price = float(self.cost_price_var.get())
            if cost_price < 0:
                errors.append("Cost price must be positive")
        except ValueError:
            errors.append("Cost price must be a valid number")
            
        try:
            sell_price = float(self.sell_price_var.get())
            if sell_price < 0:
                errors.append("Sell price must be positive")
        except ValueError:
            errors.append("Sell price must be a valid number")
            
        try:
            current_stock = int(self.current_stock_var.get())
            if current_stock < 0:
                errors.append("Current stock must be non-negative")
        except ValueError:
            errors.append("Current stock must be a valid integer")
            
        try:
            min_stock = int(self.min_stock_var.get())
            if min_stock < 0:
                errors.append("Minimum stock must be non-negative")
        except ValueError:
            errors.append("Minimum stock must be a valid integer")
            
        # Optional fields
        if self.monthly_stock_var.get().strip():
            try:
                monthly_stock = int(self.monthly_stock_var.get())
                if monthly_stock < 0:
                    errors.append("Monthly stock must be non-negative")
            except ValueError:
                errors.append("Monthly stock must be a valid integer")
                
        # Expiry date
        if self.expiry_date_var.get().strip():
            try:
                datetime.strptime(self.expiry_date_var.get(), '%Y-%m-%d')
            except ValueError:
                errors.append("Expiry date must be in YYYY-MM-DD format")
                
        return errors
        
    def save(self):
        """Save product data"""
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
            
        try:
            # Create product object
            product_data = Product(
                id=self.product.id if self.product else None,
                name=self.name_var.get().strip(),
                barcode=self.barcode_var.get().strip() or None,
                category=self.category_var.get(),
                cost_price=float(self.cost_price_var.get()),
                sell_price=float(self.sell_price_var.get()),
                current_stock=int(self.current_stock_var.get()),
                monthly_stock=int(self.monthly_stock_var.get()) if self.monthly_stock_var.get().strip() else 0,
                min_stock=int(self.min_stock_var.get()),
                vat_rate=float(self.vat_rate_var.get()) if self.vat_rate_var.get().strip() else 15.0,
                vat_inclusive=self.vat_inclusive_var.get(),
                expiry_date=datetime.strptime(self.expiry_date_var.get(), '%Y-%m-%d').date() if self.expiry_date_var.get().strip() else None
            )
            
            if self.product:
                # Update existing product
                success = self.product_manager.update_product(product_data, self.user.id)
            else:
                # Create new product
                product_id = self.product_manager.create_product(product_data, self.user.id)
                success = product_id is not None
                
            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save product")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {str(e)}")
            
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()

class StockAdjustmentDialog:
    """Dialog for stock adjustments"""
    
    def __init__(self, parent, product_manager, user, product_id):
        self.parent = parent
        self.product_manager = product_manager
        self.user = user
        self.product_id = product_id
        self.result = None
        
        # Get product info
        self.product = product_manager.get_product_by_id(product_id)
        if not self.product:
            messagebox.showerror("Error", "Product not found")
            return
            
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
        self.dialog.title("Stock Adjustment")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product info
        info_frame = ttk.LabelFrame(main_frame, text="Product Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Product: {self.product.name}", font=('Arial', 11, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, text=f"Current Stock: {self.product.current_stock}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Minimum Level: {self.product.min_stock}").pack(anchor='w')
        
        # Adjustment form
        form_frame = ttk.LabelFrame(main_frame, text="Stock Adjustment", padding="10")
        form_frame.pack(fill=tk.X, pady=(0, 20))
        form_frame.columnconfigure(1, weight=1)
        
        # Adjustment type
        ttk.Label(form_frame, text="Adjustment Type:").grid(row=0, column=0, sticky="w", pady=5)
        self.adjustment_type_var = tk.StringVar(value="addition")
        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Radiobutton(type_frame, text="Add Stock", variable=self.adjustment_type_var, 
                       value="addition").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Remove Stock", variable=self.adjustment_type_var, 
                       value="adjustment").pack(side=tk.LEFT, padx=(10, 0))
        
        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, sticky="w", pady=5)
        self.quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var)
        quantity_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Reason
        ttk.Label(form_frame, text="Reason:").grid(row=2, column=0, sticky="w", pady=5)
        self.reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(form_frame, textvariable=self.reason_var,
                                  values=["Stock delivery", "Stock addition", "Damage", "Theft", 
                                         "Spoilage", "Count correction", "Transfer", "Other"])
        reason_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky="nw", pady=5)
        self.notes_var = tk.StringVar()
        notes_entry = ttk.Entry(form_frame, textvariable=self.notes_var)
        notes_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Apply Adjustment", command=self.apply_adjustment).pack(side=tk.RIGHT)
        
        # Focus on quantity
        quantity_entry.focus()
        
    def apply_adjustment(self):
        """Apply stock adjustment"""
        try:
            quantity_str = self.quantity_var.get().strip()
            reason = self.reason_var.get().strip()
            notes = self.notes_var.get().strip()
            adjustment_type = self.adjustment_type_var.get()
            
            if not quantity_str:
                messagebox.showerror("Error", "Please enter a quantity")
                return
                
            if not reason:
                messagebox.showerror("Error", "Please select or enter a reason")
                return
                
            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than zero")
                return
                
            # Convert to positive/negative based on type
            if adjustment_type == "adjustment":  # Remove stock
                quantity = -quantity
                
            # Create reason with notes
            full_reason = f"{reason}"
            if notes:
                full_reason += f" - {notes}"
                
            # Apply adjustment
            success = self.product_manager.adjust_stock(
                self.product_id, quantity, adjustment_type, self.user.id, full_reason
            )
            
            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to apply stock adjustment")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity number")
        except Exception as e:
            messagebox.showerror("Error", f"Stock adjustment failed: {str(e)}")
            
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()

def main():
    """Main entry point for product management"""
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
            app = ProductManagementWindow(user=demo_user)
            app.root.mainloop()
        else:
            messagebox.showerror("Error", "Failed to authenticate demo user")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start product management: {str(e)}")

if __name__ == "__main__":
    main()
