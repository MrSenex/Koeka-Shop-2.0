# Product Deletion Functionality

This document describes the comprehensive product deletion system added to Tembie's Spaza Shop POS System.

## Overview

The system provides safe and flexible product deletion with the following features:

- **Smart Deletion**: Automatically detects if a product can be safely deleted
- **Archiving**: Safe alternative to deletion that preserves all data
- **Force Deletion**: Option for permanent removal when needed
- **Restoration**: Ability to restore archived products
- **Data Integrity**: Maintains referential integrity and audit trails

## Core Components

### 1. ProductManager Methods

#### `delete_product(product_id, user_id, force=False)`
Permanently deletes a product from the database.

**Parameters:**
- `product_id`: ID of the product to delete
- `user_id`: ID of the user performing the deletion
- `force`: If True, forces deletion even with associated records

**Returns:** `bool` - True if successful

**Raises:** `ValueError` if product has constraints and force=False

#### `archive_product(product_id, user_id)`
Archives a product (soft delete) - safer for products with sales history.

**Parameters:**
- `product_id`: ID of the product to archive
- `user_id`: ID of the user performing the archival

**Returns:** `bool` - True if successful

#### `restore_product(product_id, user_id)`
Restores an archived product to active status.

**Parameters:**
- `product_id`: ID of the product to restore
- `user_id`: ID of the user performing the restoration

**Returns:** `bool` - True if successful

#### `can_delete_product(product_id)`
Checks if a product can be safely deleted.

**Returns:** `dict` with:
- `can_delete`: Boolean indicating if safe to delete
- `sales_count`: Number of associated sales
- `movements_count`: Number of stock movements
- `current_stock`: Current stock level
- `recommendation`: 'delete' or 'archive'

#### `get_archived_products()`
Returns list of all archived products.

**Returns:** `List[Product]` - Archived products

#### `get_all_products(include_archived=False)`
Enhanced to optionally include archived products.

**Parameters:**
- `include_archived`: If True, includes archived products

**Returns:** `List[Product]` - Product list

### 2. Database Schema Changes

The system adds an `archived` column to the products table:

```sql
ALTER TABLE products ADD COLUMN archived BOOLEAN DEFAULT 0;
```

This enables soft deletion while maintaining all existing functionality.

### 3. User Interface Enhancements

#### Main Product Management Window

**Enhanced Delete Button:**
- Automatically detects deletion constraints
- Provides appropriate options based on product status
- Shows detailed information about associated data

**New Archived Products Button:**
- Opens dedicated archive management window
- Allows viewing, restoring, and permanently deleting archived products

#### Delete Options Dialog

When a product has associated data, users see:

1. **Archive Option (Recommended):**
   - Hides product from active lists
   - Preserves all historical data
   - Can be restored later
   - Clears current stock

2. **Force Delete Option:**
   - Permanently removes product
   - Keeps historical data orphaned
   - Cannot be undone
   - Requires additional confirmation

#### Archive Management Window

Dedicated interface for managing archived products:
- List all archived products
- Restore products to active status
- Permanently delete archived products
- View archival dates and details

## Usage Scenarios

### Scenario 1: Delete Unused Product
```python
# Check if product can be safely deleted
delete_info = product_manager.can_delete_product(product_id)

if delete_info['can_delete']:
    # Safe to delete - no sales or movements
    success = product_manager.delete_product(product_id, user_id)
```

### Scenario 2: Archive Product with Sales History
```python
# Product has associated sales/movements
delete_info = product_manager.can_delete_product(product_id)

if not delete_info['can_delete']:
    # Archive instead of delete
    success = product_manager.archive_product(product_id, user_id)
```

### Scenario 3: Manage Archived Products
```python
# View archived products
archived = product_manager.get_archived_products()

# Restore a product
success = product_manager.restore_product(product_id, user_id)

# Permanently delete archived product
success = product_manager.delete_product(product_id, user_id, force=True)
```

## Safety Features

### 1. Constraint Checking
The system automatically checks for:
- Associated sales transactions
- Stock movement history
- Current stock levels

### 2. Data Preservation
- Archiving preserves all historical data
- Stock movements are logged for all operations
- Sales history remains intact

### 3. User Confirmation
- Multiple confirmation dialogs for destructive operations
- Clear warnings about data loss
- Detailed information about constraints

### 4. Audit Trail
All deletion and archival operations are logged in the stock_movements table with:
- Operation type
- User performing action
- Timestamp
- Reason/description

## Error Handling

The system handles various error conditions:

1. **Product Not Found:** Clear error messages
2. **Database Constraints:** Graceful handling of foreign key issues
3. **Permission Issues:** User-friendly error reporting
4. **Data Integrity:** Prevents orphaned records where possible

## Migration Considerations

### Existing Installations
The system gracefully handles databases without the `archived` column:
- Automatically attempts to add the column when needed
- Falls back gracefully if column addition fails
- Maintains backward compatibility

### Data Migration
No existing data migration is required:
- All existing products default to `archived = 0` (active)
- Existing functionality remains unchanged
- New features are additive

## Testing

Use the provided test script to verify functionality:

```bash
python test_product_deletion.py
```

This script tests:
- Product creation and deletion
- Constraint checking
- Archiving and restoration
- Data integrity
- Error handling

## Best Practices

### For Users
1. **Always try archiving first** for products with sales history
2. **Use permanent deletion sparingly** and only when absolutely necessary
3. **Review archived products periodically** to clean up old data
4. **Understand the implications** of force deletion

### For Developers
1. **Always check constraints** before deletion
2. **Log all operations** for audit purposes
3. **Provide clear user feedback** about operation results
4. **Handle errors gracefully** with informative messages
5. **Test with realistic data** including products with sales history

## Future Enhancements

Potential improvements for future versions:

1. **Bulk Operations:** Archive/restore multiple products at once
2. **Scheduled Cleanup:** Automatically archive old products
3. **Advanced Filters:** Search and filter archived products
4. **Export/Import:** Backup and restore archived products
5. **Permissions:** Role-based deletion permissions
6. **Analytics:** Reports on deleted/archived products
