"""
Sales Screen for Tembie's Spaza Shop POS System
Handles sales transactions and receipt display optimized for mobile photography
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.products.management import ProductManager
from core.sales.transaction import TransactionManager
from core.sales.receipt import ReceiptGenerator
from config.settings import get_settings_manager

class SalesScreen:
    """Sales transaction interface"""
    
    def __init__(self, parent=None, user_id=1):
        self.parent = parent
        self.user_id = user_id
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        
        # Initialize managers
        self.product_manager = ProductManager()
        self.transaction_manager = TransactionManager()
        self.receipt_generator = ReceiptGenerator()
        self.settings_manager = get_settings_manager()
        
        # Current sale
        self.current_sale = None
        self.last_completed_sale = None  # Store for receipt actions
        
        self.setup_window()
        self.create_widgets()
        self.start_new_sale()
    
    def setup_window(self):
        """Configure sales window"""
        self.root.title("Sales Transaction - Tembie's Spaza Shop")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Configure style
        style = ttk.Style()
        style.configure('Large.TButton', font=('Arial', 12, 'bold'), padding=10)
        style.configure('Small.TButton', font=('Arial', 10), padding=5)
        style.configure('Receipt.TLabel', font=('Courier', 11), background='white', foreground='black')
        style.configure('Total.TLabel', font=('Arial', 16, 'bold'), foreground='red')
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
    
    def create_widgets(self):
        """Create and layout all widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure main layout: left panel (sales) + right panel (receipt)
        main_frame.columnconfigure(0, weight=2)  # Sales panel gets more space
        main_frame.columnconfigure(1, weight=1)  # Receipt panel
        main_frame.rowconfigure(0, weight=1)
        
        # Sales panel
        self.create_sales_panel(main_frame)
        
        # Receipt panel
        self.create_receipt_panel(main_frame)
    
    def create_sales_panel(self, parent):
        """Create left panel for sales operations"""
        sales_frame = ttk.Frame(parent)
        sales_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        sales_frame.rowconfigure(2, weight=1)  # Items list gets most space
        sales_frame.columnconfigure(0, weight=1)
        
        # Transaction header
        self.create_transaction_header(sales_frame)
        
        # Product search/add section
        self.create_product_search(sales_frame)
        
        # Current sale items
        self.create_items_list(sales_frame)
        
        # Payment section
        self.create_payment_section(sales_frame)
    
    def create_transaction_header(self, parent):
        """Create transaction header with sale info"""
        header_frame = ttk.LabelFrame(parent, text="Current Transaction", padding="10")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Transaction reference
        ttk.Label(header_frame, text="Transaction:").grid(row=0, column=0, sticky="w")
        self.transaction_ref_label = ttk.Label(header_frame, text="", font=('Arial', 10, 'bold'))
        self.transaction_ref_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Date/time
        ttk.Label(header_frame, text="Date/Time:").grid(row=1, column=0, sticky="w")
        self.datetime_label = ttk.Label(header_frame, text="")
        self.datetime_label.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=0, column=2, rowspan=2, sticky="e")
        
        ttk.Button(button_frame, text="New Sale", command=self.start_new_sale, style='Small.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Void Sale", command=self.void_current_sale, style='Small.TButton').pack(side=tk.LEFT, padx=2)
    
    def create_product_search(self, parent):
        """Create product search and add section"""
        search_frame = ttk.LabelFrame(parent, text="Add Products", padding="10")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # Barcode entry
        ttk.Label(search_frame, text="Barcode:").grid(row=0, column=0, sticky="w")
        self.barcode_entry = ttk.Entry(search_frame, width=20)
        self.barcode_entry.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        self.barcode_entry.bind('<Return>', self.add_by_barcode)
        
        ttk.Button(search_frame, text="Add", command=self.add_by_barcode, style='Small.TButton').grid(row=0, column=2)
        
        # Product search
        ttk.Label(search_frame, text="Search:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Search results dropdown
        self.search_var = tk.StringVar()
        self.search_combo = ttk.Combobox(search_frame, textvariable=self.search_var, state="readonly", width=40)
        self.search_combo.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.search_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        
        # Quantity
        ttk.Label(search_frame, text="Qty:").grid(row=2, column=2, sticky="w", padx=(10, 5), pady=(5, 0))
        self.quantity_var = tk.StringVar(value="1")
        quantity_spinbox = tk.Spinbox(search_frame, from_=1, to=999, textvariable=self.quantity_var, width=5)
        quantity_spinbox.grid(row=2, column=3, pady=(5, 0))
    
    def create_items_list(self, parent):
        """Create current sale items list"""
        items_frame = ttk.LabelFrame(parent, text="Sale Items", padding="10")
        items_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        items_frame.columnconfigure(0, weight=1)
        items_frame.rowconfigure(1, weight=1)
        
        # Items treeview
        columns = ("Product", "Qty", "Price", "Total")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.items_tree.heading("Product", text="Product")
        self.items_tree.heading("Qty", text="Qty")
        self.items_tree.heading("Price", text="Unit Price")
        self.items_tree.heading("Total", text="Total")
        
        self.items_tree.column("Product", width=300)
        self.items_tree.column("Qty", width=60)
        self.items_tree.column("Price", width=100)
        self.items_tree.column("Total", width=100)
        
        # Scrollbar
        items_scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        self.items_tree.grid(row=1, column=0, sticky="nsew")
        items_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Item actions
        actions_frame = ttk.Frame(items_frame)
        actions_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(actions_frame, text="Remove Item", command=self.remove_selected_item, style='Small.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Update Qty", command=self.update_item_quantity, style='Small.TButton').pack(side=tk.LEFT)
        
        # Totals frame
        totals_frame = ttk.Frame(items_frame)
        totals_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        totals_frame.columnconfigure(1, weight=1)
        
        # Subtotal
        ttk.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, sticky="w")
        self.subtotal_label = ttk.Label(totals_frame, text="R 0.00")
        self.subtotal_label.grid(row=0, column=1, sticky="e")
        
        # VAT
        ttk.Label(totals_frame, text="VAT (15%):").grid(row=1, column=0, sticky="w")
        self.vat_label = ttk.Label(totals_frame, text="R 0.00")
        self.vat_label.grid(row=1, column=1, sticky="e")
        
        # Total
        ttk.Label(totals_frame, text="TOTAL:", font=('Arial', 14, 'bold')).grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.total_label = ttk.Label(totals_frame, text="R 0.00", style='Total.TLabel')
        self.total_label.grid(row=2, column=1, sticky="e", pady=(5, 0))
    
    def create_payment_section(self, parent):
        """Create payment processing section"""
        payment_frame = ttk.LabelFrame(parent, text="Payment", padding="10")
        payment_frame.grid(row=3, column=0, sticky="ew")
        payment_frame.columnconfigure(1, weight=1)
        
        # Payment method
        ttk.Label(payment_frame, text="Method:").grid(row=0, column=0, sticky="w")
        self.payment_method = tk.StringVar(value="cash")
        payment_combo = ttk.Combobox(payment_frame, textvariable=self.payment_method, 
                                   values=["cash", "card", "mixed"], state="readonly", width=10)
        payment_combo.grid(row=0, column=1, sticky="w", padx=(5, 0))
        payment_combo.bind('<<ComboboxSelected>>', self.on_payment_method_change)
        
        # Cash amount
        ttk.Label(payment_frame, text="Cash:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.cash_var = tk.StringVar()
        self.cash_entry = ttk.Entry(payment_frame, textvariable=self.cash_var, width=15)
        self.cash_entry.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=(5, 0))
        self.cash_entry.bind('<KeyRelease>', self.calculate_change)
        
        # Card amount (for mixed payments)
        self.card_label = ttk.Label(payment_frame, text="Card:")
        self.card_var = tk.StringVar()
        self.card_entry = ttk.Entry(payment_frame, textvariable=self.card_var, width=15)
        self.card_entry.bind('<KeyRelease>', self.calculate_change)
        
        # Change
        ttk.Label(payment_frame, text="Change:").grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.change_label = ttk.Label(payment_frame, text="R 0.00", font=('Arial', 12, 'bold'))
        self.change_label.grid(row=2, column=1, sticky="w", padx=(5, 0), pady=(5, 0))
        
        # Complete sale button
        self.complete_button = ttk.Button(payment_frame, text="Complete Sale", 
                                        command=self.complete_sale, style='Large.TButton')
        self.complete_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Initially hide card entry
        self.on_payment_method_change()
    
    def create_receipt_panel(self, parent):
        """Create right panel for receipt display (optimized for mobile photography)"""
        receipt_frame = ttk.LabelFrame(parent, text="Receipt Preview", padding="10")
        receipt_frame.grid(row=0, column=1, sticky="nsew")
        receipt_frame.columnconfigure(0, weight=1)
        receipt_frame.rowconfigure(1, weight=1)
        
        # Receipt instructions
        instructions = ttk.Label(receipt_frame, 
                               text=" Receipt optimized for mobile photography\n"
                                    "Customer can photograph this screen as proof of purchase",
                               justify=tk.CENTER, font=('Arial', 10))
        instructions.grid(row=0, column=0, pady=(0, 10))
        
        # Receipt display area with white background for better photos
        receipt_display_frame = ttk.Frame(receipt_frame, relief='solid', borderwidth=2)
        receipt_display_frame.grid(row=1, column=0, sticky="nsew")
        receipt_display_frame.columnconfigure(0, weight=1)
        receipt_display_frame.rowconfigure(0, weight=1)
        
        # Receipt text area with courier font for clarity
        self.receipt_text = tk.Text(receipt_display_frame, 
                                  font=('Courier', 11), 
                                  bg='white', 
                                  fg='black',
                                  wrap=tk.WORD,
                                  state=tk.DISABLED,
                                  padx=15,
                                  pady=15)
        
        receipt_scrollbar = ttk.Scrollbar(receipt_display_frame, orient="vertical", command=self.receipt_text.yview)
        self.receipt_text.configure(yscrollcommand=receipt_scrollbar.set)
        
        self.receipt_text.grid(row=0, column=0, sticky="nsew")
        receipt_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Receipt actions
        receipt_actions = ttk.Frame(receipt_frame)
        receipt_actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(receipt_actions, text="️ Print Receipt", 
                  command=self.print_receipt, style='Small.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(receipt_actions, text=" Email Receipt", 
                  command=self.email_receipt, style='Small.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(receipt_actions, text=" SMS Receipt", 
                  command=self.sms_receipt, style='Small.TButton').pack(side=tk.LEFT)
        
        # Initialize with placeholder
        self.update_receipt_display("No active transaction")
    
    def start_new_sale(self):
        """Start a new sale transaction"""
        self.current_sale = self.transaction_manager.start_new_sale(self.user_id)
        
        # Update UI
        self.transaction_ref_label.config(text=self.current_sale.transaction_ref)
        self.datetime_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Clear items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Reset payment
        self.cash_var.set("")
        self.card_var.set("")
        self.payment_method.set("cash")
        self.on_payment_method_change()
        
        # Update displays
        self.update_totals()
        self.update_receipt_display("Transaction started. Add products to continue.")
        
        # Focus on barcode entry
        self.barcode_entry.focus_set()
    
    def add_by_barcode(self, event=None):
        """Add product by barcode"""
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            return
        
        try:
            quantity = int(self.quantity_var.get())
            self.transaction_manager.add_item_by_barcode(barcode, quantity)
            
            # Clear barcode entry
            self.barcode_entry.delete(0, tk.END)
            
            # Update displays
            self.update_items_display()
            self.update_totals()
            self.update_receipt_preview()
            
            # Focus back to barcode entry
            self.barcode_entry.focus_set()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
    
    def on_search_change(self, event=None):
        """Handle product search"""
        search_term = self.search_entry.get().strip()
        if len(search_term) < 2:
            self.search_combo['values'] = ()
            return
        
        # Search products
        products = self.product_manager.search_products(search_term)
        
        # Update combo box
        product_options = []
        self.product_map = {}  # Map display text to product
        
        for product in products[:20]:  # Limit to 20 results
            display_text = f"{product.name} - R{product.sell_price:.2f} (Stock: {product.current_stock})"
            product_options.append(display_text)
            self.product_map[display_text] = product
        
        self.search_combo['values'] = product_options
        
        if product_options:
            self.search_combo.set('')  # Clear selection
    
    def on_product_selected(self, event=None):
        """Handle product selection from search"""
        selected = self.search_var.get()
        if selected and selected in self.product_map:
            product = self.product_map[selected]
            
            try:
                quantity = int(self.quantity_var.get())
                self.transaction_manager.add_item_to_sale(product.id, quantity)
                
                # Clear search
                self.search_entry.delete(0, tk.END)
                self.search_combo.set('')
                self.search_combo['values'] = ()
                
                # Update displays
                self.update_items_display()
                self.update_totals()
                self.update_receipt_preview()
                
                # Focus back to search
                self.search_entry.focus_set()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {str(e)}")
    
    def update_items_display(self):
        """Update the items list display"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add current sale items
        if self.current_sale and self.current_sale.items:
            for item in self.current_sale.items:
                self.items_tree.insert("", "end", values=(
                    item.product_name,
                    item.quantity,
                    f"R{item.unit_price:.2f}",
                    f"R{item.total_price:.2f}"
                ))
    
    def update_totals(self):
        """Update total amounts display"""
        if self.current_sale:
            self.subtotal_label.config(text=f"R {self.current_sale.subtotal:.2f}")
            self.vat_label.config(text=f"R {self.current_sale.vat_amount:.2f}")
            self.total_label.config(text=f"R {self.current_sale.total_amount:.2f}")
        else:
            self.subtotal_label.config(text="R 0.00")
            self.vat_label.config(text="R 0.00")
            self.total_label.config(text="R 0.00")
    
    def on_payment_method_change(self, event=None):
        """Handle payment method change"""
        method = self.payment_method.get()
        
        if method == "mixed":
            # Show card entry for mixed payments
            self.card_label.grid(row=1, column=2, sticky="w", padx=(20, 5), pady=(5, 0))
            self.card_entry.grid(row=1, column=3, sticky="w", pady=(5, 0))
        else:
            # Hide card entry
            self.card_label.grid_remove()
            self.card_entry.grid_remove()
            self.card_var.set("")
        
        self.calculate_change()
    
    def calculate_change(self, event=None):
        """Calculate and display change"""
        if not self.current_sale:
            self.change_label.config(text="R 0.00")
            return
        
        try:
            total_due = self.current_sale.total_amount
            cash_amount = float(self.cash_var.get() or 0)
            card_amount = float(self.card_var.get() or 0)
            
            if self.payment_method.get() == "cash":
                change = max(0, cash_amount - total_due)
            elif self.payment_method.get() == "card":
                change = 0
            else:  # mixed
                cash_due = max(0, total_due - card_amount)
                change = max(0, cash_amount - cash_due)
            
            self.change_label.config(text=f"R {change:.2f}")
            
        except ValueError:
            self.change_label.config(text="R 0.00")
    
    def complete_sale(self):
        """Complete the current sale"""
        if not self.current_sale or not self.current_sale.items:
            messagebox.showerror("Error", "No items in sale")
            return
        
        try:
            # Set payment details
            cash_amount = float(self.cash_var.get() or 0)
            card_amount = float(self.card_var.get() or 0)
            method = self.payment_method.get()
            
            if method == "cash":
                self.transaction_manager.set_payment_method("cash", cash_amount)
            elif method == "card":
                self.transaction_manager.set_payment_method("card", 0.0, self.current_sale.total_amount)
            else:  # mixed
                self.transaction_manager.set_payment_method("mixed", cash_amount, card_amount)
            
            # Validate payment
            if not self.transaction_manager.validate_payment():
                messagebox.showerror("Error", "Payment amount is insufficient")
                return
            
            # Complete the sale
            sale_id = self.transaction_manager.complete_sale()
            
            # Get completed sale for receipt
            completed_sale = self.transaction_manager.get_sale_by_id(sale_id)
            
            if completed_sale:
                # Store for receipt actions
                self.last_completed_sale = completed_sale
                
                # Show receipt
                receipt_text = self.receipt_generator.generate_receipt_text(completed_sale)
                self.update_receipt_display(receipt_text)
                
                # Show success message
                change_msg = f"\nChange given: R{completed_sale.change_given:.2f}" if completed_sale.change_given > 0 else ""
                messagebox.showinfo("Sale Complete", 
                                  f"Sale completed successfully!\n"
                                  f"Transaction: {completed_sale.transaction_ref}\n"
                                  f"Total: R{completed_sale.total_amount:.2f}{change_msg}\n\n"
                                  f"Receipt is displayed for customer to photograph.")
                
                # Prepare for next sale
                self.start_new_sale()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid payment amount: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
    
    def update_receipt_preview(self):
        """Update receipt preview for current sale"""
        if not self.current_sale or not self.current_sale.items:
            self.update_receipt_display("Add products to see receipt preview")
            return
        
        # Create a temporary receipt preview
        preview_text = f"""
{self.settings_manager.get_settings().shop_name}

Transaction: {self.current_sale.transaction_ref}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Items:
"""
        for item in self.current_sale.items:
            preview_text += f"{item.product_name[:20]:<20} {item.quantity:>3} x R{item.unit_price:>6.2f} = R{item.total_price:>8.2f}\n"
        
        preview_text += f"""
Subtotal: R{self.current_sale.subtotal:>12.2f}
VAT (15%): R{self.current_sale.vat_amount:>11.2f}
TOTAL: R{self.current_sale.total_amount:>15.2f}

[Payment details will appear here after payment]
"""
        
        self.update_receipt_display(preview_text)
    
    def update_receipt_display(self, text):
        """Update receipt display area"""
        self.receipt_text.config(state=tk.NORMAL)
        self.receipt_text.delete(1.0, tk.END)
        self.receipt_text.insert(1.0, text)
        self.receipt_text.config(state=tk.DISABLED)
    
    def remove_selected_item(self):
        """Remove selected item from sale"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        # Get product name from selection
        item_values = self.items_tree.item(selection[0])['values']
        product_name = item_values[0]
        
        # Find product ID
        for item in self.current_sale.items:
            if item.product_name == product_name:
                self.transaction_manager.remove_item_from_sale(item.product_id)
                break
        
        # Update displays
        self.update_items_display()
        self.update_totals()
        self.update_receipt_preview()
    
    def update_item_quantity(self):
        """Update quantity of selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to update")
            return
        
        # Get current quantity
        item_values = self.items_tree.item(selection[0])['values']
        current_qty = item_values[1]
        
        # Ask for new quantity
        from tkinter.simpledialog import askinteger
        new_qty = askinteger("Update Quantity", f"Enter new quantity:", initialvalue=current_qty, minvalue=1)
        
        if new_qty is None:
            return
        
        # Find and update product
        product_name = item_values[0]
        for item in self.current_sale.items:
            if item.product_name == product_name:
                try:
                    self.transaction_manager.update_item_quantity(item.product_id, new_qty)
                    
                    # Update displays
                    self.update_items_display()
                    self.update_totals()
                    self.update_receipt_preview()
                    break
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    break
    
    def void_current_sale(self):
        """Void the current sale"""
        if not self.current_sale or not self.current_sale.items:
            messagebox.showwarning("Warning", "No active sale to void")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to void this sale?"):
            self.start_new_sale()
    
    def print_receipt(self):
        """Print receipt (placeholder for future printer support)"""
        messagebox.showinfo("Print Receipt", 
                          "Thermal printer support coming soon!\n\n"
                          "For now, customers can photograph the receipt display.")
    
    def email_receipt(self):
        """Email receipt (placeholder for future email support)"""
        messagebox.showinfo("Email Receipt", 
                          "Email receipt feature coming in future update!\n\n"
                          "For now, customers can photograph the receipt display.")
    
    def sms_receipt(self):
        """Send receipt via SMS"""
        if not self.last_completed_sale:
            messagebox.showerror("Error", "No completed sale to send. Complete a sale first.")
            return
        
        # Create SMS dialog
        sms_dialog = SMSReceiptDialog(self.root, self.last_completed_sale, self.receipt_generator)

class SMSReceiptDialog:
    """Dialog for sending receipt via SMS"""
    
    def __init__(self, parent, sale, receipt_generator):
        self.parent = parent
        self.sale = sale
        self.receipt_generator = receipt_generator
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Send Receipt via SMS")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # Make modal
        
        # Center the dialog
        self.dialog.transient(parent)
        self.center_dialog()
        
        self.create_widgets()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (450 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (350 // 2)
        self.dialog.geometry(f"450x350+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Header
        header_label = ttk.Label(main_frame, text=" Send Receipt via SMS", 
                                font=('Arial', 14, 'bold'))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Transaction info
        info_frame = ttk.LabelFrame(main_frame, text="Transaction Details", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Transaction: {self.sale.transaction_ref}").grid(row=0, column=0, sticky="w")
        ttk.Label(info_frame, text=f"Date: {self.sale.date_time.strftime('%Y-%m-%d %H:%M')}").grid(row=1, column=0, sticky="w")
        ttk.Label(info_frame, text=f"Total: R{self.sale.total_amount:.2f}").grid(row=2, column=0, sticky="w")
        
        # Phone number input
        phone_frame = ttk.LabelFrame(main_frame, text="Customer Phone Number", padding="10")
        phone_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        ttk.Label(phone_frame, text="Enter phone number:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(phone_frame, textvariable=self.phone_var, font=('Arial', 12), width=20)
        phone_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        phone_entry.focus()
        
        ttk.Label(phone_frame, text="Format: 0XX XXX XXXX or +27XX XXX XXXX", 
                 foreground="gray").grid(row=2, column=0, sticky="w")
        
        phone_frame.columnconfigure(0, weight=1)
        
        # SMS preview
        preview_frame = ttk.LabelFrame(main_frame, text="SMS Preview", padding="10")
        preview_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 20))
        
        # Generate SMS preview
        from core.sales.sms_service import get_sms_service
        sms_service = get_sms_service()
        sms_preview = sms_service.generate_sms_receipt(self.sale)
        
        preview_text = tk.Text(preview_frame, height=8, width=50, wrap=tk.WORD, 
                              font=('Courier', 9), state=tk.DISABLED)
        preview_text.grid(row=0, column=0, sticky="nsew")
        
        # Add preview content
        preview_text.config(state=tk.NORMAL)
        preview_text.insert("1.0", sms_preview)
        preview_text.config(state=tk.DISABLED)
        
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(button_frame, text=" Send SMS", 
                  command=self.send_sms, style='Large.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Bind Enter key to send
        self.dialog.bind('<Return>', lambda e: self.send_sms())
        phone_entry.bind('<Return>', lambda e: self.send_sms())
    
    def send_sms(self):
        """Send the SMS receipt"""
        phone = self.phone_var.get().strip()
        
        if not phone:
            messagebox.showerror("Error", "Please enter a phone number")
            return
        
        # Show progress
        progress_window = tk.Toplevel(self.dialog)
        progress_window.title("Sending SMS...")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        # Center progress window
        progress_window.transient(self.dialog)
        x = self.dialog.winfo_x() + (self.dialog.winfo_width() // 2) - 150
        y = self.dialog.winfo_y() + (self.dialog.winfo_height() // 2) - 50
        progress_window.geometry(f"300x100+{x}+{y}")
        
        progress_label = ttk.Label(progress_window, text=" Sending SMS receipt...", 
                                  font=('Arial', 12))
        progress_label.pack(expand=True)
        
        # Disable main dialog
        self.dialog.config(cursor="wait")
        progress_window.update()
        
        try:
            # Send SMS
            from core.sales.sms_service import get_sms_service
            sms_service = get_sms_service()
            result = sms_service.send_receipt_sms(self.sale, phone)
            
            # Close progress window
            progress_window.destroy()
            self.dialog.config(cursor="")
            
            if result['success']:
                messagebox.showinfo("SMS Sent", 
                                   f" Receipt sent successfully to {result.get('phone', phone)}!\n\n"
                                   f"Message ID: {result.get('message_id', 'N/A')}")
                self.dialog.destroy()
            else:
                messagebox.showerror("SMS Failed", 
                                    f" Failed to send SMS:\n{result['error']}")
        
        except Exception as e:
            progress_window.destroy()
            self.dialog.config(cursor="")
            messagebox.showerror("Error", f"Failed to send SMS: {str(e)}")

def main():
    """Main entry point for sales screen"""
    try:
        app = SalesScreen()
        app.root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start sales screen: {str(e)}")

if __name__ == "__main__":
    main()
