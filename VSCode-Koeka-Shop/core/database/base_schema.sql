-- Core database schema for Tembie's Spaza Shop POS System
-- Based on functional specification requirements

-- Products table with dual stock level system
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    barcode TEXT UNIQUE,
    category TEXT NOT NULL CHECK(category IN ('Food', 'Household', 'Sweets', 'Cooldrinks', 'Other')),
    cost_price DECIMAL(10,2) NOT NULL,
    sell_price DECIMAL(10,2) NOT NULL,
    current_stock INTEGER NOT NULL DEFAULT 0,
    monthly_stock INTEGER NOT NULL DEFAULT 0,
    min_stock INTEGER NOT NULL DEFAULT 0,
    vat_rate DECIMAL(5,2) NOT NULL DEFAULT 15.00,
    vat_inclusive BOOLEAN NOT NULL DEFAULT 1,
    expiry_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Users table for role-based access
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'pos_operator', 'stock_manager')),
    full_name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Sales transactions
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_ref TEXT UNIQUE NOT NULL,
    date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    vat_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method TEXT NOT NULL CHECK(payment_method IN ('cash', 'card', 'mixed')),
    cash_amount DECIMAL(10,2) DEFAULT 0,
    card_amount DECIMAL(10,2) DEFAULT 0,
    change_given DECIMAL(10,2) DEFAULT 0,
    voided BOOLEAN DEFAULT 0,
    voided_by INTEGER,
    voided_at DATETIME,
    void_reason TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (voided_by) REFERENCES users(id)
);

-- Individual sale items
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    vat_rate DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Stock movements audit trail
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL CHECK(movement_type IN ('sale', 'adjustment', 'addition', 'damage', 'theft', 'expiry')),
    quantity_change INTEGER NOT NULL,
    previous_stock INTEGER NOT NULL,
    new_stock INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    reference_id INTEGER, -- Link to sale_id for sales movements
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Daily cash management
CREATE TABLE IF NOT EXISTS daily_cash (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    opening_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    cash_sales DECIMAL(10,2) NOT NULL DEFAULT 0,
    card_sales DECIMAL(10,2) NOT NULL DEFAULT 0,
    withdrawals DECIMAL(10,2) NOT NULL DEFAULT 0,
    expected_closing DECIMAL(10,2) NOT NULL DEFAULT 0,
    actual_closing DECIMAL(10,2),
    variance DECIMAL(10,2),
    reconciled BOOLEAN DEFAULT 0,
    reconciled_by INTEGER,
    reconciled_at DATETIME,
    notes TEXT,
    FOREIGN KEY (reconciled_by) REFERENCES users(id)
);

-- System configuration
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- SMS log for tracking receipt SMS messages
CREATE TABLE IF NOT EXISTS sms_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_ref TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL DEFAULT 0,
    error_message TEXT,
    message_id TEXT,
    provider TEXT DEFAULT 'demo',
    FOREIGN KEY (transaction_ref) REFERENCES sales(transaction_ref)
);

-- Insert default configuration
INSERT OR IGNORE INTO system_config (key, value, description) VALUES
('shop_name', 'Tembie''s Spaza Shop', 'Shop name for receipts'),
('vat_rate', '15.00', 'Default VAT rate percentage'),
('currency', 'ZAR', 'Currency code'),
('receipt_footer', 'Thank you for your business!', 'Receipt footer message'),
('low_stock_threshold', '5', 'Default low stock warning threshold'),
('sms_enabled', 'true', 'Enable SMS receipt functionality'),
('sms_provider', 'demo', 'SMS provider (demo, twilio, africastalking)'),
('sms_sender_name', 'Tembie''s Shop', 'SMS sender name');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date_time);
CREATE INDEX IF NOT EXISTS idx_sales_user ON sales(user_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_product ON stock_movements(product_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_date ON stock_movements(date_time);
CREATE INDEX IF NOT EXISTS idx_sms_log_transaction ON sms_log(transaction_ref);
CREATE INDEX IF NOT EXISTS idx_sms_log_phone ON sms_log(phone_number);
