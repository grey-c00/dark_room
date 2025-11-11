So far we know:
1. What is SQL and why it exists
2. How to create tables and perform CRUD operations
3. What are indexes and how they work (B+ Tree)
4. How PostgreSQL stores data on disk
5. What is MVCC, transactions, and locks
6. **What is horizontal scaling/sharding** - splitting data across multiple servers

Today, we will understand **Database Replication & High Availability**.

---

## Recap: Why Sharding Was Needed

From Day 09, we learned that when data grows beyond what a single server can handle (e.g., 1.5 TB when we only have 1 TB SSD), we split data across multiple servers (shards).

Example:
- Server A: Contains users with even userIds
- Server B: Contains users with odd userIds

This solves the **storage problem**. But it creates new problems...

---

## Problems with Current Setup (Even After Sharding)

### Problem 1: What if a server goes down?

Imagine this scenario:
```markdown
           ┌──────────────┐
           │  App Server  │
           └──────┬───────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────────┐        ┌────────┐
    │Shard 1 │        │Shard 2 │
    │Even IDs│        │Odd IDs │
    └────────┘        └────────┘
         ❌              ✅
      (DOWN)         (Working)
```

**Result:** 
- All users with even userIds cannot access the system
- 50% of your users are locked out
- Data loss if the server crashed without backup
- **This is called a Single Point of Failure (SPOF)**

### Problem 2: Read-Heavy Workload

Let's say your application has:
- 90% READ operations (SELECT queries)
- 10% WRITE operations (INSERT, UPDATE, DELETE)

**Current problem:**
- All reads and writes go to the same server
- Server gets overwhelmed with read requests
- Even though we have storage capacity, we don't have enough CPU/RAM to handle concurrent reads

**Question for you:** 
If we have 10,000 read requests per second on Shard 1, and the server can only handle 2,000 requests per second, what happens?

<Write your answer here>

---

## Solution: Database Replication

**Replication** = Copying the same data to multiple servers

Instead of having just one Shard 1, we have multiple copies:

```markdown
           ┌──────────────┐
           │  App Server  │
           └──────┬───────┘
                  │
         ┌────────┴────────────────┐
         │                         │
    ┌────────┐              ┌────────┐
    │Shard 1 │              │Shard 2 │
    └────┬───┘              └───┬────┘
         │                      │
    ┌────┴─────┐           ┌────┴─────┐
    │          │           │          │
┌───────┐  ┌───────┐   ┌───────┐  ┌───────┐
│Shard 1│  │Shard 1│   │Shard 2│  │Shard 2│
│Master │  │Replica│   │Master │  │Replica│
│(Write)│  │(Read) │   │(Write)│  │(Read) │
└───────┘  └───────┘   └───────┘  └───────┘
```

**Benefits:**
1. **High Availability**: If Master goes down, Replica can take over
2. **Load Distribution**: Reads can be distributed across replicas
3. **Backup**: Always have a copy of data

---

## Types of Replication

### 1. Master-Slave Replication (Most Common)

**Architecture:**
```markdown
┌─────────────┐
│   Master    │  ← All WRITES go here
│  (Primary)  │
└──────┬──────┘
       │
       │ (replication)
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
┌──────┐┌──────┐┌──────┐┌──────┐
│Slave1││Slave2││Slave3││Slave4│  ← READS distributed here
└──────┘└──────┘└──────┘└──────┘
```

**How it works:**
1. All **WRITE** operations (INSERT, UPDATE, DELETE) go to **Master**
2. Master records all changes in a **replication log** (e.g., WAL in PostgreSQL)
3. **Slaves** continuously read from Master's log and apply the same changes
4. All **READ** operations (SELECT) can be distributed across Slaves

**Advantages:**
- ✅ Master handles writes efficiently (no conflicts)
- ✅ Slaves handle reads, reducing load on Master
- ✅ Can add more slaves to handle more reads
- ✅ If a slave goes down, other slaves continue working

**Disadvantages:**
- ❌ Master is still a Single Point of Failure (SPOF) for writes
- ❌ If Master goes down, you need to promote a Slave to Master (failover)
- ❌ Replication lag - slaves might be slightly behind Master

### 2. Master-Master Replication (Multi-Master)

**Architecture:**
```markdown
┌─────────────┐  ←→  ┌─────────────┐
│   Master 1  │      │   Master 2  │
│ (Read/Write)│  ←→  │ (Read/Write)│
└─────────────┘      └─────────────┘
     Both can accept writes
     Both sync with each other
```

**How it works:**
1. Both servers can accept WRITE operations
2. Changes are synced between both masters
3. Both can handle READ operations

**Advantages:**
- ✅ No single point of failure for writes
- ✅ Better availability - if one master goes down, other continues
- ✅ Can distribute writes geographically

**Disadvantages:**
- ❌ **Write conflicts** - What if both masters update the same row simultaneously?
- ❌ More complex to manage
- ❌ Conflict resolution logic needed

**Example of Write Conflict:**

```markdown
Time T1:
Master 1: UPDATE users SET age=30 WHERE id=1;
Master 2: UPDATE users SET age=35 WHERE id=1;

Which value should win? 30 or 35?
```

**Conflict Resolution Strategies:**
1. Last Write Wins (based on timestamp)
2. Version Vectors
3. Application-level conflict resolution

---

## Replication Strategies

### 1. Synchronous Replication

**How it works:**
```markdown
1. Client sends WRITE to Master
2. Master writes to its disk
3. Master waits for Slave to acknowledge write
4. Slave writes to its disk and sends ACK
5. Master responds to Client: "Write successful"
```

**Characteristics:**
- ✅ **Strong Consistency**: Slave always has latest data
- ✅ No data loss if Master crashes
- ❌ **Slower writes**: Must wait for Slave's acknowledgment
- ❌ If Slave is down or slow, writes are delayed

**Example Timeline:**
```
Client → Master: Write Request (t=0ms)
Master → Disk: Write (t=10ms)
Master → Slave: Replicate (t=15ms)
Slave → Disk: Write (t=25ms)
Slave → Master: ACK (t=30ms)
Master → Client: Success (t=35ms)

Total time: 35ms
```

### 2. Asynchronous Replication (More Common)

**How it works:**
```markdown
1. Client sends WRITE to Master
2. Master writes to its disk
3. Master immediately responds to Client: "Write successful"
4. Master sends changes to Slave in background
5. Slave applies changes when it can
```

**Characteristics:**
- ✅ **Faster writes**: Don't wait for Slave
- ✅ Master not affected by Slave's performance
- ❌ **Eventual Consistency**: Slave might be slightly behind
- ❌ Possible data loss if Master crashes before replicating

**Example Timeline:**
```
Client → Master: Write Request (t=0ms)
Master → Disk: Write (t=10ms)
Master → Client: Success (t=12ms)
Master → Slave: Replicate (background, t=15ms)

Total time: 12ms (much faster!)
```

### 3. Semi-Synchronous Replication

A compromise between the two:
- Wait for **at least one** slave to acknowledge
- Don't wait for all slaves

**PostgreSQL, MySQL both support this!**

---

## Replication Lag

**Replication Lag** = Time delay between Master's write and Slave catching up

**Example:**
```
T=0:  Master: User's balance = $100
T=1:  Master: UPDATE balance = $50 (user withdrew $50)
T=2:  User refreshes page, reads from Slave
T=2:  Slave still shows: balance = $100 (hasn't caught up yet)
T=5:  Slave catches up: balance = $50
```

**Problems caused by lag:**
- User sees stale data
- Inconsistent user experience
- "I just updated my profile, why do I see old data?"

**Solutions:**
1. **Read from Master** for critical reads (after recent writes)
2. **Session Stickiness** - keep user connected to same replica
3. **Read Your Writes** consistency pattern
4. Monitor lag and alert if it's too high

---

## High Availability & Failover

### What is High Availability (HA)?

**High Availability** = System remains operational even when components fail

**Measured in "nines":**
- 99% availability = 3.65 days downtime per year
- 99.9% availability = 8.76 hours downtime per year
- 99.99% availability = 52.56 minutes downtime per year
- 99.999% availability = 5.26 minutes downtime per year (five nines!)

### Failover Mechanism

**Failover** = Switching from a failed Master to a Slave

**Scenario: Master goes down**

```markdown
Before Failover:
┌─────────────┐
│   Master    │  ❌ CRASHED
└──────┬──────┘
       │
   ┌───┴───┬───────┐
   │       │       │
┌──────┐┌──────┐┌──────┐
│Slave1││Slave2││Slave3│
└──────┘└──────┘└──────┘

After Failover:
┌──────────────────────┐
│   Slave1 (promoted)  │  ← Now the new Master
│   NEW MASTER         │
└──────────┬───────────┘
           │
       ┌───┴───────┐
       │           │
   ┌──────┐    ┌──────┐
   │Slave2│    │Slave3│
   └──────┘    └──────┘
```

### Types of Failover

#### 1. Automatic Failover

**How it works:**
1. Monitoring system detects Master is down (health checks fail)
2. System automatically promotes a Slave to Master
3. Application is redirected to new Master
4. DNS or load balancer updated

**Tools:**
- PostgreSQL: `Patroni`, `repmgr`
- MySQL: `MHA (Master High Availability)`
- Cloud: AWS RDS, Google Cloud SQL (built-in)

**Advantages:**
- ✅ Fast recovery (seconds to minutes)
- ✅ No human intervention needed
- ✅ Works 24/7 even when engineers are sleeping

**Risks:**
- ❌ Split-brain problem (two masters think they're primary)
- ❌ Data loss if replication lag exists

#### 2. Manual Failover

**How it works:**
1. Engineer is alerted that Master is down
2. Engineer investigates and verifies
3. Engineer manually promotes Slave to Master
4. Engineer updates application configuration

**Advantages:**
- ✅ Human verification before failover
- ✅ Can choose which slave to promote
- ✅ Less risk of split-brain

**Disadvantages:**
- ❌ Slower (can take 15-60 minutes)
- ❌ Requires on-call engineers
- ❌ Downtime during investigation

---

## Split-Brain Problem

**Split-Brain** = Multiple servers think they are the Master

**How it happens:**
```markdown
Scenario:
1. Master and Slave are running
2. Network partition occurs (they can't communicate)
3. Monitoring system thinks Master is down
4. Slave is promoted to new Master
5. Old Master is still running (but isolated)

Result:
┌─────────────┐         ┌─────────────┐
│ Old Master  │    X    │ New Master  │
│ (Isolated)  │         │ (Promoted)  │
└─────────────┘         └─────────────┘
     Both think they're Primary!
     Both accept writes!
     Data diverges!
```

**Solution: Fencing / STONITH**
- "Shoot The Other Node In The Head"
- When promoting a new Master, explicitly shut down old Master
- Use techniques like:
  - Power off old server
  - Remove its network access
  - Use distributed consensus (e.g., Quorum)

---

## CAP Theorem (Brief Introduction)

**CAP Theorem** states that a distributed database can only guarantee 2 out of 3:

1. **C**onsistency - All nodes see the same data at the same time
2. **A**vailability - Every request gets a response (success or failure)
3. **P**artition Tolerance - System works even when network is broken

```markdown
        C (Consistency)
           /\
          /  \
         /    \
        /  CP  \
       /   or   \
      /    AP    \
     /____________\
    A              P
(Availability)  (Partition Tolerance)

You can pick only 2!
```

**Examples:**
- **CP System** (Consistency + Partition Tolerance): Traditional SQL databases with synchronous replication
  - Chooses consistency over availability
  - May reject writes if can't guarantee consistency
  
- **AP System** (Availability + Partition Tolerance): Cassandra, DynamoDB
  - Chooses availability over consistency
  - May serve stale data, but always responds
  
- **CA System** (Consistency + Availability): Single-node databases
  - No partition tolerance (doesn't work in distributed systems)

**Real-world trade-off:**
```sql
-- Banking system (CP)
-- Would rather be unavailable than show wrong balance
-- Must have strong consistency

-- Social media feed (AP)
-- Would rather show slightly old posts than be unavailable
-- Can tolerate eventual consistency
```

---

## Real-World Example: PostgreSQL Streaming Replication

### Setting Up Streaming Replication

**On Master:**
```bash
# postgresql.conf
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1GB

# pg_hba.conf (allow replication connection)
host replication replicator 192.168.1.0/24 md5
```

**On Slave:**
```bash
# Create standby.signal file
touch /var/lib/postgresql/data/standby.signal

# postgresql.conf
primary_conninfo = 'host=master_ip port=5432 user=replicator password=xxx'
hot_standby = on
```

**Monitoring replication lag:**
```sql
-- On Master
SELECT client_addr, state, sync_state, 
       pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS lag_bytes
FROM pg_stat_replication;

-- On Slave
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn(), 
       pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) AS lag;
```

---

## Backup & Recovery Strategies

Even with replication, you need backups! Why?
- Replication protects against hardware failure
- Backups protect against human errors and data corruption

### Types of Backups

#### 1. Logical Backup
Export database as SQL statements.

```bash
# PostgreSQL
pg_dump mydb > mydb_backup.sql

# MySQL
mysqldump mydb > mydb_backup.sql
```

**Characteristics:**
- ✅ Human-readable
- ✅ Can restore specific tables
- ❌ Slower for large databases
- ❌ Larger file size

#### 2. Physical Backup
Copy actual database files.

```bash
# PostgreSQL Base Backup
pg_basebackup -D /backup/location -Ft -z -P
```

**Characteristics:**
- ✅ Faster for large databases
- ✅ Smaller file size (with compression)
- ❌ Must restore entire database
- ❌ Not human-readable

### Recovery Strategies

#### Point-in-Time Recovery (PITR)

**Scenario:** 
```markdown
Monday 9 AM: Full backup taken
Tuesday 3 PM: Developer accidentally runs: DELETE FROM users;
Tuesday 3:01 PM: "OH NO!"
```

**Solution:** Restore to Tuesday 2:59 PM (before the accident)

**How it works:**
1. Restore from last full backup (Monday 9 AM)
2. Replay Write-Ahead Log (WAL) up to Tuesday 2:59 PM
3. Database is now in state before the accident

```sql
-- PostgreSQL PITR
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2024-11-12 14:59:00'
```

#### Hot vs Cold Backups

**Cold Backup:**
- Database must be shut down
- Guaranteed consistent state
- ❌ Requires downtime

**Hot Backup:**
- Database keeps running
- Backups happen in background
- ✅ No downtime
- More common in production

---

## Read Replicas vs Backup Replicas

**Read Replica:**
- Actively serves read queries
- Reduces load on Master
- Up-to-date (or nearly so)
- Used for performance

**Backup Replica:**
- Not serving queries
- Kept for disaster recovery
- May be geographically distant
- Used for safety

**Best Practice:** Have both!

```markdown
┌─────────────┐
│   Master    │
│ (us-east-1) │
└──────┬──────┘
       │
   ┌───┴────────────────┬─────────────┐
   │                    │             │
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Read Replica │  │ Read Replica │  │Backup Replica│
│ (us-east-1)  │  │ (us-east-1)  │  │ (us-west-2)  │
│ Serves reads │  │ Serves reads │  │   Disaster   │
│              │  │              │  │   Recovery   │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## AWS RDS Example (Real-World)

Amazon RDS handles replication automatically:

**Features:**
1. **Multi-AZ Deployment** (High Availability)
   - Synchronous replication to standby in different Availability Zone
   - Automatic failover in 60-120 seconds
   - Used for disaster recovery, NOT for reads

2. **Read Replicas** (Performance)
   - Asynchronous replication
   - Can create up to 5 read replicas
   - Can be in different regions
   - Used for distributing read load

```markdown
AWS RDS Multi-AZ:
┌──────────────────┐       ┌──────────────────┐
│  Availability    │       │  Availability    │
│   Zone A         │       │   Zone B         │
│                  │       │                  │
│  ┌──────────┐   │ sync  │  ┌──────────┐   │
│  │  Master  │───┼───────┼──│ Standby  │   │
│  └──────────┘   │       │  └──────────┘   │
└──────────────────┘       └──────────────────┘

If Zone A fails, automatic failover to Zone B
```

---

## Best Practices Summary

1. **Always use replication** for production databases
   - At least 1 Master + 1 Slave (minimum)
   - Prefer 1 Master + 2+ Slaves for better availability

2. **Choose replication strategy based on needs:**
   - Synchronous for financial/critical data
   - Asynchronous for better performance
   - Semi-synchronous as compromise

3. **Monitor replication lag**
   - Alert if lag exceeds threshold (e.g., 10 seconds)
   - Have runbooks for handling lag

4. **Plan for failover**
   - Test failover procedures regularly (quarterly)
   - Document steps clearly
   - Consider automatic failover for 24/7 operations

5. **Take regular backups**
   - Daily full backups (minimum)
   - Continuous WAL archiving
   - Test restore procedures

6. **Separate concerns:**
   - Read Replicas for performance
   - Backup Replicas for disaster recovery
   - Don't rely on Read Replicas as backups!

7. **Geographic distribution:**
   - Keep backup replica in different region
   - Protects against regional disasters

---

## Connection to Previous Days

- **Day 01-02**: We learned about chunking and fast searches
  - Replication uses similar concepts for distributing data!

- **Day 08**: We learned about B+ Trees and how indexes work
  - Both Master and Slaves have indexes
  - Replication must keep indexes in sync

- **Day 09**: We learned about horizontal scaling/sharding
  - Sharding = split data for storage capacity
  - Replication = copy data for reliability and read performance
  - Real systems use BOTH: Shard + Replicate each shard!

**Combined Architecture:**
```markdown
           ┌──────────────┐
           │  App Server  │
           └──────┬───────┘
                  │
         ┌────────┴────────────┐
         │                     │
    ┌────────┐            ┌────────┐
    │Shard 1 │            │Shard 2 │
    │Master  │            │Master  │
    └────┬───┘            └───┬────┘
         │                    │
    ┌────┴─────┐         ┌────┴─────┐
    │          │         │          │
┌───────┐  ┌───────┐ ┌───────┐  ┌───────┐
│Shard 1│  │Shard 1│ │Shard 2│  │Shard 2│
│Replica│  │Replica│ │Replica│  │Replica│
└───────┘  └───────┘ └───────┘  └───────┘

This is how real large-scale systems work!
(Facebook, Google, Amazon, etc.)
```

---

## Practice Questions

### Conceptual Questions:

1. **What is the difference between sharding and replication?**

2. **Explain Master-Slave replication. Why do we send all writes to Master?**

3. **What is replication lag? Give an example where it could cause problems for users.**

4. **What is the difference between synchronous and asynchronous replication? When would you choose each?**

5. **Explain the split-brain problem. How can it be prevented?**

6. **What is the CAP theorem? Give examples of CP and AP systems.**

7. **Why do we need backups even if we have replication?**

8. **What is Point-in-Time Recovery (PITR)? Give a scenario where it would be useful.**

9. **Explain the difference between Read Replica and Backup Replica.**

10. **What is automatic failover? What are the risks?**

### Practical Scenarios:

**Scenario 1: E-commerce Website**
You're building an e-commerce site with these requirements:
- 1 million products
- 100,000 active users daily
- 80% reads (browsing), 20% writes (orders, updates)
- Must be available 24/7
- Orders must be accurate (no lost data)

Design a database architecture including:
- Number of servers
- Replication strategy
- Backup strategy
- Justify your choices

**Scenario 2: Banking Application**
You're designing a banking system where:
- Account balances must always be accurate
- Can tolerate a few seconds of downtime
- Cannot afford to show wrong balance to users
- Regulatory requirement: Must have 30 days of backups

Questions:
1. Would you use synchronous or asynchronous replication? Why?
2. How many replicas would you keep?
3. What backup strategy would you use?
4. CP or AP system? Justify.

**Scenario 3: Social Media Feed**
Designing a social media platform where:
- Users post updates
- Other users view feeds
- 95% reads (viewing feeds), 5% writes (posting)
- Okay if users see posts with 1-2 seconds delay
- Must never go down (availability is critical)

Questions:
1. How would you distribute read load?
2. What replication strategy?
3. How many read replicas?
4. CP or AP system?

**Scenario 4: Disaster Recovery**
Your Master database crashes and cannot be recovered. You have:
- 1 Read Replica (2 seconds behind)
- 1 Backup Replica in different region (10 seconds behind)
- Last night's full backup
- WAL logs up to 1 minute ago

Questions:
1. What data have you lost?
2. Which replica would you promote to Master? Why?
3. How would you prevent this in future?
4. What is your RTO (Recovery Time Objective)?

### Challenge Questions:

1. **Design a failover system:**
   Write pseudocode for an automatic failover system that:
   - Detects when Master is down
   - Chooses which Slave to promote
   - Prevents split-brain
   - Updates application configuration

2. **Replication lag monitoring:**
   You notice replication lag is increasing:
   ```
   T=0:  Lag = 1 second
   T=1:  Lag = 3 seconds
   T=2:  Lag = 7 seconds
   T=3:  Lag = 15 seconds
   ```
   What could be the causes? How would you fix it?

3. **Read-your-writes consistency:**
   User posts a comment and immediately refreshes the page. Due to replication lag, they don't see their comment. Design a solution that ensures users always see their own writes.

4. **Cost optimization:**
   You have:
   - 1 Master (m5.4xlarge) = $100/day
   - 5 Read Replicas (m5.4xlarge each) = $500/day
   
   During off-peak hours (8 PM - 6 AM), traffic drops by 80%.
   How can you optimize costs while maintaining availability?

5. **Cross-region replication:**
   Your users are in USA, Europe, and Asia. Design a multi-region architecture that:
   - Minimizes latency for all users
   - Handles regional failures
   - Keeps data consistent
   - Consider: Which region is Master? How to handle writes?

---

## Additional Resources

**Tools to explore:**
- **PostgreSQL**: Patroni, repmgr, pg_auto_failover
- **MySQL**: MHA, Orchestrator, MySQL Router
- **Cloud**: AWS RDS Multi-AZ, Google Cloud SQL, Azure SQL Database

**Metrics to monitor:**
- Replication lag
- Slave status (is it connected?)
- Disk space (WAL files can accumulate)
- CPU/Memory usage on Master and Slaves

**Testing:**
- Regularly test failover procedures
- Simulate Master failure in staging
- Practice restore from backups
- Measure RTO (Recovery Time Objective) and RPO (Recovery Point Objective)

---

## What's Next?

**Day 11 and beyond could cover:**
- Query optimization (EXPLAIN, indexes strategies)
- Connection pooling (PgBouncer, ProxySQL)
- Monitoring and observability
- Database migrations and schema changes
- Partitioning and table inheritance
- NoSQL databases (when to use SQL vs NoSQL)
- Distributed SQL (CockroachDB, YugabyteDB)

---

**Remember:** 
- Sharding solves **storage and scalability**
- Replication solves **availability and reliability**
- Real production systems need **BOTH**
- Always test your disaster recovery plans!

High availability is not about preventing failures—it's about surviving them gracefully. 🚀

