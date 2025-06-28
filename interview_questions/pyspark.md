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
### where does the .cache() resides, On driver or each node?
### what is there is no enough space to cache the data then what will happen?


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


## what is partitioning in Spark?
## what is partition / shuffle partition
## How to optimize Spark jobs?


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




# Spark in standalone mode
# spark in cluster mode such as EMR
# Spark executor and driver memory

# Spark Architecture (master, driver, slave)




