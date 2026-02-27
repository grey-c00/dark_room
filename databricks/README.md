## Introduction

Databricks is a unified analytics and data engineering platform built on top of Apache Spark. It was designed to simplify working with big data, machine learning, and data pipelines — all in one place.

- It’s a cloud-based platform (available on Azure, AWS, and GCP) for data engineering, data science, and machine learning.
- It provides a collaborative workspace with notebooks (like Jupyter), integrated with Spark clusters.
- It allows users to ingest, transform, and analyze data at scale using languages like Python, SQL, Scala, R, and Java.

Why It Exists / Why It’s Useful:

- Abstracts Spark’s complexity: You don’t need to manage Spark clusters manually — Databricks automates cluster creation, scaling, and tuning.
- End-to-end workflows: You can build data pipelines, perform analytics, train ML models, and deploy them — all within one platform.
- Collaboration: Data engineers, analysts, and scientists can share code and outputs in shared notebooks.
- Optimized performance: Databricks runtime is a customized, faster version of Spark with optimizations like Photon (a vectorized query engine in C++).
- Supports Delta Lake: This provides ACID transactions, schema enforcement, and time travel for data lakes — turning a data lake into a Lakehouse.


Key Components:

| Component          | Description                                                                   |
| ------------------ | ----------------------------------------------------------------------------- |
| **Workspace**      | The web-based environment where users create notebooks, dashboards, and jobs. |
| **Cluster**        | A group of virtual machines that execute Spark jobs.                          |
| **Notebook**       | Interactive environment for code, visualizations, and documentation.          |
| **Jobs**           | Automated, scheduled runs of notebooks or workflows.                          |
| **Delta Lake**     | Storage layer that adds reliability and consistency to data lakes.            |
| **Databricks SQL** | For interactive SQL queries and dashboards.                                   |


Typical Use Cases

- ETL pipelines (extract-transform-load)
- Machine learning model training
- Real-time streaming analytics
- BI dashboards with Databricks SQL
- Data lakehouse architecture implementation


At its core, Databricks sits between your cloud storage (like S3, ADLS, GCS) and your compute (Spark clusters).

General flow:

```markdown
+-------------------+
|   User Interface  |  (Web UI, API, CLI)
+-------------------+
          |
          v
+-------------------+
|   Workspace Layer |  (Notebooks, Repos, Jobs)
+-------------------+
          |
          v
+---------------------------+
|  Control Plane (Managed)  |  (Cluster orchestration, security, job scheduling)
+---------------------------+
          |
          v
+---------------------------+
|  Data Plane (Customer)    |  (Spark clusters process data from storage)
+---------------------------+
          |
          v
+-------------------+
|   Cloud Storage   |  (S3 / ADLS / GCS)
+-------------------+

```


Databricks dynamically manages clusters using the Databricks Cluster Manager:

- You define the node types, autoscaling policy, and runtime version.
- When a job starts, Databricks provisions VMs (workers + driver) using the cloud provider’s API.
- Autoscaling adjusts the number of workers based on load.
- Runtime environments (Databricks Runtime) include:
    - Optimized Apache Spark
    - Preinstalled libraries (pandas, numpy, scikit-learn, etc.)
    - Photon Engine (for accelerated SQL execution in C++)

📌 The runtime is what gives Databricks its speed advantage — it’s tuned at the JVM, Spark, and I/O levels.


Databricks’ real magic comes from Delta Lake, which brings database-like reliability to data lakes.
🔹 Delta Lake adds:

| Feature                | Description                                                            |
| ---------------------- | ---------------------------------------------------------------------- |
| **ACID Transactions**  | Ensures consistent reads/writes using transaction logs (`_delta_log`). |
| **Schema Enforcement** | Prevents writing invalid data.                                         |
| **Time Travel**        | Query previous table versions.                                         |
| **Upserts / Deletes**  | You can use SQL `MERGE` statements.                                    |
| **Compaction**         | Merges small parquet files into optimized ones for faster reads.       |


How it works:
- Every operation on a Delta table writes to _delta_log (JSON files).
- When you query the table, Databricks reads the latest snapshot by combining Parquet data files + transaction log.
- Optimizations like Z-Ordering and Data Skipping help prune unnecessary files during scans.


Performance Optimizations: Databricks employs several internal techniques:
- Photon Engine → Vectorized C++ query engine for SQL workloads.
- Cache Layer → Automatic caching of hot data in memory or local SSDs.
- Query Optimizer → Catalyst optimizer (from Spark) + Databricks extensions.
- Auto-Compaction → Merges small Delta files automatically.
- Adaptive Query Execution (AQE) → Dynamically adjusts joins and shuffles at runtime.


Storage is Always in Your Cloud Account:
When you create a Databricks workspace on:

- AWS → you connect it to S3 buckets
- Azure → you connect it to Azure Data Lake Storage (ADLS Gen2)
- GCP → you connect it to Google Cloud Storage (GCS)

Your data, tables, and files are stored there permanently, not inside Databricks.

Databricks just reads and writes from that storage using Spark I/O.

There are only a few temporary or metadata-related places where Databricks uses internal storage:


## How databrics is different from snowflake

Core Purpose:
- Databricks is a Data + AI platform designed for data engineering, data science, and machine learning.
- Snowflake is a cloud data warehouse built mainly for SQL analytics and business intelligence.

Databricks was born from Apache Spark (open-source compute engine), while Snowflake was built from scratch for analytical SQL queries.


Architecture:

| Component     | Databricks                                           | Snowflake                               |
| ------------- | ---------------------------------------------------- | --------------------------------------- |
| **Storage**   | Uses your own cloud storage (S3, ADLS, GCS)          | Uses Snowflake-managed internal storage |
| **Compute**   | Managed Spark clusters you control                   | Fully managed virtual warehouses        |
| **Format**    | Open format – Delta Lake (Parquet + transaction log) | Proprietary columnar format             |
| **Ownership** | You own your data                                    | Snowflake owns and manages storage      |


Performance & Optimization:

Databricks: Optimized Spark engine + Photon (C++ vectorized SQL), Delta Lake for ACID transactions and time travel.

Snowflake: Fully managed optimizer, automatic caching, and transparent scaling for predictable SQL performance.

Rule of thumb:
→ Databricks = best for large-scale data processing + ML
→ Snowflake = best for ad-hoc SQL analytics and BI

## How performant


## what all feature

## how does it store data


## is it noSQL or RDBMs

## what is azure databricks



## tech behind it?

## how can i use it in Python