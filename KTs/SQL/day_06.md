So far we have great understanding of 
- Table
- Indexing
- What happens when table size increases and how do we optimized reads and writes this.

Now, let me repeat again that - 
- Accessing permanent storage such as SSD or Hard Drvie is slow compared to RAM. [This is very intutive and important in System Design]
  - Question? Why reading SSD/Hard drive is slow


Lets get back to setting up SQL in local.

Let me remaind you that what SQL is and what SQL Server is?

- SQL Server: A server that manages table (or tables), insertion, deletion, updation, creation of new table, access management, writing files in permanent storage etc
- SQL: A language that instructs SQL Server to do something. So, any instruction needs to be executed on instruction. To do that, we will have to make connection to server. Once, connection is established, instruction can be executed.

Example:
```makrdown
lets say that server is running on <ip>:5432

There is a python application that wants to create a new table. So how will we do that.
We will need - 
1. A library that can actually talk to SQL Servers. Lets say library name is `sql_library_x`
2. We need to tell this libarary about which server to connect, what is user and password and what instructions to execute.

Its all step by step. Nothing extraordinary is happening.
```


## Lets move ahead
We already have SQL serve running in our local machine.
Install tablePlus and access it via UI. (Use some youtube video to do this or let me know).

Lets do some operation on it.

### Create a DATABASSE
Execute command: `CREATE DATABLE local_database`

Here, we have create a database and we are going to do some operation in this db. Remember, there can be more than one database on a server. But collectively, we just call them Database. But just remeber....

[-] What will be happening at the server side:
    - its a very lightweight command, server will just create `local_database` , sort of workspace

### CREATE TABLE

Lets create a table `Users` in `local_database`
Execute command:

```markdown

CREATE TABLE Users 
(
	userId INT,
	"name" VARCHAR,
	country VARCHAR,
	state VARCHAR,
	age INT,
	dateOfBirth DATE
	
);
```

#### What will be happening at the server side:

- Server wil check if table `Users` exits, if yes, then operation is failed.
- Else, Server will create table `Users` in database `local_database` and store its metdata such as name of columns, datatypes etc. It a very lightweight operation.

### Viewing content (rows and columns) of a table

lets view content of `Users` table.

Run command:
`SELECT * FROM Users;`

- `SELECT` a keyword that tell to retrive data
-  `*` it tell the server to select all of the columns
-  `FROM` a keyword used to specify table (right now just assume table)
-  `Users` name of the table.
  
This query will look like:

<Unable to attach screenshot here>
But it will return table with all of the column but no rows.

### What will be happening at the server side:
- Server will check if the table exists, if no operation is failed.
- Server will retrive all of the rows from storage and send it back to the client (here client is tablePlue) and client will understand the response and show it nicely on UI.
  - [Question] is it a lightweight operation?
  - [Question] if Yes, why?
  - [Question] if No, why?


Run command:
`SELECT userId FROM Users;`

Here, we instructed server to only return the `userId` column and its content.

This query will look like:

<Unable to attach screenshot here>
But it will return table with just `userId` column but no rows.

### What will be happening at the server side:
- Server will check if the table exists, if no operation is failed.
- Server will check if column `userId` exists. if no, operation is failed
- Server will retrive all of the rows from storage and will only send `useId` column's data, back to the client (here client is tablePlue) and client will understand the response and show it nicely on UI.
  - [Question] is it a lightweight operation?
  - [Question] if Yes, why?
  - [Question] if No, why?
  - Which one will be faster `SELECT * FROM Users;` or `SELECT userId fROM Users;`
    - [Question] why?


### Inserting data (row or rows):

Run command
```
INSERT INTO Users 
(userId, "name", country, state, age, dateofbirth) 
VALUES
(1, 'user_one', 'India', 'Rajsthan', -1, '01-01-1971');
```

its a standard syntax: `INSERT INTO <table_name>  (col1, col2, ..., coln) VALUES (val1, val2, ..., valn);`

### What will be happening at the server side:
- Server will check if the table exists, if no, operation is failed.
- Serve will check if all of the columns specified exists or not, if at least one column is not found in table then operation is failed.
- Server will check if inserted values are of correct type. Example: in userId column, we can put string values. If incorrect data types are found then operation is failed.
- Server will return an acknowledgement to the client (here tablePlus) stating that I have successfully written data.

Lets run another Insert command:

```
INSERT INTO Users 
(userId, "name", country, state, age, dateofbirth) 
VALUES
(2, 'user_two', 'India', 'Rajsthan', 100, '01-01-1947');
```

Now, we have 2 rows in `Users` table. you can run `SELECT * FROM Users;` and see the output.


## Deleting data from table

Run command:

`DELETE FROM Users WHERE userId=1;`

### What will be happening at the server side:
- Server will check if the table exists, if no, operation is failed.
- Serve will check if all of the columns specified (here `userId`) exists or not, if at least one column is not found in table then operation is failed.
- Server will delete that row (tricky part, we will discuss it later)
- Server will return an acknowledgement to the client (here tablePlus) stating that I have successfully deleted data.

Now, we have just 1 row in `Users` table. you can run `SELECT * FROM Users;` and see the output.

## Deleting a table:

RUN Command:

`DROP TABLE Users;`

### What will be happening at the server side:
- Server will check if the table exists, if no, operation is failed.
- Server will mark table as deleted.
- Server will return an acknowledgement to the client (here tablePlus) stating that I have successfully deleted table.

Now if you run `SELECT * FROM Users;`, it should fail.



Similary, there are so many operation that we can do on a table, on more than one table. We can set contraints, rules, CDCs etc. But all of them are dependet on usecase. If we have great understanding of the operation discussed so far then every operation, question, pros/cons will be real easy to understand.

# Question:
<write here>



