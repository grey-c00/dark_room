So from, day 7 we know that there are some problems such as 
1. Table contains redundent columns - that should be calculated at the runtime
2. No Indexing on columns - indexes should be added based on search pattern
3. TODO: Add

Problem 1 is easy to handle and problem 2 can be handled based on load pattern. Now, lets understand that how Indexes work at the file level for quick retrivel.

## How Indexes work in DB
A index let the search query succeed, without scanning the entire table.

Reduced search space -> Reduced search time -> Increased query performance

Most relational databases (PostgreSQL, MySQL, SQL Server, Oracle, etc.) use B+ Tree datastructure for ordering Indexes.

Ideally, we should be knowing about B+ Tree because we have already gone through DSA.

But lets understand it again.

In this tree, there is 
1. a root node
2. Internal node [could be zero for very short tables]
3. Leaf Nodes

Job of 
1. root node - is to maintain pointers for its child nodes
2. Internal Node - is to maintain pointers for its child nodes
3. Leaf Node - contains pointer to the memory block that actually hold data.


B+ tree is a balanced tree and by comparing metadata on particular node (root or internal) we will know that where can we potentially find data, either on the left side or the tree or on the right side of the tree. Hence, search can be done in O(Logn) time.

example:
lets say that we create an index on email then - tree might look like as follow - 

```kotlin
               [bob@]
              /      \
 [adam@, alice@]   [bob@, charlie@, david@]
        |                 |             |
        Memory            Memory        Memory

```

Searching for charlie@:

- Read root page (contains [bob@])
- Since charlie@ > bob@, follow right pointer
- Read that leaf page, find the matching row

Each read of a node = one I/O operation, which is why B+ trees are designed to minimize height — so most lookups only touch 2–3 pages total.


To Know more about B+ Tree - go through: https://www.geeksforgeeks.org/dbms/introduction-of-b-tree/

And add any new points, here:
1. New Point:
2. New Point:
3. New Point:
4. New Point:
5. New Point:


## How files are stored in memory
The way, files are created, really dependes on the type of database. Lets understand it for PostgreSQL Database.

When you create a table or an index, PostgreSQL creates separate physical files under its data directory, usually at:
```
/var/lib/postgresql/<version>/main/base/<database_oid>/
```
Each table or index is a separate file, named by its relfilenode (an internal ID).

Lets take a step back and understand it again - 

### The Big Picture — PostgreSQL Storage Hierarchy

```pgsql
Database Cluster
│
├── Databases
│   ├── Schemas
│   │   ├── Tables
│   │   │   ├── Table file(s)
│   │   │   └── Index file(s)
│   │   └── TOAST tables (for large data)
│   └── System catalogs
└── Global objects
```

### Physical Storage on Disk

By default, PostgreSQL stores its data in:
```pgsql
/var/lib/postgresql/<version>/main/
```

Inside the directory:

| Folder       | Contains                               |
| ------------ | -------------------------------------- |
| `base/`      | All user and system databases          |
| `global/`    | Cluster-wide tables (roles, databases) |
| `pg_wal/`    | Write-ahead log (for crash recovery)   |
| `pg_tblspc/` | Tablespace directories (if any)        |
| `pg_stat/`   | Stats data                             |
--------------------------------------------------------

"Question" You must ask what is verion here?


Lets get back to where we left off - 

### Table Files — How Data Rows Are Stored

Each table file (corresponding to a file_id) is made up of 8 KB pages (blocks).

Each block contains:
```sql
+-------------------------------+
| Page Header (24 bytes + ...)  |
| Item Identifiers (row pointers)|
| Tuples (actual rows)          |
| Free Space                    |
+-------------------------------+

```

Visualization:
```sql
|------------------------------------------------|
| Block 0 | Block 1 | Block 2 | Block 3 | ...    |
|------------------------------------------------|

Each Block = 8 KB

Inside each block:
+------------------------------------------------------+
| Header | Item Ids | Tuple 1 | Tuple 2 | Free Space   |
+------------------------------------------------------+
```

- Header — metadata like checksum, LSN, flags
- Item Ids — small directory of where each row lives in this page
- Tuples — the actual rows (ctid points here)
- Free space — room for future inserts/updates

Each row = tuple, containing:
- Heap header (transaction IDs, visibility info)
- Actual data values

### Index Files — How B+ Trees Store Data

When you create an index:
```sql
CREATE INDEX idx_users_email ON users(email);
```
PostgreSQL creates a separate file (e.g., 16386) containing a B+ tree structure.

Each index file is also made of 8 KB pages. And B+ tree maintains a tree like structure (as we dicussed earlier).

### Physical Example: Number of Files

If you have a simple table:
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email TEXT,
  name TEXT
);
CREATE INDEX idx_users_email ON users(email);
```

PostgreSQL creates:

| Object                 | File                  | Description                 |
| ---------------------- | --------------------- | --------------------------- |
| `users`                | `base/16384/24576`    | Main heap table (rows)      |
| `users_pkey`           | `base/16384/24577`    | Primary key index (B+ tree) |
| `idx_users_email`      | `base/16384/24578`    | Secondary index (B+ tree)   |
| (maybe) `pg_toast_...` | for large text fields | Stores big values           |


So, under the hood lot more is going on. Such as
1. write ahead logs for crash recovery
2. Write in disk
3. Updation of indexes
4. Make sure ACID property is maintained by variour checks
5. Maintaining metdata, access level etc.



## What happens during update operation

| Step | What Happens            | Notes                             |
| ---- | ----------------------- | --------------------------------- |
| 1    | Locate tuple            | via index or seq scan             |
| 2    | Create new tuple        | new version with new `xmin`       |
| 3    | Set `xmax` on old tuple | marks it as deleted by current tx |
| 4    | Update indexes          | new entries for updated keys      |
| 5    | Write to WAL            | ensures durability                |
| 6    | Commit                  | transaction marked as committed   |
| 7    | Vacuum later            | cleans up old versions            |

In step3, dead tuples are created which are removed via vaccum. This activity is done asynchronously and can have significant impact on DB. So, it would be great if we consider this operation as well while discussing query optmization.


**This is known as PostgreSQL’s MVCC (Multi-Version Concurrency Control) architecture.**


### What Happens to Files on Disk

- The heap file (table file) gets new tuple versions appended.
- The index file (B+ tree) gets new entries.
- The WAL file records every change.
- The pg_xact file tracks transaction commit state.
- Autovacuum eventually cleans up old tuples.

No existing data file is rewritten in place — everything is append-only, ensuring:
- Crash safety
- Consistent snapshots
- Simple rollback


## PostgreSQL Locks & Concurrency — Quick Reference
PostgreSQL uses MVCC (Multi-Version Concurrency Control):

- Readers never block writers (and vice versa)
- Each transaction sees a snapshot of data as of its start
- Updates create new row versions instead of overwriting

So:
- ✅ SELECT → doesn’t block UPDATE
- ✅ UPDATE → doesn’t block SELECT
- ❌ Two UPDATEs on the same row → conflict (row-level lock)

### Transaction Isolation Levels

| Level               | Behavior                                          | Notes                         |
| ------------------- | ------------------------------------------------- | ----------------------------- |
| **READ COMMITTED**  | Default — each statement sees only committed data | Safe & performant             |
| **REPEATABLE READ** | Sees same snapshot throughout the transaction     | Prevents non-repeatable reads |
| **SERIALIZABLE**    | True serial execution (via predicate locks)       | Slower but safest             |


These isolation levels can be set on db level. Example:

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```


Deadlocks
- Occur when transactions wait on each other in a cycle
- PostgreSQL detects and aborts one automatically

