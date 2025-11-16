SO far, we have understanding of - 

1. what is sql
2. what is sql server
3. what is a database
4. what is table
5. table creation/updation/insertion etc
6. do/don't around table creation
7. ACID properties
8. Handling large dataserts - sharing/partitioning
9. Making database more reliable, reducing redundency: Normalization
10. Joins between tables and their example
11. Enhancing serving layer's response time: De-normalization


Now, lets talk about anoth important feature (their are many feature, but this is most commonly used) CDC.

## What is CDC: 
CDC stands for change data capture. Means, in a table, we can enable CDC and whenever a new action such as insertion, updation, deletion action is perfomed, this change is capture and dumped to a certain location (fixed or configured position in database).

example:
table: `Student`
columns: `name`, `dataOfBirth`

if name is updated then data: {"name": current_name, "dateOfBirth": current_dob, "change" : {"action": "updated", "name": prev_name}} (ps: keys might changes and styling might change from databsase to databse) will be dumped at a certain location.


## Why is it useful?
Any service can consume those CDCs and replice its logic. Usually, its very useful while desiging analytical system. Because, analytical systems need data from transcations happening on platform. And, relevent platform will keep on sending CDCs to this analytics system. A asynchronous flow of event starts to happen between two systems without making too many code.


## Similar other feature
Several other database features behave similarly by enforcing rules, automating logic, or controlling data integrity at the database layer. Some examples include:

1. Triggers / Rules: Automatically execute logic when an event occurs on a table (INSERT, UPDATE, DELETE).
    Example: Whenever a row in the Student table is updated, ensure that the dateOfBirth column cannot be changed. If an update attempt is made, block it or raise an error.
2. Constraints: Built-in rules that the database enforces on data.
    - PRIMARY KEY – ensures each student has a unique ID.
    - FOREIGN KEY – ensures StudentScore.StudentId must exist in Student.
    - UNIQUE – prevents duplicate values (e.g., unique email).
    - CHECK – ensures values satisfy a condition (e.g., TestScore >= 0).

3. Stored Procedures: A pre-defined block of SQL logic that can be reused.
   Example: A stored procedure to calculate a student's average score.

4. Views: Virtual tables generated from SQL queries. Example: A view that joins Student, StudentScore, and TestDetails into a single unified dataset.

5. Functions (UDFs): Custom functions that return a value for use in queries. Example: A function calculateGrade(score) that converts numeric scores into grades A–F.

6. Audit Logs / Change Tracking: Automatically record changes to data for compliance or debugging. Example: Track every modification to student records along with user ID and timestamp.

7. Cascading Actions: Automatic propagation of changes across related tables.Example:
   - ON DELETE CASCADE – deleting a student also deletes their scores.
   - ON UPDATE CASCADE – changing a TestId updates related tables.

8. Materialized Views: Pre-computed and stored views that improve performance for heavy analytical queries.Example: A materialized view storing summary statistics of student performance.

9. Indices: Speed up lookups and joins. Example: Index on StudentId in StudentScore for faster retrieval.

10. Triggers for Notifications: Triggers that send alerts or publish events when data changes. Example: When a student’s score falls below the passing threshold, trigger a notification.
