# Simple concepts

## What is PySpark?
PySpark is the Python API for Apache Spark, a powerful open-source distributed computing framework used for:
- Big Data processing 
- Machine Learning at scale 
- ETL (Extract, Transform, Load) pipelines 
- Data analysis on massive datasets

It allows you to write Spark jobs using Python, while leveraging the power of the underlying JVM-based Spark engine.

###  What is the JVM-based Spark Engine?
Apache Spark is written in Scala, which runs on the JVM (Java Virtual Machine). So when we say Spark has a "JVM-based engine", it means:Spark’s core processing engine, including memory management, task scheduling, and execution, runs inside the JVM.

 ### What is the JVM?
- JVM (Java Virtual Machine) is a virtual environment that runs Java (and JVM-compatible) bytecode.
- Languages like Scala, Java, Kotlin, and Clojure compile to JVM bytecode.
- It’s highly optimized for performance and memory management, especially on large-scale systems.

Why Spark Uses the JVM:
- Mature ecosystem: Built-in support for distributed computing (via Hadoop, etc.)
- JIT Compilation: Just-In-Time compilation for speed
- Automatic Garbage Collection: Memory is efficiently managed
- High Performance: JVM is battle-tested in enterprise apps


### So How Does PySpark Fit In?
PySpark = Python Interface 🐍 → to the JVM Engine ⚙️

PySpark runs Python code, but under the hood, it talks to the JVM-based Spark engine using Py4J, a gateway between Python and Java.

```commandline
Python (you) → Py4J → JVM (real Spark engine)

```

So when we do - 
```commandline
df.filter(df.age > 30)
```
What really happens:
1. Your Python code constructs commands 
2. Those are sent to the JVM using Py4J 
3. Spark engine executes them in JVM 
4. Results come back to Python

Why This Matters:-
- Python UDFs are slow because data must move in and out of the JVM.
- Built-in functions and SQL run inside the JVM, so they are much faster and more optimizable.


In summary - 
- spark core is written in Scala and runs on the JVM.
- PySpark is the Python API that allows you to interact with Spark using Python.


## Resource management in PySpark:
Lets understand it with an example that we have a master instance (instance_m) and driver instance (instance_d) and three slave (node1, node2 and node3, consider it 4 cores and 8GB RAM).
Here - 
- instance_m: Runs Spark Master (cluster manager)
- instance_d: Runs Spark Driver (your PySpark application)
- node1, node2, node3: Run Spark Executors (where tasks run)

1. When we run spark_submit on driver machine then A JVM process is started on instance_d and it creates a `SparkContext` which initiates a connection to the Master at instance_m:7077 
2. The Driver contacts the Master to request resources. Sends details like: Application ID, Required executor memory and cores. Eg: Driver says to Master: I want 6 cores in total, with 2 cores per executor and 4GB RAM per executor.
3. Master checks cluster state: 3 workers (node1, node2, node3) and each has 4 cores and 8 GB.
    - Master logic: 
      - Create 3 Executors: Each needs 2 cores and 4GB RAM 
      - Total needed: 6 cores, 12 GB RAM 
      - It chooses 3 workers and launches 1 executor on each.
      - `Each executor is a JVM process launched by the Worker node`.
4. All 3 executors notify the Driver: “We’re ready.” The Driver maintains a list of executors and their locations.
5. When an action (like .show() or .collect()) is triggered:
   - Driver breaks job into stages and tasks.
   - Sends tasks to executors based on:
     - Available cores 
     - Data locality 
     - Shuffle dependencies
   - Each executor:
     - Runs up to 2 tasks concurrently (2 cores per executor)
     - Processes partitions of data
6. Executors Finish Their Tasks:
   - Each executor: 
     - Processes its assigned partitions, Runs transformations 
     - Writes task results:
       - To memory (if small)
       - Or to local disk (for shuffle data)
     - Sends completion status and output (if any) back to the Driver
     - If action is collect() or show():
       - Executors send results back over the network to the Driver
       - Driver assembles and displays data
     - If action is write() (e.g., .write.parquet()):
       - Executors write output to storage (HDFS/S3/local FS/etc.)
       - Driver gets only status info, not actual data

7. Driver Gathers Task Completion Info: Driver:
   - Collects metadata for each task 
   - Updates Spark UI / DAG scheduler 
   - If all tasks in a stage are complete → marks stage as finished 
   - If all stages are complete → job is marked as completed
   - Driver also maintains the final state for logs, event timeline, and metrics
8. Post-Action Clean-Up: What happens next depends on what you're doing after the action:
   - More Actions to Run?
     - Executors stay alive and ready to accept new tasks 
     - Driver may re-use them for subsequent actions
   - No More Actions?
     - If you're done with your job (or exiting the program):
       - Driver triggers cleanup:
       - Tells Master it’s done 
       - Executors are shut down by their respective Workers 
     - If using dynamic allocation:
       - Idle executors may time out and get removed








? what about remaining memory and Cores: Either the spark will create idle launch executors upfront and reserve them OR based on configuration if dynamic allocation is allowed then it will do accordingly. Spark can scale down executors automatically if they remain idle for some time (config derived). fter a timeout (e.g., spark.dynamicAllocation.executorIdleTimeout, default is 60s): Executors with no tasks get killed and resources are released. `In standalone more, master won't really claim those resource even if they are under utilized. Only claimed when dyamic config is set to true`.




? is resource allocation happens at the beginning or how?

`Yes, resource allocation happens at the beginning itself. Such as in case of batch job it happens at the beginning, in case of streaming it happens when the streaming query starts. Though, resources might change if Dynamic allocation is enabled.`

### core vs VCPUs
- spark.executor.cores: Number of tasks each executor can run in parallel
- spark.driver.cores: Number of cores (vCPUs) assigned to driver
- spark.default.parallelism	: Default number of tasks per stage (defaults to total vCPUs)
- --total-executor-cores: Total number of vCPUs across all executors

We can say the Core is the actual physical unit that is responsible for execution. While vCPUs is a logical unit. Usually, 1 Core = 2 vCPUs but it can be 1 Core = 1 vCPUs.
When Spark asks for "cores", in most practical (cloud/VM) environments, you’re giving it vCPUs — and that’s okay.

## Caching in PySpark
Caching (and persistence) allows Spark to store intermediate results in memory (or disk) so they can be reused across multiple actions without recomputing them.

Let’s Take This Example:

```python
df = spark.read.csv("bigfile.csv", header=True)

df.cache()  # Step 1: Cache raw input

df_filtered = df.filter("status = 'active'")
df_filtered.groupBy("city").count().show()  # Step 2: Triggers shuffle

```
- Step 1 caches the original input 
- When you do groupBy("city"), Spark must reshuffle the data based on hash(city)
- So, even though the data is cached, it is not pre-shuffled 
- ➡️ Shuffle still happens


### where does the .cache() resides, On driver or each node?
When you cache a DataFrame (or RDD), Spark partitions it and stores each partition in memory (or on disk) on the executor where it was last computed. Spark does not move cached partitions around. The driver only holds references to metadata, not actual data blocks.

So if you cache a DataFrame with 8 partitions and you have 4 executors:
- Some executors may store 2 cached partitions each 
- Others might store more if skewed

### what is there is no enough space to cache the data then what will happen?
If Spark cannot cache all data in memory, it will spill to disk or evict blocks, depending on the storage level used. Disk spill files are temporary and exist on the executor's local disk (check /tmp or spark.local.dir path)


In case of `MEMORY_ONLY` caching - 
- Spark will only use memory 
- If not enough memory:
  - Uncached partitions are **recomputed** when needed

Here, What does “recomputed” mean:- 
- If you're using MEMORY_ONLY and caching fails due to lack of space:
  - Spark will discard that partition 
  - If a future action needs it → Spark re-runs the entire lineage (all previous transformations) to recreate that partition
- What Happens Under the Hood?
  - Spark stores cached partitions in BlockManager
  - When memory is full:
    - It may evict less-used cached blocks using LRU (Least Recently Used) strategy
    - If using MEMORY_AND_DISK, the evicted blocks go to disk
  - If not enough memory + disk (or you use MEMORY_ONLY), blocks are discarded
  - which blocks will be evicted?: 
    - When your executors' memory starts to run out, Spark must evict older or less-used cached data to allow new data to be cached — this is what we call eviction.
    - Eviction is handled by Spark’s BlockManager, which manages the memory used for:
      - Cached data (RDD/DataFrame partitions)
      - Broadcast variables 
      - Shuffle data
    - Only cached RDD/DataFrame blocks are evicted. 
    - Broadcast variables and shuffle blocks are managed differently. 
    - Spark never evicts data actively being used in a task — only idle blocks.
    - Spark uses LRU (Least Recently Used) eviction policy by default.
    - The partition that was used least recently is evicted first when more memory is needed.

### executor memory configuration around caching and computations
Here `--executor-memory` from CLI is equivalent to `spark.executor.memory` from configurations.

Lets understand memory breakdown of PySpark executor - 
```commandline
+----------------------------+  ← Total executor memory (--executor-memory)
| Reserved Memory (~300 MB) |  ← Fixed, for JVM internals [e.g., GC, thread stacks, code cache etc][Not configurable, Spark subtracts this upfront]
+----------------------------+
| Spark Memory              |  ← Managed by Unified Memory Manager
|                            |
|  +----------------------+ |
|  | Execution Memory     | | ← For shuffles, joins, aggregations, sort, etc. [Temporary and released after stage completes]
|  +----------------------+ |
|  | Storage Memory       | | ← For caching/persisting DataFrames/RDDs [May evict cached blocks if execution memory needs more]
|  +----------------------+ |
+----------------------------+

```
#### Dynamic Borrowing Between Execution & Storage:
Thanks to Unified Memory Manager, there’s no hard boundary.

Rules:
- Execution can borrow from Storage by evicting cached blocks 
- Storage CANNOT borrow from Execution (it will fail to cache if space is full)
- This ensures Spark always favors computation over caching

#### Actual Memory Calculations
Lets say, --executor-memory 8g, then Internally:
- Reserved Memory ≈ 300 MB 
- Usable memory = 8 GB - 300 MB = 7.7 GB 
- Spark Memory = ~6.16 GB (by default, 75% of usable memory)
- Default breakdown:
  - Execution = ~3.08 GB 
  - Storage = ~3.08 GB (for cache)

Memory breakdown to Execution and Storage can be controlled by:
```bash
--conf spark.memory.fraction=0.6       # default is 0.6
--conf spark.memory.storageFraction=0.5  # 50% for cache, 50% for execution

```
Meaning:
- 60% of heap goes to Spark memory (execution + storage)
- 50% of that 60% goes to storage (i.e. 30% of total executor memory)


### cache vs Persist

`cache()` is a shorthand for `persist(StorageLevel.MEMORY_AND_DISK)`, meaning it stores data in memory only. While, persist() offers more control over how data is stored, including options like MEMORY_ONLY, MEMORY_AND_DISK_SER, and DISK_ONLY. 


## How to read a big file that is not partitioned (in PBs ) and then process it?
1. in single machine
2. In cluster





## ETL vs ELT

###  ETL (Extract, Transform, Load)
Source --> Transform (cleaning, enrich, dedup, filtering) --> Load (Date Lake, Data Warehouse, etc.)
- Extract: Read from source systems (e.g., SQL, APIs)
- Transform: Clean, validate, aggregate using Spark, Python, etc. 
- Load: Save the result into data warehouse or lake

Used when:
- You have strict data quality rules 
- You want to control logic outside the DB 
- Your warehouse isn't powerful for large transforms

### ELT (Extract, Load, Transform)
Source --> Load (Data Lake, Data Warehouse, etc.) --> Transform (Transform in Snowflake/BigQuery/Databricks, etc.)
- Extract: Read from sources 
- Load: Dump raw data into your data warehouse or data lake 
- Transform: Use SQL / Snowpark / dbt to do analytics

Used when:
- You're using modern cloud warehouses (Snowflake, Redshift, BigQuery)
- Warehouses are optimized for in-warehouse compute 
- You want to keep raw data for auditing or reprocessing


#### Data Lake vs Data Warehouse
These terms are often confused or used interchangeably, but they serve different purposes, and understanding the distinction helps you build better ETL/ELT pipelines and architectures.

| Feature	      |                 Data Lake	                  |                               Data Warehouse |
|---------------|:-------------------------------------------:|---------------------------------------------:|
| Purpose	Store |   raw, unstructured/semi-structured data	   | Store structured, processed, analytical data |
| Data Type	    | All types (text, video, JSON, logs, images) |             	Structured/tabular (SQL tables) |
| Schema	       |               Schema-on-read	               |                              Schema-on-write |
| Storage	      |      Cheap, scalable (e.g., S3, HDFS)	      |           Costly, optimized for fast queries |
| Performance	  |             Slower for queries	             |                        Fast for analytics/BI |
| Examples	     |  AWS S3, Azure Data Lake, HDFS, Delta Lake  |      	Snowflake, Redshift, BigQuery, Synapse |
| Use Cases	    |    ML, big data processing, raw backup	     |             Reporting, dashboards, analytics |

## How to write custom UDFs in PySpark?
UDF is User Defined Function. It is used to extend the functionality of PySpark by allowing you to define your own functions that can be applied to DataFrame columns.

steps to write a custom UDF in PySpark:
1. define a python functions with all of the arguments that it takes
2. use `pyspark.sql.functions.udf` to convert the python function into a UDF, pass python function (defined in step 1) and return type as the arguments.
3. Use this UDF to create a new columns by passing all of the relevant columns (that will be referencing to the python function defined in step 1) to the `withColumn` method of the DataFrame.

```commandline
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, IntegerType, FloatType

spark = SparkSession.builder.appName("Custom UDF Example").getOrCreate()


def to_uppercase(s):
    if s:
        return s.upper()
    return None
    
uppercase_udf = F.udf(to_uppercase, StringType())  # explicity specified the python function and return type

data = [("alice",), ("bob",), (None,)]
df = spark.createDataFrame(data, ["name"])


df_with_uppercase = df.withColumn("name_upper", uppercase_udf(F.col("name")))  # used function with all of the relevant columns, F.lit() and all such functions can be used
df_with_uppercase.show()
```

### performance of udf:
UDFs are usually slow because - 
1. PySpark’s query planner (Catalyst) can’t optimize what's inside a Python UDF. This means:
   - No predicate pushdown 
   - No constant folding 
   - No code generation (like with native functions)
2. Serialization Overhead: Data must be serialized from JVM to Python when using Python UDFs (via Py4J). Results must then be deserialized back into the JVM. This round trip is slow, especially on large datasets.
3. Python UDFs Are Single-Threaded: Each executor runs the UDF in a single Python process, not parallelized within the executor. This becomes a bottleneck on large-scale transformations.

Solution - 
1. Use Built-in Spark SQL Functions wherever possible. Fast, optimized, and run entirely in the JVM.
    ```commandline
    from pyspark.sql.functions import upper
    df.withColumn("name_upper", upper(df["name"]))
    ```
2. Use Pandas UDFs (a.k.a. Vectorized UDFs) (Introduced in Spark 2.3+)

## what is shuffle in Spark?
Shuffle in Spark is one of the most important, yet most expensive operations.

Shuffle is the process of redistributing data across different executors and partitions, usually due to operations that require data movement, such as:
- groupBy 
- reduceByKey 
- join 
- distinct 
- repartition

### Why Does Shuffle Happen?
Because some operations require data with the same key to be on the same executor (or partition).

`rdd.groupByKey()` -> All records with the same key must go to the same task, Spark must shuffle data across the network from different partitions

### Why Is Shuffle Expensive?
| Reason              | Impact                                             |
| ------------------- | -------------------------------------------------- |
| **Disk IO**         | Intermediate results are written to disk           |
| **Network IO**      | Data is transferred across nodes                   |
| **Serialization**   | Data must be serialized/deserialized               |
| **Memory pressure** | Large shuffle can cause OOM if insufficient memory |


### shuffle in local mode
Yes. Any operation that causes a shuffle in cluster mode (e.g., groupBy, join, repartition) will also cause a shuffle in local mode. The only difference is where and how the shuffle happens.

Even though everything runs in a single JVM process:
- Spark still follows the same logical plan:
  - Map → Shuffle → Reduce
- It still creates shuffle stages
- Each stage is divided into tasks, assigned to threads (not distributed across machines)

Here, data will move across the threads in same JVM and Intermediate shuffle files written to local disk. Use `spark.local.dir` conf to see files created in between.

### How number of partitions affect shuffling:
Quick Recap: What Is a Partition?
- A partition is a logical chunk of your data. 
- Each task in Spark operates on one partition. 
- When a shuffle happens, data is re-partitioned → leading to data movement across partitions (and in cluster mode, across executors).

#### So, How Do Partitions Affect Shuffling [TODO, only partially understood]
1. **More partitions → More shuffle tasks → Finer granularity**

    Example: If you do `groupBy(city)` and set `spark.sql.shuffle.partitions=200`
   - Spark will hash-partition the keys into 200 buckets 
   - So 200 shuffle tasks will be created
   -  Pros:
      - Better parallelism (especially in cluster mode)
      - Smaller memory footprint per task
   - Cons:
      - Higher task scheduling overhead 
      - More shuffle file creation 
      - Can overwhelm the driver (especially in local mode)
2. **Fewer partitions → Less parallelism, heavier shuffle load per task**
    Example: If `spark.sql.shuffle.partitions=4`, you only get 4 shuffle tasks
    - Pros:
      - Simpler to manage 
      - Less file IO 
      - Less overhead
3. 


### coalesce vs repartition:
`repartition(n)` : Evenly redistribute data into n partitions
`coalesce(n)`: Merge existing partitions to reduce to n partitions (without full shuffle)

Detailed Comparison: 

| Feature                      | `repartition(n)`                              | `coalesce(n)`                         |
| ---------------------------- | --------------------------------------------- | ------------------------------------- |
| **Shuffle?**                 | ✅ Full shuffle                                | ⚠️ No (or minimal) shuffle            |
| **Use case**                 | Increasing or reorganizing partitions         | Reducing partitions only              |
| **Data movement**            | All data is shuffled and evenly spread        | Only combines adjacent partitions     |
| **Performance**              | Slower (more expensive)                       | Faster (less costly)                  |
| **Partition balance**        | Even                                          | May result in unbalanced partitions   |
| **When to use**              | After filtering, joins, to rebalance workload | Before writing to reduce output files |
| **Can increase partitions?** | ✅ Yes                                         | ❌ No, only reduce                     |

Best Practices:

|                                                                   Scenario |                               Method |
|---------------------------------------------------------------------------:|-------------------------------------:|
| You want to **increase** partitions (after reading a file, before shuffle) |                      `repartition()` |
|  You want to **decrease** partitions (before writing to avoid small files) |                         `coalesce()` |
|                         You're writing large data to disk (e.g., S3, HDFS) | `coalesce(n)` — to reduce file count |
|                                    Data is highly skewed and needs balance |                     `repartition(n)` |
|                       You filtered a large DataFrame to a small result set |                        `coalesce(n)` |


### what do we mean by skewness in data?
Data skew means some partitions contain much more data than others.

This leads to unbalanced workloads where:
- Some tasks finish quickly (small partitions)
- Others take much longer (huge partitions)
- Causes stragglers, poor parallelism, and wasted resources

Imagine you're grouping a DataFrame by a column like country, and your data looks like this:

| Country   | Count      |
| --------- | ---------- |
| India     | 10,000,000 |
| US        | 100,000    |
| UK        | 90,000     |
| Australia | 85,000     |

If Spark partitions data by country hash:
- One partition (India) may hold 90%+ of the data 
- Others are mostly empty

Why Is Skew a Problem in Spark:

| Problem                  | What Happens                                                |
| ------------------------ | ----------------------------------------------------------- |
| **Straggler tasks**      | One task takes much longer → slows down whole stage         |
| **OutOfMemoryError**     | Skewed task may require more memory than available          |
| **Poor CPU usage**       | Most threads are idle waiting for 1 heavy task              |
| **Inefficient shuffles** | Large partitions → huge shuffle data → slow disk/network IO |



### how to control shuffle?

## Why dataframe is efficient then RDD?
DataFrames are more efficient than RDDs in Spark for several reasons:
1. **Optimized Execution**: DataFrames use Catalyst optimizer to optimize query plans, which can reorder operations, push down filters, and apply other optimizations that RDDs do not benefit from.
2. **Tungsten Execution Engine**: DataFrames leverage the Tungsten execution engine, which optimizes memory usage and CPU efficiency by using off-heap memory management and code generation.
3. **Columnar Storage**: DataFrames store data in a columnar format, which allows for better compression and faster access patterns compared to RDDs, which store data in a row-based format.
4. **Built-in Functions**: DataFrames come with a rich set of built-in functions that are optimized for performance, while RDDs require you to write custom functions for most operations.



## what is partitioning in Spark?
## what is partition / shuffle partition
## Partition tuning in transformations
## where and how computations of multiple stages are written? where internal RDDs resides
## How to optimize Spark jobs?
## what happens when we do .collect(), How do i know if OOM happened at driver side or executor side?
1. in cluster mode
2. in local mode


# How many resource should be left for the OS in case of
1. Driver machine
2. master machine
3. executor machine
4. In local mode

# Spark in local mode
Spark local mode runs the entire Spark application (Driver + Executors) on a single machine, using the local CPU cores. It does not use a cluster manager like YARN, Mesos, or Kubernetes.

##  What's Happening Under the Hood?
|            Component |                                                                             Behavior |
|---------------------:|-------------------------------------------------------------------------------------:|
|               Driver |    Runs the main application logic, creates SparkContext, and manages job execution. |
|             Executor | There’s only one executor (no cluster), which runs inside the same JVM as the driver |
|       Task execution |                                    Parallelized via multi-threading, not distributed |
|              Storage |                             Local file system (unless explicitly writing to S3/HDFS) |
|           Scheduling |                        Done by the local thread pool — no external cluster scheduler |
|  ------------------: |                                                        ----------------------------- |

Now lets understand what happens step by step when a job is submitted - 
1. Spark Process Starts
   - You run spark-submit --master local[8] your_script.py
   - This starts a single JVM process on your local machine
   - The JVM will act as:
     - The Driver
     - And contain one Executor (no remote nodes involved) (🧩 Note: In local[8], the Executor is multi-threaded and can run 8 tasks in parallel.)
2. SparkSession Is Created
   - Your Python code calls `SparkSession.builder`
   - Internally, a SparkContext is created
   - Spark initializes its DAG scheduler, task scheduler, memory manager, and thread pool (?created in driver memory ?)
   - Spark sets up a thread pool with 8 threads, one for each core you specified
3. Your DataFrame is Built (Lazy Execution)
   - Spark parses the command but does not load any data yet
   - It builds a logical plan for the read
   - Spark builds a DAG (Directed Acyclic Graph) of transformations
4. Action is Called → Job Starts
   - Spark submits a job
   - The DAG is divided into stages
   - Each stage is divided into tasks
   - Each task is a unit of execution on a partition
   - Let’s say your file is split into 16 partitions
     - Spark generates 16 tasks
     - The tasks are scheduled to run across 8 threads (since local[8]).So: Up to 8 tasks run in parallel, others wait
5. Tasks Execute in Executor (Inside Local JVM)
   - The executor (running in the same JVM) processes partitions using the thread pool
   - CPU utilization: Uses 8 vCPUs in parallel
   - Memory: You can configure it.
   - JVM heap is allocated to store shuffle buffers, broadcast variables, execution data.
6. Data Flow During Execution
   - Read Stage:
     - Reads 16 partitions → 16 tasks 
     - 8 threads pick up first 8 tasks 
     - Next 8 run as soon as threads free up
   - Shuffle Stage (if any):
     - Output from previous stage is shuffled in memory/disk 
     - Spark performs wide dependency joins via hash shuffle 
     - New stage starts, again divided into tasks
   - Final Stage:
     - Aggregated result is collected to Driver 
     - and rest is done such as show() or something
7. Job Completes, JVM Cleans Up
   - All tasks finish
   - Spark prints result to console
   - Spark context shuts down unless you explicitly keep it alive


## Lets understand a bit about memory distribution, JVM, driver and executor memory, os requirements, DAG scheduler, Job scheduler, memory manager, threadpool executor -

```commandline
+-------------------------------------------------------------+
| JVM Process (your PySpark/Spark app)                        |
|                                                             |
|  +------------------+     +-----------------------------+  |
|  | Driver           |     | Executor (local thread pool)|  |
|  |------------------|     |-----------------------------|  |
|  | DAG Scheduler    |     | Task Execution (threads)    |  |
|  | Task Scheduler   |     | Memory Manager              |  |
|  | Thread Pool Mgmt |     | Shuffle / Storage Mgmt      |  |
|  | Accumulators     |     | Broadcast Variables         |  |
|  +------------------+     +-----------------------------+  |
|                                                             |
|        Shared JVM Heap (configurable via --executor-memory)|
+-------------------------------------------------------------+

```

1. JVM Heap Space in Spark
   - The allocated memory area for object storage and processing inside the JVM. 
   - Controlled by:
     - --executor-memory for executors 
     - spark.driver.memory for driver (optional in local mode)
     - Within the heap:
     
        |        Memory Region |                                      Use |
        |---------------------:|-----------------------------------------:|
        | **Execution Memory** |   Used for shuffles, joins, aggregations |
        |   **Storage Memory** |    Used for caching, broadcast variables |
        |      **User Memory** | Internal data structures, Spark overhead |
        |  **Reserved/System** |               JVM internals, GC overhead |
        |---------------------:|-----------------------------------------:|



2. Driver Memory
   - Memory used by the Driver program 
   - Includes:
     - DAG construction 
     - Task scheduling metadata 
     - Collecting results 
     - Broadcast data to executors
   - In local mode, the driver and executor share the same JVM heap → driver-memory setting is ignored unless explicitly set.
3. Where Are Spark Core Components Created?
   - DAG Scheduler
     - Created inside the Driver 
     - Builds the stages from the RDD lineage 
     - Determines shuffle boundaries
   - Task Scheduler
     - Also in the Driver 
     - Takes the stages from DAG scheduler and turns them into task sets 
     - Schedules them to be executed (in local mode → to internal thread pool)
   - ThreadPool Scheduler (Task Execution)
     - Created in Executor backend 
     - Number of threads = number of cores 
     - In local mode, uses localSchedulerBackend which runs tasks in threads in the same JVM
   - Memory Manager
     - Initialized inside each executor 
     - Splits memory into:
       - Execution memory 
       - Storage memory
       - Unified Memory Manager introduced in Spark 1.6 combines both execution and storage spaces (dynamically grows/shrinks based on pressure)
4. 


## Serializer in Pyspark
### Kryo vs Java

# Spark in standalone mode
# spark in cluster mode such as EMR
# Spark executor and driver memory

# Spark Architecture (master, driver, slave)

# what if master and driver are sitting on same instance?

# Spark UI
port: 4040 (default)

port can be changed by updating the configuration: `spark.ui.port`

# Spark Join Strategies, Sorting & Merging — Complete Internal Deep Dive

---

## 📌 The Big Picture — How Spark Picks a Join Strategy

When you write `df1.join(df2, "key")`, Spark never just "joins".
It goes through this decision tree EVERY time:

```
                    Is one side small enough to broadcast?
                    (< spark.sql.autoBroadcastJoinThreshold = 10MB default)
                              │
                 ┌────────────┴────────────┐
                YES                        NO
                 │                          │
        BroadcastHashJoin          Can the smaller side fit
        (NO shuffle at all)        in memory as a hash table?
                                              │
                                 ┌────────────┴────────────┐
                                YES                        NO
                                 │                          │
                        ShuffleHashJoin           Are both sides
                        (shuffle + hash)          already sorted?
                                                            │
                                                 ┌──────────┴──────────┐
                                                YES                    NO
                                                 │                      │
                                        SortMergeJoin          SortMergeJoin
                                        (no sort needed)       (sort + merge)
                                        ← rare in practice

Special cases:
    Cartesian Join   → when NO join key exists (cross join)
    BroadcastNestedLoopJoin → fallback for non-equi joins
```

---

## 🔵 STRATEGY 1 — BroadcastHashJoin (BHJ)

### When Spark uses it:
```
One side of the join is SMALL (< 10 MB by default)
Config: spark.sql.autoBroadcastJoinThreshold = 10485760 (10 MB)

You can also force it:
    from pyspark.sql.functions import broadcast
    df1.join(broadcast(df2), "key")
```

### How it works internally — step by step:

```
Setup:
    Large table:  orders     = 100 GB (800 partitions)
    Small table:  country_codes = 2 MB (1 partition)

Step 1 — Collect small table to Driver
    Spark reads country_codes (2 MB) completely
    Sends it to the Driver process memory

Step 2 — Build Hash Map on Driver
    Driver builds an in-memory hash map:
    {
      "US" → Row("US", "United States", "USD"),
      "IN" → Row("IN", "India", "INR"),
      "UK" → Row("UK", "United Kingdom", "GBP"),
      ...
    }

Step 3 — Broadcast hash map to ALL executors
    Driver serializes the hash map
    Sends a COPY to every executor via SparkContext broadcast mechanism
    Each executor now has the full hash map in its memory

    Executor 1 memory: full country_codes hash map (2 MB)
    Executor 2 memory: full country_codes hash map (2 MB)
    Executor 3 memory: full country_codes hash map (2 MB)

Step 4 — Each task does a LOCAL lookup (no shuffle at all)
    Task reads its 128 MB partition of orders
    For each row:
        country = row["country_code"]
        match   = hashMap.get(country)   ← local memory lookup, O(1)
        if match: emit joined row

    NO data movement between executors
    NO shuffle files written
    NO network transfer of orders data
```

### Memory layout of the hash map:

```
Key:   "US"   (String → hashed to int → bucket index)
Value: Row object stored at that bucket

Lookup:
    hash("US") → bucket 42 → Row("US", "United States", "USD")
    Time complexity: O(1) per row
    Zero network I/O after broadcast
```

### Why it's the FASTEST join:

```
✅ Zero shuffle (no disk write, no network for the large side)
✅ Large table reads flow directly through → never leave their executor
✅ Only cost: broadcasting the small table once

Performance:
    orders (100 GB) processed at disk read speed
    No stage boundaries → all runs in ONE stage
    No shuffle files written at all
```

### When it FAILS:

```
❌ Small table is NOT actually small (> 10 MB) → Spark falls back to SMJ
❌ Small table after filter is still large → AQE can fix this at runtime
❌ Driver OOM if small table is collected to driver

Increase threshold (use carefully):
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 50 * 1024 * 1024)  # 50MB
```

---

## 🔵 STRATEGY 2 — SortMergeJoin (SMJ) ← Most Common for Large Tables

### When Spark uses it:
```
Both tables are large (both > broadcast threshold)
This is the DEFAULT for large-large joins
Config: spark.sql.join.preferSortMergeJoin = true (default)
```

### How it works internally — step by step:

```
Setup:
    Table A: orders    = 100 GB
    Table B: customers = 100 GB
    Join key: customer_id
    spark.sql.shuffle.partitions = 200
```

#### Phase 1 — SHUFFLE (redistribute by join key)

```
Step 1: Both tables are shuffled independently

For orders table:
    Each of 800 read tasks computes:
        target = hash(customer_id) % 200
    Writes data to 200 shuffle buckets on local disk

For customers table:
    Each of 800 read tasks computes:
        target = hash(customer_id) % 200
    Writes data to 200 shuffle buckets on local disk

GUARANTEE after shuffle:
    All rows with customer_id=8823 from orders   → partition 47
    All rows with customer_id=8823 from customers → partition 47
    → same partition number = same executor = can be joined locally
```

#### Phase 2 — SORT (within each partition)

```
Step 2: Each of the 200 Stage-1 tasks receives its partition

Task 47 has:
    orders    partition 47: [cid=8823 row, cid=1201 row, cid=8823 row, ...]  ← UNSORTED
    customers partition 47: [cid=1201 row, cid=8823 row, cid=4455 row, ...]  ← UNSORTED

Step 3: Task 47 sorts BOTH sides by customer_id

    orders    partition 47 SORTED: [cid=1201, cid=1201, cid=4455, cid=8823, cid=8823]
    customers partition 47 SORTED: [cid=1201, cid=4455, cid=8823, cid=9001]
```

#### Phase 3 — MERGE (two-pointer scan)

```
Step 4: Two-pointer merge scan (like merge sort's merge step)

    orders_ptr    → points to first row: cid=1201
    customers_ptr → points to first row: cid=1201

    Iteration 1:
        orders_ptr.cid    == customers_ptr.cid (1201 == 1201) → MATCH
        Emit joined row
        Advance orders_ptr → cid=1201 (next orders row, same cid)
        Emit another joined row (handles duplicates)
        Advance orders_ptr → cid=4455
        All 1201 orders exhausted → advance customers_ptr → cid=4455

    Iteration 2:
        orders_ptr.cid (4455) == customers_ptr.cid (4455) → MATCH
        Emit joined row
        Advance both

    Iteration 3:
        orders_ptr.cid (8823) == customers_ptr.cid (8823) → MATCH
        orders has TWO rows with 8823:
            emit row1 × customer_8823
            emit row2 × customer_8823
        Advance customers_ptr → cid=9001

    Iteration 4:
        orders_ptr.cid (end) < customers_ptr.cid (9001)
        orders exhausted → done

Time complexity: O(N log N) for sort + O(N) for merge
```

### How sort handles spill (when partition > memory):

```
Task has 805 MB of data, only 600 MB memory:

    Pass 1 (in-memory sort):
        Load 600 MB into memory
        Sort in memory using TimSort (Java's Arrays.sort)
        Write sorted chunk to local disk: spill_file_1  (600 MB, sorted)
        Free memory

    Pass 2 (in-memory sort):
        Load remaining 205 MB into memory
        Sort in memory
        Write sorted chunk to local disk: spill_file_2  (205 MB, sorted)
        Free memory

    Pass 3 (merge pass):
        Open both spill files with streaming readers
        Merge two sorted streams into one sorted output
        Uses only O(1) memory per stream (just a read buffer)
        Output: one fully sorted partition ready for merge join

    Multiple spill files → multi-way merge:
        If 5 spill files: open all 5, use a min-heap of 5 elements
        Pop minimum element, advance that stream
        O(N log k) where k = number of spill files
```

---

## 🔵 STRATEGY 3 — ShuffleHashJoin (SHJ)

### When Spark uses it:
```
One side fits in memory as a hash table but is > broadcast threshold
Spark prefers SMJ by default — must be explicitly enabled or chosen by cost optimizer

Enable:
    spark.conf.set("spark.sql.join.preferSortMergeJoin", "false")
    or AQE switches to it dynamically
```

### How it works internally — step by step:

```
Setup:
    Table A: orders      = 100 GB  (large side)
    Table B: customers   = 15 GB   (smaller side, > 10MB so no broadcast)

Step 1 — SHUFFLE BOTH SIDES by join key
    Same as SMJ: hash(customer_id) % 200

Step 2 — BUILD phase (smaller side only)
    Each task receives its partition of customers (15 GB / 200 = 75 MB)
    Builds an in-memory hash map from customers partition:
    {
        cid=1201 → [Row(1201, "Alice", ...)],
        cid=8823 → [Row(8823, "Bob",   ...)],
        ...
    }
    75 MB hash map lives in task memory ✅

Step 3 — PROBE phase (larger side)
    Task streams through its partition of orders (100 GB / 200 = 500 MB)
    For each order row:
        key = order.customer_id
        matches = hashMap.get(key)   ← O(1) local lookup
        if matches: emit joined rows
    
    Only 500 MB of orders needs to be in memory at a time
    (streamed, not all loaded at once)

Total memory per task:
    hash map (75 MB) + streaming probe buffer (~few MB) = ~80 MB ✅
```

### SHJ vs SMJ comparison:

```
ShuffleHashJoin:
    ✅ Faster when one side is small-medium (hash lookup = O(1))
    ✅ No sort step needed
    ❌ Hash map must fit in memory → OOM risk if estimation is wrong
    ❌ Not safe for very large or skewed data

SortMergeJoin:
    ✅ Always safe — spills gracefully to disk
    ✅ Works for any size data
    ❌ Sorting is O(N log N) — slower than hash lookup
    ❌ Requires two sort passes if data spills
```

---

## 🔵 STRATEGY 4 — BroadcastNestedLoopJoin (BNLJ)

### When Spark uses it:
```
Non-equi joins (no = condition):
    df1.join(df2, df1.price.between(df2.min_price, df2.max_price))
    df1.join(df2, df1.date < df2.expiry_date)
    CROSS JOIN (cartesian product)
    LEFT/RIGHT/FULL OUTER joins that can't use hash-based methods
```

### How it works internally:

```
Step 1 — Broadcast the smaller side (same as BHJ)
    Serialize small table → broadcast to all executors

Step 2 — Nested Loop scan (no hash, no sort)
    Each task:
        for each row in large_partition:          ← outer loop
            for each row in broadcast_table:      ← inner loop
                if join_condition(outer, inner):  ← evaluate condition
                    emit joined row

Time complexity: O(N × M) per partition
    N = rows in large partition
    M = rows in broadcast table

Example:
    Large partition: 10,000 rows
    Broadcast table: 500 rows
    → 5,000,000 comparisons per task

This is WHY it's only viable when broadcast table is very small
```

### Why it's the SLOWEST:

```
No hash map shortcut → must check every combination
For equi-joins: always use BHJ or SMJ instead
BNLJ is truly a last resort
```

---

## 🔵 STRATEGY 5 — CartesianJoin

### When Spark uses it:
```
df1.crossJoin(df2)  ← explicit
or any join with NO join condition

Output rows = rows_in_df1 × rows_in_df2

Example:
    df1 = 1,000 rows
    df2 = 1,000 rows
    Result = 1,000,000 rows

WARNING: 100 GB × 100 GB = petabytes of output → almost always a mistake
Must explicitly enable: spark.sql.crossJoin.enabled = true
```

---

## 🔵 SORTING STRATEGIES — Internal Details

### TimSort (default in-memory sort)

```
What: Java's Arrays.sort() → hybrid MergeSort + InsertionSort
When: Data fits entirely in memory

Phase 1 — Find "runs" (already-sorted subsequences):
    Input: [3, 1, 4, 1, 5, 9, 2, 6, 5]
    Run 1: [3]  (length 1, trivially sorted)
    Run 2: [1, 4]  (ascending run detected)
    ...
    MinRunLength = 32-64 elements
    Short runs extended to minRunLength using InsertionSort

Phase 2 — Merge runs using MergeSort:
    Merge pairs of runs bottom-up
    Until one fully sorted array remains

Time:  O(N log N) worst case, O(N) for already-sorted data
Space: O(N) auxiliary memory
```

### External Sort (when data spills to disk)

```
What: Multi-pass sort for data larger than available memory
When: Partition size > task memory

Pass 1 — Sort runs:
    Load chunk_1 (fits in memory) → TimSort → write sorted_run_1 to disk
    Load chunk_2 (fits in memory) → TimSort → write sorted_run_2 to disk
    Load chunk_3 (fits in memory) → TimSort → write sorted_run_3 to disk
    ...

Pass 2 — K-way merge:
    Open all sorted runs as streaming readers
    Use a MIN-HEAP of size K (one entry per run):

    Initial heap: [run1.peek(), run2.peek(), run3.peek(), ...]

    Loop:
        min_row = heap.pop_minimum()
        emit min_row to output
        advance the run that min_row came from
        push next row from that run into heap

    Time: O(N log K)  where K = number of spill files
    Memory: O(K) for the heap + O(1) per run (streaming read buffer)
```

### RadixSort (used internally for some aggregations)

```
What: Non-comparison sort on integer keys
When: Sorting by integer join keys or hash values internally

How:
    Pass 1: Sort by least significant byte (0-255)
    Pass 2: Sort by next byte
    Pass 3: Sort by next byte
    Pass 4: Sort by most significant byte (for 32-bit int = 4 passes)

Each pass is O(N) → Total: O(N × bytes_in_key) = O(N) for fixed-width keys
Much faster than O(N log N) for integer keys

Used in: UnsafeExternalSorter when keys are fixed-width integers/longs
```

---

## 🔵 MERGING STRATEGIES — Internal Details

### Two-Way Merge (basic SMJ merge)

```
Used when: Only 2 sorted runs to merge (no spill, clean SMJ)

left  = [1, 3, 3, 7, 9]   (sorted orders partition)
right = [2, 3, 5, 8]      (sorted customers partition)

ptr_L = 0, ptr_R = 0

Step 1: left[0]=1, right[0]=2 → 1 < 2 → advance left
Step 2: left[1]=3, right[0]=2 → 3 > 2 → advance right (no match for 2)
Step 3: left[1]=3, right[1]=3 → MATCH → emit joined row
            left has multiple 3s: check left[2]=3 → also 3 → emit another
            right has only one 3: advance right
Step 4: left[3]=7, right[2]=5 → 7 > 5 → advance right (no match for 5)
...

Time: O(N + M) — single linear scan of both sides
Memory: O(1) — just two pointers + a small lookahead buffer for duplicates
```

### K-Way Merge (used when data spills to multiple files)

```
Used when: Task produced K spill files during sort phase

K sorted spill files:
    file_1: [1, 5, 9, 13]
    file_2: [2, 4, 11, 15]
    file_3: [3, 6, 8, 12]

Min-heap with K=3 slots:
    Initialize: heap = [(1,file1), (2,file2), (3,file3)]

    Round 1: pop (1,file1) → emit 1 → push next from file1: (5,file1)
             heap = [(2,file2), (3,file3), (5,file1)]
    Round 2: pop (2,file2) → emit 2 → push next from file2: (4,file2)
             heap = [(3,file3), (4,file2), (5,file1)]
    Round 3: pop (3,file3) → emit 3 → push next from file3: (6,file3)
             heap = [(4,file2), (5,file1), (6,file3)]
    ...

Output stream: 1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 15  ← fully sorted

Time:   O(N log K)
Memory: O(K) for heap — does NOT load all spill files into memory!
        Only one element per file is in the heap at a time
```

### Partial Aggregation Merge (for groupBy + agg)

```
Used when: groupBy().agg() — two-phase aggregation

Phase 1 — Map-side partial merge (BEFORE shuffle):
    Each task builds a local hash map:
    {
        "Engineering" → (sum=170000, count=2),
        "Marketing"   → (sum=70000,  count=1),
    }
    Reduces 1M rows → hundreds of partial aggregate rows
    MUCH less data to shuffle

Phase 2 — Reduce-side final merge (AFTER shuffle):
    Each partition receives ALL partial aggregates for its keys
    Merges them:
    "Engineering":
        partial_1: (sum=170000, count=2)
        partial_2: (sum=150000, count=2)
        partial_3: (sum=200000, count=3)
        Merged:    (sum=520000, count=7) → avg = 74285.71

Time:   O(N/P) where P = number of partitions
Memory: O(distinct_keys_per_partition) for hash map
```

---

## 🔵 JOIN STRATEGIES + SORT/MERGE COMBINATION TABLE

```
┌───────────────────────┬──────────┬──────────┬──────────┬────────────────────────┐
│ Strategy              │ Shuffle? │ Sort?    │ Merge?   │ Best for               │
├───────────────────────┼──────────┼──────────┼──────────┼────────────────────────┤
│ BroadcastHashJoin     │ ❌ None  │ ❌ None  │ ❌ None  │ large + tiny (<10MB)   │
│ ShuffleHashJoin       │ ✅ Both  │ ❌ None  │ Hash     │ large + medium         │
│ SortMergeJoin         │ ✅ Both  │ ✅ Both  │ 2-way    │ large + large          │
│ BroadcastNestedLoop   │ ❌ None  │ ❌ None  │ Nested   │ non-equi joins         │
│ CartesianJoin         │ ❌ None  │ ❌ None  │ Nested   │ cross join (danger!)   │
└───────────────────────┴──────────┴──────────┴──────────┴────────────────────────┘

Sort types used internally:
┌──────────────┬─────────────────────────────────────────────────────────────┐
│ TimSort      │ In-memory, data fits in RAM, O(N log N)                     │
│ External Sort│ Data > memory, multi-pass spill + K-way merge, O(N log K)  │
│ RadixSort    │ Integer keys only, O(N), used in UnsafeExternalSorter       │
└──────────────┴─────────────────────────────────────────────────────────────┘

Merge types used internally:
┌──────────────────────┬──────────────────────────────────────────────────────┐
│ Two-way merge        │ SMJ with 2 sorted partitions, O(N+M), O(1) memory   │
│ K-way merge          │ Multiple spill files, min-heap, O(N log K)          │
│ Partial agg merge    │ groupBy aggregation, hash-map based, two-phase      │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 🔵 AQE — Runtime Join Strategy Switching

With `spark.sql.adaptive.enabled = true` (default Spark 3.2+):

```
Planned at compile time:   SortMergeJoin
                                │
                         Stage 0 executes
                                │
                    AQE measures actual data sizes:
                    "customers after filter = 4 MB"
                                │
                    4 MB < 10 MB threshold
                                │
                    AQE switches plan at runtime:
                    SortMergeJoin → BroadcastHashJoin
                                │
                    Stage 1 uses BroadcastHashJoin instead
                    Saves: one full shuffle + two full sorts

This is why AQE is such a big deal — it catches cases where
compile-time estimates were wrong due to filter selectivity
```

---

## ⚠️ Common Mistakes

```
❌ Mistake 1: Broadcast threshold too low
   symptom: always falls back to SMJ even for 15 MB tables
   fix: spark.sql.autoBroadcastJoinThreshold = 52428800  (50 MB)

❌ Mistake 2: Preferring SMJ when SHJ would be faster
   symptom: unnecessary sort for medium-sized joins
   fix: spark.sql.join.preferSortMergeJoin = false  (let optimizer choose)

❌ Mistake 3: Data skew in SMJ
   symptom: one task takes 100x longer (hot key problem)
   fix: spark.sql.adaptive.skewJoin.enabled = true  (AQE handles it)
   or:  manually salt the join key

❌ Mistake 4: Accidental CartesianJoin
   symptom: result has rows_A × rows_B rows — job never finishes
   fix: always specify a join condition; enable
        spark.sql.crossJoin.enabled = false  to catch mistakes
```

# Spark File Reading Internals — Complete Deep Dive

---

## 📌 Setup

```
Cluster:  3 Executors × 4 cores × 4 GB
File:     employees.csv = 20 GB
Config:   spark.sql.files.maxPartitionBytes = 128 MB (default)
```

---

## 🔵 STEP 1 — How Many Partitions Are Created?

```
Total file size  = 20 GB = 20,480 MB
Partition size   = 128 MB

Number of partitions = ceil(20,480 / 128) = 160 partitions

So Spark plans:
    Partition 0:   bytes 0         → 134,217,728     (128 MB)
    Partition 1:   bytes 134217728 → 268,435,456     (128 MB)
    Partition 2:   bytes 268435456 → 402,653,184     (128 MB)
    ...
    Partition 159: bytes 19,327,352,832 → 20,480 MB  (last chunk)
```

### The Key Config Parameters That Affect This:

```
spark.sql.files.maxPartitionBytes  = 128 MB  (max size per partition)
spark.sql.files.minPartitionNum    = total_cores (minimum partitions)
spark.default.parallelism          = total_cores × 2 (for RDD operations)
spark.sql.files.openCostInBytes    = 4 MB   (cost to open a file, used for small files)

Formula:
    maxSplitBytes = min(maxPartitionBytes, max(openCostInBytes, totalSize / minPartitionNum))

For our case:
    totalSize = 20 GB
    minPartitionNum = 3 executors × 4 cores = 12
    max(4MB, 20480MB/12) = max(4MB, 1706MB) = 1706MB
    min(128MB, 1706MB) = 128MB  ← partition size stays 128MB
```

---

## 🔵 STEP 2 — Who Decides Which Executor Reads Which Partition?

### The Chain of Responsibility

```
YOU call:
    df = spark.read.csv("path/employees.csv")
    df.show()   ← action triggers everything
         │
         ▼
DRIVER process
    │
    ├── SparkContext contacts FileSystem (HDFS/S3/local)
    ├── Gets file metadata: size, block locations
    ├── Calculates 160 partitions + their byte ranges
    ├── Creates 160 Tasks (one per partition)
    └── Hands task list to DAGScheduler
         │
         ▼
DAGScheduler
    │
    └── Creates Stage 0 with 160 tasks
         │
         ▼
TaskScheduler
    │
    ├── Maintains list of available executor slots
    ├── 3 executors × 4 cores = 12 slots available
    ├── Assigns tasks to executors based on DATA LOCALITY
    └── Sends task to Executor via ExecutorBackend
         │
         ▼
EXECUTOR receives task:
    "Read bytes 134217728 → 268435456 of employees.csv"
    Executor opens file connection and reads its assigned byte range
```

### Data Locality Tiers (Priority Order)

```
PROCESS_LOCAL   → data is in the same JVM process memory (cached RDD)
NODE_LOCAL      → data is on the same physical machine (HDFS block on same node)
RACK_LOCAL      → data is on a different machine but same rack
NO_PREF         → data has no location preference (S3, databases)
ANY             → any executor, anywhere

TaskScheduler tries each tier with a wait timeout before falling back:
    spark.locality.wait         = 3 seconds  (wait for PROCESS_LOCAL)
    spark.locality.wait.node    = 3 seconds  (wait for NODE_LOCAL)
    spark.locality.wait.rack    = 3 seconds  (wait for RACK_LOCAL)
    spark.locality.wait.any     = 0 seconds  (no wait for ANY)
```

---

## 🔵 STEP 3 — How Are 160 Partitions Distributed Across 3 Executors?

```
12 cores available = 12 tasks run simultaneously

Wave 1  (t=0s):    Tasks 0–11   assigned (4 per executor)
Wave 2  (t=Xs):    Tasks 12–23  assigned (as Wave 1 tasks complete)
Wave 3  (t=2Xs):   Tasks 24–35  assigned
...
Wave 14 (t=13Xs):  Tasks 156–159 assigned (only 4 tasks, 8 cores idle)

Total waves = ceil(160/12) ≈ 14 waves

At any point in time:
    Executor 1: reads partitions P0, P1, P2, P3   (4 simultaneous reads)
    Executor 2: reads partitions P4, P5, P6, P7   (4 simultaneous reads)
    Executor 3: reads partitions P8, P9, P10, P11 (4 simultaneous reads)

Assignment is NOT fixed — it's dynamic:
    If Executor 1 finishes P0 early → immediately gets P12
    Faster executors get more tasks
    Slower executors (GC pauses, slower disk) get fewer tasks in same time
```

---

## 🔵 STEP 4 — THE CRITICAL QUESTION: How Is a Line Not Split Across Executors?

This is the most important internal mechanism most people don't know.

### The Problem

```
File on disk (raw bytes):
    ...Alice,30,Engineering\nBob,25,Marketi|ng,500\nCarol...
                             ^                  ^
                         partition boundary  next partition starts here
                         at byte 134217728

If Spark blindly reads bytes 0→128MB and 128MB→256MB:
    Partition 0 ends with:  "...Bob,25,Marketi"   ← INCOMPLETE ROW!
    Partition 1 starts with: "ng,500\nCarol..."    ← INCOMPLETE ROW!
    
This would corrupt data. Spark prevents this with split boundary logic.
```

### The Solution — InputSplit Boundary Adjustment

```
Step 1: Spark calculates logical split at byte 134,217,728 (128 MB mark)

Step 2: The InputFormat/RecordReader for the task assigned to Partition 0:
    Opens file at byte 0
    Reads until byte 134,217,728 (the boundary)
    CONTINUES READING past the boundary until it finds '\n' (newline)
    INCLUDES that partial line in Partition 0
    Stops AFTER the newline

Step 3: The RecordReader for Partition 1:
    Opens file at byte 134,217,728 (the boundary)
    SKIPS bytes until it finds the FIRST '\n' after the boundary
    Starts reading from the character AFTER that '\n'
    This ensures it doesn't re-read the line already claimed by Partition 0

RESULT:
    Partition 0 reads: bytes 0 → 134,217,792  (boundary + 64 extra bytes for partial line)
    Partition 1 reads: bytes 134,217,793 → 268,435,456 (starts after the overrun line)

Every line is complete, no line is ever split, no line is ever duplicated.
```

### Visualized

```
Raw file bytes:
|-------- 128 MB ---------|-------- 128 MB ----------|

byte: 0                134217728                268435456
      │                    │                        │
      │                    │←─ boundary             │
      ▼                    ▼                        ▼
...salary\nAlice,30,Eng\nBo|b,25,Marketing\nCarol,35|,Eng\n...
                           ^                        ^
                     exact 128MB mark         exact 256MB mark

Partition 0 RecordReader:
    Reads: bytes 0 → finds \n after 134217728
    Actual end: ...Marketing\n   (includes Bob's complete row)
    ✅ Bob's row is COMPLETE in Partition 0

Partition 1 RecordReader:
    Opens at: byte 134217728
    Skips forward to first \n  (skips "b,25,Marketing")
    Starts reading from: Carol,35,...
    ✅ Carol's row is COMPLETE in Partition 1
    ✅ Bob's row is NOT duplicated
```

### Who implements this logic?

```
For CSV files:
    → org.apache.spark.sql.execution.datasources.csv.CSVFileFormat
    → Uses Hadoop's LineRecordReader internally
    → LineRecordReader handles the split boundary skip logic

For Parquet files:
    → org.apache.spark.sql.execution.datasources.parquet.ParquetFileFormat
    → Parquet is columnar + row-group aware → splits always fall on row group boundaries
    → Row groups are self-contained → no split boundary problem exists

For ORC files:
    → Similar to Parquet — stripe boundaries used as split points
    → ORC stripes = natural split boundaries

For JSON files:
    → org.apache.spark.sql.execution.datasources.json.JsonFileFormat
    → Same LineRecordReader boundary logic as CSV

For custom binary formats:
    → Developer must implement custom RecordReader with proper split handling
```

---

## 🔵 SCENARIO A — Reading from LOCAL FILESYSTEM

### Who pulls the data?

```
Architecture:
    Driver runs on: Machine A
    Executor 1 on:  Machine A (same machine as driver)
    Executor 2 on:  Machine B
    Executor 3 on:  Machine C
    File lives on:  Machine A's local disk /data/employees.csv

Data locality situation:
    Executor 1 (Machine A): NODE_LOCAL or PROCESS_LOCAL
    Executor 2 (Machine B): ANY (must fetch over network)
    Executor 3 (Machine C): ANY (must fetch over network)
```

### Step-by-step execution:

```
Step 1: Driver asks OS for file metadata
    → file size: 20 GB
    → file path: /data/employees.csv
    → NO block location info (local FS has no block registry)

Step 2: Driver creates 160 tasks with byte ranges
    Each task knows: "read bytes X → Y from /data/employees.csv"

Step 3: TaskScheduler assigns tasks with locality preference = NO_PREF
    (local filesystem has no block registry, so any executor can run any task)

Step 4: Executor pulls data
    Executor 1 (same machine):
        Opens /data/employees.csv directly from local disk ✅
        Fast: disk read speed (~500 MB/s for SSD)
        No network involved

    Executor 2 (different machine):
        Cannot access /data/employees.csv directly!
        Spark does NOT automatically share local files across machines
        
        OPTIONS:
        A) File must be on shared filesystem (NFS mount) accessible from all machines
        B) File must be replicated on each machine
        C) Use HDFS/S3 instead (designed for distributed access)

    REAL LIMITATION:
        spark.read.csv("/local/path/file.csv") on a cluster:
        → Only works if ALL executors can see that path
        → NFS, GPFS, or identical local files on all nodes
        → Otherwise: FileNotFoundException on executors that can't see the file
```

### Local file read internals:

```
Executor process:
    FileInputStream.open("/data/employees.csv")
    FileChannel.position(134217728)   ← seek to partition start
    FileChannel.read(buffer, 134217728, 134217728 + 128MB)
    
    OS kernel:
        Checks page cache (is this file already in OS memory?)
        If YES → zero-copy read from page cache (fast)
        If NO  → disk I/O request → DMA transfer → page cache → JVM buffer

    JVM buffer → LineRecordReader → Row objects → task processing
```

---

## 🔵 SCENARIO B — Reading from HDFS (Hadoop Distributed File System)

### How HDFS stores the file:

```
employees.csv = 20 GB

HDFS splits file into BLOCKS (default 128 MB each):
    Block 0:   bytes 0         → 134,217,728    stored on: DataNode 1, DataNode 2, DataNode 3
    Block 1:   bytes 134217728 → 268,435,456    stored on: DataNode 1, DataNode 3, DataNode 2
    Block 2:   bytes 268435456 → 402,653,184    stored on: DataNode 2, DataNode 1, DataNode 3
    ...
    Block 159: last chunk                        stored on: DataNode 3, DataNode 1, DataNode 2

Replication factor = 3 (default)
Each block exists on 3 different DataNodes for fault tolerance
NameNode maintains the block → DataNode mapping (block registry)
```

### Step-by-step HDFS read:

```
Step 1: Driver contacts HDFS NameNode
    Request: "Give me block locations for employees.csv"
    Response: {
        Block 0:   [DataNode1:50010, DataNode2:50010, DataNode3:50010]
        Block 1:   [DataNode1:50010, DataNode3:50010, DataNode2:50010]
        ...
        Block 159: [DataNode3:50010, DataNode1:50010, DataNode2:50010]
    }

Step 2: Driver creates tasks WITH location hints
    Task 0:   "read block 0"  preferredLocations=[DataNode1, DataNode2, DataNode3]
    Task 1:   "read block 1"  preferredLocations=[DataNode1, DataNode3, DataNode2]
    ...

Step 3: TaskScheduler checks if any executor runs on a DataNode machine

    If Executor 1 runs on DataNode1's machine:
        Block 0 can be read locally → NODE_LOCAL
        TaskScheduler waits up to 3 seconds to give Task 0 to Executor 1
        → Fast: no network, disk read speed

    If no executor is on any DataNode:
        All reads are RACK_LOCAL or ANY
        Data fetched over network from DataNode to Executor

Step 4: Executor reads the HDFS block

    Executor contacts HDFS NameNode:
        "I need block 47, where is it?"
    NameNode responds:
        "Block 47 is on DataNode2 at port 50010"
    Executor opens TCP connection to DataNode2:50010
    DataNode2 streams block 47 bytes → Executor memory

    Internally uses: org.apache.hadoop.hdfs.DFSInputStream
    → Handles retry on DataNode failure
    → Switches to replica on DataNode3 if DataNode2 is slow
    → Checksum verification of each block
```

### HDFS vs Local — Key Difference:

```
Local filesystem:
    File exists on ONE machine
    Only that machine can read it directly
    No block registry → no locality optimization

HDFS:
    File blocks spread across ALL DataNodes
    Each block replicated 3 times
    Block registry in NameNode → Spark knows EXACTLY where each block lives
    Data locality optimization possible → NODE_LOCAL reads common
    Any executor can reach any block via network if needed
```

---

## 🔵 SCENARIO C — Reading from S3

### S3 architecture:

```
S3 is OBJECT STORAGE — not a filesystem, not a block store

employees.csv on S3:
    s3://my-bucket/data/employees.csv
    Single object, 20 GB
    No blocks, no DataNodes, no NameNode
    Stored in AWS infrastructure, unknown physical location
    AWS exposes it via HTTPS REST API

No concept of "data locality" → always NO_PREF
```

### Step-by-step S3 read:

```
Step 1: Driver talks to S3 via AWS SDK
    HEAD request: s3://my-bucket/data/employees.csv
    Response: {
        ContentLength: 21,474,836,480  (20 GB)
        ETag: "abc123..."
        LastModified: ...
    }
    NO block location info (S3 is a black box)

Step 2: Driver creates 160 tasks with byte ranges
    Task 0:   bytes 0         → 134,217,728
    Task 1:   bytes 134217728 → 268,435,456
    ...
    preferredLocations = []  ← empty, S3 has no locality

Step 3: TaskScheduler assigns tasks to ANY available executor
    No locality preference → tasks distributed round-robin or by availability

Step 4: Executor reads from S3 using HTTP Range Request

    Executor sends HTTP request:
    GET s3://my-bucket/data/employees.csv
    Range: bytes=134217728-268435455
    Authorization: AWS4-HMAC-SHA256 ...

    AWS S3 responds:
    HTTP 206 Partial Content
    [streams 128 MB of data]

    Internally: S3AInputStream (hadoop-aws library)
    → Handles authentication (AWS SigV4)
    → Handles retry on network errors (exponential backoff)
    → Handles multipart reads for large ranges
    → Supports vectored I/O (Spark 3.3+): multiple byte ranges in one request
```

### S3 specific challenges and solutions:

```
Challenge 1: S3 is NOT a real filesystem
    s3://bucket/dir/ is not a real directory
    Listing 10,000 files in "directory" = 10,000 individual API calls
    Very slow for large datasets with many small files

    Solution:
    → Use S3 Inventory for metadata
    → Use Delta Lake / Iceberg for file listing optimization
    → Avoid millions of tiny files (the "small file problem")

Challenge 2: S3 Eventual Consistency (OLD — before 2020)
    Write a file → might not be immediately visible to list operations
    
    Solution: S3 now provides strong read-after-write consistency (Dec 2020)
    No longer an issue in modern Spark

Challenge 3: High latency per request (~50-200ms vs ~1ms for local disk)
    Opening many small files = thousands of API calls = seconds of overhead

    Solution: spark.sql.files.openCostInBytes = 4MB
    Spark groups small files together into one partition to minimize open calls

Challenge 4: S3 throttling (rate limits)
    Too many requests → HTTP 503 SlowDown

    Solution:
    → spark.hadoop.fs.s3a.connection.maximum = 200
    → Use S3A committer (not the default FileOutputCommitter)
    → Avoid listing the same prefix repeatedly

Challenge 5: Network bandwidth from S3 to your cluster
    Reading 20 GB over network is slower than local disk

    Solution:
    → Run Spark on EC2 in same AWS region as S3 bucket
    → Use S3 Transfer Acceleration for cross-region
    → Use Amazon EMR with EMRFS for optimized S3 access
```

---

## 🔵 SCENARIO D — Reading from a SQL Database (JDBC)

### Architecture:

```
spark.read
    .format("jdbc")
    .option("url",      "jdbc:postgresql://host:5432/mydb")
    .option("dbtable",  "employees")
    .option("user",     "spark_user")
    .option("password", "****")
    .load()
```

### The Default (Terrible) Behavior:

```
Without partitioning config:
    Spark creates EXACTLY 1 partition
    1 executor opens 1 JDBC connection
    Reads ENTIRE employees table sequentially
    Result: completely sequential, no parallelism at all

Why? 
    JDBC has no concept of "byte ranges"
    Database doesn't expose block locations
    Spark doesn't know how to split the table automatically
```

### The Right Way — Parallel JDBC Read:

```python
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://host:5432/mydb") \
    .option("dbtable", "employees") \
    .option("partitionColumn", "employee_id") \   ← numeric column to split on
    .option("lowerBound",      "1") \              ← min value
    .option("upperBound",      "1000000") \        ← max value
    .option("numPartitions",   "10") \             ← 10 parallel connections
    .load()
```

### How parallel JDBC read works internally:

```
Spark generates 10 SQL queries with WHERE clause ranges:

    Task 0 (Executor 1):
        SELECT * FROM employees WHERE employee_id >= 1       AND employee_id < 100001
    Task 1 (Executor 1):
        SELECT * FROM employees WHERE employee_id >= 100001  AND employee_id < 200001
    Task 2 (Executor 2):
        SELECT * FROM employees WHERE employee_id >= 200001  AND employee_id < 300001
    ...
    Task 9 (Executor 3):
        SELECT * FROM employees WHERE employee_id >= 900001  AND employee_id <= 1000000

Each task:
    Opens its OWN JDBC connection to the database
    Sends its WHERE-clause query
    Streams result rows into a Spark partition
    Closes connection when done

Executor 1 opens 4 JDBC connections (4 cores)
Executor 2 opens 3–4 JDBC connections
Executor 3 opens 3–4 JDBC connections

Warning: 10 simultaneous connections to DB → ensure DB connection pool can handle it
Config:  .option("numPartitions", "10") should match DB connection pool size
```

### Predicate Pushdown for JDBC:

```
df.filter(col("age") > 30).select("name", "department")

WITHOUT pushdown (bad):
    SELECT * FROM employees          ← sends all data
    Spark applies filter in memory

WITH pushdown (good, Spark does this automatically for JDBC):
    SELECT name, department FROM employees WHERE age > 30  ← DB does the work
    Only filtered, projected data sent over network

Config: spark.sql.jdbc.dialect  ← Spark uses DB-specific SQL dialect
Supported: PostgreSQL, MySQL, Oracle, SQL Server, DB2, etc.
```

### JDBC Line Boundary Equivalent:

```
No line boundary problem for JDBC!

Why? Database returns complete rows via ResultSet
    ResultSet.next() → always returns one complete row
    No concept of byte ranges or partial rows
    The JDBC driver handles all protocol-level framing

The "split boundary" problem only exists for flat files (CSV, JSON, text)
    because they're raw bytes without row framing
```

---

## 🔵 SCENARIO E — Reading Many Small Files (The Small File Problem)

### Setup:

```
Instead of 1 file of 20 GB:
    10,000 files × 2 MB each = 20 GB total

Default behavior:
    Each file = 1 partition (even though 2 MB << 128 MB limit)
    Result: 10,000 partitions = 10,000 tasks

Problems:
    10,000 tasks ÷ 12 cores = 834 waves of execution
    Each task: open file (50ms overhead) + read 2 MB + close file
    Overhead dominates actual work
    Task scheduling overhead is massive
```

### How Spark handles this — File Coalescing:

```
spark.sql.files.openCostInBytes = 4 MB (default)

This config says: "treat each file open as if it costs 4 MB of data"

Packing algorithm:
    Start new partition (budget = 128 MB)
    
    File 1: 2 MB data + 4 MB open cost = 6 MB → pack into partition 0 (budget: 122 MB left)
    File 2: 2 MB data + 4 MB open cost = 6 MB → pack into partition 0 (budget: 116 MB left)
    File 3: 2 MB data + 4 MB open cost = 6 MB → pack into partition 0 (budget: 110 MB left)
    ...
    File 21: would exceed 128 MB budget → start partition 1
    
    Files per partition = 128 MB / 6 MB ≈ 21 files
    Total partitions = 10,000 / 21 ≈ 477 partitions

477 partitions ÷ 12 cores = 40 waves  ← much better than 834!
```

### Solution for extreme small file problems:

```python
# Option 1: Increase partition size to pack more files
spark.conf.set("spark.sql.files.maxPartitionBytes", str(256 * 1024 * 1024))  # 256MB

# Option 2: Explicitly coalesce after reading
df = spark.read.csv("s3://bucket/many-small-files/*")
df = df.coalesce(160)  # reduce from 477 to 160 partitions

# Option 3: Use wholeTextFiles (for very tiny files)
rdd = sc.wholeTextFiles("s3://bucket/many-small-files/*", minPartitions=160)

# Option 4: Fix upstream — write larger files
df.write.option("maxRecordsPerFile", 1000000).parquet("output/")
```

---

## 🔵 SCENARIO F — Reading Parquet Files (Columnar Format)

### How Parquet splits differently from CSV:

```
Parquet file internal structure:
    ┌─────────────────────────────────┐
    │  File Header (magic bytes)      │
    ├─────────────────────────────────┤
    │  Row Group 0  (e.g., 128 MB)    │  ← natural split boundary
    │    Column chunk: name           │
    │    Column chunk: age            │
    │    Column chunk: salary         │
    ├─────────────────────────────────┤
    │  Row Group 1  (e.g., 128 MB)    │  ← natural split boundary
    │    Column chunk: name           │
    │    Column chunk: age            │
    │    Column chunk: salary         │
    ├─────────────────────────────────┤
    │  ...                            │
    ├─────────────────────────────────┤
    │  File Footer (schema + metadata)│
    └─────────────────────────────────┘

Each Row Group = one Spark partition
No split boundary adjustment needed — Row Groups are self-contained
```

### Column Pruning — Why Parquet is much faster:

```
Query: SELECT name, salary FROM employees WHERE age > 30

CSV read:
    Must read ALL bytes of all columns: name, age, salary, department, phone...
    Then discard unwanted columns in memory

Parquet read:
    Only reads column chunks for: name, age, salary
    Completely SKIPS column chunks for: department, phone, email, ...
    For age > 30 filter: reads age column first, builds bitmask of matching rows
    Then only fetches those specific rows from name and salary columns
    
Result: if you select 3 of 20 columns, Parquet reads only 15% of the data
```

### Row Group Statistics — Predicate Pushdown:

```
Parquet stores min/max statistics per Row Group per column:
    Row Group 0: age min=18, max=25
    Row Group 1: age min=26, max=35
    Row Group 2: age min=36, max=65

Query: WHERE age > 30

Spark reads footer statistics BEFORE reading any Row Group data:
    Row Group 0: max=25, 25 < 30 → SKIP ENTIRE ROW GROUP ✅ (128 MB saved!)
    Row Group 1: min=26, max=35, overlaps 30 → must read
    Row Group 2: min=36, 36 > 30 → read all rows (all match)

This is "Parquet predicate pushdown" — skip entire chunks before reading
```

---

## 🔵 SCENARIO G — Reading a Compressed File (gzip vs snappy vs lz4)

### Splittable vs Non-Splittable compression:

```
NON-SPLITTABLE formats:
    .csv.gz   (gzip)
    .csv.bz2  (bzip2 — actually splittable but rare)
    .csv.zip

    Problem:
        gzip is a STREAM compression — must decompress from byte 0
        Cannot seek to byte 134,217,728 and start decompressing
        Therefore: entire file = 1 partition, 1 task, NO parallelism

    employees.csv.gz = 20 GB compressed
    → 1 partition
    → 1 task
    → 1 executor reads and decompresses entire file
    → Other 11 cores sit idle
    → Very slow

SPLITTABLE formats:
    .parquet  (internally splittable by row groups)
    .orc      (internally splittable by stripes)
    .avro     (splittable with sync markers)
    .csv.snappy (snappy-compressed parquet/avro is splittable)
    .bz2      (has sync points every 900KB — technically splittable)
    .lz4      (in certain container formats)

    For splittable formats:
        Each split can be decompressed independently
        Full parallelism maintained

RULE: Never store large datasets as .csv.gz on a cluster
      Always use Parquet + Snappy for analytical workloads
```

---

## 🔵 SCENARIO H — Schema Inference (inferSchema=True) — The Hidden Cost

```python
df = spark.read.csv("employees.csv", header=True, inferSchema=True)
```

### What inferSchema actually does:

```
Step 1: Spark runs a SEPARATE FULL SCAN of the entire file
    → Reads all 20 GB
    → Samples values from each column
    → Determines types: is "age" always an integer? could it be double? string?

Step 2: Type resolution rules:
    All values parseable as Int → IntegerType
    Any value is float → DoubleType
    Any value is non-numeric → StringType
    All values are "true"/"false" → BooleanType

Step 3: Returns inferred schema to Driver
Step 4: SECOND full scan happens when action is called

Total: 20 GB read TWICE (once for schema, once for data)

Performance fix:
    Provide schema explicitly:
    from pyspark.sql.types import *
    schema = StructType([
        StructField("name",       StringType(),  True),
        StructField("age",        IntegerType(), True),
        StructField("department", StringType(),  True),
        StructField("salary",     DoubleType(),  True)
    ])
    df = spark.read.csv("employees.csv", header=True, schema=schema)
    → Only ONE scan, schema not inferred
```

---

## 🔵 SCENARIO I — What Happens When a Read Task Fails?

```
Task 5 is reading partition 5 (bytes 640MB → 768MB) from HDFS
Executor 2 crashes mid-read

Step 1: Executor 2 stops sending heartbeats to Driver
Step 2: Driver detects timeout (spark.network.timeout = 120s default)
Step 3: Driver marks Task 5 as FAILED
Step 4: Driver marks all tasks running on Executor 2 as FAILED
Step 5: TaskScheduler re-queues failed tasks
Step 6: Cluster Manager launches new Executor 4 (replacement)
Step 7: Task 5 re-assigned to Executor 4
Step 8: Executor 4 reads from HDFS:
    Contacts NameNode: "where is block 5?"
    NameNode: "DataNode 1 and DataNode 3 have it" (replica!)
    Executor 4 reads from DataNode 1 → success

Why this works:
    HDFS replication = 3 → even if one DataNode is down, 2 replicas remain
    S3 → AWS handles redundancy internally, always available
    Local filesystem → if the machine is down, the data is gone → job fails

Config:
    spark.task.maxFailures = 4  ← retry each task up to 4 times before giving up
```

---

## 📊 Complete Comparison Table

```
┌─────────────────┬──────────────┬────────────────────┬─────────────────┬───────────────┐
│ Aspect          │ Local FS     │ HDFS               │ S3              │ JDBC          │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Block/split     │ No blocks    │ 128 MB blocks       │ No blocks       │ No blocks     │
│ registry        │             │ in NameNode        │                 │               │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Data locality   │ NO_PREF      │ NODE_LOCAL possible│ NO_PREF (always)│ NO_PREF       │
│                 │             │                    │                 │               │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Who pulls data  │ Executor     │ Executor from      │ Executor via    │ Executor via  │
│                 │ direct read  │ DataNode TCP conn  │ HTTPS GET Range │ JDBC TCP conn │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Split boundary  │ LineRecord   │ LineRecordReader   │ LineRecord      │ N/A           │
│ handling        │ Reader       │                    │ Reader          │ (DB rows)     │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Fault tolerance │ ❌ Single    │ ✅ 3x replication  │ ✅ AWS managed  │ ✅ DB managed  │
│                 │ point        │                    │                 │               │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Parallelism     │ Limited      │ ✅ Full parallel   │ ✅ Full parallel │ Needs config  │
│                 │ (shared FS)  │                    │                 │               │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Line boundary   │ LineRecord   │ LineRecordReader   │ LineRecord      │ ResultSet     │
│ guarantee       │ Reader skip  │ skip logic         │ Reader skip     │ (auto, rows)  │
└─────────────────┴──────────────┴────────────────────┴─────────────────┴───────────────┘
```

---

## 🧠 Scenarios You Might Not Have Thought to Ask

### Q1: What if the file has Windows line endings (\r\n)?

```
LineRecordReader handles both \n and \r\n
When it finds the split boundary, it searches for \n
Automatically strips \r if present before \n
Result: rows work correctly regardless of OS line endings
```

### Q2: What if one row is 200 MB (larger than partition size)?

```
A single row > 128 MB:
    Partition 0 tries to read up to 128 MB → finds no \n → keeps reading
    Reads entire 200 MB row into memory (crosses partition boundary)
    Next partition starts after that row
    Result: Partition 0 = 200 MB (larger than configured 128 MB)
    
    Spark DOES NOT split a single row across partitions
    Memory impact: that executor task needs > 128 MB just for one row
    If row is extremely large → executor OOM possible
```

### Q3: What if the CSV has quoted fields with newlines inside?

```
Example:
    Alice,30,"Engineering
    Department",90000

LineRecordReader splits on \n → would break "Engineering\nDepartment" into two records!

Solution:
    spark.read.option("multiLine", "true").csv(...)

With multiLine=true:
    Spark uses a different reader (not LineRecordReader)
    Reads entire file into one partition (no parallel split)
    Parser handles quoted multiline fields correctly
    
    Trade-off: loses parallelism → entire file = 1 task
    For large multiline CSV files: consider converting to Parquet instead
```

### Q4: What if you read a directory, not a file?

```
spark.read.csv("s3://bucket/data/")

Behavior:
    Spark lists ALL files in the directory recursively
    Treats each file as a source
    Creates partitions spanning multiple files
    Files are processed in parallel

Gotcha: hidden files and SUCCESS files
    _SUCCESS file (written by Spark after job) → NOT read (underscore prefix ignored)
    _metadata file → NOT read
    .crc files → NOT read (dot prefix ignored)

Config to control recursion:
    spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive = true
```

### Q5: What if you read a Hive partitioned directory?

```
data/
    year=2023/month=01/part-0.parquet
    year=2023/month=02/part-0.parquet
    year=2024/month=01/part-0.parquet

spark.read.parquet("data/")
    → Spark reads directory structure
    → Automatically detects partition columns (year, month) from folder names
    → Adds year and month as columns in DataFrame (partition discovery)

Partition pruning:
    df.filter(col("year") == 2024)
    → Spark ONLY reads year=2024/ directory
    → year=2023/ directories never opened → massive I/O savings
    → No data even requested from S3/HDFS for pruned partitions
```

### Q6: What if two tasks try to read the same block simultaneously?

```
HDFS:
    DataNode handles concurrent reads fine
    Multiple executors can request the same block simultaneously
    DataNode streams to each requester independently
    No locking, fully parallel

S3:
    S3 is stateless HTTP — handles unlimited concurrent GET requests
    No issue at all

Local filesystem:
    OS page cache shared → second reader gets data from cache (fast)
    Concurrent reads to same file = fine (read-only, no locking needed)
```

### Q7: What happens to the data in memory after a partition is processed?

```
Task completes processing partition → output written to shuffle files or result
JVM Garbage Collector reclaims the memory
Next task assigned to same executor slot
New task reads its own partition into memory

Memory is REUSED across tasks — Spark doesn't hold all 160 partitions in memory
At any time, only 12 partitions (one per active task) are in executor memory

Exception: if you call df.cache() / df.persist()
    Processed partitions stored in executor memory as RDD[InternalRow]
    Cached partitions survive task completion
    Used on next action without re-reading from disk/S3
```

### Q8: What if S3 file is modified while Spark is reading it?

```
S3 object modified mid-read:
    S3 objects are IMMUTABLE — you cannot modify, only replace entirely
    Replace = new version with new ETag
    
    If file replaced during a Spark job:
        Tasks reading old version: continue reading (S3 serves old version briefly)
        Tasks starting later: might get new version
        Result: some partitions from old file, some from new → corrupt dataset

Solution:
    Never modify files being read by active Spark jobs
    Use Delta Lake / Iceberg for ACID transactions on data lakes
    These table formats use transaction logs to handle concurrent read/write
```

### Q9: What is Vectorized Reading and how does it help?

```
Traditional reading (row-at-a-time):
    RecordReader → parse Row 1 → process → parse Row 2 → process → ...
    One function call per row → high overhead

Vectorized reading (Spark 2.3+ for Parquet, ORC):
    RecordReader → parse 4096 rows at once into columnar batch
    Process entire batch in tight CPU loop
    Returns ColumnarBatch instead of Row

Benefits:
    CPU SIMD instructions can process multiple values simultaneously
    Better CPU cache utilization (all age values contiguous in memory)
    Fewer JVM function calls → less overhead
    
Enable:
    spark.sql.parquet.enableVectorizedReader = true   (default for Parquet)
    spark.sql.orc.enableVectorizedReader    = true    (default for ORC)

NOT available for CSV/JSON (text parsing is inherently row-at-a-time)
```

### Q10: What is the Driver's role during reading vs execution?

```
During PLANNING (Driver is busy):
    ✅ Contact filesystem for metadata
    ✅ Calculate partition byte ranges
    ✅ Run Catalyst optimizer
    ✅ Create Physical Plan
    ✅ Create tasks and assign to executors

During EXECUTION (Driver mostly idle):
    ✅ Monitor task progress via heartbeats
    ✅ Handle task failures and re-assignment
    ✅ Collect results if action = collect() / show()
    ❌ Driver does NOT read data (executors do)
    ❌ Driver does NOT process rows (executors do)

    Driver is the "coordinator" — not a worker
    If Driver OOM: usually caused by collect() pulling too much data to Driver
```

# Spark File Reading Internals — Complete Deep Dive

---

## 📌 Setup

```
Cluster:  3 Executors × 4 cores × 4 GB
File:     employees.csv = 20 GB
Config:   spark.sql.files.maxPartitionBytes = 128 MB (default)
```

---

## 🔵 STEP 1 — How Many Partitions Are Created?

```
Total file size  = 20 GB = 20,480 MB
Partition size   = 128 MB

Number of partitions = ceil(20,480 / 128) = 160 partitions

So Spark plans:
    Partition 0:   bytes 0         → 134,217,728     (128 MB)
    Partition 1:   bytes 134217728 → 268,435,456     (128 MB)
    Partition 2:   bytes 268435456 → 402,653,184     (128 MB)
    ...
    Partition 159: bytes 19,327,352,832 → 20,480 MB  (last chunk)
```

### The Key Config Parameters That Affect This:

```
spark.sql.files.maxPartitionBytes  = 128 MB  (max size per partition)
spark.sql.files.minPartitionNum    = total_cores (minimum partitions)
spark.default.parallelism          = total_cores × 2 (for RDD operations)
spark.sql.files.openCostInBytes    = 4 MB   (cost to open a file, used for small files)

Formula:
    maxSplitBytes = min(maxPartitionBytes, max(openCostInBytes, totalSize / minPartitionNum))

For our case:
    totalSize = 20 GB
    minPartitionNum = 3 executors × 4 cores = 12
    max(4MB, 20480MB/12) = max(4MB, 1706MB) = 1706MB
    min(128MB, 1706MB) = 128MB  ← partition size stays 128MB
```

---

## 🔵 STEP 2 — Who Decides Which Executor Reads Which Partition?

### The Chain of Responsibility

```
YOU call:
    df = spark.read.csv("path/employees.csv")
    df.show()   ← action triggers everything
         │
         ▼
DRIVER process
    │
    ├── SparkContext contacts FileSystem (HDFS/S3/local)
    ├── Gets file metadata: size, block locations
    ├── Calculates 160 partitions + their byte ranges
    ├── Creates 160 Tasks (one per partition)
    └── Hands task list to DAGScheduler
         │
         ▼
DAGScheduler
    │
    └── Creates Stage 0 with 160 tasks
         │
         ▼
TaskScheduler
    │
    ├── Maintains list of available executor slots
    ├── 3 executors × 4 cores = 12 slots available
    ├── Assigns tasks to executors based on DATA LOCALITY
    └── Sends task to Executor via ExecutorBackend
         │
         ▼
EXECUTOR receives task:
    "Read bytes 134217728 → 268435456 of employees.csv"
    Executor opens file connection and reads its assigned byte range
```

### Data Locality Tiers (Priority Order)

```
PROCESS_LOCAL   → data is in the same JVM process memory (cached RDD)
NODE_LOCAL      → data is on the same physical machine (HDFS block on same node)
RACK_LOCAL      → data is on a different machine but same rack
NO_PREF         → data has no location preference (S3, databases)
ANY             → any executor, anywhere

TaskScheduler tries each tier with a wait timeout before falling back:
    spark.locality.wait         = 3 seconds  (wait for PROCESS_LOCAL)
    spark.locality.wait.node    = 3 seconds  (wait for NODE_LOCAL)
    spark.locality.wait.rack    = 3 seconds  (wait for RACK_LOCAL)
    spark.locality.wait.any     = 0 seconds  (no wait for ANY)
```

---

## 🔵 STEP 3 — How Are 160 Partitions Distributed Across 3 Executors?

```
12 cores available = 12 tasks run simultaneously

Wave 1  (t=0s):    Tasks 0–11   assigned (4 per executor)
Wave 2  (t=Xs):    Tasks 12–23  assigned (as Wave 1 tasks complete)
Wave 3  (t=2Xs):   Tasks 24–35  assigned
...
Wave 14 (t=13Xs):  Tasks 156–159 assigned (only 4 tasks, 8 cores idle)

Total waves = ceil(160/12) ≈ 14 waves

At any point in time:
    Executor 1: reads partitions P0, P1, P2, P3   (4 simultaneous reads)
    Executor 2: reads partitions P4, P5, P6, P7   (4 simultaneous reads)
    Executor 3: reads partitions P8, P9, P10, P11 (4 simultaneous reads)

Assignment is NOT fixed — it's dynamic:
    If Executor 1 finishes P0 early → immediately gets P12
    Faster executors get more tasks
    Slower executors (GC pauses, slower disk) get fewer tasks in same time
```

---

## 🔵 STEP 4 — THE CRITICAL QUESTION: How Is a Line Not Split Across Executors?

This is the most important internal mechanism most people don't know.

### The Problem

```
File on disk (raw bytes):
    ...Alice,30,Engineering\nBob,25,Marketi|ng,500\nCarol...
                             ^                  ^
                         partition boundary  next partition starts here
                         at byte 134217728

If Spark blindly reads bytes 0→128MB and 128MB→256MB:
    Partition 0 ends with:  "...Bob,25,Marketi"   ← INCOMPLETE ROW!
    Partition 1 starts with: "ng,500\nCarol..."    ← INCOMPLETE ROW!
    
This would corrupt data. Spark prevents this with split boundary logic.
```

### The Solution — InputSplit Boundary Adjustment

```
Step 1: Spark calculates logical split at byte 134,217,728 (128 MB mark)

Step 2: The InputFormat/RecordReader for the task assigned to Partition 0:
    Opens file at byte 0
    Reads until byte 134,217,728 (the boundary)
    CONTINUES READING past the boundary until it finds '\n' (newline)
    INCLUDES that partial line in Partition 0
    Stops AFTER the newline

Step 3: The RecordReader for Partition 1:
    Opens file at byte 134,217,728 (the boundary)
    SKIPS bytes until it finds the FIRST '\n' after the boundary
    Starts reading from the character AFTER that '\n'
    This ensures it doesn't re-read the line already claimed by Partition 0

RESULT:
    Partition 0 reads: bytes 0 → 134,217,792  (boundary + 64 extra bytes for partial line)
    Partition 1 reads: bytes 134,217,793 → 268,435,456 (starts after the overrun line)

Every line is complete, no line is ever split, no line is ever duplicated.
```

### Visualized

```
Raw file bytes:
|-------- 128 MB ---------|-------- 128 MB ----------|

byte: 0                134217728                268435456
      │                    │                        │
      │                    │←─ boundary             │
      ▼                    ▼                        ▼
...salary\nAlice,30,Eng\nBo|b,25,Marketing\nCarol,35|,Eng\n...
                           ^                        ^
                     exact 128MB mark         exact 256MB mark

Partition 0 RecordReader:
    Reads: bytes 0 → finds \n after 134217728
    Actual end: ...Marketing\n   (includes Bob's complete row)
    ✅ Bob's row is COMPLETE in Partition 0

Partition 1 RecordReader:
    Opens at: byte 134217728
    Skips forward to first \n  (skips "b,25,Marketing")
    Starts reading from: Carol,35,...
    ✅ Carol's row is COMPLETE in Partition 1
    ✅ Bob's row is NOT duplicated
```

### Who implements this logic?

```
For CSV files:
    → org.apache.spark.sql.execution.datasources.csv.CSVFileFormat
    → Uses Hadoop's LineRecordReader internally
    → LineRecordReader handles the split boundary skip logic

For Parquet files:
    → org.apache.spark.sql.execution.datasources.parquet.ParquetFileFormat
    → Parquet is columnar + row-group aware → splits always fall on row group boundaries
    → Row groups are self-contained → no split boundary problem exists

For ORC files:
    → Similar to Parquet — stripe boundaries used as split points
    → ORC stripes = natural split boundaries

For JSON files:
    → org.apache.spark.sql.execution.datasources.json.JsonFileFormat
    → Same LineRecordReader boundary logic as CSV

For custom binary formats:
    → Developer must implement custom RecordReader with proper split handling
```

---

## 🔵 SCENARIO A — Reading from LOCAL FILESYSTEM

### Who pulls the data?

```
Architecture:
    Driver runs on: Machine A
    Executor 1 on:  Machine A (same machine as driver)
    Executor 2 on:  Machine B
    Executor 3 on:  Machine C
    File lives on:  Machine A's local disk /data/employees.csv

Data locality situation:
    Executor 1 (Machine A): NODE_LOCAL or PROCESS_LOCAL
    Executor 2 (Machine B): ANY (must fetch over network)
    Executor 3 (Machine C): ANY (must fetch over network)
```

### Step-by-step execution:

```
Step 1: Driver asks OS for file metadata
    → file size: 20 GB
    → file path: /data/employees.csv
    → NO block location info (local FS has no block registry)

Step 2: Driver creates 160 tasks with byte ranges
    Each task knows: "read bytes X → Y from /data/employees.csv"

Step 3: TaskScheduler assigns tasks with locality preference = NO_PREF
    (local filesystem has no block registry, so any executor can run any task)

Step 4: Executor pulls data
    Executor 1 (same machine):
        Opens /data/employees.csv directly from local disk ✅
        Fast: disk read speed (~500 MB/s for SSD)
        No network involved

    Executor 2 (different machine):
        Cannot access /data/employees.csv directly!
        Spark does NOT automatically share local files across machines
        
        OPTIONS:
        A) File must be on shared filesystem (NFS mount) accessible from all machines
        B) File must be replicated on each machine
        C) Use HDFS/S3 instead (designed for distributed access)

    REAL LIMITATION:
        spark.read.csv("/local/path/file.csv") on a cluster:
        → Only works if ALL executors can see that path
        → NFS, GPFS, or identical local files on all nodes
        → Otherwise: FileNotFoundException on executors that can't see the file
```

### Local file read internals:

```
Executor process:
    FileInputStream.open("/data/employees.csv")
    FileChannel.position(134217728)   ← seek to partition start
    FileChannel.read(buffer, 134217728, 134217728 + 128MB)
    
    OS kernel:
        Checks page cache (is this file already in OS memory?)
        If YES → zero-copy read from page cache (fast)
        If NO  → disk I/O request → DMA transfer → page cache → JVM buffer

    JVM buffer → LineRecordReader → Row objects → task processing
```

---

## 🔵 SCENARIO B — Reading from HDFS (Hadoop Distributed File System)

### How HDFS stores the file:

```
employees.csv = 20 GB

HDFS splits file into BLOCKS (default 128 MB each):
    Block 0:   bytes 0         → 134,217,728    stored on: DataNode 1, DataNode 2, DataNode 3
    Block 1:   bytes 134217728 → 268,435,456    stored on: DataNode 1, DataNode 3, DataNode 2
    Block 2:   bytes 268435456 → 402,653,184    stored on: DataNode 2, DataNode 1, DataNode 3
    ...
    Block 159: last chunk                        stored on: DataNode 3, DataNode 1, DataNode 2

Replication factor = 3 (default)
Each block exists on 3 different DataNodes for fault tolerance
NameNode maintains the block → DataNode mapping (block registry)
```

### Step-by-step HDFS read:

```
Step 1: Driver contacts HDFS NameNode
    Request: "Give me block locations for employees.csv"
    Response: {
        Block 0:   [DataNode1:50010, DataNode2:50010, DataNode3:50010]
        Block 1:   [DataNode1:50010, DataNode3:50010, DataNode2:50010]
        ...
        Block 159: [DataNode3:50010, DataNode1:50010, DataNode2:50010]
    }

Step 2: Driver creates tasks WITH location hints
    Task 0:   "read block 0"  preferredLocations=[DataNode1, DataNode2, DataNode3]
    Task 1:   "read block 1"  preferredLocations=[DataNode1, DataNode3, DataNode2]
    ...

Step 3: TaskScheduler checks if any executor runs on a DataNode machine

    If Executor 1 runs on DataNode1's machine:
        Block 0 can be read locally → NODE_LOCAL
        TaskScheduler waits up to 3 seconds to give Task 0 to Executor 1
        → Fast: no network, disk read speed

    If no executor is on any DataNode:
        All reads are RACK_LOCAL or ANY
        Data fetched over network from DataNode to Executor

Step 4: Executor reads the HDFS block

    Executor contacts HDFS NameNode:
        "I need block 47, where is it?"
    NameNode responds:
        "Block 47 is on DataNode2 at port 50010"
    Executor opens TCP connection to DataNode2:50010
    DataNode2 streams block 47 bytes → Executor memory

    Internally uses: org.apache.hadoop.hdfs.DFSInputStream
    → Handles retry on DataNode failure
    → Switches to replica on DataNode3 if DataNode2 is slow
    → Checksum verification of each block
```

### HDFS vs Local — Key Difference:

```
Local filesystem:
    File exists on ONE machine
    Only that machine can read it directly
    No block registry → no locality optimization

HDFS:
    File blocks spread across ALL DataNodes
    Each block replicated 3 times
    Block registry in NameNode → Spark knows EXACTLY where each block lives
    Data locality optimization possible → NODE_LOCAL reads common
    Any executor can reach any block via network if needed
```

---

## 🔵 SCENARIO C — Reading from S3

### S3 architecture:

```
S3 is OBJECT STORAGE — not a filesystem, not a block store

employees.csv on S3:
    s3://my-bucket/data/employees.csv
    Single object, 20 GB
    No blocks, no DataNodes, no NameNode
    Stored in AWS infrastructure, unknown physical location
    AWS exposes it via HTTPS REST API

No concept of "data locality" → always NO_PREF
```

### Step-by-step S3 read:

```
Step 1: Driver talks to S3 via AWS SDK
    HEAD request: s3://my-bucket/data/employees.csv
    Response: {
        ContentLength: 21,474,836,480  (20 GB)
        ETag: "abc123..."
        LastModified: ...
    }
    NO block location info (S3 is a black box)

Step 2: Driver creates 160 tasks with byte ranges
    Task 0:   bytes 0         → 134,217,728
    Task 1:   bytes 134217728 → 268,435,456
    ...
    preferredLocations = []  ← empty, S3 has no locality

Step 3: TaskScheduler assigns tasks to ANY available executor
    No locality preference → tasks distributed round-robin or by availability

Step 4: Executor reads from S3 using HTTP Range Request

    Executor sends HTTP request:
    GET s3://my-bucket/data/employees.csv
    Range: bytes=134217728-268435455
    Authorization: AWS4-HMAC-SHA256 ...

    AWS S3 responds:
    HTTP 206 Partial Content
    [streams 128 MB of data]

    Internally: S3AInputStream (hadoop-aws library)
    → Handles authentication (AWS SigV4)
    → Handles retry on network errors (exponential backoff)
    → Handles multipart reads for large ranges
    → Supports vectored I/O (Spark 3.3+): multiple byte ranges in one request
```

### S3 specific challenges and solutions:

```
Challenge 1: S3 is NOT a real filesystem
    s3://bucket/dir/ is not a real directory
    Listing 10,000 files in "directory" = 10,000 individual API calls
    Very slow for large datasets with many small files

    Solution:
    → Use S3 Inventory for metadata
    → Use Delta Lake / Iceberg for file listing optimization
    → Avoid millions of tiny files (the "small file problem")

Challenge 2: S3 Eventual Consistency (OLD — before 2020)
    Write a file → might not be immediately visible to list operations
    
    Solution: S3 now provides strong read-after-write consistency (Dec 2020)
    No longer an issue in modern Spark

Challenge 3: High latency per request (~50-200ms vs ~1ms for local disk)
    Opening many small files = thousands of API calls = seconds of overhead

    Solution: spark.sql.files.openCostInBytes = 4MB
    Spark groups small files together into one partition to minimize open calls

Challenge 4: S3 throttling (rate limits)
    Too many requests → HTTP 503 SlowDown

    Solution:
    → spark.hadoop.fs.s3a.connection.maximum = 200
    → Use S3A committer (not the default FileOutputCommitter)
    → Avoid listing the same prefix repeatedly

Challenge 5: Network bandwidth from S3 to your cluster
    Reading 20 GB over network is slower than local disk

    Solution:
    → Run Spark on EC2 in same AWS region as S3 bucket
    → Use S3 Transfer Acceleration for cross-region
    → Use Amazon EMR with EMRFS for optimized S3 access
```

---

## 🔵 SCENARIO D — Reading from a SQL Database (JDBC)

### Architecture:

```
spark.read
    .format("jdbc")
    .option("url",      "jdbc:postgresql://host:5432/mydb")
    .option("dbtable",  "employees")
    .option("user",     "spark_user")
    .option("password", "****")
    .load()
```

### The Default (Terrible) Behavior:

```
Without partitioning config:
    Spark creates EXACTLY 1 partition
    1 executor opens 1 JDBC connection
    Reads ENTIRE employees table sequentially
    Result: completely sequential, no parallelism at all

Why? 
    JDBC has no concept of "byte ranges"
    Database doesn't expose block locations
    Spark doesn't know how to split the table automatically
```

### The Right Way — Parallel JDBC Read:

```python
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://host:5432/mydb") \
    .option("dbtable", "employees") \
    .option("partitionColumn", "employee_id") \   ← numeric column to split on
    .option("lowerBound",      "1") \              ← min value
    .option("upperBound",      "1000000") \        ← max value
    .option("numPartitions",   "10") \             ← 10 parallel connections
    .load()
```

### How parallel JDBC read works internally:

```
Spark generates 10 SQL queries with WHERE clause ranges:

    Task 0 (Executor 1):
        SELECT * FROM employees WHERE employee_id >= 1       AND employee_id < 100001
    Task 1 (Executor 1):
        SELECT * FROM employees WHERE employee_id >= 100001  AND employee_id < 200001
    Task 2 (Executor 2):
        SELECT * FROM employees WHERE employee_id >= 200001  AND employee_id < 300001
    ...
    Task 9 (Executor 3):
        SELECT * FROM employees WHERE employee_id >= 900001  AND employee_id <= 1000000

Each task:
    Opens its OWN JDBC connection to the database
    Sends its WHERE-clause query
    Streams result rows into a Spark partition
    Closes connection when done

Executor 1 opens 4 JDBC connections (4 cores)
Executor 2 opens 3–4 JDBC connections
Executor 3 opens 3–4 JDBC connections

Warning: 10 simultaneous connections to DB → ensure DB connection pool can handle it
Config:  .option("numPartitions", "10") should match DB connection pool size
```

### Predicate Pushdown for JDBC:

```
df.filter(col("age") > 30).select("name", "department")

WITHOUT pushdown (bad):
    SELECT * FROM employees          ← sends all data
    Spark applies filter in memory

WITH pushdown (good, Spark does this automatically for JDBC):
    SELECT name, department FROM employees WHERE age > 30  ← DB does the work
    Only filtered, projected data sent over network

Config: spark.sql.jdbc.dialect  ← Spark uses DB-specific SQL dialect
Supported: PostgreSQL, MySQL, Oracle, SQL Server, DB2, etc.
```

### JDBC Line Boundary Equivalent:

```
No line boundary problem for JDBC!

Why? Database returns complete rows via ResultSet
    ResultSet.next() → always returns one complete row
    No concept of byte ranges or partial rows
    The JDBC driver handles all protocol-level framing

The "split boundary" problem only exists for flat files (CSV, JSON, text)
    because they're raw bytes without row framing
```

---

## 🔵 SCENARIO E — Reading Many Small Files (The Small File Problem)

### Setup:

```
Instead of 1 file of 20 GB:
    10,000 files × 2 MB each = 20 GB total

Default behavior:
    Each file = 1 partition (even though 2 MB << 128 MB limit)
    Result: 10,000 partitions = 10,000 tasks

Problems:
    10,000 tasks ÷ 12 cores = 834 waves of execution
    Each task: open file (50ms overhead) + read 2 MB + close file
    Overhead dominates actual work
    Task scheduling overhead is massive
```

### How Spark handles this — File Coalescing:

```
spark.sql.files.openCostInBytes = 4 MB (default)

This config says: "treat each file open as if it costs 4 MB of data"

Packing algorithm:
    Start new partition (budget = 128 MB)
    
    File 1: 2 MB data + 4 MB open cost = 6 MB → pack into partition 0 (budget: 122 MB left)
    File 2: 2 MB data + 4 MB open cost = 6 MB → pack into partition 0 (budget: 116 MB left)
    File 3: 2 MB data + 4 MB open cost = 6 MB → pack into partition 0 (budget: 110 MB left)
    ...
    File 21: would exceed 128 MB budget → start partition 1
    
    Files per partition = 128 MB / 6 MB ≈ 21 files
    Total partitions = 10,000 / 21 ≈ 477 partitions

477 partitions ÷ 12 cores = 40 waves  ← much better than 834!
```

### Solution for extreme small file problems:

```python
# Option 1: Increase partition size to pack more files
spark.conf.set("spark.sql.files.maxPartitionBytes", str(256 * 1024 * 1024))  # 256MB

# Option 2: Explicitly coalesce after reading
df = spark.read.csv("s3://bucket/many-small-files/*")
df = df.coalesce(160)  # reduce from 477 to 160 partitions

# Option 3: Use wholeTextFiles (for very tiny files)
rdd = sc.wholeTextFiles("s3://bucket/many-small-files/*", minPartitions=160)

# Option 4: Fix upstream — write larger files
df.write.option("maxRecordsPerFile", 1000000).parquet("output/")
```

---

## 🔵 SCENARIO F — Reading Parquet Files (Columnar Format)

### How Parquet splits differently from CSV:

```
Parquet file internal structure:
    ┌─────────────────────────────────┐
    │  File Header (magic bytes)      │
    ├─────────────────────────────────┤
    │  Row Group 0  (e.g., 128 MB)    │  ← natural split boundary
    │    Column chunk: name           │
    │    Column chunk: age            │
    │    Column chunk: salary         │
    ├─────────────────────────────────┤
    │  Row Group 1  (e.g., 128 MB)    │  ← natural split boundary
    │    Column chunk: name           │
    │    Column chunk: age            │
    │    Column chunk: salary         │
    ├─────────────────────────────────┤
    │  ...                            │
    ├─────────────────────────────────┤
    │  File Footer (schema + metadata)│
    └─────────────────────────────────┘

Each Row Group = one Spark partition
No split boundary adjustment needed — Row Groups are self-contained
```

### Column Pruning — Why Parquet is much faster:

```
Query: SELECT name, salary FROM employees WHERE age > 30

CSV read:
    Must read ALL bytes of all columns: name, age, salary, department, phone...
    Then discard unwanted columns in memory

Parquet read:
    Only reads column chunks for: name, age, salary
    Completely SKIPS column chunks for: department, phone, email, ...
    For age > 30 filter: reads age column first, builds bitmask of matching rows
    Then only fetches those specific rows from name and salary columns
    
Result: if you select 3 of 20 columns, Parquet reads only 15% of the data
```

### Row Group Statistics — Predicate Pushdown:

```
Parquet stores min/max statistics per Row Group per column:
    Row Group 0: age min=18, max=25
    Row Group 1: age min=26, max=35
    Row Group 2: age min=36, max=65

Query: WHERE age > 30

Spark reads footer statistics BEFORE reading any Row Group data:
    Row Group 0: max=25, 25 < 30 → SKIP ENTIRE ROW GROUP ✅ (128 MB saved!)
    Row Group 1: min=26, max=35, overlaps 30 → must read
    Row Group 2: min=36, 36 > 30 → read all rows (all match)

This is "Parquet predicate pushdown" — skip entire chunks before reading
```

---

## 🔵 SCENARIO G — Reading a Compressed File (gzip vs snappy vs lz4)

### Splittable vs Non-Splittable compression:

```
NON-SPLITTABLE formats:
    .csv.gz   (gzip)
    .csv.bz2  (bzip2 — actually splittable but rare)
    .csv.zip

    Problem:
        gzip is a STREAM compression — must decompress from byte 0
        Cannot seek to byte 134,217,728 and start decompressing
        Therefore: entire file = 1 partition, 1 task, NO parallelism

    employees.csv.gz = 20 GB compressed
    → 1 partition
    → 1 task
    → 1 executor reads and decompresses entire file
    → Other 11 cores sit idle
    → Very slow

SPLITTABLE formats:
    .parquet  (internally splittable by row groups)
    .orc      (internally splittable by stripes)
    .avro     (splittable with sync markers)
    .csv.snappy (snappy-compressed parquet/avro is splittable)
    .bz2      (has sync points every 900KB — technically splittable)
    .lz4      (in certain container formats)

    For splittable formats:
        Each split can be decompressed independently
        Full parallelism maintained

RULE: Never store large datasets as .csv.gz on a cluster
      Always use Parquet + Snappy for analytical workloads
```

---

## 🔵 SCENARIO H — Schema Inference (inferSchema=True) — The Hidden Cost

```python
df = spark.read.csv("employees.csv", header=True, inferSchema=True)
```

### What inferSchema actually does:

```
Step 1: Spark runs a SEPARATE FULL SCAN of the entire file
    → Reads all 20 GB
    → Samples values from each column
    → Determines types: is "age" always an integer? could it be double? string?

Step 2: Type resolution rules:
    All values parseable as Int → IntegerType
    Any value is float → DoubleType
    Any value is non-numeric → StringType
    All values are "true"/"false" → BooleanType

Step 3: Returns inferred schema to Driver
Step 4: SECOND full scan happens when action is called

Total: 20 GB read TWICE (once for schema, once for data)

Performance fix:
    Provide schema explicitly:
    from pyspark.sql.types import *
    schema = StructType([
        StructField("name",       StringType(),  True),
        StructField("age",        IntegerType(), True),
        StructField("department", StringType(),  True),
        StructField("salary",     DoubleType(),  True)
    ])
    df = spark.read.csv("employees.csv", header=True, schema=schema)
    → Only ONE scan, schema not inferred
```

---

## 🔵 SCENARIO I — What Happens When a Read Task Fails?

```
Task 5 is reading partition 5 (bytes 640MB → 768MB) from HDFS
Executor 2 crashes mid-read

Step 1: Executor 2 stops sending heartbeats to Driver
Step 2: Driver detects timeout (spark.network.timeout = 120s default)
Step 3: Driver marks Task 5 as FAILED
Step 4: Driver marks all tasks running on Executor 2 as FAILED
Step 5: TaskScheduler re-queues failed tasks
Step 6: Cluster Manager launches new Executor 4 (replacement)
Step 7: Task 5 re-assigned to Executor 4
Step 8: Executor 4 reads from HDFS:
    Contacts NameNode: "where is block 5?"
    NameNode: "DataNode 1 and DataNode 3 have it" (replica!)
    Executor 4 reads from DataNode 1 → success

Why this works:
    HDFS replication = 3 → even if one DataNode is down, 2 replicas remain
    S3 → AWS handles redundancy internally, always available
    Local filesystem → if the machine is down, the data is gone → job fails

Config:
    spark.task.maxFailures = 4  ← retry each task up to 4 times before giving up
```

---

## 📊 Complete Comparison Table

```
┌─────────────────┬──────────────┬────────────────────┬─────────────────┬───────────────┐
│ Aspect          │ Local FS     │ HDFS               │ S3              │ JDBC          │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Block/split     │ No blocks    │ 128 MB blocks       │ No blocks       │ No blocks     │
│ registry        │             │ in NameNode        │                 │               │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Data locality   │ NO_PREF      │ NODE_LOCAL possible│ NO_PREF (always)│ NO_PREF       │
│                 │             │                    │                 │               │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Who pulls data  │ Executor     │ Executor from      │ Executor via    │ Executor via  │
│                 │ direct read  │ DataNode TCP conn  │ HTTPS GET Range │ JDBC TCP conn │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Split boundary  │ LineRecord   │ LineRecordReader   │ LineRecord      │ N/A           │
│ handling        │ Reader       │                    │ Reader          │ (DB rows)     │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Fault tolerance │ ❌ Single    │ ✅ 3x replication  │ ✅ AWS managed  │ ✅ DB managed  │
│                 │ point        │                    │                 │               │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Parallelism     │ Limited      │ ✅ Full parallel   │ ✅ Full parallel │ Needs config  │
│                 │ (shared FS)  │                    │                 │               │
├─────────────────┼──────────────┼────────────────────┼─────────────────┼───────────────┤
│ Line boundary   │ LineRecord   │ LineRecordReader   │ LineRecord      │ ResultSet     │
│ guarantee       │ Reader skip  │ skip logic         │ Reader skip     │ (auto, rows)  │
└─────────────────┴──────────────┴────────────────────┴─────────────────┴───────────────┘
```

---

## 🧠 Scenarios You Might Not Have Thought to Ask

### Q1: What if the file has Windows line endings (\r\n)?

```
LineRecordReader handles both \n and \r\n
When it finds the split boundary, it searches for \n
Automatically strips \r if present before \n
Result: rows work correctly regardless of OS line endings
```

### Q2: What if one row is 200 MB (larger than partition size)?

```
A single row > 128 MB:
    Partition 0 tries to read up to 128 MB → finds no \n → keeps reading
    Reads entire 200 MB row into memory (crosses partition boundary)
    Next partition starts after that row
    Result: Partition 0 = 200 MB (larger than configured 128 MB)
    
    Spark DOES NOT split a single row across partitions
    Memory impact: that executor task needs > 128 MB just for one row
    If row is extremely large → executor OOM possible
```

### Q3: What if the CSV has quoted fields with newlines inside?

```
Example:
    Alice,30,"Engineering
    Department",90000

LineRecordReader splits on \n → would break "Engineering\nDepartment" into two records!

Solution:
    spark.read.option("multiLine", "true").csv(...)

With multiLine=true:
    Spark uses a different reader (not LineRecordReader)
    Reads entire file into one partition (no parallel split)
    Parser handles quoted multiline fields correctly
    
    Trade-off: loses parallelism → entire file = 1 task
    For large multiline CSV files: consider converting to Parquet instead
```

### Q4: What if you read a directory, not a file?

```
spark.read.csv("s3://bucket/data/")

Behavior:
    Spark lists ALL files in the directory recursively
    Treats each file as a source
    Creates partitions spanning multiple files
    Files are processed in parallel

Gotcha: hidden files and SUCCESS files
    _SUCCESS file (written by Spark after job) → NOT read (underscore prefix ignored)
    _metadata file → NOT read
    .crc files → NOT read (dot prefix ignored)

Config to control recursion:
    spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive = true
```

### Q5: What if you read a Hive partitioned directory?

```
data/
    year=2023/month=01/part-0.parquet
    year=2023/month=02/part-0.parquet
    year=2024/month=01/part-0.parquet

spark.read.parquet("data/")
    → Spark reads directory structure
    → Automatically detects partition columns (year, month) from folder names
    → Adds year and month as columns in DataFrame (partition discovery)

Partition pruning:
    df.filter(col("year") == 2024)
    → Spark ONLY reads year=2024/ directory
    → year=2023/ directories never opened → massive I/O savings
    → No data even requested from S3/HDFS for pruned partitions
```

### Q6: What if two tasks try to read the same block simultaneously?

```
HDFS:
    DataNode handles concurrent reads fine
    Multiple executors can request the same block simultaneously
    DataNode streams to each requester independently
    No locking, fully parallel

S3:
    S3 is stateless HTTP — handles unlimited concurrent GET requests
    No issue at all

Local filesystem:
    OS page cache shared → second reader gets data from cache (fast)
    Concurrent reads to same file = fine (read-only, no locking needed)
```

### Q7: What happens to the data in memory after a partition is processed?

```
Task completes processing partition → output written to shuffle files or result
JVM Garbage Collector reclaims the memory
Next task assigned to same executor slot
New task reads its own partition into memory

Memory is REUSED across tasks — Spark doesn't hold all 160 partitions in memory
At any time, only 12 partitions (one per active task) are in executor memory

Exception: if you call df.cache() / df.persist()
    Processed partitions stored in executor memory as RDD[InternalRow]
    Cached partitions survive task completion
    Used on next action without re-reading from disk/S3
```

### Q8: What if S3 file is modified while Spark is reading it?

```
S3 object modified mid-read:
    S3 objects are IMMUTABLE — you cannot modify, only replace entirely
    Replace = new version with new ETag
    
    If file replaced during a Spark job:
        Tasks reading old version: continue reading (S3 serves old version briefly)
        Tasks starting later: might get new version
        Result: some partitions from old file, some from new → corrupt dataset

Solution:
    Never modify files being read by active Spark jobs
    Use Delta Lake / Iceberg for ACID transactions on data lakes
    These table formats use transaction logs to handle concurrent read/write
```

### Q9: What is Vectorized Reading and how does it help?

```
Traditional reading (row-at-a-time):
    RecordReader → parse Row 1 → process → parse Row 2 → process → ...
    One function call per row → high overhead

Vectorized reading (Spark 2.3+ for Parquet, ORC):
    RecordReader → parse 4096 rows at once into columnar batch
    Process entire batch in tight CPU loop
    Returns ColumnarBatch instead of Row

Benefits:
    CPU SIMD instructions can process multiple values simultaneously
    Better CPU cache utilization (all age values contiguous in memory)
    Fewer JVM function calls → less overhead
    
Enable:
    spark.sql.parquet.enableVectorizedReader = true   (default for Parquet)
    spark.sql.orc.enableVectorizedReader    = true    (default for ORC)

NOT available for CSV/JSON (text parsing is inherently row-at-a-time)
```

### Q10: What is the Driver's role during reading vs execution?

```
During PLANNING (Driver is busy):
    ✅ Contact filesystem for metadata
    ✅ Calculate partition byte ranges
    ✅ Run Catalyst optimizer
    ✅ Create Physical Plan
    ✅ Create tasks and assign to executors

During EXECUTION (Driver mostly idle):
    ✅ Monitor task progress via heartbeats
    ✅ Handle task failures and re-assignment
    ✅ Collect results if action = collect() / show()
    ❌ Driver does NOT read data (executors do)
    ❌ Driver does NOT process rows (executors do)

    Driver is the "coordinator" — not a worker
    If Driver OOM: usually caused by collect() pulling too much data to Driver
```

# How Number of Files Affects Spark Partitions — Complete Guide

---

## 📌 The Core Rule — Before Anything Else

```
Spark partition count when reading files is determined by:

    max(
        minPartitions,
        total_bytes_across_all_files / maxPartitionBytes
    )

BUT with a critical constraint:
    A SINGLE FILE IS NEVER SPLIT ACROSS FEWER THAN 1 PARTITION
    and
    A SINGLE FILE *CAN* CREATE MULTIPLE PARTITIONS if it is larger than maxPartitionBytes
    BUT only if the file format is SPLITTABLE

Splittable formats:    Parquet, ORC, Avro, uncompressed CSV/JSON, bzip2
Non-splittable formats: gzip CSV (.csv.gz), zip, snappy CSV (not in parquet container)
```

---

## 🔵 CASE 1 — One Large File

### Setup
```
File: employees.csv = 20 GB (uncompressed, splittable)
maxPartitionBytes = 128 MB
Executors: 3 × 4 cores = 12 cores
```

### What happens
```
20 GB / 128 MB = 160 partitions

Partition 0:   bytes 0         → 128 MB    → 1 task
Partition 1:   bytes 128 MB    → 256 MB    → 1 task
...
Partition 159: bytes 19.875 GB → 20 GB     → 1 task

Result: 160 partitions, 160 tasks, 14 waves (160/12)
```

### Visualized
```
employees.csv [20 GB]
│
├── Partition 0  [128 MB] ──→ Task 0  → Executor 1
├── Partition 1  [128 MB] ──→ Task 1  → Executor 1
├── Partition 2  [128 MB] ──→ Task 2  → Executor 1
├── Partition 3  [128 MB] ──→ Task 3  → Executor 1
│   (Executor 1 runs 4 at a time)
├── Partition 4  [128 MB] ──→ Task 4  → Executor 2
...
└── Partition 159 [last]  ──→ Task 159 → Executor 3
```

---

## 🔵 CASE 2 — One Large File BUT Gzip Compressed (Non-Splittable)

### Setup
```
File: employees.csv.gz = 5 GB (compressed, was 20 GB uncompressed)
maxPartitionBytes = 128 MB
```

### What happens
```
gzip is NOT splittable — cannot seek to middle and decompress

Result: 1 partition, 1 task, 11 cores sit IDLE

Partition 0: entire 20 GB file (after decompression) → 1 task → 1 executor

The other 2 executors (8 cores) do absolutely nothing until this one task finishes
```

### Visualized
```
employees.csv.gz [5 GB compressed = 20 GB uncompressed]
│
└── Partition 0  [ENTIRE FILE] ──→ Task 0 → Executor 1 only
                                   Executor 2: idle ❌
                                   Executor 3: idle ❌

Time to read: ~20x slower than the splittable version
```

### Fix
```python
# BAD — loses parallelism
df = spark.read.csv("s3://bucket/employees.csv.gz")

# GOOD — use Parquet with Snappy (splittable + compressed)
df.write.parquet("s3://bucket/employees.parquet")  # convert once
df = spark.read.parquet("s3://bucket/employees.parquet")  # fast parallel reads
```

---

## 🔵 CASE 3 — Many Small Files (The Most Common Problem)

### Setup
```
10,000 files × 2 MB each = 20 GB total
maxPartitionBytes   = 128 MB
openCostInBytes     = 4 MB  (default — cost to open one file)
```

### What naive behavior would be (WITHOUT coalescing)
```
One file = at minimum one partition
10,000 files → 10,000 partitions → 10,000 tasks

10,000 tasks ÷ 12 cores = 834 waves
Each task: open file (50ms) + read 2 MB + process + close
Overhead >> actual work
```

### What Spark ACTUALLY does — File Coalescing Algorithm

```
Spark's FilePartition packing algorithm:

Budget per partition = maxPartitionBytes = 128 MB
Cost of each file    = file_size + openCostInBytes
                     = 2 MB    + 4 MB
                     = 6 MB effective cost

Files packed into one partition:
    128 MB / 6 MB = 21 files per partition

Total partitions = ceil(10,000 / 21) = 477 partitions

477 tasks ÷ 12 cores = 40 waves  ← much better!
```

### Packing algorithm step by step
```
Start partition_0, budget = 128 MB

file_0001.csv (2 MB) → cost = 6 MB → fits (budget left: 122 MB)
file_0002.csv (2 MB) → cost = 6 MB → fits (budget left: 116 MB)
file_0003.csv (2 MB) → cost = 6 MB → fits (budget left: 110 MB)
...
file_0021.csv (2 MB) → cost = 6 MB → fits (budget left: 2 MB)
file_0022.csv (2 MB) → cost = 6 MB → does NOT fit (2 MB < 6 MB)
                    → close partition_0, start partition_1

partition_0 = files 0001–0021 (21 files, 42 MB actual data)
partition_1 = starts with file_0022
...

Note: actual data in each partition = 42 MB
      but treated as 128 MB due to open cost padding
      This PREVENTS too many tiny partitions
```

### Visualized
```
BEFORE coalescing (naive):
file_0001.csv [2MB] → Partition 0    (1 file each)
file_0002.csv [2MB] → Partition 1
file_0003.csv [2MB] → Partition 2
...
file_9999.csv [2MB] → Partition 9,999
= 10,000 partitions ❌

AFTER coalescing (what Spark does):
files 0001–0021 → Partition 0   (21 files, 42 MB)
files 0022–0042 → Partition 1   (21 files, 42 MB)
files 0043–0063 → Partition 2   (21 files, 42 MB)
...
= 477 partitions ✅
```

---

## 🔵 CASE 4 — Mix of Small and Large Files

### Setup
```
5 files × 500 MB  = 2.5 GB  (large files)
100 files × 1 MB  = 0.1 GB  (small files)
Total             = 2.6 GB
maxPartitionBytes = 128 MB
openCostInBytes   = 4 MB
```

### What happens to large files (500 MB each)
```
500 MB > 128 MB → each large file gets split into multiple partitions

File_A.csv (500 MB):
    Partition 0: bytes 0     → 128 MB
    Partition 1: bytes 128MB → 256 MB
    Partition 2: bytes 256MB → 384 MB
    Partition 3: bytes 384MB → 500 MB
    = 4 partitions from File_A

5 large files × 4 partitions = 20 partitions from large files
```

### What happens to small files (1 MB each)
```
1 MB + 4 MB open cost = 5 MB effective cost
128 MB / 5 MB = 25 files per partition

100 small files / 25 = 4 partitions from small files
```

### Total
```
Large files: 20 partitions
Small files:  4 partitions
Total:        24 partitions

Without coalescing of small files: 100 + 20 = 120 partitions
With coalescing:                          24 partitions ✅
```

---

## 🔵 CASE 5 — S3 Specific: Listing Overhead

### How S3 file listing works
```
spark.read.csv("s3://bucket/data/")

Spark must LIST all files before it can plan partitions:

S3 LIST API:
    One LIST request = max 1,000 objects returned
    10,000 files = 10 LIST requests
    100,000 files = 100 LIST requests
    1,000,000 files = 1,000 LIST requests

Each LIST request ≈ 50-200ms latency
1,000,000 files → 1,000 requests × 100ms = 100 seconds JUST TO LIST FILES

This happens BEFORE any data is read
This is a driver-side operation — driver is blocked during listing
```

### Visualized listing overhead
```
spark.read.parquet("s3://bucket/data/")  ← you call this
         │
         ▼
Driver → S3 LIST s3://bucket/data/?prefix=data/&max-keys=1000
         ← returns 1000 file names + sizes
Driver → S3 LIST s3://bucket/data/?prefix=data/&continuation-token=abc
         ← returns next 1000 file names + sizes
...repeated N times...
Driver has full file list → calculates partitions → submits tasks

With 1M files:   listing = minutes
With 10M files:  listing = tens of minutes → job appears "stuck"
```

### S3 listing solutions
```python
# Solution 1: Use Hive-style partitioning (partition pruning skips directories)
s3://bucket/data/year=2024/month=01/  ← Spark only lists year=2024/month=01/
s3://bucket/data/year=2024/month=02/  ← skipped if filter doesn't need it
df = spark.read.parquet("s3://bucket/data/").filter("year=2024 AND month=1")

# Solution 2: Delta Lake / Iceberg (transaction log replaces directory listing)
df = spark.read.format("delta").load("s3://bucket/delta-table/")
# Delta reads _delta_log/ JSON files instead of listing all data files
# Listing 1M files → reading 1 transaction log file

# Solution 3: Manifest files
# Pre-generate a file listing, read from manifest
df = spark.read.option("pathGlobFilter", "*.parquet") \
              .parquet("s3://bucket/data/specific-prefix-*")
```

---

## 🔵 CASE 6 — S3 with Hive Partitioned Data

### Directory structure
```
s3://bucket/sales/
    year=2022/month=01/day=01/part-00000.parquet  [500 MB]
    year=2022/month=01/day=02/part-00000.parquet  [500 MB]
    ...
    year=2024/month=12/day=31/part-00000.parquet  [500 MB]

Total: 3 years × 12 months × 30 days = 1,080 files × 500 MB = 540 GB
```

### Without filter (reads everything)
```python
df = spark.read.parquet("s3://bucket/sales/")

Partitions = 540 GB / 128 MB = 4,320 partitions
All 1,080 files listed and read
```

### With filter (partition pruning)
```python
df = spark.read.parquet("s3://bucket/sales/") \
              .filter("year = 2024 AND month = 6")

Spark sees filter on partition columns (year, month)
Only lists: s3://bucket/sales/year=2024/month=6/
Finds: 30 files (one per day) × 500 MB = 15 GB

Partitions = 15 GB / 128 MB = 120 partitions
Only 30 files read (not 1,080)
S3 LIST calls: 1 (not 1,080)

Speedup: 36x less data read, 36x fewer partitions
```

---

## 🔵 HOW TO CONTROL PARTITION COUNT — All Methods

### Method 1: Change maxPartitionBytes (affects read-time splitting)

```python
# Increase partition size → fewer, larger partitions
spark.conf.set("spark.sql.files.maxPartitionBytes", str(256 * 1024 * 1024))  # 256 MB
df = spark.read.csv("s3://bucket/data/")

# 20 GB / 256 MB = 80 partitions (was 160 at 128 MB)

# Decrease partition size → more, smaller partitions
spark.conf.set("spark.sql.files.maxPartitionBytes", str(64 * 1024 * 1024))  # 64 MB
df = spark.read.csv("s3://bucket/data/")

# 20 GB / 64 MB = 320 partitions

# When to increase: tasks are too small, too many waves
# When to decrease: tasks are OOMing, data is skewed
```

### Method 2: Change openCostInBytes (affects small file coalescing)

```python
# INCREASE → more files packed per partition (fewer partitions for small files)
spark.conf.set("spark.sql.files.openCostInBytes", str(8 * 1024 * 1024))  # 8 MB
# 10,000 files × 2 MB:
# cost per file = 2 MB + 8 MB = 10 MB
# files per partition = 128 MB / 10 MB = 12
# total partitions = 10,000 / 12 = 834 (fewer, larger partitions)

# DECREASE → fewer files packed per partition (more partitions for small files)
spark.conf.set("spark.sql.files.openCostInBytes", str(1 * 1024 * 1024))  # 1 MB
# cost per file = 2 MB + 1 MB = 3 MB
# files per partition = 128 MB / 3 MB = 42
# total partitions = 10,000 / 42 = 238

# When to increase: too many tiny-task partitions
# When to decrease: files are large enough, don't need aggressive coalescing
```

### Method 3: repartition() — Full Shuffle

```python
df = spark.read.csv("s3://bucket/data/")
# df has 477 partitions (small file coalescing result)

# Repartition to EXACTLY 160 partitions
df = df.repartition(160)

# What happens internally:
# → Triggers a FULL SHUFFLE (expensive)
# → All data redistributed across cluster
# → 160 new evenly-sized partitions created
# → Use when you need EXACTLY N evenly distributed partitions

# Repartition by column (for downstream join/groupBy optimization)
df = df.repartition(200, col("department"))
# → All rows with same department → same partition
# → Useful if many groupBy("department") operations follow
```

### Method 4: coalesce() — No Shuffle (Reduce Only)

```python
df = spark.read.csv("s3://bucket/data/")
# df has 477 partitions

# Reduce to 160 partitions WITHOUT shuffle
df = df.coalesce(160)

# What happens internally:
# → NO shuffle — just merges adjacent partitions
# → Partition 0 + Partition 1 + Partition 2 → new Partition 0
# → Fast, but partitions may be UNEVEN in size
# → Can only REDUCE partition count, never increase

# When to use coalesce vs repartition:
# coalesce:     reducing partitions, don't care about balance, want speed
# repartition:  need even balance, or need to increase partitions, or by column
```

### Method 5: minPartitions hint (for text files)

```python
# Force minimum partition count
df = spark.read \
         .option("minPartitions", "200") \
         .csv("s3://bucket/small-file/employees.csv")

# If file is 100 MB normally = 1 partition
# With minPartitions=200 → Spark tries to create at least 200 partitions
# Splits the 100 MB file into 200 × 0.5 MB chunks

# Useful when: one large file needs more parallelism than maxPartitionBytes gives
```

### Method 6: JDBC numPartitions

```python
df = spark.read \
    .format("jdbc") \
    .option("url",             "jdbc:postgresql://host:5432/mydb") \
    .option("dbtable",         "employees") \
    .option("partitionColumn", "id") \
    .option("lowerBound",      "1") \
    .option("upperBound",      "10000000") \
    .option("numPartitions",   "50") \     ← controls exactly how many parallel queries
    .load()

# Creates 50 tasks each running:
# SELECT * FROM employees WHERE id >= X AND id < Y
# 50 parallel JDBC connections to database
```

### Method 7: Explicit repartition at write time (fix for future reads)

```python
# You have 10,000 small files → slow future reads
# Fix: rewrite as optimally-sized files

df = spark.read.parquet("s3://bucket/10000-small-files/")
# df has 477 partitions of small data

df.repartition(160) \
  .write \
  .parquet("s3://bucket/160-good-files/")

# Now future reads:
# 160 files × ~125 MB = 160 partitions, perfect ✅
```

### Method 8: AQE Coalescing (Automatic, Spark 3.x)

```python
# Enable AQE (default in Spark 3.2+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128mb")
spark.conf.set("spark.sql.adaptive.coalescePartitions.minPartitionNum", "1")

# After a shuffle, AQE measures actual partition sizes
# Automatically coalesces tiny shuffle output partitions
# e.g., 200 shuffle partitions → only 50 MB total → AQE coalesces to 1 partition

# NOTE: AQE affects post-shuffle partitions, NOT initial file read partitions
```

---

## 🔵 DECISION GUIDE — What to Use When

```
SCENARIO                                → SOLUTION
────────────────────────────────────────────────────────────────────────────────
One large splittable file, right size   → default maxPartitionBytes, do nothing

One large gzip file, no parallelism     → convert to Parquet+Snappy first

10,000 small files, too many tasks      → increase openCostInBytes
                                        → OR repartition after read
                                        → OR rewrite as fewer larger files

Too few partitions, cores underutilized → decrease maxPartitionBytes
                                        → OR repartition(N) after read

Too many partitions, task overhead high → increase maxPartitionBytes
                                        → OR coalesce(N) after read

Need exactly N partitions               → repartition(N) after read

Need partitions aligned to a column    → repartition(N, col("key"))

JDBC single-partition bottleneck        → add partitionColumn + numPartitions

S3 listing slow (millions of files)     → use Delta Lake / Iceberg
                                        → OR use Hive partitioning + filters

Post-shuffle partitions too many/few   → enable AQE (auto-tuning)
```

---

## 📊 Summary Comparison Table

```
┌─────────────────────────────┬────────────────────────────────────────────────────────┐
│ Config / Method             │ What it controls                                       │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ maxPartitionBytes (128 MB)  │ Max bytes per partition when SPLITTING large files     │
│                             │ Fewer → more partitions  /  More → fewer partitions   │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ openCostInBytes (4 MB)      │ Penalty added per file to prevent too many tiny tasks  │
│                             │ Higher → fewer partitions for small files              │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ minPartitions               │ Floor on partition count (forces more splits)          │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ repartition(N)              │ Exact N partitions, even distribution, causes shuffle  │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ repartition(N, col)         │ N partitions, distributed by column hash, shuffle      │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ coalesce(N)                 │ Reduce-only, no shuffle, possibly uneven sizes         │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ JDBC numPartitions          │ Number of parallel DB queries / connections            │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ AQE coalescePartitions      │ Auto-coalesce tiny post-shuffle partitions at runtime  │
├─────────────────────────────┼────────────────────────────────────────────────────────┤
│ Write with repartition      │ Fix file count at write time for future read speed     │
└─────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 🔢 Quick Mental Math Formula

```
For reading files:

    partitions = max(
                    minPartitions,
                    sum(file_sizes) / maxPartitionBytes
                 )

    But for SMALL FILES, effective partition count uses coalescing:
    partitions = sum(file_sizes + openCostInBytes per file) / maxPartitionBytes

For JDBC:
    partitions = numPartitions  (you control it directly)

For POST-SHUFFLE (groupBy, join, orderBy):
    partitions = spark.sql.shuffle.partitions  (default 200)
    With AQE:  auto-coalesced based on actual data sizes

Rule of thumb for target partition size:
    100 MB – 200 MB per partition = sweet spot
    Less than 10 MB per partition = too small (use coalesce)
    More than 500 MB per partition = too large (use repartition or reduce maxPartitionBytes)
```

---

## ⚠️ The 3 Most Common Mistakes

### Mistake 1: Reading millions of small files without coalescing
```python
# BAD — 1M files → 1M partitions → massive overhead
df = spark.read.parquet("s3://bucket/raw-events/")

# GOOD — control partition size
spark.conf.set("spark.sql.files.maxPartitionBytes", str(256 * 1024 * 1024))
df = spark.read.parquet("s3://bucket/raw-events/")
# OR rewrite files into proper sizes first
```

### Mistake 2: Using repartition() when coalesce() is enough
```python
# BAD — causes a full shuffle just to reduce partitions
df = df.repartition(50)   # was 160 partitions

# GOOD — coalesce merges adjacent partitions, no shuffle
df = df.coalesce(50)      # was 160 partitions, no shuffle needed
```

### Mistake 3: Not fixing the small file problem at write time
```python
# BAD — writes 200 tiny files (one per partition)
# If partition data = 1 MB each → 200 × 1 MB = 200 MB in 200 files
df.write.parquet("s3://bucket/output/")

# GOOD — coalesce before writing to control output file count
target_file_size_mb = 128
total_data_mb = 200
num_files = max(1, total_data_mb // target_file_size_mb)  # = 2

df.coalesce(num_files).write.parquet("s3://bucket/output/")
# Writes 2 files × ~100 MB = fast future reads ✅

# OR use maxRecordsPerFile option
df.write.option("maxRecordsPerFile", 1_000_000).parquet("s3://bucket/output/")
```

# Bucketing & Salting in Spark — Complete Guide with Local CSV & S3 Examples

---

## 📌 Why These Two Techniques Exist — The Root Problems

```
Problem 1: REPEATED SHUFFLES
    Every time you join or groupBy the same column → Spark reshuffles EVERY TIME
    join(orders, customers, "customer_id") → 110 GB shuffled across network
    Run same join 10 times/day → 1.1 TB shuffled per day — for same data!

    BUCKETING solves this → pre-shuffle ONCE at write time, ZERO shuffle forever after

────────────────────────────────────────────────────────────────────────────────

Problem 2: DATA SKEW
    Some keys appear WAY more often than others:
    customer_id = 1 (corporate account) → 50,000,000 rows
    customer_id = 2 (regular user)      →         50 rows

    After shuffle → 1 task gets 50M rows → takes 3 hours
    Other 199 tasks finish in seconds → cluster sits idle
    Entire job waits for that 1 task

    SALTING solves this → spread hot keys across multiple tasks artificially
```

---

# ═══════════════════════════════════════
# PART 1 — BUCKETING
# ═══════════════════════════════════════

---

## 🔵 What Is Bucketing?

```
Bucketing = writing data to disk PRE-PARTITIONED and PRE-SORTED by a chosen column
            so that future joins and groupBys on that column require ZERO shuffle

Normal join:   shuffle 110 GB every time      → slow, expensive, repeated
Bucketed join: read matching bucket files locally → zero network transfer, instant

Stored as: Hive-compatible bucketed Parquet files registered in Hive metastore
```

---

## 🔵 The Problem Without Bucketing — Local CSV Example

### Our data (local CSV files)

```
/data/orders.csv    — 100 GB
    order_id, customer_id, product_id, amount, order_date
    1001, 5, 101, 250.00, 2024-01-15
    1002, 8, 204, 89.99,  2024-01-15
    1003, 5, 305, 120.50, 2024-01-16
    ...

/data/customers.csv — 10 GB
    customer_id, name, email, city
    5,  Alice Johnson, alice@email.com, Mumbai
    8,  Bob Smith,     bob@email.com,   Delhi
    ...
```

### Without bucketing — shuffle fires EVERY time

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, count, avg, col

spark = SparkSession.builder \
    .appName("NoBucketingDemo") \
    .getOrCreate()

# Read from local CSV files
orders = spark.read.csv(
    "file:///data/orders.csv",
    header=True,
    inferSchema=True
)

customers = spark.read.csv(
    "file:///data/customers.csv",
    header=True,
    inferSchema=True
)

print(f"Orders partitions:    {orders.rdd.getNumPartitions()}")     # → 800 (100GB/128MB)
print(f"Customers partitions: {customers.rdd.getNumPartitions()}")  # →  80 (10GB/128MB)

# ── Query 1 (Monday morning) ──────────────────────────────────────
result1 = orders.join(customers, "customer_id") \
                .groupBy("city") \
                .agg(sum("amount").alias("revenue"))
result1.show()
# Internally: SHUFFLE orders 100GB + SHUFFLE customers 10GB = 110 GB moved

# ── Query 2 (Monday afternoon — same join!) ───────────────────────
result2 = orders.join(customers, "customer_id") \
                .filter(col("order_date") == "2024-01-15") \
                .groupBy("customer_id") \
                .agg(count("*").alias("orders_today"))
result2.show()
# Internally: SHUFFLE orders 100GB + SHUFFLE customers 10GB = AGAIN 110 GB moved!

# ── Query 3 (Tuesday) — same join again ───────────────────────────
result3 = orders.join(customers, "customer_id") \
                .groupBy("name") \
                .agg(avg("amount").alias("avg_spend"))
result3.show()
# Internally: SHUFFLE orders 100GB + SHUFFLE customers 10GB = AGAIN 110 GB moved!

# Total: 3 queries × 110 GB = 330 GB shuffled for the SAME join key
# 10 queries/day = 1.1 TB shuffled daily — completely avoidable!
```

### What shuffle looks like on disk without bucketing

```
After spark.sql.shuffle.partitions = 200:

orders (100 GB, 800 partitions, random order):
    Part 0:   [cid=5, cid=8, cid=1, cid=302, ...]   ← random mix of customer_ids
    Part 1:   [cid=8, cid=5, cid=99, cid=1,  ...]   ← same customer_id in multiple parts
    Part 2:   [cid=1, cid=5, cid=8,  cid=77, ...]
    ...

Every join must shuffle ALL 100 GB to co-locate matching customer_ids:
    hash(cid=5) % 200 = 12  → all cid=5 rows go to partition 12
    hash(cid=8) % 200 = 87  → all cid=8 rows go to partition 87
    ...
    EVERY PARTITION sends rows to EVERY other partition = full network scan
```

---

## 🔵 Bucketing — The Fix: Same Example, With Bucketing

### Step 1: One-time write as bucketed tables (from local CSV)

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, count, avg, col

spark = SparkSession.builder \
    .appName("BucketingDemo") \
    .enableHiveSupport() \          # ← REQUIRED for bucketing
    .config("spark.sql.warehouse.dir", "/warehouse") \
    .getOrCreate()

# ── Read raw CSV files ─────────────────────────────────────────────
orders_raw = spark.read.csv(
    "file:///data/orders.csv",
    header=True,
    inferSchema=True
)

customers_raw = spark.read.csv(
    "file:///data/customers.csv",
    header=True,
    inferSchema=True
)

# ── ONE-TIME WRITE: bucket both tables by customer_id ─────────────
orders_raw.write \
    .bucketBy(200, "customer_id") \     # split into 200 buckets by customer_id
    .sortBy("customer_id") \            # sort within each bucket
    .mode("overwrite") \
    .saveAsTable("orders_bucketed")     # registered in Hive metastore

customers_raw.write \
    .bucketBy(200, "customer_id") \     # MUST match: same 200 buckets
    .sortBy("customer_id") \
    .mode("overwrite") \
    .saveAsTable("customers_bucketed")

print("Bucketed tables written. This cost one shuffle — paid once, never again.")
```

### What lands on disk after bucketing

```
/warehouse/orders_bucketed/
    part-00000-xxxx.parquet  ← ONLY rows where hash(customer_id) % 200 = 0
                                e.g., cid=200, cid=400, cid=1800, ...
    part-00001-xxxx.parquet  ← ONLY rows where hash(customer_id) % 200 = 1
                                e.g., cid=1, cid=401, cid=1201, ...
    part-00002-xxxx.parquet  ← ONLY rows where hash(customer_id) % 200 = 2
    ...
    part-00199-xxxx.parquet  ← ONLY rows where hash(customer_id) % 200 = 199

/warehouse/customers_bucketed/
    part-00000-xxxx.parquet  ← ONLY customers where hash(customer_id) % 200 = 0
    part-00001-xxxx.parquet  ← ONLY customers where hash(customer_id) % 200 = 1
    ...
    part-00199-xxxx.parquet  ← ONLY customers where hash(customer_id) % 200 = 199

GUARANTEE:
    customer_id = 5  → hash(5) % 200 = 12
    orders_bucketed/part-00012  has ALL orders  for cid=5
    customers_bucketed/part-00012 has ALL customers for cid=5

    Bucket 12 from orders ↔ Bucket 12 from customers → always co-located ✅
```

### Step 2: Every future query — ZERO shuffle

```python
# ── Read bucketed tables ───────────────────────────────────────────
orders    = spark.table("orders_bucketed")
customers = spark.table("customers_bucketed")

# ── Query 1 (Monday morning) — ZERO shuffle ───────────────────────
result1 = orders.join(customers, "customer_id") \
                .groupBy("city") \
                .agg(sum("amount").alias("revenue"))
result1.show()
# Task 0:   reads orders/part-00000  + customers/part-00000 → local join ✅
# Task 1:   reads orders/part-00001  + customers/part-00001 → local join ✅
# ...
# Task 199: reads orders/part-00199  + customers/part-00199 → local join ✅
# ZERO bytes shuffled across network

# ── Query 2 (Monday afternoon — ZERO shuffle again) ───────────────
result2 = orders.join(customers, "customer_id") \
                .filter(col("order_date") == "2024-01-15") \
                .groupBy("customer_id") \
                .agg(count("*").alias("orders_today"))
result2.show()
# Still ZERO shuffle — bucket structure already on disk

# ── Query 3 (Tuesday — ZERO shuffle again) ────────────────────────
result3 = orders.join(customers, "customer_id") \
                .groupBy("name") \
                .agg(avg("amount").alias("avg_spend"))
result3.show()
# Still ZERO shuffle

# Total: 3 queries × 0 GB = 0 GB shuffled ✅
# vs unbucketed: 3 × 110 GB = 330 GB shuffled ❌
```

### Proof — check the physical plan (no Exchange = no shuffle)

```python
orders    = spark.table("orders_bucketed")
customers = spark.table("customers_bucketed")
result    = orders.join(customers, "customer_id")

result.explain(mode="formatted")

# ── WITHOUT bucketing — see Exchange nodes (shuffles): ────────────
# == Physical Plan ==
# AdaptiveSparkPlan
# +- SortMergeJoin [customer_id]
#    :- Sort [customer_id]
#    :  +- Exchange hashpartitioning(customer_id, 200)  ← SHUFFLE ❌
#    :     +- FileScan csv [order_id, customer_id, ...]
#    +- Sort [customer_id]
#       +- Exchange hashpartitioning(customer_id, 200)  ← SHUFFLE ❌
#          +- FileScan csv [customer_id, name, ...]

# ── WITH bucketing — no Exchange nodes at all: ────────────────────
# == Physical Plan ==
# SortMergeJoin [customer_id]
#   :- Sort [customer_id]
#   :  +- FileScan parquet orders_bucketed [...]         ← NO shuffle ✅
#   +- Sort [customer_id]
#      +- FileScan parquet customers_bucketed [...]       ← NO shuffle ✅
```

---

## 🔵 The Problem Without Bucketing — S3 Example

### Our data (S3 files)

```
s3://my-company-bucket/raw/orders/
    part-00000.parquet   (128 MB)
    part-00001.parquet   (128 MB)
    ...
    part-00799.parquet   (128 MB)
    Total = 100 GB

s3://my-company-bucket/raw/customers/
    part-00000.parquet   (128 MB)
    ...
    part-00079.parquet   (128 MB)
    Total = 10 GB
```

### Without bucketing — same shuffle problem on S3

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, count, col

spark = SparkSession.builder \
    .appName("S3NoBucketingDemo") \
    .config("spark.hadoop.fs.s3a.access.key", "YOUR_ACCESS_KEY") \
    .config("spark.hadoop.fs.s3a.secret.key", "YOUR_SECRET_KEY") \
    .getOrCreate()

# Read from S3
orders = spark.read.parquet("s3a://my-company-bucket/raw/orders/")
customers = spark.read.parquet("s3a://my-company-bucket/raw/customers/")

print(f"Orders partitions:    {orders.rdd.getNumPartitions()}")     # → 800
print(f"Customers partitions: {customers.rdd.getNumPartitions()}")  # →  80

# Every join → 110 GB pulled from S3 into executors + 110 GB shuffled again
# S3 latency makes this even worse than local (HTTPS requests per partition)
result = orders.join(customers, "customer_id") \
               .groupBy("city") \
               .agg(sum("amount").alias("revenue"))
result.show()

# Cost: 110 GB S3 → executor transfer + 110 GB executor shuffle = very slow ❌
```

---

## 🔵 Bucketing — S3 Example

### Step 1: One-time write as bucketed tables to S3-backed warehouse

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, count, avg, col

spark = SparkSession.builder \
    .appName("S3BucketingDemo") \
    .enableHiveSupport() \
    .config("spark.sql.warehouse.dir", "s3a://my-company-bucket/warehouse/") \
    .config("spark.hadoop.fs.s3a.access.key", "YOUR_ACCESS_KEY") \
    .config("spark.hadoop.fs.s3a.secret.key", "YOUR_SECRET_KEY") \
    .getOrCreate()

# ── Read raw data from S3 ──────────────────────────────────────────
orders_raw = spark.read.parquet("s3a://my-company-bucket/raw/orders/")
customers_raw = spark.read.parquet("s3a://my-company-bucket/raw/customers/")

# ── ONE-TIME WRITE: bucket and store back to S3 warehouse ─────────
orders_raw.write \
    .bucketBy(200, "customer_id") \
    .sortBy("customer_id") \
    .mode("overwrite") \
    .saveAsTable("orders_bucketed")
# Written to: s3a://my-company-bucket/warehouse/orders_bucketed/

customers_raw.write \
    .bucketBy(200, "customer_id") \
    .sortBy("customer_id") \
    .mode("overwrite") \
    .saveAsTable("customers_bucketed")
# Written to: s3a://my-company-bucket/warehouse/customers_bucketed/

print("Done. Files on S3:")
print("  s3a://my-company-bucket/warehouse/orders_bucketed/part-00000.parquet")
print("  s3a://my-company-bucket/warehouse/orders_bucketed/part-00001.parquet")
print("  ...")
print("  s3a://my-company-bucket/warehouse/orders_bucketed/part-00199.parquet")
```

### What lands on S3 after bucketing

```
s3://my-company-bucket/warehouse/orders_bucketed/
    part-00000-xxxx.parquet  ← all orders where hash(customer_id) % 200 = 0
    part-00001-xxxx.parquet  ← all orders where hash(customer_id) % 200 = 1
    ...
    part-00199-xxxx.parquet  ← all orders where hash(customer_id) % 200 = 199

s3://my-company-bucket/warehouse/customers_bucketed/
    part-00000-xxxx.parquet  ← all customers where hash(customer_id) % 200 = 0
    part-00001-xxxx.parquet  ← all customers where hash(customer_id) % 200 = 1
    ...
    part-00199-xxxx.parquet  ← all customers where hash(customer_id) % 200 = 199
```

### Step 2: Every future S3 query — ZERO shuffle

```python
# Read bucketed tables (Spark reads metadata from Hive metastore)
orders    = spark.table("orders_bucketed")     # points to S3 bucketed files
customers = spark.table("customers_bucketed")  # points to S3 bucketed files

# ── Run any join — zero shuffle ────────────────────────────────────
result = orders.join(customers, "customer_id") \
               .groupBy("city") \
               .agg(
                   sum("amount").alias("total_revenue"),
                   count("*").alias("order_count"),
                   avg("amount").alias("avg_order_value")
               ) \
               .orderBy(col("total_revenue").desc())

result.show(10)
# +──────────────+───────────────+─────────────+──────────────────+
# | city         | total_revenue | order_count | avg_order_value  |
# +──────────────+───────────────+─────────────+──────────────────+
# | Mumbai       | 4,500,000.00  | 18,000      | 250.00           |
# | Delhi        | 3,200,000.00  | 14,500      | 220.69           |
# +──────────────+───────────────+─────────────+──────────────────+

# What happened:
# Task 0:   fetched orders/part-00000 from S3 + customers/part-00000 from S3
#           joined locally in executor memory (NO network shuffle between executors)
# Task 1:   fetched orders/part-00001 from S3 + customers/part-00001 from S3
#           joined locally
# ...
# Task 199: fetched orders/part-00199 + customers/part-00199, joined locally
#
# S3 → executor: yes (reading data)
# executor → executor: ZERO (no shuffle) ✅
```

---

## 🔵 Bucketing — groupBy Also Shuffle-Free

```python
# ── From local CSV (bucketed) ──────────────────────────────────────
orders = spark.table("orders_bucketed")   # bucketed by customer_id

# groupBy on bucket column → ZERO shuffle
revenue_by_customer = orders \
    .groupBy("customer_id") \
    .agg(
        sum("amount").alias("total_spent"),
        count("*").alias("order_count")
    )
revenue_by_customer.show(5)
# All customer_id=5 rows are in bucket 12 → task 12 aggregates locally ✅

# ── From S3 (bucketed) ─────────────────────────────────────────────
orders_s3 = spark.table("orders_bucketed")  # same table, backed by S3

# groupBy on bucket column → ZERO shuffle (even from S3)
revenue_s3 = orders_s3 \
    .groupBy("customer_id") \
    .agg(sum("amount").alias("total_spent")) \
    .orderBy(col("total_spent").desc())
revenue_s3.show(5)
# Task 12 reads only orders/part-00012 from S3 → aggregates cid=5 locally ✅
```

---

## 🔵 Bucketing Rules — Must Get These Right

```
Rule 1: SAME number of buckets on both tables
    orders.bucketBy(200, "customer_id")    ✅ match
    customers.bucketBy(200, "customer_id") ✅ match

    orders.bucketBy(200, "customer_id")    ❌ mismatch!
    customers.bucketBy(100, "customer_id") ❌ → Spark falls back to full shuffle

Rule 2: SAME bucket column on both tables
    orders.bucketBy(200, "customer_id")    ✅ same column
    customers.bucketBy(200, "customer_id") ✅ same column

    orders.bucketBy(200, "customer_id")    ❌ different columns
    customers.bucketBy(200, "order_id")    ❌ → full shuffle fallback

Rule 3: enableHiveSupport() MUST be in SparkSession
    Without it: bucketing metadata not stored → Spark silently ignores bucketing

Rule 4: Join condition MUST be on the bucket column
    orders.join(customers, "customer_id")  ✅ joins on bucket col → no shuffle
    orders.join(customers, "order_date")   ❌ not bucket col → full shuffle

Rule 5: Number of buckets ideally = spark.sql.shuffle.partitions
    Mismatched → Spark may still shuffle to reconcile partition counts

Rule 6: Both tables must be saveAsTable() — not write.parquet()
    df.write.bucketBy(200,"id").parquet(path)    ❌ metadata not in Hive
    df.write.bucketBy(200,"id").saveAsTable(name) ✅ metadata in Hive
```

---

## 🔵 How Many Buckets?

```
Formula:
    target_bucket_file_size = 128 MB – 256 MB  (sweet spot)
    num_buckets = total_table_size / target_bucket_file_size

For orders (100 GB):
    100,000 MB / 200 MB = 500 buckets

For our 3-executor cluster (12 cores):
    Minimum useful buckets = total_cores × 2 = 24
    But use 200 for future scaling

Rule of thumb:
    Always match spark.sql.shuffle.partitions (default 200)
    Use power of 2 or round numbers: 64, 128, 200, 256, 512
```

---

# ═══════════════════════════════════════
# PART 2 — SALTING
# ═══════════════════════════════════════

---

## 🔵 What Is Data Skew? — Local CSV Example First

### Our skewed data

```
/data/orders.csv — skewed on customer_id

customer_id distribution:
    customer_id = 1    (large corporate client) → 50,000,000 rows  ← HOT KEY 🔥
    customer_id = 2    (medium business)        →      10,000 rows
    customer_id = 3    (small shop)             →          200 rows
    ...
    customer_id = 9999 (individual)             →           3 rows

After shuffle with spark.sql.shuffle.partitions = 200:
    hash(1) % 200 = 83  → Partition 83 gets ALL 50M rows of cid=1 → 1 task overwhelmed
    hash(2) % 200 = 134 → Partition 134 gets 10K rows → done in seconds
    ...

Partition 83 task:  50,000,000 rows → runs 3 HOURS ❌
All other tasks:    tiny            → done in seconds, sit idle
Whole job waits for partition 83 = 3 hours wasted
```

### Visualized skew

```
Task timeline (200 tasks, 12 cores):

Task 0:   ██ (2s)
Task 1:   ██ (3s)
Task 2:   ██ (1s)
...
Task 83:  █████████████████████████████████████████████ (3 hours!) ← cid=1 all here
...
Task 199: ██ (2s)

JOB COMPLETION = max(all tasks) = 3 HOURS ❌
199 executors sit idle for 3 hours waiting for task 83
```

---

## 🔵 What Is Salting? — The Core Idea

```
Salting = append a random number (0 to SALT_FACTOR-1) to the hot key
          so rows with the same hot key scatter across MULTIPLE partitions

Before salting:
    customer_id = 1  →  hash("1") % 200 = 83  →  1 partition  →  50M rows  →  3 hours

After salting (SALT_FACTOR = 10):
    customer_id + "_0"  →  "1_0"  →  hash("1_0") % 200 = 15   →  ~5M rows  → 18 min
    customer_id + "_1"  →  "1_1"  →  hash("1_1") % 200 = 143  →  ~5M rows  → 18 min
    customer_id + "_2"  →  "1_2"  →  hash("1_2") % 200 = 67   →  ~5M rows  → 18 min
    customer_id + "_3"  →  "1_3"  →  hash("1_3") % 200 = 188  →  ~5M rows  → 18 min
    customer_id + "_4"  →  "1_4"  →  hash("1_4") % 200 = 22   →  ~5M rows  → 18 min
    customer_id + "_5"  →  "1_5"  →  hash("1_5") % 200 = 91   →  ~5M rows  → 18 min
    customer_id + "_6"  →  "1_6"  →  hash("1_6") % 200 = 55   →  ~5M rows  → 18 min
    customer_id + "_7"  →  "1_7"  →  hash("1_7") % 200 = 177  →  ~5M rows  → 18 min
    customer_id + "_8"  →  "1_8"  →  hash("1_8") % 200 = 39   →  ~5M rows  → 18 min
    customer_id + "_9"  →  "1_9"  →  hash("1_9") % 200 = 112  →  ~5M rows  → 18 min

10 tasks each handle 5M rows → run in PARALLEL → done in 18 min instead of 3 hours
```

---

## 🔵 Salting for groupBy — Local CSV Example

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, rand, concat_ws, sum, count, avg, desc
)

spark = SparkSession.builder \
    .appName("SaltingGroupByLocal") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

# ── Read skewed CSV from local disk ───────────────────────────────
orders = spark.read.csv(
    "file:///data/orders.csv",
    header=True,
    inferSchema=True
)

print(f"Total rows: {orders.count()}")
print(f"Partitions: {orders.rdd.getNumPartitions()}")

# ── Check skew first ──────────────────────────────────────────────
print("\nTop 5 keys by row count:")
orders.groupBy("customer_id") \
      .count() \
      .orderBy(desc("count")) \
      .show(5)
# +─────────────+────────────+
# | customer_id | count      |
# +─────────────+────────────+
# |           1 | 50,000,000 |  ← HOT KEY
# |           2 |     10,000 |
# |           3 |        200 |
# +─────────────+────────────+

# ════════════════════════════════════════════════════════════════
# WITHOUT SALTING — SLOW (one task gets 50M rows)
# ════════════════════════════════════════════════════════════════
print("\n--- WITHOUT salting ---")
result_no_salt = orders.groupBy("customer_id") \
                       .agg(
                           sum("amount").alias("total_spent"),
                           count("*").alias("order_count")
                       )
result_no_salt.show(5)
# Task for cid=1 → 50M rows → takes ~3 hours to complete ❌


# ════════════════════════════════════════════════════════════════
# WITH SALTING — FAST (50M rows spread across 10 tasks)
# ════════════════════════════════════════════════════════════════
print("\n--- WITH salting ---")
SALT_FACTOR = 10   # spread hot key across 10 tasks

# Step 1: Add random salt to every row
orders_salted = orders.withColumn(
    "salt",
    (rand() * SALT_FACTOR).cast("int")               # random int 0 to 9
).withColumn(
    "salted_key",
    concat_ws("_",
        col("customer_id").cast("string"),
        col("salt").cast("string")
    )
    # cid=1, salt=3 → salted_key = "1_3"
    # cid=1, salt=7 → salted_key = "1_7"
    # cid=2, salt=1 → salted_key = "2_1"
)

print("Sample after salting:")
orders_salted.select("customer_id", "salt", "salted_key", "amount").show(5)
# +─────────────+────+────────────+────────+
# | customer_id |salt| salted_key | amount |
# +─────────────+────+────────────+────────+
# |           1 |  3 | 1_3        | 250.00 |
# |           1 |  7 | 1_7        |  89.99 |
# |           2 |  1 | 2_1        | 120.50 |
# +─────────────+────+────────────+────────+


# Step 2: Partial aggregation on salted_key (splits the hot key across tasks)
partial_agg = orders_salted \
    .groupBy("customer_id", "salted_key") \
    .agg(
        sum("amount").alias("partial_total"),
        count("*").alias("partial_count")
    )

print("Partial aggregation results:")
partial_agg.orderBy("salted_key").show(15)
# +─────────────+────────────+───────────────+───────────────+
# | customer_id | salted_key | partial_total | partial_count |
# +─────────────+────────────+───────────────+───────────────+
# |           1 | 1_0        |   500,000.00  |   5,000,000   |  ← 1/10 of cid=1
# |           1 | 1_1        |   490,000.00  |   4,900,000   |
# |           1 | 1_2        |   510,000.00  |   5,100,000   |
# |           1 | 1_3        |   498,000.00  |   4,980,000   |
# ...
# |           2 | 2_0        |     2,500.00  |      1,000    |  ← normal key
# |           2 | 2_3        |     3,100.00  |      1,200    |
# +─────────────+────────────+───────────────+───────────────+


# Step 3: Final aggregation on real customer_id (merge partial results)
final_result = partial_agg \
    .groupBy("customer_id") \
    .agg(
        sum("partial_total").alias("total_spent"),
        sum("partial_count").alias("order_count")
    ) \
    .withColumn("avg_order", col("total_spent") / col("order_count")) \
    .orderBy(desc("total_spent"))

print("Final result (correct totals):")
final_result.show(5)
# +─────────────+───────────────+─────────────+───────────+
# | customer_id | total_spent   | order_count | avg_order |
# +─────────────+───────────────+─────────────+───────────+
# |           1 | 5,000,000.00  |  50,000,000 | 0.10      |  ← full correct total ✅
# |           2 |    10,000.00  |      10,000 | 1.00      |
# +─────────────+───────────────+─────────────+───────────+

# Time: ~18 minutes instead of 3 hours (10x speedup for the hot key) ✅
```

---

## 🔵 Salting for groupBy — S3 Example

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, rand, concat_ws, sum, count, desc
)

spark = SparkSession.builder \
    .appName("SaltingGroupByS3") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.hadoop.fs.s3a.access.key", "YOUR_ACCESS_KEY") \
    .config("spark.hadoop.fs.s3a.secret.key", "YOUR_SECRET_KEY") \
    .getOrCreate()

# ── Read skewed data from S3 ───────────────────────────────────────
orders = spark.read.parquet("s3a://my-company-bucket/raw/orders/")

# ── Detect skew ───────────────────────────────────────────────────
print("Checking key distribution...")
orders.groupBy("customer_id") \
      .count() \
      .orderBy(desc("count")) \
      .show(5)

# ════════════════════════════════════════════════════════════════
# WITH SALTING — all same logic as local, just data source differs
# ════════════════════════════════════════════════════════════════
SALT_FACTOR = 10

# Step 1: Add salt
orders_salted = orders \
    .withColumn("salt", (rand() * SALT_FACTOR).cast("int")) \
    .withColumn("salted_key",
        concat_ws("_",
            col("customer_id").cast("string"),
            col("salt").cast("string")
        )
    )

# Step 2: Partial aggregation
partial = orders_salted \
    .groupBy("customer_id", "salted_key") \
    .agg(
        sum("amount").alias("partial_total"),
        count("*").alias("partial_cnt")
    )

# Step 3: Final merge
final = partial \
    .groupBy("customer_id") \
    .agg(
        sum("partial_total").alias("total_spent"),
        sum("partial_cnt").alias("order_count")
    )

# Step 4: Write results back to S3
final.write \
     .mode("overwrite") \
     .parquet("s3a://my-company-bucket/output/customer-totals/")

print("Results written to S3 ✅")
print(f"Output location: s3a://my-company-bucket/output/customer-totals/")
```

---

## 🔵 Salting for JOIN — Local CSV Example

Joining is harder than groupBy. The challenge: if you randomly salt the left side, the right side doesn't know which salt value to match.

**Solution: randomly salt the left (large) side, then REPLICATE the right (small) side across ALL salt values.**

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, rand, concat_ws, explode, array, lit, sum, count
)

spark = SparkSession.builder \
    .appName("SaltingJoinLocal") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

# ── Read both tables from local CSV ───────────────────────────────
orders = spark.read.csv(
    "file:///data/orders.csv",
    header=True,
    inferSchema=True
)
customers = spark.read.csv(
    "file:///data/customers.csv",
    header=True,
    inferSchema=True
)

SALT_FACTOR = 10

# ════════════════════════════════════════════════════════════════
# WITHOUT salting — skewed join (3 hours for cid=1 task)
# ════════════════════════════════════════════════════════════════
result_no_salt = orders.join(customers, "customer_id") \
                       .groupBy("name") \
                       .agg(sum("amount").alias("total"))
result_no_salt.show(5)  # ← one task takes 3 hours ❌


# ════════════════════════════════════════════════════════════════
# WITH salting — balanced join
# ════════════════════════════════════════════════════════════════

# Step 1: Salt LEFT side (orders) with a RANDOM salt per row
orders_salted = orders \
    .withColumn("salt", (rand() * SALT_FACTOR).cast("int")) \
    .withColumn("salted_cid",
        concat_ws("_",
            col("customer_id").cast("string"),
            col("salt").cast("string")
        )
    )

print("Orders after salting (left side):")
orders_salted.select("order_id","customer_id","salt","salted_cid","amount").show(5)
# +──────────+─────────────+────+────────────+────────+
# | order_id | customer_id |salt| salted_cid | amount |
# +──────────+─────────────+────+────────────+────────+
# |     1001 |           1 |  3 | 1_3        | 250.00 |
# |     1002 |           1 |  7 | 1_7        |  89.99 |  ← same cid, different salt
# |     1003 |           5 |  2 | 5_2        | 120.50 |
# +──────────+─────────────+────+────────────+────────+


# Step 2: REPLICATE RIGHT side (customers) across ALL salt values
customers_exploded = customers \
    .withColumn(
        "salted_cid",
        explode(
            array([
                concat_ws("_",
                    col("customer_id").cast("string"),
                    lit(i).cast("string")
                )
                for i in range(SALT_FACTOR)   # i = 0, 1, 2, ..., 9
            ])
        )
    )
# Each customer row → 10 rows (one for each salt value)

print("Customers after exploding (right side):")
customers_exploded.select("customer_id","name","salted_cid").show(12)
# +─────────────+───────────────+────────────+
# | customer_id | name          | salted_cid |
# +─────────────+───────────────+────────────+
# |           1 | Alice Johnson | 1_0        |  ← copy for salt 0
# |           1 | Alice Johnson | 1_1        |  ← copy for salt 1
# |           1 | Alice Johnson | 1_2        |  ← copy for salt 2
# ...
# |           1 | Alice Johnson | 1_9        |  ← copy for salt 9
# |           5 | Bob Smith     | 5_0        |
# ...
# |           5 | Bob Smith     | 5_9        |
# +─────────────+───────────────+────────────+
# customers went from N rows → N × 10 rows (10x larger)


# Step 3: JOIN on salted_cid (now balanced!)
result_salted = orders_salted.join(
    customers_exploded,
    orders_salted.salted_cid == customers_exploded.salted_cid,
    "left"
).drop(orders_salted.salted_cid) \
 .drop(customers_exploded.salted_cid) \
 .drop("salt") \
 .groupBy("customer_id", "name") \
 .agg(
     sum("amount").alias("total_spent"),
     count("*").alias("order_count")
 ) \
 .orderBy(col("total_spent").desc())

result_salted.show(10)
# +─────────────+───────────────+───────────────+─────────────+
# | customer_id | name          | total_spent   | order_count |
# +─────────────+───────────────+───────────────+─────────────+
# |           1 | Alice Johnson | 5,000,000.00  |  50,000,000 | ✅ correct total
# |           5 | Bob Smith     |    10,000.00  |      10,000 | ✅
# +─────────────+───────────────+───────────────+─────────────+

# Task times after salting:
# Tasks for "1_0" through "1_9": each ~5M rows → ~18 min (in parallel) ✅
# Total time: 18 min instead of 3 hours ✅
```

---

## 🔵 Salting for JOIN — S3 Example

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, rand, concat_ws, explode, array, lit, sum, count, desc
)

spark = SparkSession.builder \
    .appName("SaltingJoinS3") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.hadoop.fs.s3a.access.key", "YOUR_ACCESS_KEY") \
    .config("spark.hadoop.fs.s3a.secret.key", "YOUR_SECRET_KEY") \
    .getOrCreate()

# ── Read both tables from S3 ──────────────────────────────────────
orders    = spark.read.parquet("s3a://my-company-bucket/raw/orders/")
customers = spark.read.parquet("s3a://my-company-bucket/raw/customers/")

print(f"Orders    rows: {orders.count():,}")       # 60,000,000
print(f"Customers rows: {customers.count():,}")    #    500,000

SALT_FACTOR = 10

# Step 1: Salt left side (orders) — random salt per row
orders_salted = orders \
    .withColumn("salt", (rand() * SALT_FACTOR).cast("int")) \
    .withColumn("salted_cid",
        concat_ws("_",
            col("customer_id").cast("string"),
            col("salt").cast("string")
        )
    )

# Step 2: Replicate right side (customers) — 10 copies per row
customers_exploded = customers \
    .withColumn("salted_cid",
        explode(
            array([
                concat_ws("_",
                    col("customer_id").cast("string"),
                    lit(i).cast("string")
                )
                for i in range(SALT_FACTOR)
            ])
        )
    )

print(f"Exploded customers rows: {customers_exploded.count():,}")
# → 500,000 × 10 = 5,000,000 rows (10x, but still small vs orders)

# Step 3: Join on salted key
result = orders_salted.join(
    customers_exploded,
    orders_salted.salted_cid == customers_exploded.salted_cid,
    "left"
).drop(orders_salted.salted_cid) \
 .drop(customers_exploded.salted_cid) \
 .drop("salt") \
 .groupBy("customer_id", "name", "city") \
 .agg(
     sum("amount").alias("total_revenue"),
     count("*").alias("order_count")
 )

# Step 4: Write results back to S3
result.write \
      .mode("overwrite") \
      .parquet("s3a://my-company-bucket/output/salted-join-results/")

print("Done ✅")
print("Results at: s3a://my-company-bucket/output/salted-join-results/")
```

---

## 🔵 Salting — Only Salt the Hot Keys (Smarter Approach)

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, rand, when, concat_ws, explode, array, lit, sum, count, desc
)

spark = SparkSession.builder \
    .appName("SmartSalting") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

# Works same way for both local and S3 — only source path differs
# Using S3 here
orders    = spark.read.parquet("s3a://my-company-bucket/raw/orders/")
customers = spark.read.parquet("s3a://my-company-bucket/raw/customers/")

# ── Step 1: Identify hot keys programmatically ────────────────────
HOT_THRESHOLD = 1_000_000   # keys with > 1M rows = hot
SALT_FACTOR   = 10

key_counts = orders.groupBy("customer_id").count()
hot_keys   = key_counts.filter(col("count") > HOT_THRESHOLD) \
                        .select("customer_id")

hot_key_list = [row.customer_id for row in hot_keys.collect()]
print(f"Hot keys found: {hot_key_list}")
# Hot keys found: [1, 42, 99]

# ── Step 2: Salt ONLY hot keys on left side ───────────────────────
orders_salted = orders.withColumn(
    "salted_cid",
    when(
        col("customer_id").isin(hot_key_list),
        # Hot key → append random salt
        concat_ws("_",
            col("customer_id").cast("string"),
            (rand() * SALT_FACTOR).cast("int").cast("string")
        )
    ).otherwise(
        # Cold key → keep unchanged (no overhead for normal keys)
        col("customer_id").cast("string")
    )
)

print("Sample — hot key gets salt, cold key does not:")
orders_salted.select("customer_id","salted_cid") \
             .filter(col("customer_id").isin(1, 500)) \
             .show(6)
# +─────────────+────────────+
# | customer_id | salted_cid |
# +─────────────+────────────+
# |           1 | 1_3        |  ← hot key, salted
# |           1 | 1_7        |  ← hot key, different salt
# |         500 | 500        |  ← cold key, unchanged
# +─────────────+────────────+

# ── Step 3: Replicate ONLY hot keys on right side ─────────────────
customers_salted = customers.withColumn(
    "salted_cid",
    when(
        col("customer_id").isin(hot_key_list),
        # Hot key → explode into SALT_FACTOR copies
        explode(
            array([
                concat_ws("_",
                    col("customer_id").cast("string"),
                    lit(i).cast("string")
                )
                for i in range(SALT_FACTOR)
            ])
        )
    ).otherwise(
        # Cold key → keep as single copy (no replication overhead)
        col("customer_id").cast("string")
    )
)

# ── Step 4: Join and aggregate ────────────────────────────────────
result = orders_salted.join(
    customers_salted,
    orders_salted.salted_cid == customers_salted.salted_cid,
    "left"
).drop(orders_salted.salted_cid) \
 .drop(customers_salted.salted_cid) \
 .groupBy("customer_id", "name") \
 .agg(
     sum("amount").alias("total_spent"),
     count("*").alias("order_count")
 ) \
 .orderBy(desc("total_spent"))

result.show(10)
# Hot keys → 10x parallel tasks, no skew ✅
# Cold keys → zero overhead, processed normally ✅
```

---

## 🔵 AQE — Automatic Skew Handling (Spark 3.0+, No Manual Salting Needed for Joins)

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("AQESkewJoin") \
    .config("spark.sql.adaptive.enabled",                                   "true") \
    .config("spark.sql.adaptive.skewJoin.enabled",                          "true") \
    .config("spark.sql.adaptive.skewJoin.skewedPartitionFactor",            "5") \
    .config("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes",  "256mb") \
    .getOrCreate()

# ── Works the same for local or S3 ───────────────────────────────

# Local
orders    = spark.read.csv("file:///data/orders.csv", header=True, inferSchema=True)
customers = spark.read.csv("file:///data/customers.csv", header=True, inferSchema=True)

# OR S3
# orders    = spark.read.parquet("s3a://my-company-bucket/raw/orders/")
# customers = spark.read.parquet("s3a://my-company-bucket/raw/customers/")

# Normal join — AQE handles skew automatically at runtime
result = orders.join(customers, "customer_id") \
               .groupBy("name") \
               .agg(sum("amount").alias("total"))
result.show(10)

# What AQE does internally (invisible to you):
#   1. Stage 0 runs → Spark measures actual partition sizes
#   2. Detects: partition 83 = 50 GB (vs median 300 MB → 166x larger) → SKEWED
#   3. Automatically splits partition 83 into 10 sub-partitions of ~5 GB each
#   4. Replicates matching customers partition to all 10 sub-partitions
#   5. Runs 10 parallel sub-tasks instead of 1 massive task
#   6. Merges results transparently

# AQE vs manual salting:
# AQE (Spark 3.0+):  handles JOIN skew automatically ✅
# Manual salting:    still needed for groupBy skew, or Spark < 3.0
```

---

## 🔵 How to Detect Skew — Before Deciding to Salt

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, spark_partition_id, desc

spark = SparkSession.builder.appName("SkewDetection").getOrCreate()

# Works same for local or S3 source
# Local:
df = spark.read.csv("file:///data/orders.csv", header=True, inferSchema=True)
# S3:
# df = spark.read.parquet("s3a://my-company-bucket/raw/orders/")

# ── Method 1: Check key frequency ────────────────────────────────
print("Key distribution (top 10):")
df.groupBy("customer_id") \
  .count() \
  .orderBy(desc("count")) \
  .show(10)
# If top key has 100x more rows than 10th key → salt it

# ── Method 2: Check actual partition sizes after shuffle ──────────
# Force a shuffle and look at partition row counts
shuffled = df.repartition(200, col("customer_id"))  # simulate join shuffle
partition_sizes = shuffled \
    .withColumn("pid", spark_partition_id()) \
    .groupBy("pid") \
    .count() \
    .orderBy(desc("count"))

partition_sizes.show(10)
# +────+────────────+
# | pid|       count|
# +────+────────────+
# |  83|  50,000,000|  ← skewed partition!
# | 134|      10,000|
# |  12|         200|
# +────+────────────+

# ── Method 3: Compute skew ratio ─────────────────────────────────
from pyspark.sql.functions import max as spark_max, percentile_approx

stats = partition_sizes.agg(
    spark_max("count").alias("max_rows"),
    percentile_approx("count", 0.5).alias("median_rows")
)
stats.show()

# If max_rows / median_rows > 5 → significant skew → consider salting
# +────────────+─────────────+
# | max_rows   | median_rows |
# +────────────+─────────────+
# | 50,000,000 |       3,000 |  ← ratio = 16,666 → severe skew → SALT IT
# +────────────+─────────────+
```

---

## 🔵 Complete Combined Example — Bucketing + Salting Together (S3)

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, rand, when, concat_ws, explode, array, lit,
    sum, count, avg, desc
)

spark = SparkSession.builder \
    .appName("BucketingSaltingFull") \
    .enableHiveSupport() \
    .config("spark.sql.warehouse.dir",               "s3a://my-company-bucket/warehouse/") \
    .config("spark.sql.shuffle.partitions",          "200") \
    .config("spark.sql.adaptive.enabled",            "true") \
    .config("spark.sql.adaptive.skewJoin.enabled",   "true") \
    .config("spark.hadoop.fs.s3a.access.key",        "YOUR_ACCESS_KEY") \
    .config("spark.hadoop.fs.s3a.secret.key",        "YOUR_SECRET_KEY") \
    .getOrCreate()

# ════════════════════════════════════════════════════════════════
# STEP 1: Read raw data (S3 — run once)
# ════════════════════════════════════════════════════════════════
orders_raw    = spark.read.parquet("s3a://my-company-bucket/raw/orders/")
customers_raw = spark.read.parquet("s3a://my-company-bucket/raw/customers/")

# ════════════════════════════════════════════════════════════════
# STEP 2: Write as bucketed tables (S3 — run once, benefit forever)
# ════════════════════════════════════════════════════════════════
orders_raw.write \
    .bucketBy(200, "customer_id") \
    .sortBy("customer_id") \
    .mode("overwrite") \
    .saveAsTable("orders_bucketed")

customers_raw.write \
    .bucketBy(200, "customer_id") \
    .sortBy("customer_id") \
    .mode("overwrite") \
    .saveAsTable("customers_bucketed")

print("Bucketed tables written to S3 warehouse ✅")

# ════════════════════════════════════════════════════════════════
# STEP 3: Read bucketed tables for every query
# ════════════════════════════════════════════════════════════════
orders    = spark.table("orders_bucketed")
customers = spark.table("customers_bucketed")

# ════════════════════════════════════════════════════════════════
# STEP 4: Detect hot keys
# ════════════════════════════════════════════════════════════════
HOT_THRESHOLD = 1_000_000
SALT_FACTOR   = 10

key_counts   = orders.groupBy("customer_id").count()
hot_key_list = [r.customer_id for r in
                key_counts.filter(col("count") > HOT_THRESHOLD).collect()]
print(f"Hot keys: {hot_key_list}")

# ════════════════════════════════════════════════════════════════
# STEP 5: Salt hot keys only
# ════════════════════════════════════════════════════════════════
orders_salted = orders.withColumn(
    "salted_cid",
    when(col("customer_id").isin(hot_key_list),
         concat_ws("_", col("customer_id").cast("string"),
                         (rand() * SALT_FACTOR).cast("int").cast("string"))
    ).otherwise(col("customer_id").cast("string"))
)

customers_salted = customers.withColumn(
    "salted_cid",
    when(col("customer_id").isin(hot_key_list),
         explode(array([
             concat_ws("_", col("customer_id").cast("string"), lit(i).cast("string"))
             for i in range(SALT_FACTOR)
         ]))
    ).otherwise(col("customer_id").cast("string"))
)

# ════════════════════════════════════════════════════════════════
# STEP 6: Join + aggregate → write results back to S3
# ════════════════════════════════════════════════════════════════
result = orders_salted.join(
    customers_salted,
    orders_salted.salted_cid == customers_salted.salted_cid
).drop(orders_salted.salted_cid) \
 .drop(customers_salted.salted_cid) \
 .groupBy("customer_id", "name", "city") \
 .agg(
     sum("amount").alias("total_spent"),
     count("*").alias("order_count"),
     avg("amount").alias("avg_order")
 ) \
 .orderBy(desc("total_spent"))

result.show(10)

result.write \
      .mode("overwrite") \
      .parquet("s3a://my-company-bucket/output/final-results/")

print("All done ✅")
print("What we achieved:")
print("  ✅ Zero shuffle (bucketing — same join key, reads matching buckets locally)")
print("  ✅ Zero skew   (salting  — hot keys spread across 10 parallel tasks)")
print("  ✅ AQE enabled (auto-handles any remaining skew Spark detects at runtime)")
```

---

## ⚠️ Common Mistakes — With Examples

### Mistake 1: Mismatched bucket counts (silent failure)
```python
# BAD — different counts → Spark falls back to full shuffle silently
orders.write.bucketBy(200, "customer_id").saveAsTable("orders_b")
customers.write.bucketBy(100, "customer_id").saveAsTable("customers_b")
# Join will STILL work but will shuffle — no error, no warning ❌

# GOOD — both must be exactly 200
orders.write.bucketBy(200, "customer_id").saveAsTable("orders_b")
customers.write.bucketBy(200, "customer_id").saveAsTable("customers_b")  # ✅
```

### Mistake 2: Forgetting two-phase aggregation after salting
```python
# BAD — groupBy on salted key gives WRONG partial results
orders_salted = orders.withColumn("salt", (rand()*10).cast("int")) \
                      .withColumn("key", concat_ws("_", col("cid"), col("salt")))

result = orders_salted.groupBy("key").agg(sum("amount"))
# "1_0" → 500,000  ← only 1/10 of cid=1's total!  WRONG ❌

# GOOD — always two phases: partial then final
partial = orders_salted.groupBy("customer_id","key").agg(sum("amount").alias("p"))
final   = partial.groupBy("customer_id").agg(sum("p").alias("total"))  # ✅
```

### Mistake 3: Forgetting enableHiveSupport() for bucketing
```python
# BAD — bucketing silently ignored
spark = SparkSession.builder.appName("App").getOrCreate()
df.write.bucketBy(200, "id").saveAsTable("my_table")
# Writes parquet but WITHOUT bucket metadata → reads like normal table → full shuffle

# GOOD
spark = SparkSession.builder \
    .appName("App") \
    .enableHiveSupport() \    # ← essential
    .getOrCreate()            # ✅
```

### Mistake 4: Salt factor too high
```python
# BAD — 50M rows / 1000 = 50K rows per salt partition → too small
SALT_FACTOR = 1000
# Task scheduling overhead > actual compute benefit

# GOOD — target 1M–5M rows per salted partition
# SALT_FACTOR = hot_key_rows / target_rows_per_task
SALT_FACTOR = 50_000_000 // 5_000_000   # = 10 ✅
```

---

## 🎯 Summary

```
┌────────────────┬──────────────────────────────────────────────────────────────────┐
│ Technique      │ What / How / When                                                │
├────────────────┼──────────────────────────────────────────────────────────────────┤
│ BUCKETING      │ Pre-partitions data by join column at write time                 │
│                │ .bucketBy(N, col).sortBy(col).saveAsTable()                      │
│                │ USE WHEN: same join column queried repeatedly                    │
│                │ BENEFIT: zero shuffle on all future joins + groupBys             │
│                │ COST: one-time write, enableHiveSupport required                 │
├────────────────┼──────────────────────────────────────────────────────────────────┤
│ SALTING        │ Spreads hot keys across multiple partitions artificially         │
│ (groupBy)      │ Add random salt → partial agg → final agg                       │
│                │ USE WHEN: one key has far more rows than others                  │
├────────────────┼──────────────────────────────────────────────────────────────────┤
│ SALTING        │ Salt left side randomly, EXPLODE right side N times              │
│ (join)         │ Join on salted key → drop salt column                            │
│                │ USE WHEN: join key is skewed, Spark < 3.0                       │
├────────────────┼──────────────────────────────────────────────────────────────────┤
│ AQE Skew Join  │ Automatic — enable and Spark handles join skew at runtime        │
│ (Spark 3.0+)   │ spark.sql.adaptive.skewJoin.enabled = true                      │
│                │ USE WHEN: Spark 3.0+, join skew (NOT groupBy skew)              │
└────────────────┴──────────────────────────────────────────────────────────────────┘

Data source doesn't change the technique:
    Local CSV → spark.read.csv("file:///data/file.csv", header=True)
    S3        → spark.read.parquet("s3a://bucket/path/")
    Everything else (bucketing, salting logic) is identical
```


# What is Cardinality, high cardinality vs low cardinality and partitioning stretegy on them?

# Catalyst Analyzer, Catalyst Optimized, Filter Pushdown, prediction Pushdown, Cost estimation


# 

# SparkSession  vs SparkContext — Complete Deep Dive

---

## 📌 One-Line Summary

| | SparkContext | SparkSession |
|---|---|---|
| **Introduced** | Spark 1.0 (2014) | Spark 2.0 (2016) |
| **What it is** | Entry point to the **core Spark engine** (RDDs) | Unified entry point to **all of Spark** (RDD + SQL + Streaming + ML) |
| **Analogy** | Raw engine of a car | Full car with dashboard, GPS, AC — and the engine inside |

---

## 🕰️ Historical Context — Why Both Exist

### Spark 1.x Era (Before 2016)
In early Spark, there were **multiple separate entry points** depending on what you wanted to do:

```
SparkContext     → for RDDs (core Spark)
SQLContext       → for DataFrames / SQL
HiveContext      → for Hive support
StreamingContext → for Spark Streaming
```

This was painful. Developers had to manage multiple context objects, and they couldn't always share configurations or resources easily.

### Spark 2.0 Era (2016 onward)
Spark introduced **SparkSession** as a **single unified entry point** that wraps all of the above:

```
SparkSession
    ├── SparkContext     (still exists inside)
    ├── SQLContext       (wrapped inside)
    ├── HiveContext      (wrapped inside)
    └── SparkConf        (configuration unified)
```

> SparkContext did NOT go away — it still powers the low-level engine. SparkSession just wraps it.

---

## 🔬 What is SparkContext?

### Definition
`SparkContext` is the **original entry point** to Spark's core distributed computing engine. It is responsible for connecting your application to the Spark cluster.

### What SparkContext Does Internally — Step by Step

```
Step 1: Reads SparkConf (configuration object)
            ↓
Step 2: Connects to the Cluster Manager
        (Standalone / YARN / Mesos / Kubernetes)
            ↓
Step 3: Requests resources (CPU cores, memory) from Cluster Manager
            ↓
Step 4: Cluster Manager launches Executors on Worker nodes
            ↓
Step 5: SparkContext registers these Executors
            ↓
Step 6: Your application can now distribute work via RDDs
```

### What SparkContext Can Do
- Create **RDDs** (Resilient Distributed Datasets)
- Read files → `sc.textFile()`, `sc.wholeTextFiles()`
- Create RDDs from collections → `sc.parallelize([1,2,3])`
- Set log levels, broadcast variables, accumulators
- Access cluster info → `sc.master`, `sc.appName`
- Cancel jobs, manage job groups

### How to Create SparkContext (Old Way — Spark 1.x style)

```python
from pyspark import SparkConf, SparkContext

conf = SparkConf() \
    .setAppName("MyApp") \
    .setMaster("local[*]") \
    .set("spark.executor.memory", "2g")

sc = SparkContext(conf=conf)

# Now use RDDs
rdd = sc.parallelize([1, 2, 3, 4, 5])
result = rdd.map(lambda x: x * 2).collect()
print(result)  # [2, 4, 6, 8, 10]
```

### SparkContext Limitations
- ❌ Cannot run SQL queries directly
- ❌ Cannot create DataFrames or Datasets
- ❌ No built-in Hive support
- ❌ Only one SparkContext allowed per JVM at a time
- ❌ No unified config with SQL or ML libraries

---

## 🚀 What is SparkSession?

### Definition
`SparkSession` is the **unified entry point** introduced in Spark 2.0. It consolidates SparkContext, SQLContext, and HiveContext into one object.

### What SparkSession Does Internally — Step by Step

```
Step 1: You call SparkSession.builder
            ↓
Step 2: Builder checks if a SparkSession already exists (singleton pattern)
            ↓
Step 3: If not exists → creates SparkConf internally
            ↓
Step 4: Creates SparkContext internally (the engine)
            ↓
Step 5: Wraps SQLContext and HiveContext internally
            ↓
Step 6: Returns a fully configured SparkSession object
            ↓
Step 7: You can now use DataFrames, SQL, RDDs, ML — all from one object
```

### How to Create SparkSession (Modern Way — Spark 2.0+)

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \
    .config("spark.executor.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "200") \
    .enableHiveSupport() \   # optional
    .getOrCreate()           # reuses existing session if already created
```

### What SparkSession Can Do
- Everything SparkContext can do (via `spark.sparkContext`)
- Create **DataFrames** → `spark.read.csv()`, `spark.read.parquet()`
- Run **SQL queries** → `spark.sql("SELECT * FROM table")`
- Create DataFrames from collections → `spark.createDataFrame(data, schema)`
- Access **Hive metastore** (with `enableHiveSupport()`)
- Manage **catalog** → `spark.catalog.listTables()`
- Register **UDFs** (User Defined Functions)
- Use **Spark Streaming**, **MLlib**, **GraphX** — all through one session

---

## 🔗 Relationship Between SparkSession and SparkContext

This is the most important thing to understand:

```
SparkSession
│
├── .sparkContext  ← SparkContext lives INSIDE SparkSession
│       │
│       ├── Connects to Cluster Manager
│       ├── Manages Executors
│       ├── Manages RDD operations
│       └── Is the actual low-level engine
│
├── .read          ← DataFrameReader (reads files into DataFrames)
├── .sql()         ← Runs SQL queries
├── .catalog       ← Manages tables, databases, functions
└── .conf          ← Runtime configuration
```

### Accessing SparkContext from SparkSession

```python
spark = SparkSession.builder.appName("App").getOrCreate()

# Access SparkContext from SparkSession
sc = spark.sparkContext

# Now use RDD operations
rdd = sc.parallelize([1, 2, 3])
print(rdd.collect())
```

> You should **never create a separate SparkContext** when using SparkSession. Just access it via `spark.sparkContext`.

---

## ⚖️ Side-by-Side Feature Comparison

| Feature | SparkContext | SparkSession |
|---|---|---|
| Introduced in | Spark 1.0 | Spark 2.0 |
| Primary abstraction | RDD | DataFrame / Dataset |
| Create RDDs | ✅ Yes | ✅ Via `.sparkContext` |
| Create DataFrames | ❌ No | ✅ Yes |
| Run SQL queries | ❌ No | ✅ Yes |
| Read CSV/JSON/Parquet | ❌ Limited | ✅ Yes (`.read`) |
| Hive support | ❌ No | ✅ Yes (with flag) |
| Broadcast variables | ✅ Yes | ✅ Via `.sparkContext` |
| Accumulators | ✅ Yes | ✅ Via `.sparkContext` |
| Multiple instances | ❌ Only 1 per JVM | ✅ Multiple (different sessions) |
| Configuration | Via `SparkConf` | Via `.config()` builder |
| Catalog management | ❌ No | ✅ Yes |
| Used in production today | Rarely alone | ✅ Standard |

---

## 🧪 Code Comparison — Same Task, Two Ways

### Task: Count lines in a file

**Using SparkContext (RDD way)**
```python
from pyspark import SparkContext

sc = SparkContext("local", "WordCount")
lines = sc.textFile("data.txt")         # returns RDD
count = lines.count()
print(count)
sc.stop()
```

**Using SparkSession (DataFrame way)**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("WordCount").getOrCreate()
df = spark.read.text("data.txt")        # returns DataFrame
count = df.count()
print(count)
spark.stop()
```

---

### Task: Word count

**SparkContext / RDD way**
```python
sc = SparkContext("local", "WC")
rdd = sc.textFile("data.txt") \
        .flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a, b: a + b)
print(rdd.collect())
```

**SparkSession / DataFrame way**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, col

spark = SparkSession.builder.appName("WC").getOrCreate()
df = spark.read.text("data.txt")
result = df.select(explode(split(col("value"), " ")).alias("word")) \
           .groupBy("word").count()
result.show()
```

---

## 🔑 The `getOrCreate()` Pattern — Singleton Behavior

SparkSession uses a **singleton pattern**. If a session already exists, it reuses it instead of creating a new one.

```python
# First call — creates a new session
spark1 = SparkSession.builder.appName("App1").getOrCreate()

# Second call — returns the SAME session (does not create new)
spark2 = SparkSession.builder.appName("App2").getOrCreate()

print(spark1 is spark2)  # True — same object
```

This is important because:
- Only **one SparkContext** can exist per JVM
- SparkSession wraps that single SparkContext
- `getOrCreate()` prevents accidental duplicate context errors

---

## 🏗️ Internal Architecture — What Happens When You Create SparkSession

```
SparkSession.builder.appName("App").master("local").getOrCreate()
        │
        ▼
1. SparkSession.Builder collects all config
        │
        ▼
2. Checks thread-local / global session registry
        │
        ├── Session exists? → Return existing session ✅
        │
        └── No session? → Continue
                │
                ▼
        3. Create SparkConf from all .config() calls
                │
                ▼
        4. Create SparkContext(conf)
                │
                ▼
        5. SparkContext connects to Cluster Manager
                │
                ▼
        6. Executors launched on workers
                │
                ▼
        7. SQLContext / HiveContext initialized inside
                │
                ▼
        8. SparkSession object returned to user ✅
```

---

## ⚠️ Common Mistakes & Gotchas

### ❌ Mistake 1: Creating SparkContext separately when SparkSession exists
```python
# WRONG — will throw error: "Cannot run multiple SparkContexts"
spark = SparkSession.builder.getOrCreate()
sc = SparkContext("local", "App")  # ❌ Error!

# CORRECT
spark = SparkSession.builder.getOrCreate()
sc = spark.sparkContext  # ✅ Reuse the existing one
```

### ❌ Mistake 2: Forgetting to call stop()
```python
# Always stop your session when done (especially in scripts/tests)
spark.stop()
```

### ❌ Mistake 3: Using SparkContext to read structured data
```python
# WRONG — clunky, loses schema info
sc = SparkContext("local", "App")
rdd = sc.textFile("data.csv")  # Just raw text lines

# CORRECT — structured, typed, optimized
spark = SparkSession.builder.getOrCreate()
df = spark.read.csv("data.csv", header=True, inferSchema=True)  # ✅
```

### ❌ Mistake 4: Creating SparkSession in a loop
```python
# WRONG — wasteful, but won't error due to getOrCreate
for i in range(10):
    spark = SparkSession.builder.getOrCreate()  # creates only once, reuses rest

# CORRECT — create once, reuse
spark = SparkSession.builder.getOrCreate()
for i in range(10):
    # use spark here
    pass
```

---

## 🧠 When to Use What — Decision Guide

```
Do you need to work with structured data (CSV, JSON, Parquet, DB)?
    → Use SparkSession (.read, DataFrame, SQL)

Do you need to run SQL queries?
    → Use SparkSession (.sql())

Do you need fine-grained low-level control (custom partitioning, complex transformations)?
    → Use SparkContext via spark.sparkContext → RDDs

Are you maintaining legacy Spark 1.x code?
    → SparkContext was required; consider migrating to SparkSession

Do you need both RDDs and DataFrames?
    → Use SparkSession, access RDDs via spark.sparkContext
```

---

## 📦 Quick Reference Cheat Sheet

```python
# ✅ Modern standard way to start any Spark application
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

# Access SparkContext when needed for RDDs
sc = spark.sparkContext

# DataFrames
df = spark.read.csv("file.csv", header=True, inferSchema=True)
df.show()

# SQL
spark.sql("SELECT * FROM my_table").show()

# RDD (when needed)
rdd = sc.parallelize([1, 2, 3, 4])
print(rdd.map(lambda x: x**2).collect())

# Clean up
spark.stop()
```

---

## 🎯 Summary

| Concept | Key Point |
|---|---|
| **SparkContext** | Low-level engine; connects to cluster; works with RDDs; existed since Spark 1.0 |
| **SparkSession** | High-level unified API; wraps SparkContext; works with DataFrames, SQL, ML; since Spark 2.0 |
| **Relationship** | SparkSession **contains** SparkContext — they are not alternatives, one wraps the other |
| **Use today** | Always create `SparkSession`; access SparkContext via `spark.sparkContext` only when needed |
| **getOrCreate()** | Singleton pattern — safe to call multiple times, won't create duplicate contexts |


# Schedulers in Spark:
https://moderndata101.substack.com/cp/188499149



# RDD vs DataFrame — Complete Deep Dive

---

## 📌 One-Line Summary

| | RDD | DataFrame |
|---|---|---|
| **Full Name** | Resilient Distributed Dataset | DataFrame |
| **Introduced** | Spark 1.0 (2014) | Spark 1.3 (2015) |
| **What it is** | Low-level distributed collection of **any Java/Python/Scala objects** | Distributed collection of **rows with a named, typed schema** (like a database table) |
| **Analogy** | A distributed list of raw objects | A distributed Excel sheet / SQL table |

---

## 🕰️ Historical Context — Why Both Exist

### Spark 1.0 — Only RDDs
When Spark was born, the only abstraction was the RDD. It was powerful but:
- No schema → no SQL support
- No automatic optimization → slow for structured data
- Very verbose code for simple operations

### Spark 1.3 — DataFrames Introduced
Spark borrowed the DataFrame concept from R/Pandas and added:
- Schema (column names + types)
- SQL query support
- Catalyst Optimizer (automatic query optimization)
- Tungsten execution engine (memory + CPU efficiency)

### Spark 2.0+ — Datasets (Typed DataFrames)
- Spark merged DataFrame into the **Dataset API**
- `DataFrame = Dataset[Row]` (a Dataset where each row is an untyped Row object)
- In PySpark, you mostly use DataFrame; in Scala/Java, you can use typed Datasets

---

## 🔬 What is an RDD?

### Definition
An RDD (Resilient Distributed Dataset) is Spark's **fundamental low-level data structure**. It represents an **immutable, partitioned collection of records** distributed across the cluster that can be operated on in parallel.

### Breaking Down the Name

```
R — Resilient   → Fault-tolerant: if a partition is lost, Spark can recompute it
                  using the lineage graph (DAG of transformations)

D — Distributed → Data is split into partitions spread across multiple nodes

D — Dataset     → A collection of data records (any type: String, Int, custom objects)
```

### RDD Internal Structure

```
RDD[T]
│
├── Partition 1  → lives on Worker Node 1  (subset of data)
├── Partition 2  → lives on Worker Node 2  (subset of data)
├── Partition 3  → lives on Worker Node 3  (subset of data)
└── Partition N  → lives on Worker Node N  (subset of data)
│
├── Lineage Graph (DAG) → how to recompute lost partitions
├── Partitioner          → how data is distributed (hash / range / none)
├── Dependencies         → narrow or wide (shuffle)
└── Preferred locations  → data locality hints
```

### Key Properties of RDD

**1. Immutable**
Once created, an RDD cannot be modified. Every transformation creates a new RDD.

```python
rdd1 = sc.parallelize([1, 2, 3, 4, 5])
rdd2 = rdd1.map(lambda x: x * 2)   # new RDD, rdd1 is unchanged
rdd3 = rdd2.filter(lambda x: x > 4) # another new RDD
```

**2. Lazy Evaluation**
Transformations are NOT executed immediately. Spark builds a DAG (Directed Acyclic Graph) of operations and only executes when an **action** is called.

```python
# Nothing executes here — just building the DAG
rdd = sc.parallelize([1, 2, 3, 4, 5])
rdd = rdd.map(lambda x: x * 2)
rdd = rdd.filter(lambda x: x > 4)

# THIS triggers execution
result = rdd.collect()  # ← Action — now Spark runs everything
```

**3. Fault-Tolerant via Lineage**
```
If Partition 3 is lost (worker crash):
    Spark looks at lineage:
    sc.parallelize([...]) → .map(x*2) → .filter(x>4)
    Spark recomputes only Partition 3 from scratch
    No need to re-run the entire job
```

**4. Type Safety (in a way)**
RDDs are typed: `RDD[Int]`, `RDD[String]`, `RDD[(String, Int)]`. The type is known at compile time (Scala/Java) but not enforced at runtime in Python.

---

## 📊 What is a DataFrame?

### Definition
A DataFrame is a **distributed collection of data organized into named columns**, similar to a table in a relational database or a spreadsheet. It is built on top of RDDs but adds **schema awareness** and **query optimization**.

### DataFrame Internal Structure

```
DataFrame
│
├── Schema
│       ├── Column: "name"       → StringType
│       ├── Column: "age"        → IntegerType
│       └── Column: "department" → StringType
│
├── Partitions (internally still RDD[Row] under the hood)
│       ├── Partition 1 → Row("Alice", 30, "Engineering")
│       ├── Partition 2 → Row("Bob", 25, "Marketing")
│       └── Partition N → Row(...)
│
├── Catalyst Optimizer   → optimizes your query plan
└── Tungsten Engine      → optimized memory & CPU execution
```

### How DataFrame is Created

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

spark = SparkSession.builder.appName("App").getOrCreate()

# Method 1: From a list
data = [("Alice", 30, "Engineering"),
        ("Bob",   25, "Marketing"),
        ("Carol", 35, "Engineering")]

schema = StructType([
    StructField("name",       StringType(),  True),
    StructField("age",        IntegerType(), True),
    StructField("department", StringType(),  True)
])

df = spark.createDataFrame(data, schema)
df.show()
# +-----+---+-----------+
# | name|age| department|
# +-----+---+-----------+
# |Alice| 30|Engineering|
# |  Bob| 25|  Marketing|
# |Carol| 35|Engineering|
# +-----+---+-----------+

# Method 2: From a file
df = spark.read.csv("employees.csv", header=True, inferSchema=True)

# Method 3: From SQL
spark.sql("SELECT * FROM employees").show()
```

---

## ⚙️ How RDD Works Internally — Step by Step

### Step 1: Creation
```python
sc = spark.sparkContext
rdd = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8], numSlices=4)
```
```
Data split into 4 partitions:
Partition 0: [1, 2]
Partition 1: [3, 4]
Partition 2: [5, 6]
Partition 3: [7, 8]
```

### Step 2: Transformation (Lazy — builds DAG)
```python
rdd2 = rdd.map(lambda x: x * 2)
rdd3 = rdd2.filter(lambda x: x > 6)
```
```
DAG built (nothing executed yet):
parallelize → map(x*2) → filter(x>6)
```

### Step 3: Action (Triggers Execution)
```python
result = rdd3.collect()
```
```
Spark submits job to cluster:

Partition 0: [1,2] → map → [2,4] → filter → []
Partition 1: [3,4] → map → [6,8] → filter → [8]
Partition 2: [5,6] → map → [10,12] → filter → [10,12]
Partition 3: [7,8] → map → [14,16] → filter → [14,16]

collect() gathers results to driver:
→ [8, 10, 12, 14, 16]
```

### Step 4: Fault Recovery (if needed)
```
If Partition 2 fails mid-execution:
    Spark reads lineage:
    sc.parallelize([5,6]) → map(x*2) → filter(x>6)
    Recomputes only Partition 2 on another worker
    Job continues without full restart
```

---

## ⚙️ How DataFrame Works Internally — Step by Step

### Step 1: Query Plan Creation (Unresolved Logical Plan)
```python
df = spark.read.csv("employees.csv", header=True, inferSchema=True)
result = df.filter(df.age > 30).groupBy("department").count()
```
```
Spark creates an Unresolved Logical Plan:
    Read CSV
        → Filter(age > 30)
            → GroupBy(department)
                → Count()
```

### Step 2: Analysis (Resolved Logical Plan)
```
Catalyst Analyzer checks:
    - Does column "age" exist? ✅
    - Is "age" the right type for > 30? ✅ (IntegerType)
    - Does column "department" exist? ✅
Unresolved plan → Resolved Logical Plan
```

### Step 3: Optimization (Optimized Logical Plan)
```
Catalyst Optimizer applies rules:

Rule: Predicate Pushdown
    → Push filter(age > 30) as close to data source as possible
    → Filter applied while reading CSV, not after loading everything

Rule: Column Pruning
    → Only read columns "age" and "department"
    → Skip "name" column entirely (not needed)

Rule: Constant Folding, etc.

Resolved Plan → Optimized Logical Plan
```

### Step 4: Physical Planning
```
Spark generates multiple Physical Plans:
    Plan A: BroadcastHashJoin
    Plan B: SortMergeJoin
    Plan C: ShuffleHashJoin

Cost-based optimizer picks the cheapest plan
→ Best Physical Plan selected
```

### Step 5: Code Generation (Tungsten)
```
Tungsten generates optimized Java bytecode at runtime
    → No Python overhead per row
    → CPU cache-friendly execution
    → Operates on binary data directly (avoids Java object overhead)
```

### Step 6: Execution
```
Physical Plan executed as RDD operations under the hood
Results returned to user
```

---

## 🔁 RDD vs DataFrame — Internal Execution Flow Comparison

```
RDD Execution:
──────────────
Your Python Code
    ↓
Python closures sent to JVM
    ↓
Spark executes row by row
    ↓
NO optimization
    ↓
Result

DataFrame Execution:
────────────────────
Your Python Code
    ↓
Logical Plan built
    ↓
Catalyst Optimizer (many optimization passes)
    ↓
Physical Plan chosen
    ↓
Tungsten generates JVM bytecode
    ↓
Highly optimized execution
    ↓
Result
```

> ✅ This is why DataFrames are usually **2x–10x faster** than equivalent RDD code.

---

## ⚖️ Side-by-Side Feature Comparison

| Feature | RDD | DataFrame |
|---|---|---|
| Introduced | Spark 1.0 | Spark 1.3 |
| Data model | Distributed objects (any type) | Distributed rows with named columns |
| Schema | ❌ No schema | ✅ Named columns + data types |
| Type safety | Partial (generic types) | Column-level type checking |
| SQL support | ❌ No | ✅ Yes — `spark.sql()` |
| Optimization | ❌ None — runs as-is | ✅ Catalyst optimizer |
| Performance | Slower (especially in PySpark) | Faster (Tungsten + Catalyst) |
| Memory usage | Higher (Java objects) | Lower (binary columnar format) |
| Ease of use | Verbose, functional style | Concise, SQL-like style |
| Debugging | Easier — explicit steps | Harder — optimizer transforms plan |
| Serialization | Java/Kryo serialization | Binary Tungsten format (no serialization overhead) |
| Custom objects | ✅ Yes — any Python/Java object | ❌ No — only Row types |
| Fault tolerance | ✅ Via lineage | ✅ Via lineage (same mechanism) |
| Unstructured data | ✅ Best choice | ❌ Not suitable |
| Structured data | ❌ Verbose | ✅ Best choice |
| Streaming support | DStream (legacy) | Structured Streaming (modern) |

---

## 🧪 Code Comparison — Same Tasks, Two Ways

### Task 1: Filter employees older than 30

**RDD way**
```python
# Assuming data as list of tuples: (name, age, department)
rdd = sc.parallelize([
    ("Alice", 30, "Engineering"),
    ("Bob",   25, "Marketing"),
    ("Carol", 35, "Engineering"),
    ("Dave",  40, "HR")
])

result = rdd.filter(lambda row: row[1] > 30).collect()
# [('Carol', 35, 'Engineering'), ('Dave', 40, 'HR')]
```
- No column names — you use index `row[1]` for age
- Easy to make mistakes (wrong index)
- No schema validation

**DataFrame way**
```python
df = spark.createDataFrame([
    ("Alice", 30, "Engineering"),
    ("Bob",   25, "Marketing"),
    ("Carol", 35, "Engineering"),
    ("Dave",  40, "HR")
], ["name", "age", "department"])

result = df.filter(df.age > 30)
result.show()
# +-----+---+-----------+
# | name|age| department|
# +-----+---+-----------+
# |Carol| 35|Engineering|
# | Dave| 40|         HR|
# +-----+---+-----------+
```
- Named columns — readable, self-documenting
- Schema enforced — wrong column name throws clear error

---

### Task 2: Count employees by department

**RDD way**
```python
rdd = sc.parallelize([
    ("Alice", 30, "Engineering"),
    ("Bob",   25, "Marketing"),
    ("Carol", 35, "Engineering"),
    ("Dave",  40, "HR")
])

result = rdd \
    .map(lambda row: (row[2], 1)) \          # extract department, emit 1
    .reduceByKey(lambda a, b: a + b) \        # sum by department
    .collect()

# [('Engineering', 2), ('Marketing', 1), ('HR', 1)]
```

**DataFrame way**
```python
result = df.groupBy("department").count()
result.show()
# +-----------+-----+
# | department|count|
# +-----------+-----+
# |Engineering|    2|
# |  Marketing|    1|
# |         HR|    1|
# +-----------+-----+
```

---

### Task 3: Average age per department, only departments with avg > 28

**RDD way** (much more verbose)
```python
result = rdd \
    .map(lambda row: (row[2], (row[1], 1))) \        # (dept, (age, count))
    .reduceByKey(lambda a, b: (a[0]+b[0], a[1]+b[1])) \ # sum age and count
    .mapValues(lambda v: v[0] / v[1]) \               # compute average
    .filter(lambda row: row[1] > 28) \                # filter avg > 28
    .collect()

# [('Engineering', 32.5), ('HR', 40.0)]
```

**DataFrame way**
```python
from pyspark.sql.functions import avg

result = df.groupBy("department") \
           .agg(avg("age").alias("avg_age")) \
           .filter("avg_age > 28")
result.show()
# +-----------+-------+
# | department|avg_age|
# +-----------+-------+
# |Engineering|   32.5|
# |         HR|   40.0|
# +-----------+-------+
```

---

### Task 4: SQL query on DataFrame (impossible with RDD)

```python
# Register DataFrame as a temp view
df.createOrReplaceTempView("employees")

# Run SQL directly
result = spark.sql("""
    SELECT department,
           COUNT(*)    AS headcount,
           AVG(age)    AS avg_age,
           MAX(age)    AS max_age
    FROM employees
    WHERE age > 25
    GROUP BY department
    HAVING COUNT(*) > 0
    ORDER BY avg_age DESC
""")
result.show()
```
> ❌ This is completely impossible with RDDs alone.

---

### Task 5: Working with custom objects (RDD wins here)

```python
# Custom Python class — ONLY works with RDD
class Employee:
    def __init__(self, name, age, department):
        self.name = name
        self.age = age
        self.department = department
    
    def get_seniority(self):
        return "Senior" if self.age > 30 else "Junior"

employees = [
    Employee("Alice", 30, "Engineering"),
    Employee("Bob",   25, "Marketing"),
    Employee("Carol", 35, "Engineering")
]

rdd = sc.parallelize(employees)
seniors = rdd.filter(lambda e: e.get_seniority() == "Senior") \
             .map(lambda e: e.name) \
             .collect()
# ['Carol']
```
> ✅ RDDs can hold any Python object. DataFrames cannot — they only understand structured Row types.

---

## 🔄 Converting Between RDD and DataFrame

### RDD → DataFrame
```python
from pyspark.sql import Row

# Method 1: Using Row objects
rdd = sc.parallelize([
    Row(name="Alice", age=30, department="Engineering"),
    Row(name="Bob",   age=25, department="Marketing")
])
df = spark.createDataFrame(rdd)
df.show()

# Method 2: Using toDF() with column names
rdd = sc.parallelize([("Alice", 30), ("Bob", 25)])
df = rdd.toDF(["name", "age"])
df.show()

# Method 3: Using createDataFrame with schema
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
schema = StructType([
    StructField("name", StringType(), True),
    StructField("age",  IntegerType(), True)
])
rdd = sc.parallelize([("Alice", 30), ("Bob", 25)])
df = spark.createDataFrame(rdd, schema)
```

### DataFrame → RDD
```python
df = spark.createDataFrame([("Alice", 30), ("Bob", 25)], ["name", "age"])

# Get RDD of Row objects
rdd_rows = df.rdd
print(rdd_rows.first())   # Row(name='Alice', age=30)

# Access fields by name
rdd_names = df.rdd.map(lambda row: row["name"])
print(rdd_names.collect())  # ['Alice', 'Bob']

# Or by attribute
rdd_ages = df.rdd.map(lambda row: row.age)
print(rdd_ages.collect())   # [30, 25]
```

---

## 🚀 Performance Deep Dive

### Why DataFrames Are Faster Than RDDs in PySpark

**RDD in PySpark — The Serialization Problem:**
```
Python process                     JVM (Spark)
──────────────                     ───────────
Python object                        
    ↓ serialize (pickle)             
Bytes ─────────────────────────→ Bytes
                                     ↓ deserialize
                               Java object
                                     ↓ process
                               Java object
                                     ↓ serialize
Bytes ←──────────────────────── Bytes
    ↓ deserialize (pickle)
Python object

Every single row crosses the Python↔JVM boundary = VERY SLOW
```

**DataFrame in PySpark — No Serialization:**
```
Python process                     JVM (Spark)
──────────────                     ───────────
DataFrame API call ─────────────→ Logical Plan
(just metadata,                        ↓
 no data moves)                   Catalyst Optimizer
                                       ↓
                                  Physical Plan
                                       ↓
                                  Tungsten (binary data)
                                       ↓ process in JVM
                                  Result
                                       ↓
Result ←───────────────────────── Minimal data transfer

Data NEVER leaves JVM. Python only sends instructions.
```

### Benchmark Comparison (approximate)

| Operation | RDD | DataFrame | Speedup |
|---|---|---|---|
| Filter | 100s | 10s | ~10x |
| GroupBy + Agg | 200s | 15s | ~13x |
| Join | 500s | 30s | ~16x |
| Sort | 150s | 12s | ~12x |

> Numbers are illustrative — actual speedup depends on cluster size, data size, and operation complexity.

---

## 🧠 Catalyst Optimizer — What It Does for DataFrames

```
Original Query:
df.filter(df.age > 30)
  .select("name", "department")
  .groupBy("department")
  .count()

Without Optimization:
1. Read ALL columns from disk
2. Load ALL rows into memory
3. Filter age > 30
4. Select only name, department
5. GroupBy + count

With Catalyst Optimization:
1. Column Pruning     → Only read "age", "name", "department" from disk (skip others)
2. Predicate Pushdown → Apply filter(age > 30) at data source level
3. Partition Pruning  → Skip entire partitions where age ≤ 30 (if partitioned)
4. GroupBy + count on already-filtered, already-pruned data

Result: Much less I/O, much less memory, much faster
```

---

## 🏗️ Narrow vs Wide Transformations (Applies to Both RDD & DataFrame)

### Narrow Transformation (no shuffle)
Each input partition contributes to exactly one output partition.

```
RDD Examples:    map(), filter(), flatMap(), mapPartitions()
DataFrame Examples: select(), filter(), withColumn()

Partition 1 → Partition 1 (same node, no data movement)
Partition 2 → Partition 2
Partition 3 → Partition 3
```

### Wide Transformation (shuffle — data moves across network)
Input partitions contribute to multiple output partitions.

```
RDD Examples:    groupByKey(), reduceByKey(), join(), sortBy()
DataFrame Examples: groupBy(), join(), orderBy(), distinct()

Partition 1 ──→ Partition 1 (reshuffled)
Partition 2 ──→ Partition 2 (reshuffled)
Partition 3 ──→ Partition 3 (reshuffled)
         ↑
  Data moves across network = expensive
```

---

## 🔑 Transformations vs Actions — Quick Reference

### RDD

| Category | Operation | Description |
|---|---|---|
| **Transformation** | `map(f)` | Apply function to each element |
| **Transformation** | `filter(f)` | Keep elements where f returns True |
| **Transformation** | `flatMap(f)` | Map then flatten |
| **Transformation** | `reduceByKey(f)` | Reduce values by key (wide) |
| **Transformation** | `groupByKey()` | Group values by key (wide) |
| **Transformation** | `sortBy(f)` | Sort by key (wide) |
| **Transformation** | `join(other)` | Join two RDDs (wide) |
| **Action** | `collect()` | Return all elements to driver |
| **Action** | `count()` | Return number of elements |
| **Action** | `first()` | Return first element |
| **Action** | `take(n)` | Return first n elements |
| **Action** | `saveAsTextFile(path)` | Write to disk |
| **Action** | `reduce(f)` | Aggregate all elements |

### DataFrame

| Category | Operation | Description |
|---|---|---|
| **Transformation** | `select(cols)` | Select columns |
| **Transformation** | `filter(condition)` | Filter rows |
| **Transformation** | `withColumn(name, expr)` | Add/replace column |
| **Transformation** | `groupBy(cols)` | Group rows (wide) |
| **Transformation** | `join(other, on, how)` | Join DataFrames (wide) |
| **Transformation** | `orderBy(cols)` | Sort rows (wide) |
| **Transformation** | `distinct()` | Remove duplicates (wide) |
| **Transformation** | `drop(cols)` | Remove columns |
| **Action** | `show(n)` | Print first n rows |
| **Action** | `collect()` | Return all rows to driver |
| **Action** | `count()` | Return row count |
| **Action** | `write.csv(path)` | Write to disk |
| **Action** | `toPandas()` | Convert to Pandas DataFrame |

---

## ✅ When to Use RDD vs DataFrame — Decision Guide

```
Is your data UNSTRUCTURED (raw text, binary, custom objects)?
    → Use RDD

Do you need to use CUSTOM PYTHON CLASSES or complex objects?
    → Use RDD

Are you doing COMPLEX LOW-LEVEL transformations not expressible in SQL/DSL?
    → Use RDD

Are you working with MACHINE LEARNING pipelines (MLlib)?
    → Use DataFrame (most MLlib APIs require DataFrames now)

Is your data STRUCTURED (CSV, JSON, Parquet, DB tables)?
    → Use DataFrame

Do you want to run SQL QUERIES?
    → Use DataFrame

Do you care about PERFORMANCE (most cases)?
    → Use DataFrame

Are you maintaining LEGACY Spark 1.x code?
    → RDD was required; migrate to DataFrame when possible

Do you need BOTH?
    → Use DataFrame; convert to RDD only when necessary via .rdd
```

---

## ⚠️ Common Mistakes & Gotchas

### ❌ Mistake 1: Using groupByKey() instead of reduceByKey() in RDDs
```python
# WRONG — groupByKey shuffles ALL values across network first
rdd.groupByKey().mapValues(sum)

# CORRECT — reduceByKey does partial aggregation before shuffle
rdd.reduceByKey(lambda a, b: a + b)
```

### ❌ Mistake 2: Calling collect() on large DataFrames/RDDs
```python
# WRONG — brings ALL data to driver → OutOfMemoryError
result = df.collect()

# CORRECT — only bring what you need
result = df.limit(100).collect()
result = df.show(20)
```

### ❌ Mistake 3: Using RDD when DataFrame is available
```python
# WRONG — slow, verbose, no optimization
rdd = df.rdd.map(lambda row: (row["department"], 1)) \
            .reduceByKey(lambda a, b: a + b)

# CORRECT — fast, concise, optimized
df.groupBy("department").count()
```

### ❌ Mistake 4: Not caching when reusing an RDD/DataFrame multiple times
```python
# WRONG — Spark recomputes from scratch each time
for i in range(5):
    print(df.count())  # reads CSV from disk 5 times!

# CORRECT — cache in memory after first computation
df.cache()  # or df.persist()
for i in range(5):
    print(df.count())  # reads from memory — fast
```

---

## 📦 Quick Reference Cheat Sheet

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, max, min

spark = SparkSession.builder.appName("App").getOrCreate()
sc = spark.sparkContext

# ─── RDD ───────────────────────────────────────────────────────
rdd = sc.parallelize([("Alice", 30, "Eng"),
                      ("Bob",   25, "Mkt"),
                      ("Carol", 35, "Eng")])

rdd.map(lambda x: x[0]).collect()               # names
rdd.filter(lambda x: x[1] > 28).collect()       # age > 28
rdd.map(lambda x: (x[2], 1)) \
   .reduceByKey(lambda a, b: a+b).collect()      # count by dept

# ─── DataFrame ─────────────────────────────────────────────────
df = spark.createDataFrame(
    [("Alice", 30, "Eng"), ("Bob", 25, "Mkt"), ("Carol", 35, "Eng")],
    ["name", "age", "department"]
)

df.select("name").show()                         # names
df.filter(col("age") > 28).show()               # age > 28
df.groupBy("department").count().show()          # count by dept
df.groupBy("department").agg(
    avg("age").alias("avg_age"),
    max("age").alias("max_age")
).show()

# SQL
df.createOrReplaceTempView("emp")
spark.sql("SELECT department, COUNT(*) FROM emp GROUP BY department").show()

# Convert
df_from_rdd = rdd.toDF(["name", "age", "department"])
rdd_from_df  = df.rdd

spark.stop()
```

---

## 🎯 Summary

| Concept | RDD | DataFrame |
|---|---|---|
| **Level** | Low-level, functional | High-level, declarative |
| **Best for** | Unstructured data, custom objects, complex logic | Structured data, SQL, analytics |
| **Performance** | Slower (especially Python) | Faster (Catalyst + Tungsten) |
| **Optimization** | None — runs exactly as coded | Automatic (query rewriting, predicate pushdown, column pruning) |
| **Schema** | None | Named columns + types |
| **SQL** | No | Yes |
| **Fault tolerance** | Lineage graph | Lineage graph (same) |
| **Use today** | When you must; niche use cases | Standard for 95% of use cases |
| **Relationship** | DataFrame is built ON TOP of RDD | DataFrame internally uses RDD[Row] |


# Where does RDD come into picture when we do any pyspark action?

DataFrame Full Lifecycle — Complete Under-the-Hood Deep Dive

---

## 📌 The Big Picture — What Happens When You Write DataFrame Code

```python
df1 = spark.read.csv("employees.csv", header=True, inferSchema=True)
df2 = spark.read.csv("departments.csv", header=True, inferSchema=True)
result = df1.join(df2, "dept_id") \
            .filter(col("age") > 30) \
            .groupBy("department") \
            .agg(avg("salary").alias("avg_salary")) \
            .orderBy("avg_salary", ascending=False)
result.write.parquet("output/")
```

Most people think this runs line by line. **It does NOT.**

Here is what actually happens — all 10 phases:

```
Phase 1:  SparkSession reads file metadata (NO data loaded yet)
Phase 2:  Each transformation builds a Logical Plan (NO execution)
Phase 3:  Catalyst Analyzer resolves columns and types
Phase 4:  Catalyst Optimizer rewrites the plan (predicate pushdown, etc.)
Phase 5:  Physical Planner generates multiple execution strategies
Phase 6:  Cost-based optimizer picks the best physical plan
Phase 7:  Tungsten generates optimized JVM bytecode
Phase 8:  Spark converts plan into RDD DAG (HERE is where RDD appears)
Phase 9:  Job submitted — Stages, Tasks, Shuffle executed on cluster
Phase 10: Failure detection and recovery if anything goes wrong
```

---

## 🔵 PHASE 1 — Reading the File (No Data Loaded Yet)

```python
df1 = spark.read.csv("employees.csv", header=True, inferSchema=True)
```

### What actually happens here — step by step:

```
Step 1: Spark talks to the filesystem (HDFS / S3 / local)
            → Reads file METADATA only (file size, block locations)
            → Does NOT load any actual rows into memory

Step 2: inferSchema=True triggers a SCHEMA INFERENCE JOB
            → Spark reads a SAMPLE of the file (first few rows or entire file
              depending on config)
            → Determines column names and data types
            → e.g., "age" → IntegerType, "name" → StringType, "salary" → DoubleType

Step 3: Spark calculates how many partitions to create:
            partition_count = ceil(file_size / spark.sql.files.maxPartitionBytes)
            Default maxPartitionBytes = 128MB

            Example:
            File = 512MB → 512/128 = 4 partitions planned

Step 4: An UNRESOLVED LOGICAL PLAN is created:
            Relation[employees.csv]
                Schema: (name: String, age: Int, dept_id: String, salary: Double)
                Partitions: 4 (planned, not yet read)

Step 5: df1 is just a PLAN OBJECT — no data, no RDD, nothing in memory
```

> ⚠️ **Key insight:** `df1` is NOT data. It is a RECIPE describing how to get data.

---

## 🔵 PHASE 2 — Building the Logical Plan (Every Transformation)

Every time you call `.join()`, `.filter()`, `.groupBy()`, `.agg()`, `.orderBy()` — **nothing executes**. Spark just adds a node to the Logical Plan tree.

```python
df1 = spark.read.csv("employees.csv", header=True, inferSchema=True)
df2 = spark.read.csv("departments.csv", header=True, inferSchema=True)

joined   = df1.join(df2, "dept_id")           # adds Join node
filtered = joined.filter(col("age") > 30)     # adds Filter node
grouped  = filtered.groupBy("department")      # adds Aggregate node
result   = grouped.agg(avg("salary").alias("avg_salary"))
ordered  = result.orderBy("avg_salary", ascending=False)  # adds Sort node
```

### Logical Plan Tree (Unresolved)

```
Sort [avg_salary DESC]
    └── Aggregate [department] → avg(salary) AS avg_salary
            └── Filter [age > 30]
                    └── Join [dept_id == dept_id]
                            ├── Relation[employees.csv]   (left)
                            └── Relation[departments.csv] (right)
```

- This tree is built **top-down as you write code**
- Each node holds the operation and its inputs
- Nothing is executed — this is pure metadata

---

## 🔵 PHASE 3 — Catalyst Analyzer (Resolving the Plan)

When an **action** is finally called (e.g., `.write`, `.show()`, `.count()`), Spark sends the Unresolved Logical Plan to the **Catalyst Analyzer**.

### What the Analyzer Does

```
Step 1: Checks the Catalog
            → Catalog stores table names, column names, data types
            → Is "age" a real column in df1? ✅
            → Is "dept_id" present in both DataFrames? ✅
            → Is "department" in df2? ✅
            → Is "salary" a numeric type for avg()? ✅

Step 2: Resolves column references
            → Unresolved: col("age")
            → Resolved:   employees.age#12 (IntegerType, nullable=true)
            (each column gets a unique internal ID like #12, #13, etc.)

Step 3: Resolves functions
            → avg("salary") → avg(employees.salary#15: DoubleType)

Step 4: Type coercion
            → If you compare IntegerType > LongType, Spark widens to LongType

Step 5: Output: Resolved Logical Plan
```

### Resolved Logical Plan

```
Sort [avg_salary#20 DESC]
    └── Aggregate [department#18]
              agg: avg(salary#15) AS avg_salary#20
            └── Filter [age#12 > 30]
                    └── Join [dept_id#13 == dept_id#17]
                            ├── Relation[name#11, age#12, dept_id#13, salary#15]
                            └── Relation[dept_id#17, department#18, location#19]
```

---

## 🔵 PHASE 4 — Catalyst Optimizer (The Magic)

This is the **most powerful phase**. The Catalyst Optimizer applies **rule-based transformations** to rewrite the logical plan into a more efficient one.

### Optimization Rule 1: Predicate Pushdown

```
BEFORE optimization:
    Read ALL rows from employees.csv
        → Join with departments.csv
            → THEN filter age > 30

AFTER optimization (Predicate Pushdown):
    Read employees.csv BUT filter age > 30 WHILE reading
        → Join only the already-filtered rows
            → Much less data in the join

Result: If 70% of employees are age ≤ 30, the join processes 70% less data
```

### Optimization Rule 2: Column Pruning

```
BEFORE optimization:
    Read ALL columns: name, age, dept_id, salary, address, phone, email, ...

AFTER optimization (Column Pruning):
    Only read: age, dept_id, salary, department
    (only columns actually used in the final result)

Result: Less I/O, less memory, faster scans
```

### Optimization Rule 3: Join Reordering

```
BEFORE:
    employees (10M rows) JOIN departments (50 rows)

AFTER (Join Reordering):
    Filter employees to age > 30 first → maybe 3M rows
    THEN join with departments (50 rows)

Result: Join processes 7M fewer rows
```

### Optimization Rule 4: Constant Folding

```
BEFORE: filter(col("age") > 10 + 20)
AFTER:  filter(col("age") > 30)

Result: Expression evaluated once at planning time, not per row
```

### Optimization Rule 5: Broadcast Join Detection

```
If departments.csv is small (< spark.sql.autoBroadcastJoinThreshold, default 10MB):
    → Mark it for BROADCAST
    → Entire departments table sent to ALL executor nodes
    → No shuffle needed for the join at all

Result: Massive performance gain — join becomes local to each executor
```

### Optimized Logical Plan

```
Sort [avg_salary DESC]
    └── Aggregate [department]
            └── BroadcastHashJoin [dept_id]      ← join strategy decided
                    ├── Filter [age > 30]          ← pushed DOWN near scan
                    │       └── Project [age, dept_id, salary]  ← only needed cols
                    │               └── Scan employees.csv
                    └── Broadcast
                            └── Project [dept_id, department]
                                    └── Scan departments.csv
```

---

## 🔵 PHASE 5 — Physical Planning (How to Actually Run It)

The Logical Plan describes WHAT to do. The Physical Plan describes HOW to do it.

### For each logical operation, Spark generates multiple physical strategies:

```
Logical: Join
    Physical Option A: BroadcastHashJoin   → best when one side is small
    Physical Option B: SortMergeJoin       → best for large + large tables
    Physical Option C: ShuffleHashJoin     → alternative hash-based join

Logical: Aggregate (groupBy + avg)
    Physical Option A: HashAggregate       → hash map in memory
    Physical Option B: SortAggregate       → sort then aggregate (fallback)

Logical: Sort
    Physical Option A: TakeOrderedAndProject → optimized for top-N
    Physical Option B: Sort                  → full sort
```

### Physical Plan Selected (for our example)

```
*(3) Sort [avg_salary DESC]
    └── Exchange (rangepartitioning) ← shuffle for sort
            └── *(2) HashAggregate [department] → avg(salary) AS avg_salary
                    └── Exchange (hashpartitioning dept_id) ← shuffle for groupBy
                            └── *(1) BroadcastHashJoin [dept_id]
                                    ├── Filter [age > 30]
                                    │   └── FileScan employees.csv [age, dept_id, salary]
                                    └── BroadcastExchange
                                            └── FileScan departments.csv [dept_id, department]

*(N) = code-gen stage (Tungsten whole-stage code generation)
Exchange = shuffle boundary between stages
```

---

## 🔵 PHASE 6 — Tungsten Code Generation

Tungsten is Spark's execution engine that **generates optimized JVM bytecode** at runtime.

### What Tungsten Does

```
Without Tungsten (row-at-a-time):
    For each row:
        deserialize row
        call filter function
        serialize result
        → massive overhead per row

With Tungsten (whole-stage codegen):
    Spark generates a SINGLE tight Java loop:

    for (row in partition) {
        if (row.age > 30) {
            hashMap.merge(row.dept_id, row.salary, ...)
        }
    }

    → Compiled to JVM bytecode
    → CPU cache-friendly
    → No virtual function calls
    → No row serialization within a stage
```

### Memory Layout Optimization

```
Java Object (WITHOUT Tungsten):
    Object header: 16 bytes overhead
    "Alice": String object → 40 bytes for 5 chars!
    age: Integer object → 16 bytes for one int!
    Total per row: ~150 bytes

Tungsten UnsafeRow (binary format):
    Fixed-length fields: direct binary
    "Alice": 5 bytes
    age: 4 bytes
    Total per row: ~20 bytes

→ 7x less memory
→ CPU operates on raw bytes — no GC pressure
```

---

## 🔵 PHASE 7 — WHERE DataFrame Becomes RDD

This is the answer to "when does it get converted to RDD?"

```
After Physical Planning + Tungsten codegen:

Spark calls: queryExecution.toRdd

This converts the Physical Plan into an RDD[InternalRow]

Physical Plan Node   →  RDD Operation
────────────────────────────────────────────────────────
FileScan             →  HadoopRDD / ParquetRDD (reads partitions)
Filter               →  MapPartitionsRDD (applies filter per partition)
BroadcastHashJoin    →  MapPartitionsRDD (join happens locally per partition)
Exchange (shuffle)   →  ShuffledRowRDD (data moves across network)
HashAggregate        →  MapPartitionsRDD (aggregate per partition)
Sort                 →  MapPartitionsRDD (sort within partition)
Final Exchange       →  ShuffledRowRDD (final sort shuffle)
```

### The RDD Lineage for Our Example

```
ParquetRDD / HadoopRDD (read employees.csv partitions)
    └── MapPartitionsRDD (apply filter: age > 30, project columns)
            └── MapPartitionsRDD (BroadcastHashJoin with departments)
                    └── ShuffledRowRDD (Exchange: shuffle by dept_id for groupBy)
                            └── MapPartitionsRDD (HashAggregate partial)
                                    └── ShuffledRowRDD (Exchange: shuffle for sort)
                                            └── MapPartitionsRDD (final sort)
```

> ⚠️ **Key insight:** The RDD is `RDD[InternalRow]` — NOT `RDD[Row]`.
> `InternalRow` is Tungsten's binary format. It is NOT a Python Row object.
> You never directly see this RDD unless you call `df.queryExecution.toRdd`

---

## 🔵 PHASE 8 — Job, Stage, and Task Execution

### From RDD Lineage to Jobs, Stages, Tasks

```
Spark DAGScheduler looks at the RDD lineage
    → Finds all "shuffle boundaries" (ShuffledRowRDD)
    → Each boundary = a new Stage

Our example produces 3 Stages:
```

### Stage 0 — Read + Filter + BroadcastHashJoin

```
Tasks: one per partition of employees.csv
       If employees.csv = 512MB, maxPartitionBytes = 128MB → 4 tasks

Each Task (runs on an Executor):
    1. Read its 128MB chunk of employees.csv from HDFS/S3
    2. Apply filter: age > 30
    3. Project: keep only age, dept_id, salary
    4. Receive broadcast copy of departments.csv (already sent to all executors)
    5. Perform hash join locally (look up dept_id in departments hash table)
    6. Compute PARTIAL HashAggregate (partial sum + count per department)
    7. Write shuffle files for Stage 1 (shuffle write)

Shuffle files written: 4 tasks × 200 shuffle partitions = 800 files
```

### Stage 1 — Full Aggregation (after shuffle)

```
Tasks: 200 (spark.sql.shuffle.partitions default)

Each Task:
    1. Read shuffle files from Stage 0 (shuffle read)
       → Fetches all partial aggregates for its assigned departments
    2. Merge partial aggregates → compute final avg(salary) per department
    3. Write shuffle files for Stage 2 (sort shuffle)

Shuffle files written: 200 × 200 = 40,000 (reduced by sort merge)
```

### Stage 2 — Final Sort

```
Tasks: 200 (same shuffle partition count)

Each Task:
    1. Read shuffle files from Stage 1
    2. Sort rows by avg_salary DESC within partition
    3. Write final output partition to parquet file

Output: 200 parquet part files written to output/
```

### Full Execution Timeline

```
Driver                                    Cluster Manager              Workers
──────                                    ───────────────              ───────
result.write.parquet("output/")
    ↓
Build Logical Plan
    ↓
Optimize Plan (Catalyst)
    ↓
Build Physical Plan
    ↓
Convert to RDD DAG
    ↓
Submit Job to DAGScheduler
    ↓
DAGScheduler creates Stage 0 ──────────→ Assign tasks ──────────→ Execute 4 tasks
                                                                    (read, filter, join)
                                                                    Write shuffle files
                                                                         ↓
DAGScheduler creates Stage 1 ──────────→ Assign tasks ──────────→ Execute 200 tasks
                                                                    (read shuffle, agg)
                                                                    Write shuffle files
                                                                         ↓
DAGScheduler creates Stage 2 ──────────→ Assign tasks ──────────→ Execute 200 tasks
                                                                    (read shuffle, sort)
                                                                    Write parquet output
                                                                         ↓
Job Complete ←───────────────────────────────────────────────────────────
```

---

## 🔴 PHASE 9 — Failure Handling & Recovery

This is one of the most important parts — how does Spark survive failures?

### Type 1: Task Failure (Most Common)

```
Scenario: One task in Stage 1 crashes (executor OOM, network blip, etc.)

What happens:
    Step 1: Executor sends failure signal to Driver
    Step 2: TaskScheduler marks that specific task as FAILED
    Step 3: TaskScheduler retries the task (default: 4 retries)
            → Same task, possibly on a DIFFERENT executor
    Step 4: If retry succeeds → job continues, no impact to other tasks
    Step 5: If all 4 retries fail → Stage fails → Job fails → Error to user

Retry config:
    spark.task.maxFailures = 4  (default)
```

### Type 2: Executor Failure (Worker Crashes)

```
Scenario: Entire executor (worker JVM) crashes mid-job

What happens:
    Step 1: Driver detects heartbeat timeout from executor
    Step 2: Driver asks Cluster Manager to launch a NEW executor
    Step 3: All tasks that were running on failed executor = FAILED
    Step 4: TaskScheduler re-queues those tasks on the new executor
    Step 5: BUT — shuffle files written by the failed executor are LOST
    
If shuffle files are lost:
    Step 6: Spark needs to RE-RUN the PARENT STAGE that produced those shuffle files
            (This is why lineage is so critical)
    Step 7: Only the affected partitions of the parent stage are re-run
    Step 8: Shuffle files recomputed
    Step 9: Failed tasks of the current stage now re-run successfully

Example:
    Stage 0 ran successfully, wrote shuffle files on Executor 3
    Executor 3 crashes during Stage 1
    Stage 1 tasks that needed Executor 3's shuffle files fail
    → Spark re-runs affected Stage 0 partitions on new executor
    → Rewrites shuffle files
    → Stage 1 tasks retry and succeed
```

### Type 3: Shuffle Data Loss (Without Executor Failure)

```
Scenario: Shuffle files on disk get corrupted or deleted between stages

What happens:
    → FetchFailedException thrown during shuffle read
    → Stage is re-submitted from the parent stage
    → Entire parent stage may need to re-run

This is why caching/checkpointing is important for iterative algorithms
```

### Type 4: Driver Failure (Full Job Loss)

```
Scenario: Driver process crashes

What happens:
    → ENTIRE JOB is lost (no partial recovery by default)
    → All executors are killed by Cluster Manager
    → Job must be restarted from scratch

Mitigation:
    → Use checkpointing for long-running jobs
    → In YARN: driver recovery is possible with --supervise flag
    → In Structured Streaming: checkpointing provides exactly-once guarantees
```

### Type 5: Data Skew Causing Task Failure

```
Scenario: One partition has 100x more data than others
          → That one task runs out of memory

What happens:
    → spark.sql.adaptive.enabled = true (AQE — Adaptive Query Execution)
    → Spark detects skewed partition at runtime
    → Automatically SPLITS the large partition into smaller sub-tasks
    → Re-runs only the skewed partition with splitting

Without AQE:
    → Task fails with OOM
    → 4 retries all fail → Job fails
    → You need to manually add salting or repartitioning
```

---

## 🔵 PHASE 10 — Adaptive Query Execution (AQE) — Runtime Re-optimization

AQE (enabled by default in Spark 3.0+) allows Spark to **change the physical plan at runtime** based on actual data statistics collected during execution.

### AQE Feature 1: Dynamic Coalescing of Shuffle Partitions

```
BEFORE execution (at planning time):
    spark.sql.shuffle.partitions = 200
    → Stage 1 planned with 200 tasks

AFTER Stage 0 completes (AQE kicks in):
    AQE looks at actual shuffle data sizes:
    Total shuffle data = 50MB (very small)
    200 tasks × 50MB/200 = 0.25MB per task → too many tiny tasks!

AQE action:
    Coalesces 200 → 5 partitions
    Stage 1 now runs with only 5 tasks instead of 200

Result: Less overhead, faster execution
```

### AQE Feature 2: Dynamic Join Strategy Switching

```
BEFORE execution:
    Planner chose SortMergeJoin (departments.csv looked large based on file size)

AFTER Stage 0 completes (actual data stats known):
    After filter age > 30, departments side = only 2MB
    AQE switches join strategy: SortMergeJoin → BroadcastHashJoin

Result: Eliminates shuffle for the join entirely
```

### AQE Feature 3: Skew Join Optimization

```
BEFORE: One partition in Stage 0 has 10GB of data (skewed key)
AQE:    Detects skew, automatically splits into sub-partitions
        Runs the skewed partition as multiple smaller tasks in parallel
Result: No single task OOM, faster overall completion
```

---

## 🔄 Complete End-to-End Flow — Visual Summary

```
Your Code
─────────────────────────────────────────────────────────────────────
df1 = spark.read.csv(...)
df2 = spark.read.csv(...)
result = df1.join(df2).filter(...).groupBy(...).agg(...).orderBy(...)
result.write.parquet(...)   ← ACTION triggers everything below
         │
         ▼
─────────────────────────────────────────────────────────────────────
DRIVER — PLANNING PHASE (no data movement)
─────────────────────────────────────────────────────────────────────
         │
         ▼
[1] Unresolved Logical Plan
    (tree of nodes: Scan, Join, Filter, Aggregate, Sort)
         │
         ▼
[2] Catalyst Analyzer
    → Resolve column names via Catalog
    → Assign unique IDs to columns
    → Type checking and coercion
         │
         ▼
[3] Resolved Logical Plan
         │
         ▼
[4] Catalyst Optimizer
    → Predicate Pushdown
    → Column Pruning
    → Join Reordering
    → Broadcast Detection
    → Constant Folding
    → 50+ other rules
         │
         ▼
[5] Optimized Logical Plan
         │
         ▼
[6] Physical Planner
    → Enumerate physical strategies
    → Cost-based optimizer picks best plan
    → BroadcastHashJoin vs SortMergeJoin
    → HashAggregate vs SortAggregate
         │
         ▼
[7] Physical Plan
         │
         ▼
[8] Tungsten Code Generation
    → Generate JVM bytecode per stage
    → Whole-stage codegen (fuse operators)
    → Binary UnsafeRow memory format
         │
         ▼
[9] Convert to RDD DAG
    Physical Plan nodes → RDD[InternalRow] chain
    (HERE is where DataFrame becomes RDD)
         │
         ▼
[10] DAGScheduler
    → Find shuffle boundaries
    → Split RDD DAG into Stages
    → Our example: Stage 0, Stage 1, Stage 2
         │
         ▼
─────────────────────────────────────────────────────────────────────
CLUSTER — EXECUTION PHASE (actual data movement)
─────────────────────────────────────────────────────────────────────
         │
         ▼
[11] Stage 0 submitted
    → TaskScheduler assigns tasks to executors
    → Each task: read partition → filter → join → partial agg
    → Tasks write shuffle files to local disk
    → AQE collects stats on shuffle output
         │
         ▼
[12] AQE re-optimization (between stages)
    → Coalesce partitions if data is small
    → Switch join strategies if needed
    → Handle skew if detected
         │
         ▼
[13] Stage 1 submitted
    → Tasks shuffle-read from Stage 0
    → Final aggregation per partition
    → Write shuffle files for Stage 2
         │
         ▼
[14] Stage 2 submitted
    → Tasks shuffle-read from Stage 1
    → Sort within each partition
    → Write parquet output files
         │
         ▼
─────────────────────────────────────────────────────────────────────
FAILURE HANDLING (at any stage)
─────────────────────────────────────────────────────────────────────

Task fails         → Retry on same/different executor (max 4 retries)
Executor fails     → Re-launch executor + re-run affected tasks
                   → Re-run parent stage if shuffle files lost
Shuffle data lost  → FetchFailedException → re-run parent stage
Driver fails       → Full job restart required
Data skew          → AQE splits skewed partition into sub-tasks

─────────────────────────────────────────────────────────────────────
OUTPUT
─────────────────────────────────────────────────────────────────────
200 parquet part files written to output/ ✅
Job complete signal sent to driver ✅
```

---

## 🔬 Deep Dive: The Join — What Happens Physically

Joins are the most complex operation. Here's exactly what happens for each join type:

### BroadcastHashJoin (small table + large table)

```
Trigger: departments.csv < spark.sql.autoBroadcastJoinThreshold (default 10MB)

Step 1: Driver collects departments.csv entirely (or executor collects it)
Step 2: Serialize departments into a compact hash map
Step 3: Broadcast the hash map to ALL executors (network broadcast)
Step 4: Each executor receives a full copy of departments hash map
Step 5: Each task (processing employees partition) does:
            for each employee row:
                key = employee.dept_id
                dept_row = hashMap.lookup(key)  ← local lookup, no network
                emit joined row

NO SHUFFLE — entire join is local per executor
```

### SortMergeJoin (large table + large table)

```
Trigger: Both tables too large for broadcast

Step 1: SHUFFLE PHASE — both sides shuffled by join key
            employees: hash(dept_id) % numPartitions → shuffle
            departments: hash(dept_id) % numPartitions → shuffle
            → All rows with same dept_id land in SAME partition on SAME executor

Step 2: SORT PHASE — within each partition, sort both sides by join key
            employees partition 5: sorted by dept_id
            departments partition 5: sorted by dept_id

Step 3: MERGE PHASE — two-pointer merge (like merge sort)
            pointer_left = 0, pointer_right = 0
            while both pointers valid:
                if left.dept_id == right.dept_id:
                    emit joined row
                    advance pointers
                elif left.dept_id < right.dept_id:
                    advance left pointer
                else:
                    advance right pointer

REQUIRES 2 shuffles (one per table side)
```

### ShuffleHashJoin (medium + medium tables)

```
Step 1: Shuffle smaller side by join key (hash partitioning)
Step 2: Build hash map from smaller side partitions
Step 3: Shuffle larger side by join key
Step 4: Probe hash map with larger side rows

REQUIRES 2 shuffles, but no sort step
Risky: if hash map doesn't fit in memory → OOM
```

---

## 🔬 Deep Dive: GroupBy + Aggregate — What Happens Physically

```python
df.groupBy("department").agg(avg("salary"))
```

### Two-Phase Aggregation (Partial + Final)

```
PHASE 1 — Partial Aggregation (map-side, BEFORE shuffle)
──────────────────────────────────────────────────────
Each task processes its partition BEFORE any data moves:

Partition 0 has rows:
    (Alice, Engineering, 90000)
    (Bob,   Engineering, 80000)
    (Carol, Marketing,   70000)

Partial aggregate computed LOCALLY:
    Engineering → sum=170000, count=2
    Marketing   → sum=70000,  count=1

This runs INSIDE the same stage as the filter/join
→ Data volume dramatically reduced before shuffle

──────────────────────────────────────────────────────
SHUFFLE — Route partial aggregates by department
──────────────────────────────────────────────────────
hash("Engineering") % 200 = partition 47
hash("Marketing")   % 200 = partition 123

All "Engineering" partial aggregates → executor handling partition 47
All "Marketing" partial aggregates   → executor handling partition 123

──────────────────────────────────────────────────────
PHASE 2 — Final Aggregation (reduce-side, AFTER shuffle)
──────────────────────────────────────────────────────
Partition 47 receives all Engineering partial aggregates:
    From task 0: sum=170000, count=2
    From task 1: sum=150000, count=2
    From task 2: sum=200000, count=3
    From task 3: sum=120000, count=2

Final merge:
    Engineering → sum=640000, count=9 → avg = 71111.11

No more shuffling needed — result is final
```

---

## 💾 Caching & Persistence — Avoiding Recomputation

```python
df_filtered = df1.join(df2, "dept_id").filter(col("age") > 30)
df_filtered.cache()  # or df_filtered.persist(StorageLevel.MEMORY_AND_DISK)

# Now use df_filtered multiple times
count1 = df_filtered.count()                          # triggers execution + caching
count2 = df_filtered.groupBy("dept").count().show()   # reads from cache, not disk
count3 = df_filtered.filter(col("salary") > 50000).count()  # reads from cache
```

### What cache() Does Under the Hood

```
First action (df_filtered.count()):
    → Full pipeline executes (read → join → filter)
    → Results stored as RDD[InternalRow] partitions in executor memory
    → Metadata registered in BlockManager on each executor
    → Driver's BlockManagerMaster knows which partitions are cached where

Subsequent actions:
    → Spark sees df_filtered is cached
    → Skips read → join → filter steps entirely
    → Reads directly from cached RDD[InternalRow] in executor memory
    → MUCH faster

If executor memory is full:
    → LRU eviction: oldest cached partitions removed
    → cache()        = MEMORY_ONLY → evicted partitions recomputed on demand
    → persist(MEMORY_AND_DISK) → evicted partitions spill to disk
```

### Storage Levels

```
StorageLevel.MEMORY_ONLY         → Store as deserialized Java objects in JVM heap
                                   Fastest but most memory-hungry
StorageLevel.MEMORY_AND_DISK     → Spill to disk if memory full
StorageLevel.MEMORY_ONLY_SER     → Store as serialized bytes (less memory, slower)
StorageLevel.DISK_ONLY           → Store only on disk
StorageLevel.OFF_HEAP             → Store in Tungsten off-heap memory (no GC)
```

---

## 🔑 Checkpointing — Breaking Long Lineage Chains

For iterative algorithms (ML, graph processing), the RDD lineage can get very long:

```
Iteration 1: RDD1 → RDD2 → RDD3 → RDD4 → RDD5
Iteration 2: RDD5 → RDD6 → RDD7 → RDD8 → RDD9
...
Iteration 100: RDD495 → ... → RDD500

If RDD300 fails → Spark must recompute from RDD1!
Lineage traversal itself becomes expensive
```

### Checkpointing Cuts the Lineage

```python
spark.sparkContext.setCheckpointDir("hdfs://checkpoints/")

df_iter = initial_df
for i in range(100):
    df_iter = one_iteration(df_iter)
    if i % 10 == 0:
        df_iter = df_iter.checkpoint()  # ← materializes to HDFS, cuts lineage

# Now if failure at iteration 55:
# → Recompute only from checkpoint at iteration 50 (not from start)
```

---

## ⚠️ Key Things People Get Wrong

### ❌ Misconception 1: "DataFrame IS an RDD"
```
Wrong: DataFrame is just a fancy wrapper around RDD
Right: DataFrame is a HIGHER-LEVEL ABSTRACTION with its own planning and
       optimization pipeline. It only becomes an RDD[InternalRow] at the
       FINAL execution step, after all optimization.
```

### ❌ Misconception 2: "Each transformation executes immediately"
```
Wrong: df.filter(...).groupBy(...) runs step by step
Right: These are ALL lazy. Nothing runs until an action is called.
       Spark collects ALL transformations into one plan and optimizes
       the ENTIRE plan before executing anything.
```

### ❌ Misconception 3: "More partitions = faster"
```
Wrong: Always use 1000 partitions for parallelism
Right: Too many small partitions → task scheduling overhead > actual work
       Too few large partitions → some executors idle
       Rule of thumb: 2-4 partitions per CPU core in your cluster
       AQE can auto-tune this at runtime
```

### ❌ Misconception 4: "Shuffle is always bad"
```
Wrong: Avoid all shuffles at all costs
Right: Some shuffles are unavoidable (groupBy, join on different keys, sort)
       AQE can reduce shuffle cost significantly
       Proper partitioning upfront can eliminate unnecessary shuffles
```

---

## 🎯 Complete Summary Table

| Phase | What Happens | Data Movement? | Where? |
|---|---|---|---|
| Read | File metadata + schema inference | No (metadata only) | Driver |
| Logical Plan | Build plan tree per transformation | No | Driver |
| Analysis | Resolve columns, types, functions | No | Driver |
| Optimization | Catalyst rewrites plan (50+ rules) | No | Driver |
| Physical Plan | Choose join/agg strategies | No | Driver |
| Codegen | Generate JVM bytecode per stage | No | Driver |
| RDD Conversion | Physical plan → RDD[InternalRow] | No | Driver |
| Stage Split | DAGScheduler finds shuffle boundaries | No | Driver |
| Stage 0 Execution | Read → Filter → Join → Partial Agg | Local reads | Executors |
| Shuffle Write | Write shuffle files to local disk | Local disk | Executors |
| AQE Re-optimize | Coalesce/replan based on real stats | No | Driver |
| Stage 1 Execution | Shuffle Read → Final Agg | Network transfer | Executors |
| Stage 2 Execution | Sort → Write output | Network + disk write | Executors |
| Task Failure | Retry task (up to 4x) | Minimal | Executors |
| Executor Failure | Re-run lost tasks + parent stage | Re-reads source | Executors |

# Spark configuration 
- spark.master 
- spark.sql.shuffle.partitions: `configuration controls how Spark distributes data across the cluster during shuffle operations (e.g., groupBy, join, distinct, or repartition). Number of partitions that should be avaialbel after shuffle operations.`
    ```commandline
    How It Works
    Scenario: You run a groupBy("user_id").count() on a 1TB dataset.
    
    Shuffle Behavior:
        Spark splits data into N partitions (where N = spark.sql.shuffle.partitions).
        Each partition is processed by a task.
        Example: With N=200, Spark creates 200 tasks for the shuffle stage.
        
        
    Why It Matters
        Too Low (e.g., N=10):
        
            Fewer tasks → Large partitions → Risk of OOM/spills.
        
            Example: 1TB / 10 = 100GB per partition (likely crashes).
        
        Too High (e.g., N=10,000):
        
            Many tiny tasks → Overhead (slow scheduling, disk I/O).
        
            Example: 1TB / 10,000 = 100MB per partition (inefficient).
            
            
            
    Optimal Setting
        Rule of Thumb: Set N = 2–4 × number of cores in your cluster.
        
            8-core cluster? Try N=16 to N=32.
            
            100-core cluster? Try N=200 (default may work).
        
        Adjust Based On:
        
            Data Skew: Increase N if some keys are much larger than others.
            
            Spills (UI): If spills occur, increase N or executor memory.
    ```

- spark.driver.extraJavaOptions
- spark.executor.extraJavaOptions
- spark.jars.package 
- spark.port.maxRetries 
- spark.default.parallelism : `Controls parallelism and data distribution across the cluster.`
    ```commandline
    The spark.default.parallelism parameter defines the default number of partitions Spark uses for distributed operations (like RDD transformations or DataFrame shuffles) when no explicit partitioning is specified.
  
    spark usages spark.sql.shuffle.partitions for DataFrames if specified.

    ```
- spark.python.worker.memory 
- spark.driver.memory 
- spark.executor.memory 
- spark.sql.files.maxPartitionBytes: `The maximum number of bytes to pack into a single partition when reading files. This configuration is effective only when using file-based sources such as Parquet, JSON and ORC.	`
- spark.sql.execution.arrow.maxRecordsPerBatch: `Data partitions in Spark are converted into Arrow record batches, which can temporarily lead to high memory usage in the JVM. To avoid possible out of memory exceptions, the size of the Arrow record batches can be adjusted by setting the conf spark.sql.execution.arrow.maxRecordsPerBatch to an integer that will determine the maximum number of rows for each batch. The default value is 10,000 records per batch. If the number of columns is large, the value should be adjusted accordingly. Using this limit, each data partition will be made into 1 or more record batches for processing`

# How does reading from various sources work in PySpark? and how does the chunking comes into picture?


# How to optimize a PySpark job
| Action             | Goal                 |
| ------------------ | -------------------- |
| Use `.explain()`   | Understand plan      |
| Cache smartly      | Avoid recomputation  |
| Broadcast joins    | Avoid shuffle        |
| Repartition wisely | Improve joins        |
| Filter early       | Reduce data early    |
| Avoid UDFs         | Enable optimization  |
| Use Parquet/ORC    | Speed & compression  |
| Monitor Spark UI   | See bottlenecks      |
| Tune configs       | Adapt to job/cluster |


## what if dataframes are big enough - 
1. Repartition Both DataFrames on the Join Key: This ensures rows with the same key go to the same partition before the join — reducing unnecessary shuffle:
2. Avoid Wide Rows (Drop Unused Columns Early): Before join, drop unnecessary columns: This reduces the amount of data shuffled across the network.
3. Check for Data Skew: Before optimizing anything
   - Run df1.groupBy("join_key").count().orderBy("count", ascending=False) to spot if any key dominates. 
   - If 1 or 2 keys have way more records — that’s data skew. You’ll need salting or skew hints (see below).


## What is Skewness and how to avoid Skewness using `by chaninging the joining stretegy`, `salting` and `Enabling AQE`


## What is AQE and provide an example that explains the usages of AQE and disadvantages of it


# Notebook tests

## What happens if you only set spark.driver.memory, but not spark.executor.memory?
### In cluster mode - 

Spark will allocate memory only for the driver as specified, and will use default memory settings, which is usually 1 GB (or based on your cluster manager’s default, like YARN or standalone). for the executors. This could create OOM on executors.


### In local mode - 

Local mode is where everything (driver + executors) runs in a single JVM process on your local machine.
- Driver = Executor 
- All components (DAG scheduler, task threads, memory manager, cache) live in one process 
- Threads do the work instead of launching remote JVM executors

Since there are no separate executors, spark.executor.memory (or --executor-memory) has no effect in local mode.

Memory Breakdown:-
```commandline
+-------------------------+  ← Total = --driver-memory (e.g., 6 GB)
| Reserved Memory (~300MB)|  ← JVM internals
+-------------------------+
| Spark Managed Memory    |
|                         |
|  +--------------------+ |
|  | Execution Memory   | | ← For shuffle, sort, joins, UDFs
|  +--------------------+ |
|  | Storage Memory     | | ← For cache(), broadcast, persist()
|  +--------------------+ |
+-------------------------+
| User Memory             |  ← UDF objects, accumulators, logs, etc.
+-------------------------+

```

In local mode, `spark.memory.fraction` will still be respected. Lets say
```commandline
spark.driver.memory = 8g
spark.memory.fraction = 0.7
```
- Reserved memory = ~300 MB (JVM overhead)
- Available heap = 8 GB - 300 MB = 7.7 GB 
- Spark-managed memory = 70% of 7.7 GB ≈ 5.39 GB

This 5.39 GB is split between:
- Execution memory (default: 50% of that)
- Storage memory (default: 50%)

That split is further controlled by:

`spark.memory.storageFraction = 0.5  # Default`

So:
- Execution memory = ~2.69 GB
- Storage memory = ~2.69 GB

if `spark.memory.fraction` is not specified then a default behaviour of `0.6` is used. So, it is always there in background.


## Trying out different different executor memory configuration-



# How to process 100TB large, no partitoned file in PySpark?

While local mode with limited resources isn't ideal for 100TB processing, here's how you could approach this challenging scenario:

Reality Check: Local Mode Limitations

Key constraints:
- Disk I/O: Will be your primary bottleneck (even with SSD/NVMe)
- Memory: 32GB RAM for both Spark and OS 
- CPU: 8 vCPUs for parallel processing 
- Single node: No distributed processing benefits
- 
```python
# Configure Spark to handle memory constraints

# File Chunking Strategy
spark = SparkSession.builder \
    .master("local[8]") \  # Use all 8 vCPUs
    .config("spark.driver.memory", "28g") \  # Leave 4GB for OS
    .config("spark.sql.files.maxPartitionBytes", "256m") \  # Smaller chunks
    .config("spark.sql.shuffle.partitions", "8") \  # Match vCPU count
    .config("spark.memory.fraction", "0.9") \  # Maximize usable memory
    .config("spark.memory.storageFraction", "0.3") \  # Favor execution memory
    .getOrCreate()



# Process in batches (pseudo-code)
batch_size = 100  # Number of partitions to process at once

for i in range(0, total_partitions, batch_size):
    df = spark.read \
        .option("header", "true") \
        .option("startingOffset", i) \
        .option("endingOffset", i+batch_size-1) \
        .csv("file:///path/to/100tb-file.csv")
    
    # Process this batch
    processed = transform(df)
    
    # Write output incrementally
    processed.write \
        .mode("append") \
        .parquet("file:///output/path")
    
    # Clear memory
    spark.catalog.clearCache()

```


```commandline

Spark's Parallel File Processing Explained
Yes, but with important nuances. Let me clarify exactly how parallel processing works with your 100TB file in local mode:

The Parallel Processing Model
Partition Assignment:

Spark divides the file into logical ranges (not physical splits)

Each of your 8 partitions gets assigned a starting byte offset and length

Example for a 800MB file (simplified):

text
Partition 1: bytes 0-100MB
Partition 2: bytes 100-200MB
...
Partition 8: bytes 700-800MB
Parallel Execution:

All 8 partitions process their assigned ranges simultaneously

Each partition works independently on its portion

The Sequential Chunking Within Partitions
Here's the critical detail - each partition processes its range in chunks:

For Partition 1 (0-100MB):

Reads first 256MB chunk (bytes 0-256MB)

But only processes 16MB at a time within this chunk

Uses memory buffers to stream through the chunk

After finishing 256MB, moves to next chunk (256-512MB)

Memory Footprint:

At any moment:

Each partition has ~16MB actively in memory

8 partitions × 16MB = 128MB total active memory

Plus overhead for shuffle buffers/operations

Why This Works for 100TB
File Pointer Magic:

Spark uses file seek() operations to jump to each partition's start point

Each partition maintains its own file pointer

Parallel Streams:

text
Partition 1: [0-256MB] → [256-512MB] → ...
Partition 2: [100-356MB] → [356-612MB] → ...
...
Partition 8: [700-956MB] → [956-1212MB] → ...
All streams progress simultaneously

Local Mode Constraint:

All 8 streams share the same physical disk

Creates contention (why distributed mode is better for 100TB)

Visual Timeline
text
Time  Partition 1        Partition 2        ... Partition 8
-----------------------------------------------------------
T0    Read 0-16MB       Read 100-116MB     ... Read 700-716MB
T1    Process 0-16MB    Process 100-116MB  ... Process 700-716MB
T2    Read 16-32MB      Read 116-132MB     ... Read 716-732MB
T3    Process 16-32MB   Process 116-132MB  ... Process 716-732MB
...
Key Clarifications
Not Entire File at Once:

No partition loads the entire 100TB

No partition even loads its full logical range at once

Memory Efficiency:

The 256MB read size is an I/O optimization (sequential reads)

Only the current 16MB batch is actually in JVM memory

Progressive Processing:

Think of it like 8 people reading different sections of a giant book

Each reads one page (16MB) at a time, but knows where to find their next page
```



## key points:
1. Usually spark reads data in compressed format and de-compresses it. It becomes almost 10-15 x in size of the compressed data.


## Spark reading from various sources
### Amazon S3
Behavior:

Spark treats S3 similarly to HDFS but with different splitting behavior.

S3 files are not physically split (since it's object storage), but Spark creates logical partitions.
```commandline
spark.conf.set("spark.sql.files.maxPartitionBytes", "128MB")  # Default partition size
spark.conf.set("spark.hadoop.mapreduce.input.fileinputformat.split.minsize", "134217728")  # 128MB
```
Example:
- A 1GB Parquet file in S3 → 8 partitions (1GB / 128MB = 8). 
- Many small files → Spark may combine them (based on openCostInBytes).

Pros/Cons:
- ✔️ Good for large files 
- ❌ High latency for small files

### HDFS
Behavior:

Uses physical block splitting (default block size=128MB).

1 block = 1 partition by default.

Key Settings:

```commandline
spark.hadoop.dfs.blocksize = "256MB"  # Change HDFS block size

```
Example:
- 1GB file with 128MB blocks → 8 partitions. 
- 1GB file with 256MB blocks → 4 partitions.

Pros/Cons:
- ✔️ Optimal for large-scale data 
- ❌ Block size fixed at write time


### JSON/CSV
Behavior:

Splittable: Yes (but JSON lines/CSV must be newline-delimited).

Default read: Entire file = 1 partition (unless splittable).

Key Settings:
```commandline
spark.conf.set("spark.sql.files.maxPartitionBytes", "64MB")  # Force smaller partitions

```
Example:
- 1GB CSV → 16 partitions (if maxPartitionBytes=64MB). 
- - Non-splittable JSON → 1 partition per file.

Pros/Cons:
- ✔️ Simple to use
- ❌ Poor performance for large unsplittable files

### Parquet/ORC
Behavior:

Splittable: Yes (row groups are independent).

Default partition size: 128MB (configurable).

Key Settings:
```commandline
spark.conf.set("spark.sql.parquet.rowGroupSize", "16MB")  # Smaller row groups

```
Example:
- 1GB Parquet with 128MB partitions → 8 partitions. 
- Each partition reads 1+ row groups.

Pros/Cons:
- ✔️ Highly optimized for Spark 
- ❌ Requires tuning for best performance



### PostgreSQL (JDBC)
Behavior:

Not splittable by default → 1 partition.

Parallelism requires manual partitioning.

Key Settings:

```commandline
df = spark.read.format("jdbc") \
    .option("url", "jdbc:postgresql://host/db") \
    .option("dbtable", "table") \
    .option("partitionColumn", "id") \  # Column to split on
    .option("lowerBound", "1") \
    .option("upperBound", "1000000") \
    .option("numPartitions", "10") \  # 10 parallel reads
    .load()
```
Example:

Table with 1M rows, numPartitions=10 → 10 partitions (each reads ~100K rows).

Pros/Cons:
- ✔️ Parallel reads possible
- ❌ Requires numeric partition column



### Lets understand it with an example
example 1: Lets say that I am reading a 1TB file from S3, and I want to read it in parallel using Spark. I have 8VCPUs and 32GB RAM available.

```commandline
Given:

1TB file in S3

256MB partitions (spark.sql.files.maxPartitionBytes=256MB)

8 vCPUs → 8 concurrent tasks

No data skew (perfectly uniform distribution)

Executor memory: 28GB (after overhead)

Phase 1: Reading the File
1. Partition Creation
Total partitions: 1TB / 256MB = 4,096 partitions (tasks)  

Input per task:

256MB compressed (e.g., Parquet/ORC).

Deserializes to ~768MB–1.2GB in memory (3–5× expansion).

2. Task Execution
Concurrent tasks: 8 (1 per vCPU).

Memory per task:
Execution memory = 60% of 28GB = ~16.8GB  
Memory per task = 16.8GB / 8 = ~2.1GB  

Behavior per task:

Reads 256MB compressed → Expands to ~1GB in memory (fits in 2.1GB).

No spills (since 1GB < 2.1GB).


3. Progress
Batches to complete: 4,096 tasks / 8 concurrent = 512 batches  

Time estimate:

If each batch takes 5 seconds → ~43 minutes total.


Phase 2: Processing (e.g., Aggregations)
1. Shuffle Operations (if any)
Partitions for shuffles: Controlled by spark.default.parallelism (default = 8).

Memory per shuffle task: Same ~2.1GB.

2. No Spills (Ideal Case)
Since data is uniform and fits in memory:

No disk spills.

No OOMs.


Key Observations
Metric	Value	Implications
Partitions	4,096	High task overhead (scheduling lag)
Concurrent Tasks	8	Fully utilizes CPU
Memory/Partition	~2.1GB	Safe for 256MB input (1GB expanded)
Spills	None	Ideal if data fits in memory



Potential Bottlenecks
Too many small tasks (4,096):

High scheduling overhead (slow startup per task).

Fix: Increase maxPartitionBytes to 512MB–1GB (reduces tasks to 2,048–1,024).

If data expands beyond 2.1GB:

Spills occur → Increase maxPartitionBytes further (e.g., 2GB).


Summary
256MB partitions: Safe (no spills) but suboptimal due to high task count.

Recommended: Use 512MB–1GB partitions for better throughput.

Trade-off: Fewer tasks → Faster scheduling but slightly less granularity.


```


example 2: Reading 8M Records from PostgreSQL
```commandline
Given:

8 million records in a PostgreSQL table.

Partition column (e.g., user_id, date).

8 vCPUs, 32GB RAM (executor memory ~28GB after overhead).

No data skew (perfectly balanced partitions).

Phase 1: Data Read from PostgreSQL
1. Partitioning Strategy
Spark uses the partition column to split data into chunks:
df = spark.read.format("jdbc") \
    .option("url", "jdbc:postgresql://host/db") \
    .option("dbtable", "table") \
    .option("partitionColumn", "user_id") \  # Column to split on
    .option("lowerBound", "1") \             # Min value of partitionColumn
    .option("upperBound", "8000000") \       # Max value (8M records)
    .option("numPartitions", "8") \          # Match vCPUs
    .load()
    
    
    
2. Partition Distribution
8 partitions (1 per vCPU).

Each partition gets ~1M records (8M / 8).

Query per partition:
-- Partition 1 (user_id 1–1M):
SELECT * FROM table WHERE user_id >= 1 AND user_id < 1000001;

-- Partition 2 (user_id 1M–2M):
SELECT * FROM table WHERE user_id >= 1000001 AND user_id < 2000001;
-- ... and so on.



3. Memory Usage
Per-task memory: ~3.5GB (28GB / 8).

Data size in memory:

If each record = 1KB, 1M records = ~1GB (fits easily).

Deserialization overhead: ~2–3× → ~2–3GB per task (still safe).




Phase 2: Parallel Processing
1. Task Execution
8 tasks run concurrently (1 per vCPU).

Each task:

Fetches 1M records from PostgreSQL.

Loads into memory (~2–3GB after deserialization).

Processes data (e.g., filters, transforms).

2. Network/DB Bottlenecks
PostgreSQL max_connections: Ensure it allows ≥8 connections.

Fetch size: Optimize to reduce round trips: .option("fetchsize", "10000")  # 10K rows fetched per round trip



Phase 3: Shuffle (If Needed)
Example: Running df.groupBy("country").count().

Shuffle partitions: Default = 200 (adjust to match vCPUs):
spark.conf.set("spark.sql.shuffle.partitions", "8")

Memory pressure: Each of the 8 tasks handles ~1M records during aggregation.




Key Metrics to Monitor
Metric	Expected Value	Action if Abnormal
Tasks	8 (running concurrently)	Increase numPartitions if CPU underutilized.
PostgreSQL Load	8 parallel queries	Check DB CPU/network latency.
Spill to Disk	0	Increase numPartitions or reduce fetchsize.
Task Duration	Uniform (~1–2 mins)	Investigate skew if uneven.




Optimized configurations:
spark.conf.set("spark.executor.memory", "28G")       # 28GB RAM
spark.conf.set("spark.sql.shuffle.partitions", "8")  # Match vCPUs

df = spark.read.format("jdbc") \
    .option("url", "jdbc:postgresql://host/db") \
    .option("dbtable", "table") \
    .option("partitionColumn", "user_id") \
    .option("lowerBound", "1") \
    .option("upperBound", "8000000") \
    .option("numPartitions", "8") \          # Match vCPUs
    .option("fetchsize", "10000") \          # Batch size
    .load()
    
    
    
    
Common Pitfalls & Fixes
Skewed Partitions:

Symptom: 1 task takes much longer.

Fix: Use a better partition column (e.g., date instead of user_id).

OOM Errors:

Symptom: Tasks crash with OutOfMemoryError.

Fix: Reduce numPartitions (e.g., from 8 → 4) or increase executor memory.

Slow PostgreSQL Queries:

Fix: Add an index on partitionColumn.



Summary
8 partitions = 8 parallel queries → 1M records/task.

No spills if data fits in 3.5GB/task.

Critical: Match numPartitions to vCPUs and monitor PostgreSQL load.
```


Observation: 
```commandline
Key Difference: PostgreSQL (No fetchsize) vs. S3 File Reads
PostgreSQL (JDBC) Without fetchsize
Fetches the entire partition at once (e.g., 1M rows per query).

Risk: OOM (all 1M rows load into memory before processing).

Network: Large, monolithic transfers (slow).

Example:
SELECT * FROM table WHERE user_id BETWEEN 1 AND 1000000;



S3/File Reads (e.g., Parquet/CSV)
Processes files incrementally (even without fetchsize).

Safety: Splits data into 128MB–1GB chunks (per maxPartitionBytes).

Memory: Streams records row-by-row within each chunk.

Example:
spark.read.parquet("s3://path/to/file.parquet")  # 1GB file → 8x128MB partitions

Why the Difference?
Aspect	PostgreSQL (JDBC)	S3/HDFS/File-Based
Data Source	Query-based (SQL)	File-based (fixed-size blocks)
Default Behavior	Fetches all rows per query at once	Streams partitioned files incrementally
Memory Control	Requires fetchsize for batching	Built-in chunking (per maxPartitionBytes)
OOM Risk	High (no auto-batching)	Low (auto-partitioning)


How to Make PostgreSQL Safe (Like S3):
Set fetchsize to batch rows (similar to file partitioning):
.option("fetchsize", "10000")  # Fetches 10K rows at a time per partition


Now:

PostgreSQL: Behaves like S3 (incremental batches).

Memory: Each task holds only 10K rows (~10–50MB) at once.



Summary
No fetchsize in PostgreSQL → Full partition in memory (dangerous!).

S3/File reads → Always partitioned (safe by design).

Fix: Always set fetchsize for JDBC sources!

Need a real-world analogy? Think of:

PostgreSQL without fetchsize: Drinking from a firehose.

S3/File reads: Sipping through a straw (controlled chunks).
```


example 3: Reading postgreSQL table without partitionKey
```commandline
If you don’t specify a partition key (partitionColumn), Spark will:

Read the entire table in a single task (no parallelism).

Load all data into memory on one executor (high OOM risk).

Bottleneck performance (no distributed processing).


Step-by-Step Breakdown
1. Non-Partitioned Read (Default Behavior)


df = spark.read.format("jdbc") \
    .option("url", "jdbc:postgresql://host/db") \
    .option("dbtable", "table") \  # No partitionColumn!
    .load()



Single Query:
SELECT * FROM table;  -- Full table scan in PostgreSQL

Single Task:

Spark uses 1 executor core to fetch all 8M rows.

No parallelism → Slow!




2. Memory Impact
Scenario	Memory Usage	Risk Level
With Partition Key	~1M rows/task (8 tasks, ~1GB each)	Low
No Partition Key	8M rows in 1 task (~8GB+ memory)	OOM!
PostgreSQL: May freeze due to large result set.

Spark Driver/Executor: Likely crashes with OutOfMemoryError.

3. Performance Impact
Metric	With Partition Key	No Partition Key
Tasks	8 (parallel)	1 (sequential)
Network Transfer	8 streams (~1M rows each)	1 giant stream (8M rows)
Speed	Minutes	Hours (or fails)
```


# Shuffle partitions / `spark.sql.shuffle.partitions` — Complete Clear Explanation

---

## 📌 What Is It — One Clear Definition

```
spark.sql.shuffle.partitions = N
```

**This single number answers one question:**

> *"After a shuffle (join, groupBy, orderBy), into how many pieces should the data be split?"*

- **Default value = 200**
- It controls the number of **output partitions AFTER a shuffle operation**
- It does NOT affect how files are read (that's `maxPartitionBytes`)
- It does NOT affect non-shuffle operations like `filter`, `select`, `withColumn`

---

## 🔑 The Golden Rule — What Triggers This Parameter?

This parameter ONLY fires for **wide transformations** (operations that require a shuffle):

```
Operations that USE spark.sql.shuffle.partitions:
✅ JOIN          (SortMergeJoin, ShuffleHashJoin)
✅ groupBy()
✅ orderBy() / sort()
✅ distinct()
✅ repartition(N)  ← only if you don't specify N explicitly
✅ window functions

Operations that DO NOT use spark.sql.shuffle.partitions:
❌ filter()
❌ select()
❌ withColumn()
❌ map() / flatMap()
❌ BroadcastHashJoin  ← no shuffle at all
❌ spark.read.csv()   ← controlled by maxPartitionBytes
```

---

## 🖥️ Our Cluster Setup

```
Cluster:
├── 3 Executors
│     ├── Memory per executor = 4 GB
│     └── Cores per executor  = 4
│
├── Total cores  = 3 × 4 = 12 cores
├── Total memory = 3 × 4 = 12 GB
│
└── spark.sql.shuffle.partitions = 200 (default)
```

### What does 12 cores mean for parallelism?

```
12 cores = 12 tasks can run SIMULTANEOUSLY

One task = one partition being processed at one time

So at any point in time:
    - Up to 12 partitions are being processed in parallel
    - Remaining partitions wait in a queue
```

---

## 📦 Our Data Setup

```
Table A: orders       = 100 GB
Table B: customers    = 100 GB
Total data            = 200 GB

Query:
SELECT o.order_id, c.name, o.amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.amount > 500
```

---

## 🔵 STEP 1 — Reading the Files (Before shuffle.partitions matters)

```
Reading is controlled by spark.sql.files.maxPartitionBytes = 128 MB (default)

Table A: orders (100 GB)
    100 GB / 128 MB = ~800 partitions created at read time

Table B: customers (100 GB)
    100 GB / 128 MB = ~800 partitions created at read time

State right now:
    orders_rdd    → 800 partitions spread across 3 executors
    customers_rdd → 800 partitions spread across 3 executors
```

### How 800 partitions distribute across 3 executors?

```
Executor 1: partitions 1–267   (~33 GB of orders data)
Executor 2: partitions 268–534 (~33 GB of orders data)
Executor 3: partitions 535–800 (~34 GB of orders data)

Same distribution for customers table
```

### Parallelism during read (12 cores, 800 partitions):

```
Wave 1:  12 tasks run simultaneously → process 12 partitions
Wave 2:  12 tasks run simultaneously → process next 12 partitions
...
Wave 67: 12 tasks run → process partitions 793–800 (only 8 tasks active)
Total waves = ceil(800/12) ≈ 67 waves to read one table
```

---

## 🔵 STEP 2 — Filter Pushdown (Before Shuffle)

Catalyst Optimizer pushes `WHERE o.amount > 500` down to the scan:

```
BEFORE optimization:
    Read all 800 partitions of orders → then filter

AFTER optimization (predicate pushdown):
    Filter amount > 500 WHILE reading → fewer rows enter the join

Assume 60% of orders have amount > 500:
    800 partitions × 128 MB × 60% = ~61 GB of data after filter
    Still 800 partitions but each partition is now smaller (~76 MB average)
```

---

## 🔵 STEP 3 — THE SHUFFLE (Where spark.sql.shuffle.partitions = 200 kicks in)

This is the core of the explanation. A SortMergeJoin requires both sides to be
**hash-partitioned by the join key** (`customer_id`).

### Why shuffle is needed:

```
Current state (after read):
    Partition 1 of orders    → has customer_id: 101, 450, 8823, 234, ...  (random mix)
    Partition 2 of orders    → has customer_id: 55, 8823, 101, 9001, ...  (random mix)

The SAME customer_id (e.g., 8823) appears in MULTIPLE partitions
    → You cannot join locally
    → All rows with customer_id = 8823 MUST land on the SAME executor

Solution: Shuffle — redistribute data by join key
```

### How the shuffle works with shuffle.partitions = 200:

```
Spark assigns each customer_id to a "bucket" using:
    target_partition = hash(customer_id) % 200

Example:
    customer_id = 8823  → hash(8823) % 200 = 47  → goes to shuffle partition 47
    customer_id = 101   → hash(101)  % 200 = 101 → goes to shuffle partition 101
    customer_id = 234   → hash(234)  % 200 = 34  → goes to shuffle partition 34

This applies to BOTH tables:
    orders row    with customer_id=8823 → partition 47
    customers row with customer_id=8823 → partition 47

Guarantee: ALL rows with the same customer_id land in the SAME partition number
           on the SAME executor — ready to be joined locally
```

### Shuffle Write Phase (Stage 0 — all 800 read tasks do this):

```
Each of the 800 read tasks:
    Reads its 128 MB chunk
    Applies filter (amount > 500)
    For EACH row, computes: hash(customer_id) % 200
    Sorts rows by target partition number
    Writes 200 small "shuffle files" to LOCAL disk

Shuffle files created:
    800 tasks × 200 buckets = 160,000 shuffle files per table
    2 tables = 320,000 shuffle files total on local disks

Each shuffle file is tiny:
    orders: 61 GB / 160,000 files ≈ 0.38 MB per shuffle file
```

---

## 🔵 STEP 4 — Shuffle Read (Stage 1 begins — 200 tasks start)

```
spark.sql.shuffle.partitions = 200 means 200 tasks in Stage 1

Each task is responsible for ONE shuffle partition (bucket number):
    Task 47  → fetches ALL shuffle files labeled "bucket 47" from ALL 800 read tasks
    Task 101 → fetches ALL shuffle files labeled "bucket 101" from ALL 800 read tasks
    ...

Task 47 fetches from orders side:
    800 write tasks × (61 GB / 200 buckets) ÷ 800 = ~305 MB of orders data
    (all rows where hash(customer_id) % 200 = 47)

Task 47 fetches from customers side:
    ~500 MB of customers data (no filter applied to customers)
    (100 GB / 200 buckets = 500 MB per bucket per side)

Task 47 now has:
    All order rows   with customer_id mapping to bucket 47: ~305 MB
    All customer rows with customer_id mapping to bucket 47: ~500 MB
    → Performs local SortMergeJoin → only rows with matching customer_id are joined
```

---

## 🔵 STEP 5 — The 200 Tasks Running on 12 Cores

```
200 shuffle partitions ÷ 12 cores = ~17 waves of execution

Wave 1:  Tasks 1–12   run simultaneously on 12 cores
Wave 2:  Tasks 13–24  run simultaneously on 12 cores
Wave 3:  Tasks 25–36  run simultaneously on 12 cores
...
Wave 17: Tasks 193–200 run (only 8 tasks, 4 cores idle)

Each task processes:
    orders side:    ~305 MB
    customers side: ~500 MB
    Total per task: ~805 MB

Memory check per task:
    Each executor has 4 GB, running 4 tasks simultaneously
    Available memory per task = 4 GB / 4 tasks ≈ 1 GB per task

    SortMergeJoin needs to sort both sides:
    ~805 MB of data, ~1 GB available → tight but workable
    If it doesn't fit → Spark spills to disk (slower but no failure)
```

---

## 🔵 STEP 6 — What Happens After the Join

```
After 200 tasks complete the join:
    Result has 200 partitions
    Each partition has joined rows where amount > 500

If you do nothing:
    result.write.parquet("output/") → writes 200 parquet files

If you then do groupBy or orderBy:
    Another shuffle fires → uses spark.sql.shuffle.partitions = 200 again
    200 tasks process the 200 join-result partitions → still 200 output partitions
```

---

## ❌ PROBLEM: What if shuffle.partitions = 200 is Wrong for Our Cluster?

### Scenario A: shuffle.partitions = 200 (default) — Is it right?

```
Total shuffle data (both sides combined per partition):
    orders per partition:    61 GB / 200  = ~305 MB
    customers per partition: 100 GB / 200 = ~500 MB
    Total per task:          ~805 MB

Memory available per task:
    Executor memory = 4 GB
    Spark reserves ~40% for overhead/storage → usable = ~2.4 GB for execution
    4 cores per executor → memory per task = 2.4 GB / 4 = ~600 MB

805 MB needed vs 600 MB available → SPILL TO DISK likely
Still works, just slower. 200 is borderline for this cluster.
```

### Scenario B: shuffle.partitions = 50 (too few)

```
Data per partition:
    orders:    61 GB / 50  = ~1.2 GB per partition
    customers: 100 GB / 50 = ~2.0 GB per partition
    Total:     ~3.2 GB per task

Memory available per task: ~600 MB
3.2 GB needed vs 600 MB available → MASSIVE SPILL or OOM crash

Also:
    50 partitions ÷ 12 cores = ~5 waves only
    Cluster is underutilized — many cores idle at wave 5 (only 2 tasks left)
```

### Scenario C: shuffle.partitions = 2000 (too many)

```
Data per partition:
    orders:    61 GB / 2000  = ~30 MB per partition
    customers: 100 GB / 2000 = ~50 MB per partition
    Total:     ~80 MB per task

Memory available per task: ~600 MB
80 MB needed → fits EASILY in memory ✅

BUT:
    2000 partitions ÷ 12 cores = ~167 waves
    Task scheduling overhead for tiny 80 MB tasks → inefficient
    Too many tiny output files (2000 parquet files) → small file problem

The overhead of managing 2000 tasks > benefit of smaller task size
```

### Scenario D: shuffle.partitions = 400 (sweet spot for our cluster) ✅

```
Data per partition:
    orders:    61 GB / 400  = ~152 MB
    customers: 100 GB / 400 = ~250 MB
    Total:     ~402 MB per task

Memory available per task: ~600 MB
402 MB < 600 MB → fits in memory, NO SPILL ✅

Waves:
    400 partitions ÷ 12 cores = ~34 waves
    Good parallelism, reasonable wave count ✅

Output:
    400 parquet files → manageable ✅

This is the sweet spot for our 3-executor × 4-core × 4GB cluster
```

---

## 🧮 The Formula — How to Calculate the Right Value

```
Step 1: Estimate total shuffle data size
    = largest_table × 2 (both sides of join need to fit)
    = 100 GB customers (larger, no filter) + 61 GB orders (after filter)
    = 161 GB total shuffle data

Step 2: Determine target partition size
    Sweet spot: 100 MB – 200 MB per partition
    (fits in memory without spilling, not too tiny for overhead)
    Use: 150 MB as target

Step 3: Calculate partitions
    shuffle.partitions = total_shuffle_data / target_partition_size
                       = 161,000 MB / 150 MB
                       = ~1073

    But each partition processes data from BOTH tables separately:
    orders per partition:    61,000 MB / N
    customers per partition: 100,000 MB / N
    Memory needed per task:  161,000 MB / N

    For memory to fit:
    161,000 MB / N < available_memory_per_task (600 MB)
    N > 161,000 / 600
    N > ~268

    Round up to nearest power of 2 or clean number: N = 300 or 400

Step 4: Verify parallelism
    N / total_cores = 400 / 12 = 33 waves → good ✅

Step 5: Final answer
    spark.sql.shuffle.partitions = 400 for this specific job
```

---

## ⚡ AQE — Adaptive Query Execution (Spark 3.0+)

With AQE enabled (`spark.sql.adaptive.enabled = true`, default in Spark 3.2+),
Spark automatically tunes `shuffle.partitions` at runtime:

```
spark.sql.shuffle.partitions = 200  ← you set this as the MAXIMUM

At runtime, after Stage 0 completes:
    AQE measures actual shuffle data sizes:
    "Bucket 47 only has 2 MB of data... bucket 101 has 450 MB..."

AQE then:
    Coalesces tiny partitions together → fewer, larger tasks
    Keeps large partitions as-is

Example:
    You set shuffle.partitions = 200
    AQE sees only 161 GB total, partitions are uneven
    AQE coalesces 200 → 120 effective partitions (merging tiny ones)
    Result: no tiny tasks, no wasted scheduling overhead

Config:
    spark.sql.adaptive.enabled                        = true
    spark.sql.adaptive.coalescePartitions.enabled     = true
    spark.sql.adaptive.advisoryPartitionSizeInBytes   = 128MB  ← target size per partition
    spark.sql.adaptive.coalescePartitions.minPartitionNum = 1
```

### AQE skew handling:

```
Without AQE:
    customer_id = 1 (a mega-popular customer) → 30 GB in one partition
    → Task for that partition: needs 30 GB memory → OOM

With AQE (skew join optimization):
    spark.sql.adaptive.skewJoin.enabled = true
    AQE detects partition is 30 GB (>> median of 300 MB)
    Automatically SPLITS partition into sub-tasks:
    30 GB → 100 sub-tasks of 300 MB each → runs fine
```

---

## 📊 Full Visual — Our 100GB × 100GB Join End-to-End

```
CLUSTER: 3 executors × 4 cores × 4 GB
════════════════════════════════════════════════════════════════════════

STAGE 0 — READ + FILTER (800 tasks, 12 at a time)
────────────────────────────────────────────────────────────────────────
┌─────────────────────────────────────────────────────────────────────┐
│  HDFS/S3                                                            │
│  orders.parquet    [100 GB] → 800 partitions (128MB each)           │
│  customers.parquet [100 GB] → 800 partitions (128MB each)           │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ read 12 partitions at a time
                            ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Executor 1  │  │  Executor 2  │  │  Executor 3  │
│  4 tasks     │  │  4 tasks     │  │  4 tasks     │
│  reading     │  │  reading     │  │  reading     │
│  + filter    │  │  + filter    │  │  + filter    │
│  amount>500  │  │  amount>500  │  │  amount>500  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │  each task writes 200 shuffle files to local disk
       │  (one file per shuffle partition bucket)
       ▼                 ▼                 ▼
  local disk         local disk         local disk
  267×200 files      267×200 files      266×200 files
  = 53,400 files     = 53,400 files     = 53,200 files

Total shuffle files: ~160,000 (orders) + ~160,000 (customers) = 320,000 files

────────────────────────────────────────────────────────────────────────
SHUFFLE — DATA REDISTRIBUTION BY customer_id
────────────────────────────────────────────────────────────────────────

hash(customer_id) % 200 determines which executor gets each row

customer_id=8823 from partition 1   (Executor 1 disk) ──┐
customer_id=8823 from partition 45  (Executor 1 disk) ──┤
customer_id=8823 from partition 267 (Executor 2 disk) ──┼──→ Executor 2, Task 47
customer_id=8823 from partition 400 (Executor 2 disk) ──┤    (all 8823 rows together)
customer_id=8823 from partition 600 (Executor 3 disk) ──┤
customer_id=8823 from partition 799 (Executor 3 disk) ──┘

────────────────────────────────────────────────────────────────────────
STAGE 1 — SHUFFLE READ + JOIN + AGG (200 tasks, 12 at a time)
────────────────────────────────────────────────────────────────────────
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Executor 1  │  │  Executor 2  │  │  Executor 3  │
│  Tasks       │  │  Tasks       │  │  Tasks       │
│  1,2,3,4     │  │  5,6,7,8     │  │  9,10,11,12  │
│              │  │              │  │              │
│ Each task:   │  │ Each task:   │  │ Each task:   │
│ - Fetch ~305 │  │ - Fetch ~305 │  │ - Fetch ~305 │
│   MB orders  │  │   MB orders  │  │   MB orders  │
│ - Fetch ~500 │  │ - Fetch ~500 │  │ - Fetch ~500 │
│   MB cust    │  │   MB cust    │  │   MB cust    │
│ - Sort both  │  │ - Sort both  │  │ - Sort both  │
│ - Merge join │  │ - Merge join │  │ - Merge join │
│ - Output     │  │ - Output     │  │ - Output     │
│   joined rows│  │   joined rows│  │   joined rows│
└──────────────┘  └──────────────┘  └──────────────┘

200 tasks ÷ 12 cores = ~17 waves of execution

════════════════════════════════════════════════════════════════════════
FINAL OUTPUT: 200 partitions of joined results
```

---

## 🧠 Summary — Everything You Need to Know

### What `spark.sql.shuffle.partitions` controls:

```
BEFORE shuffle:  data is in N partitions (could be 800 from file read)
                 ↓  shuffle happens (join / groupBy / orderBy)
AFTER shuffle:   data is in spark.sql.shuffle.partitions partitions (200 by default)
```

### The 3-way tradeoff:

```
Too LOW (e.g., 50):
    ❌ Each partition too large → OOM / excessive spill to disk
    ❌ Less parallelism → some cores idle
    ❌ Skew impact is worse (one big partition = one slow task = whole stage waits)

Too HIGH (e.g., 2000):
    ❌ Too many tiny partitions → task scheduling overhead
    ❌ Thousands of tiny output files → downstream read is slow (small file problem)
    ❌ More shuffle files to manage = more metadata overhead

Just Right (e.g., 400 for our cluster):
    ✅ Each partition fits comfortably in memory (~400 MB)
    ✅ Good parallelism (33 waves for 12 cores)
    ✅ Reasonable output file count
    ✅ Minimal spill
```

### Quick sizing formula:

```
shuffle.partitions = max(
    total_shuffle_data_MB / target_partition_size_MB,   ← memory constraint
    total_cores × 2                                      ← parallelism constraint
)

For our example:
    = max(161,000 / 150,  12 × 2)
    = max(1073, 24)
    = 1073  ← but each task sees only ONE side at a time
    
    Revised (each task sees both sides summed, not divided):
    = 161,000 / 600  (available memory per task)
    = ~268 → round to 300 or 400

With AQE enabled: set to 1000, let AQE coalesce down automatically ✅
```

### The one-line rule:

```
spark.sql.shuffle.partitions = (total shuffle data) / (memory per task)

where memory per task = executor_memory × 0.6 / cores_per_executor
```

| Cluster Size | Shuffle Data | Recommended Value |
|---|---|---|
| Small (2 exec × 2 core × 2GB) | < 10 GB | 10–50 |
| Medium (3 exec × 4 core × 4GB) | 50–200 GB | 200–500 |
| Large (10 exec × 8 core × 16GB) | 500 GB–2 TB | 500–2000 |
| With AQE (Spark 3.2+) | Any | Set high (1000+), let AQE tune |


## # Where Are Shuffle Intermediate Files Stored? — Step by Step

---

## Our Setup (Quick Reminder)
```
3 Executors × 4 cores × 4 GB
Join: 100 GB orders + 100 GB customers = 200 GB total
Available memory per task = ~600 MB
Total shuffle data = ~161 GB  ← WAY bigger than 12 GB total cluster memory
```

---

## The Core Answer

```
Shuffle intermediate files go to:
    LOCAL DISK of each executor (not memory, not HDFS, not S3)

Specifically:
    spark.local.dir = /tmp/spark-xxx/  (default)
    (configurable — should always point to fast SSD in production)
```

---

## Step-by-Step: What Happens to the 161 GB

### Step 1 — Each Task Reads Its Partition Into Memory (128 MB chunk)

```
Task on Executor 1:
    Reads 128 MB partition of orders into executor memory ✅
    Applies filter (amount > 500) → maybe 76 MB remains in memory
    Computes hash(customer_id) % 200 for each row → groups into 200 buckets
```

### Step 2 — Shuffle Write: Buckets Written to LOCAL DISK Immediately

```
Task does NOT hold all 200 buckets in memory at once.

It writes each bucket to local disk as it fills up:

Executor 1 — local disk (/tmp/spark-local/):
    shuffle_0_0_0.data   → bucket 0   (~0.38 MB)
    shuffle_0_0_1.data   → bucket 1   (~0.38 MB)
    shuffle_0_0_2.data   → bucket 2   (~0.38 MB)
    ...
    shuffle_0_0_199.data → bucket 199 (~0.38 MB)

Memory used during write: only ONE bucket in memory at a time → tiny
Memory freed: partition buffer released after write completes
```

### Step 3 — All 800 Tasks Write Their Shuffle Files

```
800 tasks × 200 buckets = 160,000 files per table
2 tables = 320,000 shuffle files total

Stored on LOCAL DISK across 3 executors:
    Executor 1 local disk: ~107,000 files (~54 GB)
    Executor 2 local disk: ~107,000 files (~54 GB)
    Executor 3 local disk: ~106,000 files (~53 GB)

Total on disk: ~161 GB spread across local disks
```

### Step 4 — Shuffle Read: Fetch Over Network Into Memory

```
Stage 1 starts — 200 tasks begin

Task 47 (running on Executor 2) needs bucket 47 from ALL 800 write tasks:

    Executor 2 fetches from:
        Executor 1 local disk → shuffle_*_*_47.data  (network transfer)
        Executor 2 local disk → shuffle_*_*_47.data  (local read)
        Executor 3 local disk → shuffle_*_*_47.data  (network transfer)

    All fetched data for bucket 47:
        orders side:    ~305 MB
        customers side: ~500 MB
        Total:          ~805 MB

    Available memory per task: ~600 MB

    805 MB > 600 MB → SPILL happens (see Step 5)
```

### Step 5 — Spill: When Memory Is Not Enough

```
Task 47 is trying to sort 805 MB with only 600 MB:

    Step A: Fill memory buffer up to 600 MB
    Step B: Sort what's in memory
    Step C: Write sorted chunk to LOCAL DISK as a "spill file"
            → /tmp/spark-local/spill_task47_spill1.data
    Step D: Free memory buffer
    Step E: Read next chunk into memory → sort → spill again
    Step F: Repeat until all 805 MB processed

    Spill files on local disk:
        /tmp/spark-local/spill_task47_spill1.data  (~600 MB)
        /tmp/spark-local/spill_task47_spill2.data  (~205 MB)

    Step G: Final merge pass — read all spill files, merge-sort them
            → produce final sorted output for the join
```

---

## Complete Storage Flow — Visual

```
S3 / HDFS (source)
    │
    │  read 128 MB at a time
    ▼
EXECUTOR MEMORY (128 MB partition)
    │
    │  filter + hash by join key
    │  write bucket files immediately
    ▼
EXECUTOR LOCAL DISK (/tmp/spark-local/)   ← shuffle files live here
    │
    │  Stage 1 tasks fetch over network
    ▼
EXECUTOR MEMORY (fetch + sort for join)
    │
    │  if data > available memory
    ▼
EXECUTOR LOCAL DISK (/tmp/spark-local/)   ← spill files live here
    │
    │  merge spill files → final join result
    ▼
EXECUTOR MEMORY (joined output rows)
    │
    │  write final result
    ▼
S3 / HDFS (output)
```

---

## Key Points

```
✅ Shuffle files   → always on LOCAL DISK of executor (not HDFS, not S3)
✅ Spill files     → also on LOCAL DISK of same executor
✅ Memory          → only holds ONE partition chunk at a time (not 161 GB!)
✅ Network         → used only during shuffle READ (Stage 1 fetching from Stage 0)

⚠️  If local disk fills up  → DiskSpaceException → task fails → job fails
⚠️  If executor crashes     → its shuffle files are LOST
                             → Spark must re-run the parent stage to regenerate them

Production config:
    spark.local.dir = /fast-ssd/spark-temp   ← always use SSD, not HDD
    (multiple dirs for multiple disks = more I/O bandwidth)
    spark.local.dir = /ssd1/spark,/ssd2/spark,/ssd3/spark
```

---

## Why It Works Despite 161 GB > 12 GB Cluster Memory

```
Because Spark NEVER loads 161 GB into memory at once.

At any moment, one task holds:
    - 1 input partition in memory  = 128 MB
    - 1 shuffle fetch buffer       = ~200-400 MB
    - 1 sort buffer                = remainder of task memory

Everything else sits on LOCAL DISK, waiting its turn.

This is exactly why local disk speed is critical for shuffle-heavy jobs.
Slow disk = slow shuffle = slow job.
```

