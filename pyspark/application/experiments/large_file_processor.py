from shlex import join
from pyspark.sql import SparkSession

import os
import time
import numpy as np
import pandas as pd


def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        return result
    return wrapper

@time_it
def experiment_csv():
    spark = (
        SparkSession.builder
        .appName("spark experiment")
        .master("local[16]")       # 4 threads
        .config("spark.executor.memory", "512m")  # limit memory to 256 MB
        .config("spark.sql.files.maxPartitionBytes", 1 * 1024*1024*512)  # 10 MB
        .getOrCreate()
    )

    csv_file_path = "/Users/himanshu.choudhary/work/clinical/mvp_1/cdi-python-ds/test_20gb.csv"

    df = spark.read.csv(csv_file_path, header=True, inferSchema=True)

    # print(df.count())


    # df = df.groupBy("first_name").count()

    # print(df.count())
    # print(df.show(100))
    # print(df.count())

    # print(df.columns)

    # print("Done experiment_csv")

    # print(df.show(10))
    print(df.count())

@time_it
def experiment_csv_2():
    spark = (
        SparkSession.builder
        .appName("spark experiment")
        .master("local[16]")       # 4 threads
        .config("spark.sql.files.maxPartitionBytes", 1 * 1024*1024*512)  # 10 MB
        .getOrCreate()
    )
    csv_file_path = "/Users/himanshu.choudhary/work/clinical/mvp_1/cdi-python-ds/test_20gb.csv"
    line_cnt = 0
    with open(csv_file_path, "r") as file:
        for line in file:
            line_cnt += 1
            if line_cnt % 10000000 == 0:
                print(f"Processed {line_cnt} lines")
    print(f"Total lines: {line_cnt}")

    print("Done experiment_csv_2")

@time_it
def experiment_text():
    # spark = (
    #     SparkSession.builder
    #     .appName("spark experiment")
    #     .master("local[16]")       # 4 threads
    #     .config("spark.sql.files.maxPartitionBytes", 1 * 1024*1024*10)  # 10 MB
    #     .getOrCreate()
    # )
    text_file_path = "/Users/himanshu.choudhary/work/clinical/mvp_1/cdi-python-ds/test_100mb.txt"
    df = spark.read.text(text_file_path)
    
    # print(df.show(10))

    print(df.count())

    print("Done experiment_text")


def experiment_csv_3():
    spark = (
        SparkSession.builder
        .appName("spark experiment")
        .master("local[4]")       # 4 threads
        .config("spark.executor.memory", "1g")
        .config("spark.sql.files.maxPartitionBytes", 1 * 1024*1024*512)  # 10 MB
        .getOrCreate()
    )
    csv_file_path = "/Users/himanshu.choudhary/work/clinical/mvp1/pyspark/files/csv/test_20gb.csv"
    df = spark.read.csv(csv_file_path, header=True, inferSchema=True)

    ids_path = "/Users/himanshu.choudhary/work/clinical/mvp1/pyspark/files/csv/ids_of_20gb.csv"
    id_df = spark.read.csv(ids_path, header=True, inferSchema=True)

    joined_df = df.join(id_df, df.id == id_df.id, "left")

    # joined_df.write.csv("/Users/himanshu.choudhary/work/clinical/mvp1/pyspark/files/csv/joined_20gb.csv", header=True)
    print(joined_df.explain("formatted"))

    joined_df.write.csv("/Users/himanshu.choudhary/work/clinical/mvp1/pyspark/files/csv/joined_20gb_v4", header=True)

@time_it
def experiment_python_3():
    csv_file_path = "/Users/himanshu.choudhary/work/clinical/mvp1/pyspark/files/csv/test_20gb.csv"
    ids_path = "/Users/himanshu.choudhary/work/clinical/mvp1/pyspark/files/csv/ids_of_20gb.csv"
    output_dir = "/Users/himanshu.choudhary/work/clinical/mvp1/pyspark/files/csv/joined_20gb_python_v2"

    os.makedirs(output_dir, exist_ok=True)

    # Read the small IDs dataframe fully into memory
    id_df = pd.read_csv(ids_path)

    chunk_size = 500_000
    chunk_num = 0
    total_rows = 0

    for chunk in pd.read_csv(csv_file_path, chunksize=chunk_size):
        # Left join the chunk with the IDs dataframe on the 'id' column
        joined_chunk = chunk.merge(id_df, on="id", how="left")

        # Write each joined chunk to a separate part file
        output_path = os.path.join(output_dir, f"part-{chunk_num:05d}.csv")
        joined_chunk.to_csv(output_path, index=False, header=True)

        total_rows += len(joined_chunk)
        chunk_num += 1

        if chunk_num % 10 == 0:
            print(f"Processed {chunk_num} chunks, {total_rows:,} rows so far")

    print(f"Done. Total chunks: {chunk_num}, Total rows: {total_rows:,}")
    print(f"Output written to: {output_dir}")


@time_it
def generate_skewed_dataset():
    """
    Generates a ~5GB single skewed CSV file to study skewness & shuffling in PySpark.
    Department is heavily skewed (Engineering=70%), Region is moderately skewed (US-West=55%).
    """
    output_path = "/Users/himanshu.choudhary/work/clinical/mvp1/pyspark/files/skewed_dataset/skewed_data.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    total_rows = 25_000_000  # ~5GB at ~200 bytes/row
    chunk_size = 500_000

    departments = ["Engineering", "Sales", "HR", "Marketing", "Legal", "Finance"]
    dept_weights = [0.70, 0.15, 0.05, 0.05, 0.03, 0.02]

    regions = ["US-West", "US-East", "Europe", "Asia", "Africa"]
    region_weights = [0.55, 0.20, 0.12, 0.08, 0.05]

    rng = np.random.default_rng(seed=42)
    rows_written = 0
    chunk_num = 0
    write_header = True

    print(f"Generating {total_rows:,} rows (~5GB) → {output_path}")

    with open(output_path, "w") as f:
        while rows_written < total_rows:
            current_chunk = min(chunk_size, total_rows - rows_written)

            dept_col = rng.choice(departments, size=current_chunk, p=dept_weights)
            region_col = rng.choice(regions, size=current_chunk, p=region_weights)

            chunk_df = pd.DataFrame({
                "id":            np.arange(rows_written + 1, rows_written + current_chunk + 1),
                "department":    dept_col,
                "region":        region_col,
                "employee_name": [f"emp_{i}" for i in range(rows_written + 1, rows_written + current_chunk + 1)],
                "salary":        rng.integers(40_000, 250_000, size=current_chunk),
                "bonus":         rng.integers(0, 50_000, size=current_chunk),
                "years_exp":     rng.integers(0, 35, size=current_chunk),
                "performance":   rng.uniform(1.0, 5.0, size=current_chunk).round(2),
                "transactions":  rng.integers(1, 10_000, size=current_chunk),
            })

            chunk_df.to_csv(f, index=False, header=write_header)
            write_header = False

            rows_written += current_chunk
            chunk_num += 1
            if chunk_num % 5 == 0:
                print(f"  {rows_written:>12,} / {total_rows:,} rows written")

    print(f"Done. Total rows: {rows_written:,} → {output_path}")


def experiement():
    # experiment_csv()
    # experiment_csv_2()
    # experiment_csv_3()
    # experiment_text()
    # experiment_python_3()
    generate_skewed_dataset()


if __name__ == "__main__":
    experiement()
    time.sleep(1000000)


""""
questions:
0. PySpark shuffeling
1. PySpark in standalone mode
2. File reading in PySpark from S3, data flow
1. A, AB, ABC, ABCD index answer
2. Streak in SQL
3. Multithreading in Python
4. Multithreading vs Multiprocessing


skewness - 

cache - 

AQI in pyspark


SQL - 
    Partition by
    Window function
        Aggregates
                SUM()
                AVG()
                COUNT()
                MIN()
                MAX()
                Ranking
                ROW_NUMBER()
                RANK()
                DENSE_RANK()
                Value Functions
                LAG() – previous row value
                LEAD() – next row value
    Lead 
    Lag
    Date functions
        DATEADD
        DATEDIFF

    Offset addition


    UNBOUNDED PRECEDING
"""


"""
Data type in SQL - 
    datatype size description
    | Data Type                  | Size / Storage                | Notes                                                   |
| -------------------------- | ----------------------------- | ------------------------------------------------------- |
| **TINYINT**                | 1 byte                        | -128 to 127 (signed), 0–255 (unsigned)                  |
| **SMALLINT**               | 2 bytes                       | -32,768 to 32,767                                       |
| **MEDIUMINT**              | 3 bytes (MySQL only)          | -8,388,608 to 8,388,607                                 |
| **INT / INTEGER**          | 4 bytes                       | -2,147,483,648 to 2,147,483,647                         |
| **BIGINT**                 | 8 bytes                       | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 |
| **DECIMAL / NUMERIC(p,s)** | Varies (depends on precision) | Exact fixed-point numbers; storage depends on digits    |
| **FLOAT / REAL**           | 4 bytes                       | Approximate single-precision floating-point             |
| **DOUBLE / FLOAT8**        | 8 bytes                       | Approximate double-precision floating-point             |


| Data Type                                   | Size / Storage            | Notes                                                       |
| ------------------------------------------- | ------------------------- | ----------------------------------------------------------- |
| **CHAR(n)**                                 | n bytes                   | Fixed-length; pads with spaces if shorter                   |
| **VARCHAR(n)**                              | 1–2 bytes + actual length | Variable-length; MySQL adds 1 byte if ≤255, 2 bytes if >255 |
| **TEXT / TINYTEXT / MEDIUMTEXT / LONGTEXT** | Depends                   | Can store very large text; storage overhead varies          |



maximum size of a column in a table:



## A,AB,ABC,ABCD index answer
Here's a summary of our conversation:

Conversation Summary: SQL Index Selection and Query Optimization
This conversation covered how SQL query optimizers determine which index to use, how cost is calculated, and how index selection changes based on query structure.

Topic 1: How SQL Determines Which Index to Use
The first question explored a table with columns A, B, C, D, E and five composite indexes — (A), (A,B), (A,B,C), (A,B,C,D), and (A,B,C,D,E) — for the query SELECT * FROM table WHERE B = 4.
The key concept explained was the Left-Most Prefix Rule. All five indexes start with column A, not B. Since the query only filters on B, none of the indexes can be used for a direct seek — the optimizer would have to scan all values of A first before checking B, which is inefficient. As a result, the optimizer falls back to a Full Table Scan, reading every row and checking if B = 4. The solution would be to create a dedicated index on column B.

Topic 2: How the Optimizer Calculates Cost
The second question asked how the optimizer actually calculates the cost of each plan. The explanation covered two main components — IO Cost and CPU Cost — and the following key concepts. The optimizer relies on pre-collected statistics including row counts, page counts, cardinality, and histograms. From these it estimates selectivity, which is the fraction of rows that match the WHERE condition. A full table scan cost is simply the number of data pages multiplied by the read cost, and benefits from cheap sequential IO. An index scan cost includes traversing the B-Tree (typically 3-4 levels) plus fetching matching rows from the table via expensive random IO. When selectivity is low (few matching rows), the index wins. When selectivity is high (many matching rows), the full table scan wins because random IO costs explode. Stale statistics can cause the optimizer to make poor decisions, which is why running ANALYZE TABLE or UPDATE STATISTICS regularly is important.

Topic 3: Index Selection Between (B, C) and (B, C, D)
Problem Statement 1: Given two indexes (B, C) and (B, C, D) and the query SELECT * FROM table WHERE B = 4, which index does the optimizer pick?
Answer: The optimizer picks (B, C). Both indexes start with B so both are valid candidates, but (B, C) is smaller, has fewer pages, and costs less IO to scan. Since the query only filters on B, the extra column D in the second index adds no filtering benefit — it only makes the index larger. Both indexes return the same rows, but (B, C) does it cheaper.

Problem Statement 2: Given the same two indexes and the query SELECT B, C, D FROM table WHERE B = 4, which index does the optimizer pick?
Answer: The optimizer picks (B, C, D). Since the SELECT list includes columns B, C, and D, the larger index now covers all columns referenced in the query. This means the optimizer can perform an Index Only Scan — satisfying the entire query from the index without going back to the main table at all. The index (B, C) cannot do this because D is missing, forcing an extra table lookup for every matching row. The larger index earns its overhead by eliminating these table lookups entirely.

Core Takeaway
Index selection always comes down to cost — the optimizer picks the plan with the lowest combined IO and CPU cost based on statistics, selectivity, index size, and whether an index can fully cover the query. A bigger index is only worth it when the extra columns are actively used for filtering, sorting, or covering the SELECT list.

Hope this serves as a good reference!
"""






"""
cmm-1302-test6_095cfb96-c3b5-4484-ad36-e56e1f825027

Current:

    cmm-1302-test6-sheet_<sheetNo>_<sheetName>_<loadId>_multisheet.xlsx

Now:

    cmm-1302-test6_095cfb96-c3b5-4484-ad36-e56e1f825027-sheet_<sheetNo>_<sheetName>_<loadId>_multisheet.xlsx


"""