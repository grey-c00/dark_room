## what is a SQL DB?
A SQL DB (SQL Database) is a structured database that uses SQL (Structured Query Language) to manage and manipulate data. It’s one of the most common types of databases used in applications ranging from websites to enterprise software.

Key Concepts:
SQL (Structured Query Language): The programming language used to interact with the database. You use it to:

Create and manage database structures (tables, indexes, etc.)

Insert, update, delete, and query data

Tables: Data is organized into tables, which are like spreadsheets with rows and columns. Each table typically represents one type of entity (e.g., Users, Products).

Schema: The structure that defines the tables, fields, and relationships in the database.

Relationships: Tables can be related to each other using keys (primary and foreign keys), allowing complex data modeling.

Common SQL Databases:
- MySQL
- PostgreSQL

## Why should we use SQL DB?

✅ 1. Your data is structured
SQL databases excel at handling structured data: data with a clear schema (e.g., tables with defined columns and data types).

✅ 2. You need relationships between data
You can link related data across tables using foreign keys, which is ideal for real-world systems (like users and orders, or products and categories).

✅ 3. You require data integrity and accuracy
SQL databases support ACID properties:
- Atomicity
- Consistency
- Isolation
- Durability
- 
These ensure that your data stays reliable, even if there are failures or concurrent users.

✅ 4. You want powerful querying tools
With SQL, you can perform complex queries like joins, aggregations (sums, counts), filters, and nested subqueries — efficiently and consistently.
If the query patten is on columns as well then this type of DB could be helpful.



## UseFul Function

### function to extract day/month/year from a date
- to extract day - use `DAY(date)`
- to extract month - use `MONTH(date)`
- to extract year - use `YEAR(date)`
