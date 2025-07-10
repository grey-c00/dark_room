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

# what is master and driver are sitting on same instance?

# Spark UI

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