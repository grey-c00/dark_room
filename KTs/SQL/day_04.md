So at this point we have understanding of:
- What is SQL and why it exists
- What is SQL Server and how it manages tables
- What is a table, row, and column
- Basic structure of data in tables


Now let's dive deeper into SQL and understand how to work with tables.

## Data Types in SQL

Before we create tables and store data, we need to understand what types of data can be stored in SQL tables. Just like in programming languages (Python, Java, etc.), SQL has data types.

Common SQL Data Types:

1. **Numeric Types**:
   - `INT` or `INTEGER`: Whole numbers (e.g., 1, 100, -50)
   - `FLOAT` or `DOUBLE`: Decimal numbers (e.g., 3.14, -0.5, 100.567)
   - `DECIMAL(p, s)`: Exact decimal numbers where p = total digits, s = digits after decimal
     - Example: `DECIMAL(5, 2)` can store 999.99

2. **String/Text Types**:
   - `VARCHAR(n)`: Variable-length string with max length n (e.g., VARCHAR(100))
   - `CHAR(n)`: Fixed-length string of length n
   - `TEXT`: Large text data

3. **Date and Time Types**:
   - `DATE`: Stores date (YYYY-MM-DD)
   - `TIME`: Stores time (HH:MM:SS)
   - `DATETIME` or `TIMESTAMP`: Stores both date and time

4. **Boolean Type**:
   - `BOOLEAN`: Stores TRUE or FALSE


## Basic SQL Operations

Now let's understand the basic operations we can perform on tables. These are called CRUD operations:
- **C**reate (INSERT)
- **R**ead (SELECT)
- **U**pdate (UPDATE)
- **D**elete (DELETE)

But before we can do any of these, we need to CREATE a table first!

### 1. Creating a Table

Remember our storyteller example from day_3? Let's create that table.

**Syntax:**
```sql
CREATE TABLE table_name (
    column1_name data_type constraints,
    column2_name data_type constraints,
    ...
);
```

**Example:**
```sql
CREATE TABLE stories (
    story_id INT PRIMARY KEY,
    author_name VARCHAR(100),
    author_country VARCHAR(50),
    story_name VARCHAR(200),
    publication_date DATE
);
```

**What is PRIMARY KEY?**
- A PRIMARY KEY uniquely identifies each row in a table
- Each table should have a primary key
- Primary key values must be unique and cannot be NULL
- Example: Each story has a unique `story_id`


### 2. Inserting Data (CREATE)

Now let's add data to our table.

**Syntax:**
```sql
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...);
```

**Example:**
```sql
INSERT INTO stories (story_id, author_name, author_country, story_name, publication_date)
VALUES (1, 'storyteller_x', 'India', 'story_x_1', '2024-01-15');

INSERT INTO stories (story_id, author_name, author_country, story_name, publication_date)
VALUES (2, 'storyteller_x', 'India', 'story_x_2', '2024-03-20');

INSERT INTO stories (story_id, author_name, author_country, story_name, publication_date)
VALUES (3, 'storyteller_y', 'India', 'story_y_1', '2024-02-10');
```

Our table now looks like:
```
+----------+-----------------+----------------+-------------+------------------+
| story_id | author_name     | author_country | story_name  | publication_date |
+----------+-----------------+----------------+-------------+------------------+
| 1        | storyteller_x   | India          | story_x_1   | 2024-01-15       |
| 2        | storyteller_x   | India          | story_x_2   | 2024-03-20       |
| 3        | storyteller_y   | India          | story_y_1   | 2024-02-10       |
+----------+-----------------+----------------+-------------+------------------+
```


### 3. Reading Data (READ)

This is the most commonly used operation. We use `SELECT` to read data.

**Syntax:**
```sql
SELECT column1, column2, ...
FROM table_name
WHERE condition;
```

**Example 1: Select all columns**
```sql
SELECT * FROM stories;
```
Result: All rows and all columns

**Example 2: Select specific columns**
```sql
SELECT author_name, story_name FROM stories;
```
Result:
```
+-----------------+-------------+
| author_name     | story_name  |
+-----------------+-------------+
| storyteller_x   | story_x_1   |
| storyteller_x   | story_x_2   |
| storyteller_y   | story_y_1   |
+-----------------+-------------+
```

**Example 3: Select with WHERE clause**
```sql
SELECT * FROM stories
WHERE author_name = 'storyteller_x';
```
Result: Only rows where author is storyteller_x

**Example 4: Select with multiple conditions**
```sql
SELECT * FROM stories
WHERE author_name = 'storyteller_x' AND publication_date > '2024-02-01';
```
Result: Only stories by storyteller_x published after Feb 1, 2024


### 4. Updating Data (UPDATE)

Sometimes we need to modify existing data.

**Syntax:**
```sql
UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition;
```

**Example:**
```sql
UPDATE stories
SET author_country = 'USA'
WHERE story_id = 3;
```

**⚠️ IMPORTANT WARNING:** 
Always use WHERE clause with UPDATE! If you forget WHERE, it will update ALL rows in the table!

```sql
-- DANGEROUS! This will update all rows
UPDATE stories
SET author_country = 'USA';
```


### 5. Deleting Data (DELETE)

To remove rows from a table.

**Syntax:**
```sql
DELETE FROM table_name
WHERE condition;
```

**Example:**
```sql
DELETE FROM stories
WHERE story_id = 3;
```

**⚠️ IMPORTANT WARNING:** 
Always use WHERE clause with DELETE! If you forget WHERE, it will delete ALL rows!

```sql
-- DANGEROUS! This will delete all rows
DELETE FROM stories;
```


## More Useful SQL Clauses

### ORDER BY
Sort results by a column.

```sql
-- Sort by publication_date in ascending order
SELECT * FROM stories
ORDER BY publication_date ASC;

-- Sort by publication_date in descending order (newest first)
SELECT * FROM stories
ORDER BY publication_date DESC;
```

### LIMIT
Get only first N rows.

```sql
-- Get only first 2 stories
SELECT * FROM stories
LIMIT 2;
```

### DISTINCT
Get unique values only.

```sql
-- Get unique author names
SELECT DISTINCT author_name FROM stories;
```

### COUNT, SUM, AVG, MIN, MAX
Aggregate functions to perform calculations.

Let's say we add a `page_count` column:

```sql
-- Count total stories
SELECT COUNT(*) FROM stories;

-- Average page count
SELECT AVG(page_count) FROM stories;

-- Maximum page count
SELECT MAX(page_count) FROM stories;

-- Minimum page count
SELECT MIN(page_count) FROM stories;

-- Total pages across all stories
SELECT SUM(page_count) FROM stories;
```


## Constraints in SQL

Constraints are rules applied to columns to ensure data integrity.

1. **PRIMARY KEY**: Uniquely identifies each row
2. **NOT NULL**: Column cannot have NULL value
3. **UNIQUE**: All values in column must be unique
4. **DEFAULT**: Sets a default value if none is provided
5. **CHECK**: Ensures values meet a condition

**Example:**
```sql
CREATE TABLE books (
    book_id INT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    price DECIMAL(10, 2) CHECK (price > 0),
    publication_year INT DEFAULT 2024,
    available BOOLEAN DEFAULT TRUE
);
```


## Real-World Example: Employee Database

Let's create a more practical example:

```sql
-- Create employees table
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10, 2) CHECK (salary > 0),
    hire_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Insert sample data
INSERT INTO employees VALUES
(1, 'John', 'Doe', 'john.doe@company.com', 'Engineering', 75000.00, '2023-01-15', TRUE),
(2, 'Jane', 'Smith', 'jane.smith@company.com', 'Engineering', 85000.00, '2023-02-20', TRUE),
(3, 'Bob', 'Johnson', 'bob.j@company.com', 'Marketing', 65000.00, '2023-03-10', TRUE),
(4, 'Alice', 'Williams', 'alice.w@company.com', 'HR', 70000.00, '2023-04-05', FALSE);

-- Query examples

-- Get all employees in Engineering
SELECT * FROM employees
WHERE department = 'Engineering';

-- Get employees with salary > 70000
SELECT first_name, last_name, salary
FROM employees
WHERE salary > 70000;

-- Get average salary by department
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department;

-- Count active employees
SELECT COUNT(*) as active_count
FROM employees
WHERE is_active = TRUE;

-- Get highest paid employee
SELECT first_name, last_name, salary
FROM employees
ORDER BY salary DESC
LIMIT 1;
```


## Why SQL is Powerful

Remember from day_1 and day_2 when we discussed searching in large files and maintaining metadata for faster searches? SQL Server does all of this automatically!

When you create a PRIMARY KEY or add an INDEX on a column, SQL Server automatically:
1. Creates optimized data structures (like B-Trees)
2. Maintains metadata for faster searches
3. Handles concurrent access (multiple users accessing same data)
4. Ensures data integrity
5. Manages transactions (either all operations succeed or all fail)

This is why SQL is so widely used for structured data storage and retrieval!


## Connection to Previous Days

- **Day 1**: We learned about chunking large files and maintaining metadata for faster searches
  - SQL does this automatically with indexes!
  
- **Day 2**: We discussed handling continuously changing/appending data
  - SQL handles INSERT, UPDATE, DELETE operations efficiently with ACID properties
  
- **Day 3**: We learned what SQL is and why it exists
  - Today we learned HOW to use it!


---

## Practice Questions

### Conceptual Questions:

1. **What is the difference between VARCHAR and CHAR data types? When would you use each?**

2. **Why is it important to always use WHERE clause with UPDATE and DELETE statements? What happens if you forget it?**

3. **What is a PRIMARY KEY and why is every table recommended to have one?**

4. **Explain the difference between these two queries:**
   ```sql
   SELECT * FROM employees WHERE salary > 70000;
   SELECT * FROM employees WHERE salary >= 70000;
   ```

5. **What does the DISTINCT keyword do? Give an example scenario where it would be useful.**

6. **What is the difference between COUNT(*) and COUNT(column_name)?**

7. **Can a table have more than one PRIMARY KEY? Why or why not?**

8. **What happens if you try to INSERT a row with a duplicate PRIMARY KEY value?**


### Practical Questions (Write SQL queries):

Given the following `employees` table:

```
+--------+------------+-----------+---------------------------+-------------+-----------+------------+-----------+
| emp_id | first_name | last_name | email                     | department  | salary    | hire_date  | is_active |
+--------+------------+-----------+---------------------------+-------------+-----------+------------+-----------+
| 1      | John       | Doe       | john.doe@company.com      | Engineering | 75000.00  | 2023-01-15 | TRUE      |
| 2      | Jane       | Smith     | jane.smith@company.com    | Engineering | 85000.00  | 2023-02-20 | TRUE      |
| 3      | Bob        | Johnson   | bob.j@company.com         | Marketing   | 65000.00  | 2023-03-10 | TRUE      |
| 4      | Alice      | Williams  | alice.w@company.com       | HR          | 70000.00  | 2023-04-05 | FALSE     |
| 5      | Charlie    | Brown     | charlie.b@company.com     | Engineering | 90000.00  | 2022-12-01 | TRUE      |
+--------+------------+-----------+---------------------------+-------------+-----------+------------+-----------+
```

Write SQL queries for the following:

1. **Select all employees from the Engineering department.**

2. **Find the names and salaries of all active employees (is_active = TRUE).**

3. **Count how many employees are in each department.**

4. **Find the employee with the highest salary.**

5. **Get all employees hired in 2023, ordered by hire_date.**

6. **Find all employees whose salary is between 70000 and 85000 (inclusive).**

7. **Update Bob Johnson's salary to 68000.**

8. **Find the average salary of all active employees.**

9. **Get unique department names from the employees table.**

10. **Select all employees whose first name starts with 'J'.**
    (Hint: Use `LIKE 'J%'`)

11. **Delete all inactive employees from the table.**
    (⚠️ Be careful with DELETE!)

12. **Insert a new employee with the following details:**
    - emp_id: 6
    - first_name: 'Sarah'
    - last_name: 'Connor'
    - email: 'sarah.c@company.com'
    - department: 'Engineering'
    - salary: 80000
    - hire_date: '2024-10-30'
    - is_active: TRUE


### Challenge Questions:

1. **Create a table called `departments` with the following columns:**
   - dept_id (INT, PRIMARY KEY)
   - dept_name (VARCHAR(50), NOT NULL, UNIQUE)
   - location (VARCHAR(100))
   - budget (DECIMAL(12, 2), CHECK budget > 0)

2. **Write a query to find the second highest salary in the employees table.**
   (Hint: Use ORDER BY and LIMIT with OFFSET)

3. **What is wrong with this query? How would you fix it?**
   ```sql
   SELECT first_name, last_name, salary
   FROM employees
   WHERE salary > AVG(salary);
   ```

4. **Write a query to get employees who were hired in the first quarter (January-March) of any year.**

5. **Explain what ACID properties are in databases and why they are important.**
   (Research this if you don't know - it's a fundamental concept!)


---

## Additional Notes

- SQL is case-insensitive for keywords (SELECT = select = SeLeCt), but it's convention to write keywords in UPPERCASE
- Table names and column names are typically in lowercase with underscores (snake_case)
- Always end SQL statements with a semicolon (;)
- Use comments for complex queries:
  ```sql
  -- This is a single line comment
  
  /* This is a
     multi-line comment */
  ```

**Next Topics to Learn (Day 5 and beyond):**
- JOINs (combining data from multiple tables)
- GROUP BY and HAVING clauses
- Subqueries
- Indexes and Performance Optimization
- Transactions
- Views
- Stored Procedures

---

Remember: The best way to learn SQL is by practicing! Try to write queries, make mistakes, and learn from them. Install a SQL database (like PostgreSQL, MySQL, or SQLite) and practice with real data.

