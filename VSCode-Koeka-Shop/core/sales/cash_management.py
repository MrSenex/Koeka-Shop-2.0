"""
Daily Cash Management for Tembie's Spaza Shop POS System
Handles till reconciliation, cash flow tracking, and daily reports
"""

from datetime import datetime, date
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from core.database.connection import get_db_manager

@dataclass
class DailyCash:
    """Daily cash management data"""
    date: date
    opening_amount: float
    cash_sales: float
    card_sales: float
    withdrawals: float
    expected_closing: float
    actual_closing: Optional[float] = None
    variance: Optional[float] = None
    reconciled: bool = False
    reconciled_by: Optional[int] = None
    reconciled_at: Optional[datetime] = None
    notes: str = ""

class CashManager:
    """Manages daily cash operations and till reconciliation"""
    
    def __init__(self):
        self.db = get_db_manager()
    
    def start_day(self, opening_amount: float, user_id: int) -> bool:
        """Start a new business day with opening till amount"""
        today = date.today()
        
        # Check if day already started
        existing = self.get_daily_cash(today)
        if existing:
            raise ValueError(f"Day {today} already started with opening amount R{existing.opening_amount:.2f}")
        
        query = """
            INSERT INTO daily_cash (date, opening_amount, cash_sales, card_sales, 
                                  withdrawals, expected_closing, reconciled_by)
            VALUES (?, ?, 0, 0, 0, ?, ?)
        """
        
        success = self.db.execute_update(query, (
            today.isoformat(), opening_amount, opening_amount, user_id
        )) > 0
        
        if success:
            self._log_cash_activity(user_id, f"Started day with opening amount R{opening_amount:.2f}")
        
        return success
    
    def get_daily_cash(self, target_date: date = None) -> Optional[DailyCash]:
        """Get daily cash record for specified date"""
        if target_date is None:
            target_date = date.today()
        
        query = "SELECT * FROM daily_cash WHERE date = ?"
        results = self.db.execute_query(query, (target_date.isoformat(),))
        
        if results:
            row = results[0]
            return DailyCash(
                date=datetime.fromisoformat(row['date']).date(),
                opening_amount=float(row['opening_amount']),
                cash_sales=float(row['cash_sales']),
                card_sales=float(row['card_sales']),
                withdrawals=float(row['withdrawals']),
                expected_closing=float(row['expected_closing']),
                actual_closing=float(row['actual_closing']) if row['actual_closing'] else None,
                variance=float(row['variance']) if row['variance'] else None,
                reconciled=bool(row['reconciled']),
                reconciled_by=row['reconciled_by'],
                reconciled_at=datetime.fromisoformat(row['reconciled_at']) if row['reconciled_at'] else None,
                notes=row['notes'] or ""
            )
        
        return None
    
    def update_sales_totals(self, target_date: date = None) -> bool:
        """Update cash and card sales totals from sales data"""
        if target_date is None:
            target_date = date.today()
        
        # Get sales totals for the day
        query = """
            SELECT 
                COALESCE(SUM(CASE WHEN payment_method = 'cash' THEN total_amount ELSE 0 END), 0) as cash_total,
                COALESCE(SUM(CASE WHEN payment_method = 'card' THEN total_amount ELSE 0 END), 0) as card_total,
                COALESCE(SUM(CASE WHEN payment_method = 'mixed' THEN cash_amount ELSE 0 END), 0) as mixed_cash,
                COALESCE(SUM(CASE WHEN payment_method = 'mixed' THEN card_amount ELSE 0 END), 0) as mixed_card
            FROM sales 
            WHERE DATE(date_time) = ? AND voided = 0
        """
        
        results = self.db.execute_query(query, (target_date.isoformat(),))
        
        if results:
            row = results[0]
            total_cash = float(row['cash_total']) + float(row['mixed_cash'])
            total_card = float(row['card_total']) + float(row['mixed_card'])
            
            # Update daily_cash record
            daily_cash = self.get_daily_cash(target_date)
            if daily_cash:
                expected_closing = daily_cash.opening_amount + total_cash - daily_cash.withdrawals
                
                update_query = """
                    UPDATE daily_cash 
                    SET cash_sales = ?, card_sales = ?, expected_closing = ?
                    WHERE date = ?
                """
                
                return self.db.execute_update(update_query, (
                    total_cash, total_card, expected_closing, target_date.isoformat()
                )) > 0
        
        return False
    
    def record_withdrawal(self, amount: float, reason: str, user_id: int, 
                         target_date: date = None) -> bool:
        """Record cash withdrawal from till"""
        if target_date is None:
            target_date = date.today()
        
        daily_cash = self.get_daily_cash(target_date)
        if not daily_cash:
            raise ValueError(f"No daily cash record found for {target_date}")
        
        new_withdrawals = daily_cash.withdrawals + amount
        new_expected = daily_cash.opening_amount + daily_cash.cash_sales - new_withdrawals
        
        query = """
            UPDATE daily_cash 
            SET withdrawals = ?, expected_closing = ?
            WHERE date = ?
        """
        
        success = self.db.execute_update(query, (
            new_withdrawals, new_expected, target_date.isoformat()
        )) > 0
        
        if success:
            self._log_cash_activity(user_id, f"Withdrawal: R{amount:.2f} - {reason}")
        
        return success
    
    def reconcile_till(self, actual_amount: float, user_id: int, notes: str = "",
                      target_date: date = None) -> Dict[str, Any]:
        """Reconcile till with actual cash count"""
        if target_date is None:
            target_date = date.today()
        
        # Update sales totals first
        self.update_sales_totals(target_date)
        
        daily_cash = self.get_daily_cash(target_date)
        if not daily_cash:
            raise ValueError(f"No daily cash record found for {target_date}")
        
        if daily_cash.reconciled:
            raise ValueError(f"Till for {target_date} already reconciled")
        
        variance = actual_amount - daily_cash.expected_closing
        
        query = """
            UPDATE daily_cash 
            SET actual_closing = ?, variance = ?, reconciled = 1, 
                reconciled_by = ?, reconciled_at = CURRENT_TIMESTAMP, notes = ?
            WHERE date = ?
        """
        
        success = self.db.execute_update(query, (
            actual_amount, variance, user_id, notes, target_date.isoformat()
        )) > 0
        
        if success:
            status = "balanced" if abs(variance) < 0.01 else ("over" if variance > 0 else "short")
            self._log_cash_activity(user_id, f"Till reconciled: {status} by R{abs(variance):.2f}")
        
        return {
            'success': success,
            'expected': daily_cash.expected_closing,
            'actual': actual_amount,
            'variance': variance,
            'status': 'balanced' if abs(variance) < 0.01 else ('over' if variance > 0 else 'short')
        }
    
    def get_cash_summary(self, target_date: date = None) -> Dict[str, Any]:
        """Get cash summary for dashboard display"""
        if target_date is None:
            target_date = date.today()
        
        self.update_sales_totals(target_date)
        daily_cash = self.get_daily_cash(target_date)
        
        if not daily_cash:
            return {
                'date': target_date,
                'day_started': False,
                'opening_amount': 0.0,
                'cash_sales': 0.0,
                'card_sales': 0.0,
                'withdrawals': 0.0,
                'expected_closing': 0.0,
                'reconciled': False
            }
        
        return {
            'date': target_date,
            'day_started': True,
            'opening_amount': daily_cash.opening_amount,
            'cash_sales': daily_cash.cash_sales,
            'card_sales': daily_cash.card_sales,
            'withdrawals': daily_cash.withdrawals,
            'expected_closing': daily_cash.expected_closing,
            'actual_closing': daily_cash.actual_closing,
            'variance': daily_cash.variance,
            'reconciled': daily_cash.reconciled,
            'notes': daily_cash.notes
        }
    
    def get_cash_history(self, days: int = 7) -> List[DailyCash]:
        """Get cash management history for specified number of days"""
        query = """
            SELECT * FROM daily_cash 
            WHERE date >= date('now', '-{} days')
            ORDER BY date DESC
        """.format(days)
        
        results = self.db.execute_query(query)
        history = []
        
        for row in results:
            history.append(DailyCash(
                date=datetime.fromisoformat(row['date']).date(),
                opening_amount=float(row['opening_amount']),
                cash_sales=float(row['cash_sales']),
                card_sales=float(row['card_sales']),
                withdrawals=float(row['withdrawals']),
                expected_closing=float(row['expected_closing']),
                actual_closing=float(row['actual_closing']) if row['actual_closing'] else None,
                variance=float(row['variance']) if row['variance'] else None,
                reconciled=bool(row['reconciled']),
                reconciled_by=row['reconciled_by'],
                reconciled_at=datetime.fromisoformat(row['reconciled_at']) if row['reconciled_at'] else None,
                notes=row['notes'] or ""
            ))
        
        return history
    
    def generate_daily_report(self, target_date: date = None) -> str:
        """Generate daily cash management report"""
        if target_date is None:
            target_date = date.today()
        
        daily_cash = self.get_daily_cash(target_date)
        if not daily_cash:
            return f"No cash management data for {target_date}"
        
        # Get transaction statistics
        stats_query = """
            SELECT 
                COUNT(*) as transaction_count,
                COUNT(CASE WHEN payment_method = 'cash' THEN 1 END) as cash_transactions,
                COUNT(CASE WHEN payment_method = 'card' THEN 1 END) as card_transactions,
                COUNT(CASE WHEN payment_method = 'mixed' THEN 1 END) as mixed_transactions
            FROM sales 
            WHERE DATE(date_time) = ? AND voided = 0
        """
        
        stats = self.db.execute_query(stats_query, (target_date.isoformat(),))
        
        report_lines = [
            "=" * 60,
            f"DAILY CASH MANAGEMENT REPORT - {target_date}".center(60),
            "=" * 60,
            "",
            "CASH FLOW:",
            f"  Opening Till Amount:     R{daily_cash.opening_amount:>10.2f}",
            f"  Cash Sales:              R{daily_cash.cash_sales:>10.2f}",
            f"  Card Sales:              R{daily_cash.card_sales:>10.2f}",
            f"  Withdrawals:             R{daily_cash.withdrawals:>10.2f}",
            f"  Expected Closing:        R{daily_cash.expected_closing:>10.2f}",
            ""
        ]
        
        if daily_cash.reconciled:
            status = "BALANCED" if abs(daily_cash.variance) < 0.01 else ("OVER" if daily_cash.variance > 0 else "SHORT")
            report_lines.extend([
                "RECONCILIATION:",
                f"  Actual Closing:          R{daily_cash.actual_closing:>10.2f}",
                f"  Variance:                R{daily_cash.variance:>10.2f}",
                f"  Status:                   {status:>10}",
                f"  Reconciled at:           {daily_cash.reconciled_at.strftime('%H:%M:%S')}",
                ""
            ])
            
            if daily_cash.notes:
                report_lines.extend([
                    "NOTES:",
                    f"  {daily_cash.notes}",
                    ""
                ])
        else:
            report_lines.extend([
                "RECONCILIATION: PENDING",
                ""
            ])
        
        if stats:
            stat_row = stats[0]
            report_lines.extend([
                "TRANSACTION SUMMARY:",
                f"  Total Transactions:      {stat_row['transaction_count']:>10}",
                f"  Cash Payments:           {stat_row['cash_transactions']:>10}",
                f"  Card Payments:           {stat_row['card_transactions']:>10}",
                f"  Mixed Payments:          {stat_row['mixed_transactions']:>10}",
                ""
            ])
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def _log_cash_activity(self, user_id: int, description: str):
        """Log cash management activity for audit trail"""
        # Create cash_log table if it doesn't exist
        self.db.execute_update("""
            CREATE TABLE IF NOT EXISTS cash_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        query = """
            INSERT INTO cash_log (user_id, description)
            VALUES (?, ?)
        """
        self.db.execute_update(query, (user_id, description))

# Global cash manager instance
_cash_manager = None

def get_cash_manager() -> CashManager:
    """Get global cash manager instance"""
    global _cash_manager
    if _cash_manager is None:
        _cash_manager = CashManager()
    return _cash_manager
