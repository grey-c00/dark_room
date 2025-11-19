We are done here with SQL basics and advance topics. Any system can be built on top of SQL db.
Today, we are going to discuss some terminologies and then there will be one question at the end.


# Terminologies

## What is Dead Tuple?

A **dead tuple** is a row version in PostgreSQL that is no longer visible to any transaction but still physically exists in the database files.

**Simple explanation:** When you UPDATE or DELETE a row in PostgreSQL, the old data doesn't disappear immediately. It becomes a "dead tuple" - like a ghost that's still taking up space but can't be seen anymore.

### Why Do Dead Tuples Exist?

Remember from Day 08 when we discussed **MVCC (Multi-Version Concurrency Control)**? PostgreSQL doesn't modify data in-place. Instead:

1. **On UPDATE**: Creates a NEW version of the row, keeps the OLD version (which becomes a dead tuple)
2. **On DELETE**: Marks the row as dead (doesn't physically remove it immediately)

**Why this design?**
- So that long-running transactions can still see old data
- Readers don't block writers (and vice versa)
- No locks needed for reads
- Multiple transactions can work simultaneously

---

## Example: Understanding Dead Tuples

Let's see how dead tuples are created step by step.

### Step 1: Create and Insert Data

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

INSERT INTO users VALUES (1, 'Alice', 'alice@example.com');
```

**Physical Storage (what's actually on disk):**
```
┌────┬───────┬──────────────────┬──────┬──────┬────────┐
│ id │ name  │ email            │ xmin │ xmax │ Status │
├────┼───────┼──────────────────┼──────┼──────┼────────┤
│ 1  │ Alice │ alice@example.com│ 100  │ 0    │ Live   │
└────┴───────┴──────────────────┴──────┴──────┴────────┘
```

**What are xmin and xmax?**
- `xmin`: Transaction ID that created this row (transaction 100 created it)
- `xmax`: Transaction ID that deleted/updated this row (0 = still live, nobody deleted it)

### Step 2: UPDATE the Row

```sql
UPDATE users SET email = 'alice.new@example.com' WHERE id = 1;
```

**Physical Storage (after UPDATE):**
```
┌────┬───────┬──────────────────────┬──────┬──────┬─────────────┐
│ id │ name  │ email                │ xmin │ xmax │ Status      │
├────┼───────┼──────────────────────┼──────┼──────┼─────────────┤
│ 1  │ Alice │ alice@example.com    │ 100  │ 200  │ DEAD TUPLE  │ ← Old version
├────┼───────┼──────────────────────┼──────┼──────┼─────────────┤
│ 1  │ Alice │ alice.new@example.com│ 200  │ 0    │ Live        │ ← New version
└────┴───────┴──────────────────────┴──────┴──────┴─────────────┘
```

**Notice what happened:**
- Old version is STILL there (it's a dead tuple now)
- New version is added below it
- Old version has `xmax = 200` (marked as dead by transaction 200)
- Both rows physically exist on disk!

**Question for you:** If we do `SELECT * FROM users WHERE id = 1;`, which row do we see?

<Answer: We see the new version because the old one is marked as dead (xmax = 200)>

### Step 3: DELETE the Row

```sql
DELETE FROM users WHERE id = 1;
```

**Physical Storage (after DELETE):**
```
┌────┬───────┬──────────────────────┬──────┬──────┬─────────────┐
│ id │ name  │ email                │ xmin │ xmax │ Status      │
├────┼───────┼──────────────────────┼──────┼──────┼─────────────┤
│ 1  │ Alice │ alice@example.com    │ 100  │ 200  │ DEAD TUPLE  │
├────┼───────┼──────────────────────┼──────┼──────┼─────────────┤
│ 1  │ Alice │ alice.new@example.com│ 200  │ 300  │ DEAD TUPLE  │ ← Now also dead!
└────┴───────┴──────────────────────┴──────┴──────┴─────────────┘
```

**Both versions are now dead tuples!**
- The row appears "deleted" to all new queries
- But physically, both versions still exist on disk
- Taking up space

---

## Why Not Delete Immediately?

**Excellent question!** Why keep these dead tuples at all? Why not just delete them immediately?

**Answer: MVCC (Multi-Version Concurrency Control) Benefits**

### Real-World Scenario:

Imagine this happening:

```sql
-- Transaction 1 starts (a long-running analytics query)
BEGIN;
SELECT * FROM users WHERE id = 1;
-- Returns: Alice, alice@example.com
-- Query is processing... takes 10 minutes to complete

-- Meanwhile, Transaction 2 (happens during those 10 minutes)
UPDATE users SET email = 'new@example.com' WHERE id = 1;
COMMIT;

-- Transaction 1 continues (still processing)
SELECT * FROM users WHERE id = 1;
-- Still returns: Alice, alice@example.com (sees old version!)
-- Not the new email!
COMMIT;
```

**What happened?**
- Transaction 1 started before the UPDATE
- Transaction 1 should see a consistent snapshot (the old data)
- This is only possible because the old version (dead tuple) still exists!
- If we deleted it immediately, Transaction 1 would see the new data (inconsistent!)

**This is why dead tuples exist: To support MVCC and transaction isolation!**

### Visual Explanation:

```markdown
Timeline:
T0: Transaction 1 starts → Sees snapshot at T0
T1: Transaction 2 updates row
T2: Transaction 2 commits
T3: Transaction 1 still running → Must still see snapshot at T0
T4: Transaction 1 completes

For T3 to work, old data (dead tuple) must exist until T4!
```

---

## The Problems with Dead Tuples

While dead tuples enable MVCC, they create problems if not cleaned up:

### Problem 1: Wasted Storage Space

```sql
-- Update 1 million products
UPDATE products SET price = price * 1.1 WHERE category = 'Electronics';
-- Result: 1 million NEW rows created + 1 million OLD rows (dead tuples)
-- Table size just DOUBLED!
```

**Real numbers:**
```markdown
Before UPDATE:
- Table size: 1 GB (1 million rows)

After UPDATE:
- Table size: 2 GB (1 million live + 1 million dead)
- Wasted space: 1 GB

After 10 UPDATEs:
- Table size: 11 GB (1 million live + 10 million dead!)
- Wasted space: 10 GB
```

### Problem 2: Slower Queries

When PostgreSQL scans a table, it has to read BOTH live tuples AND dead tuples!

```sql
-- Query needs to find active users
SELECT * FROM users WHERE active = true;

-- What actually happens:
-- Scans: 100,000 live rows + 50,000 dead tuples = 150,000 rows total!
-- Then filters out the 50,000 dead tuples
-- Returns: 100,000 rows
```

**Performance Impact:**
```markdown
Table with no dead tuples:
- Query scans 100,000 rows
- Time: 50ms

Table with 50% dead tuples:
- Query scans 150,000 rows
- Time: 75ms (50% slower!)

Table with 90% dead tuples:
- Query scans 1,000,000 rows (100k live + 900k dead)
- Time: 500ms (10x slower!)
```

### Problem 3: Index Bloat

Indexes also contain pointers to dead tuples!

```sql
-- Index on email
CREATE INDEX idx_users_email ON users(email);

-- After many UPDATEs:
-- Index contains:
--   - 100,000 pointers to live rows
--   - 50,000 pointers to dead tuples

-- Index size doubles!
-- Index lookups slower!
```

**Visual:**
```markdown
Healthy Index (B+ Tree):
       [Root]
      /      \
  [Node]    [Node]
   /  \      /  \
 Live Live Live Live

Bloated Index:
       [Root]
      /      \
  [Node]    [Node]
   /  \      /  \
 Live Dead Live Dead
 Live Dead Dead Dead

More nodes = Slower lookups!
```

### Problem 4: Transaction ID Wraparound

PostgreSQL uses 32-bit transaction IDs. After 2 billion transactions:
- IDs wrap around
- Old dead tuples might appear as "future" rows
- Database can become corrupt!

**Solution:** Clean up dead tuples before this happens!

---

## Solution: VACUUM

PostgreSQL has a process called **VACUUM** that cleans up dead tuples.

**What VACUUM does:**
1. Identifies dead tuples (no transaction needs them anymore)
2. Marks space as reusable
3. Updates statistics
4. Prevents transaction ID wraparound

### Types of VACUUM

#### 1. VACUUM (Regular)

```sql
-- Clean up dead tuples in users table
VACUUM users;

-- Clean up entire database
VACUUM;
```

**What it does:**
- Marks dead tuples as reusable space
- Updates statistics
- **Does NOT** shrink the file (table stays same size on disk)

**When to use:** Regular maintenance

#### 2. VACUUM FULL

```sql
-- Aggressive cleanup - reclaims disk space
VACUUM FULL users;
```

**What it does:**
- Rewrites entire table
- Removes dead tuples completely
- Shrinks table file on disk
- **Requires exclusive lock** (table unavailable during VACUUM FULL)

**When to use:** When table is heavily bloated and you can afford downtime

**Example:**
```markdown
Before VACUUM FULL:
- Table size on disk: 10 GB
- Live data: 2 GB
- Dead tuples: 8 GB

After VACUUM FULL:
- Table size on disk: 2 GB
- Live data: 2 GB
- Dead tuples: 0 GB
- Reclaimed: 8 GB!
```

#### 3. VACUUM ANALYZE

```sql
-- VACUUM + update statistics for query planner
VACUUM ANALYZE users;
```

**What it does:**
- Everything VACUUM does
- Plus: Updates table statistics
- Helps query planner make better decisions

**When to use:** After bulk updates/deletes

---

## Autovacuum (Automatic Cleanup)

PostgreSQL has **autovacuum** - a background process that automatically cleans up dead tuples!

**Default behavior:**
- Runs automatically in the background
- Monitors all tables
- Triggers VACUUM when needed

### When Autovacuum Runs

Autovacuum triggers when:
```
Number of dead tuples > threshold + (scale_factor * number of live tuples)
```

**Default settings:**
```sql
-- postgresql.conf
autovacuum = on  -- Enabled by default
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.2
```

**Example calculation:**
```markdown
Table: users
- Live rows: 1,000,000
- Threshold: 50
- Scale factor: 0.2

Autovacuum triggers when:
Dead tuples > 50 + (0.2 * 1,000,000)
Dead tuples > 50 + 200,000
Dead tuples > 200,050

So autovacuum runs when 20% of rows are dead!
```

### Configuring Autovacuum Per Table

```sql
-- More aggressive autovacuum for frequently updated table
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.05,  -- Run at 5% dead tuples
    autovacuum_vacuum_threshold = 100
);

-- Disable autovacuum for a table (not recommended!)
ALTER TABLE logs SET (autovacuum_enabled = false);
```

---

## Monitoring Dead Tuples

### Check Dead Tuple Count

```sql
-- See dead tuples for all tables
SELECT 
    schemaname,
    relname as table_name,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_percentage,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

**Example Output:**
```
table_name | live_rows | dead_rows | dead_percentage | last_vacuum          | last_autovacuum
-----------|-----------|-----------|-----------------|----------------------|------------------
orders     | 500000    | 125000    | 20.00%          | NULL                 | 2024-11-18 10:00
users      | 100000    | 25000     | 20.00%          | 2024-11-17 08:30     | 2024-11-18 09:30
products   | 50000     | 5000      | 9.09%           | NULL                 | 2024-11-18 08:00
logs       | 1000000   | 10000     | 0.99%           | 2024-11-18 06:00     | NULL
```

**What to look for:**
- `dead_percentage` > 20% → Consider manual VACUUM
- `last_autovacuum` is old → Autovacuum might not be keeping up
- High `dead_rows` → Table is bloated

### Check Table Bloat

```sql
-- Estimate table bloat
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Monitor Autovacuum Activity

```sql
-- See currently running autovacuum processes
SELECT 
    pid,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE query LIKE '%autovacuum%' AND query NOT LIKE '%pg_stat_activity%';
```

---

## Best Practices for Managing Dead Tuples

### 1. Let Autovacuum Do Its Job

```sql
-- Make sure autovacuum is enabled
SHOW autovacuum;  -- Should be 'on'
```

**Don't disable autovacuum unless you have a very good reason!**

### 2. Manual VACUUM After Bulk Operations

```sql
-- After deleting 1 million old records
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '1 year';

-- Run VACUUM immediately
VACUUM ANALYZE logs;
```

### 3. Tune Autovacuum for High-Update Tables

```sql
-- Tables that update frequently need more aggressive autovacuum
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);
```

### 4. Monitor Regularly

```bash
# Set up monitoring alerts
# Alert if dead_percentage > 30% for any table
# Alert if autovacuum hasn't run in 24 hours
```

### 5. Schedule VACUUM FULL During Maintenance Windows

```sql
-- Only during off-peak hours (requires table lock)
VACUUM FULL orders;  -- Run on Sunday 2 AM
```

### 6. Partition Large Tables

```sql
-- Instead of one huge table with lots of dead tuples
-- Partition by date
CREATE TABLE orders_2024_11 PARTITION OF orders
FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');

-- Drop old partitions instead of DELETE
DROP TABLE orders_2024_01;  -- Much faster than DELETE!
```

---

## Real-World Example: E-commerce Order Table

### Scenario:
```sql
-- Orders table
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT,
    total_amount DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 10 million orders
-- Order status updates frequently: 'pending' → 'processing' → 'shipped' → 'delivered'
-- Each status update creates a dead tuple!
```

### Problem:
```markdown
After 1 month:
- 10 million orders
- Each order updated 3 times (status changes)
- Dead tuples: 30 million!
- Table bloated to 4x original size
- Queries slowing down
```

### Solution:

```sql
-- Step 1: Check the damage
SELECT 
    pg_size_pretty(pg_total_relation_size('orders')) as total_size,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_percentage
FROM pg_stat_user_tables
WHERE relname = 'orders';

-- Output:
-- total_size | live_rows  | dead_rows  | dead_percentage
-- 15 GB      | 10,000,000 | 30,000,000 | 75.00%

-- Step 2: Immediate fix - manual VACUUM
VACUUM ANALYZE orders;
-- Takes 10 minutes, but reclaims space for reuse

-- Step 3: Configure aggressive autovacuum
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.05,  -- Run at 5% dead
    autovacuum_vacuum_threshold = 10000,
    autovacuum_analyze_scale_factor = 0.02
);

-- Step 4: Schedule weekly VACUUM FULL during maintenance
-- (Sunday 2 AM when traffic is low)
VACUUM FULL orders;
-- Takes 1 hour, but shrinks table from 15 GB to 4 GB
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Disabling Autovacuum

```sql
-- WRONG: Never do this!
ALTER TABLE users SET (autovacuum_enabled = false);
```

**Result:** Table bloats uncontrollably, queries slow down, eventually database issues.

### ❌ Mistake 2: Running VACUUM FULL on Production During Peak Hours

```sql
-- WRONG: Don't run during business hours!
-- Tuesday 2 PM
VACUUM FULL orders;  -- Locks table for 2 hours!
```

**Result:** All orders grind to a halt, customers can't place orders.

### ❌ Mistake 3: Ignoring Monitoring

```markdown
-- WRONG: "It's fine, autovacuum handles it"
-- Months later: Table has 90% dead tuples
```

**Result:** Queries become extremely slow, emergency maintenance needed.

### ❌ Mistake 4: Using DELETE for Purging Old Data

```sql
-- WRONG: Creates tons of dead tuples
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '1 year';
-- Deletes 100 million rows → 100 million dead tuples!
```

**Better:** Use partitioning and drop old partitions:
```sql
-- RIGHT: Instant, no dead tuples
DROP TABLE logs_2023;
```

---

## Summary Table

| Aspect | Description |
|--------|-------------|
| **What is it?** | Old row versions that are no longer visible to any transaction |
| **Why exists?** | MVCC - allows consistent reads without locks |
| **Created by** | UPDATE and DELETE operations |
| **Problems** | Wasted space, slower queries, index bloat |
| **Solution** | VACUUM (automatic via autovacuum) |
| **Monitoring** | `pg_stat_user_tables` view |
| **When to worry?** | When dead_percentage > 20-30% |
| **Prevention** | Let autovacuum run, tune for high-update tables |

---

## Key Takeaways

1. **Dead tuples are a feature, not a bug** - They enable MVCC and transaction isolation

2. **They become a problem when not cleaned up** - Waste space and slow queries

3. **Autovacuum is your friend** - It automatically cleans up dead tuples

4. **Monitor regularly** - Check `pg_stat_user_tables` for bloat

5. **Tune per table** - High-update tables need more aggressive autovacuum

6. **Use partitioning** - For tables with time-based deletes

7. **VACUUM FULL is a last resort** - Only during maintenance windows

---

**Connection to Previous Days:**
- **Day 08**: We discussed MVCC and mentioned vacuum - now you understand WHY vacuum is needed!
- **Day 09**: Sharding increases complexity - each shard has its own dead tuples to manage
- **Day 10**: Replication also replicates dead tuples - they need vacuuming on replicas too!