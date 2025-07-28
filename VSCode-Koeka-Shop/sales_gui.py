"""
Standalone Sales GUI for testing sales functionality
Quick way to test the sales screen without the full application
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch sales screen directly"""
    try:
        print(" Launching Sales Screen...")
        
        from core.ui.sales_screen import SalesScreen
        
        # Create sales screen without parent
        app = SalesScreen(parent=None, user_id=1)
        print(" Sales screen started successfully")
        
        app.root.mainloop()
        
    except Exception as e:
        print(f" Failed to start sales screen: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
