# Alembic Database Migrations

## Overview
This directory contains database schema migrations for TrueNAS middleware using Alembic. These migrations handle changes to the SQLite database structure across different TrueNAS versions.

## Directory Structure

- **`alembic.ini`** - Alembic configuration file
- **`env.py`** - Alembic environment configuration
- **`script.py.mako`** - Template for new migrations
- **`initial.sql`** - Initial database schema
- **`versions/`** - Migration files directory

## Migration Naming Convention

Migrations follow a strict naming pattern:
```
YYYY-MM-DD_HH-MM_description.py
```

Example:
```
2025-02-26_09-34_drop_vm_tables.py
```

This ensures:
- Chronological ordering
- Easy identification of when migration was added
- Clear description of changes

## Version Strategy

TrueNAS uses YY.MM versioning (e.g., 25.10):
- Each release has its own set of migrations
- Migrations are cumulative
- Never modify existing migrations
- Only add new migrations

## Creating New Migrations

### 1. Auto-generate Migration
```bash
cd src/middlewared
alembic revision --autogenerate -m "description of changes"
```

### 2. Manual Migration
```bash
cd src/middlewared
alembic revision -m "description of changes"
```

### 3. Rename to Follow Convention
After generation, rename the file to follow the naming pattern:
```bash
mv versions/abc123_description.py versions/2025-02-27_14-30_description.py
```

## Migration Structure

### Basic Migration Template
```python
"""Description of what this migration does

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2025-02-27 14:30:00.123456

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    """Apply schema changes"""
    # Add column
    op.add_column('table_name', 
        sa.Column('new_column', sa.String(50), nullable=True)
    )
    
    # Create table
    op.create_table('new_table',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(50))
    )
    
    # Create index
    op.create_index('ix_table_column', 'table_name', ['column'])

def downgrade():
    """Revert schema changes"""
    op.drop_index('ix_table_column')
    op.drop_table('new_table')
    op.drop_column('table_name', 'new_column')
```

## Common Migration Operations

### Table Operations
```python
# Create table
op.create_table('table_name', 
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('name', sa.String(100), nullable=False)
)

# Drop table
op.drop_table('table_name')

# Rename table
op.rename_table('old_name', 'new_name')
```

### Column Operations
```python
# Add column
op.add_column('table_name',
    sa.Column('column_name', sa.String(50), nullable=True)
)

# Drop column
op.drop_column('table_name', 'column_name')

# Rename column
op.alter_column('table_name', 'old_name', new_column_name='new_name')

# Change column type
op.alter_column('table_name', 'column_name',
    type_=sa.Integer(),
    existing_type=sa.String(50)
)
```

### Index Operations
```python
# Create index
op.create_index('ix_table_column', 'table_name', ['column'])

# Drop index
op.drop_index('ix_table_column')

# Create unique constraint
op.create_unique_constraint('uq_table_column', 'table_name', ['column'])
```

### Data Migration
```python
from sqlalchemy import table, column

def upgrade():
    # Create reference to table
    my_table = table('my_table',
        column('id', sa.Integer),
        column('old_field', sa.String),
        column('new_field', sa.String)
    )
    
    # Migrate data
    connection = op.get_bind()
    results = connection.execute(sa.select([my_table]))
    
    for row in results:
        connection.execute(
            my_table.update().where(my_table.c.id == row.id).values(
                new_field=transform_data(row.old_field)
            )
        )
```

## Best Practices

### 1. Always Include Downgrade
- Even if downgrade is complex
- Use `raise NotImplementedError()` if truly irreversible
- Document why downgrade isn't possible

### 2. Test Migrations
```python
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test full migration path
alembic downgrade base
alembic upgrade head
```

### 3. Handle Data Carefully
- Backup data before destructive operations
- Use transactions when possible
- Consider data migration in separate step

### 4. SQLite Limitations
SQLite has limitations compared to other databases:
- Cannot drop columns (need to recreate table)
- Limited ALTER TABLE support
- No proper foreign key renaming

Example of working around SQLite limitations:
```python
def upgrade():
    # SQLite doesn't support dropping columns
    # So we create new table and copy data
    op.create_table('table_new',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('kept_column', sa.String(50))
        # dropped_column is not included
    )
    
    # Copy data
    op.execute('INSERT INTO table_new SELECT id, kept_column FROM table_old')
    
    # Drop old table and rename new
    op.drop_table('table_old')
    op.rename_table('table_new', 'table_old')
```

### 5. Coordinate with Data Migrations
Some changes require both:
- Schema migration (Alembic) - Changes structure
- Data migration (`/migration/`) - Changes data with middleware running

## Running Migrations

### Development
```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head

# Upgrade one step
alembic upgrade +1

# Downgrade one step
alembic downgrade -1

# Show history
alembic history
```

### Production
Migrations run automatically during middleware startup if needed.

## Troubleshooting

### Migration Conflicts
If two developers create migrations:
1. Merge both migration files
2. Update revision IDs to create proper chain
3. Test full migration path

### Failed Migrations
1. Check `alembic_version` table for current version
2. Manually fix database if needed
3. Update `alembic_version` to correct revision
4. Re-run migration

### Common Errors
- **Foreign key constraint failed**: Check data integrity
- **Table already exists**: Check if migration already applied
- **Column doesn't exist**: Verify current schema state