"""
Daily Reports Manager for Tembie's Spaza Shop POS System
Handles daily sales reporting and analytics
"""

import sqlite3
from datetime import datetime, date
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database.connection import get_db_manager

class DailyReportsManager:
    """Manager for daily reporting functionality"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        
    def generate_daily_sales_summary(self, report_date):
        """Generate daily sales summary for a specific date"""
        try:
            if isinstance(report_date, str):
                # Convert string to date object
                report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            elif isinstance(report_date, datetime):
                report_date = report_date.date()
                
            # Get sales summary for the date
            sales_query = """
                SELECT 
                    COUNT(*) as transaction_count,
                    SUM(total_amount) as total_sales,
                    SUM(vat_amount) as total_vat,
                    AVG(total_amount) as avg_sale_value
                FROM sales 
                WHERE DATE(date_time) = ?
            """
            
            sales_data = self.db_manager.execute_query(sales_query, (report_date.strftime('%Y-%m-%d'),))
            sales_row = sales_data[0] if sales_data else (0, 0, 0, 0)
            
            # Get payment method breakdown
            payment_query = """
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM sales 
                WHERE DATE(date_time) = ?
                GROUP BY payment_method
            """
            
            payment_methods = self.db_manager.execute_query(payment_query, (report_date.strftime('%Y-%m-%d'),))
            
            # Get top selling products
            products_query = """
                SELECT 
                    p.name,
                    SUM(si.quantity) as quantity_sold,
                    SUM(si.total_price) as revenue
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.date_time) = ?
                GROUP BY p.id, p.name
                ORDER BY quantity_sold DESC
                LIMIT 10
            """
            
            top_products = self.db_manager.execute_query(products_query, (report_date.strftime('%Y-%m-%d'),))
            
            # Format results
            summary = {
                'date': report_date,
                'transaction_count': sales_row[0] or 0,
                'total_sales': sales_row[1] or 0.0,
                'total_vat': sales_row[2] or 0.0,
                'avg_sale_value': sales_row[3] or 0.0,
                'payment_methods': [
                    {
                        'method': pm[0],
                        'count': pm[1],
                        'total': pm[2]
                    } for pm in payment_methods
                ],
                'top_products': [
                    {
                        'name': tp[0],
                        'quantity_sold': tp[1],
                        'revenue': tp[2]
                    } for tp in top_products
                ]
            }
            
            return summary
            
        except Exception as e:
            print(f"Error generating daily sales summary: {e}")
            return {
                'date': report_date,
                'transaction_count': 0,
                'total_sales': 0.0,
                'total_vat': 0.0,
                'avg_sale_value': 0.0,
                'payment_methods': [],
                'top_products': []
            }
    
    def get_daily_cash_report(self, report_date):
        """Get daily cash management report"""
        try:
            if isinstance(report_date, str):
                report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            elif isinstance(report_date, datetime):
                report_date = report_date.date()
                
            # Get cash management data
            cash_query = """
                SELECT 
                    opening_amount,
                    cash_sales,
                    card_sales,
                    withdrawals,
                    closing_count
                FROM daily_cash 
                WHERE date = ?
            """
            
            cash_data = self.db_manager.execute_query(cash_query, (report_date.strftime('%Y-%m-%d'),))
            
            if cash_data:
                cash_row = cash_data[0]
                expected_closing = (cash_row[0] or 0) + (cash_row[1] or 0) - (cash_row[3] or 0)
                variance = (cash_row[4] or 0) - expected_closing
                
                return {
                    'date': report_date,
                    'opening_amount': cash_row[0] or 0,
                    'cash_sales': cash_row[1] or 0,
                    'card_sales': cash_row[2] or 0,
                    'withdrawals': cash_row[3] or 0,
                    'expected_closing': expected_closing,
                    'actual_closing': cash_row[4] or 0,
                    'variance': variance
                }
            else:
                return {
                    'date': report_date,
                    'opening_amount': 0,
                    'cash_sales': 0,
                    'card_sales': 0,
                    'withdrawals': 0,
                    'expected_closing': 0,
                    'actual_closing': 0,
                    'variance': 0
                }
                
        except Exception as e:
            print(f"Error generating daily cash report: {e}")
            return None
    
    def get_stock_alerts(self, report_date=None):
        """Get low stock alerts for reporting"""
        try:
            # Get products with low stock
            stock_query = """
                SELECT 
                    name,
                    current_stock,
                    min_stock,
                    category
                FROM products 
                WHERE current_stock <= min_stock AND current_stock >= 0
                ORDER BY (current_stock - min_stock) ASC
            """
            
            low_stock_items = self.db_manager.execute_query(stock_query)
            
            return [
                {
                    'name': item[0],
                    'current_stock': item[1],
                    'min_stock': item[2],
                    'category': item[3],
                    'deficit': item[2] - item[1]
                } for item in low_stock_items
            ]
            
        except Exception as e:
            print(f"Error getting stock alerts: {e}")
            return []

# Module interface
def get_daily_reports_manager():
    """Get the daily reports manager instance"""
    return DailyReportsManager()
