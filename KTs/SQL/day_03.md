So at this point of time we have some understanding of 
- maintaining data, search and maintaining some metadata to make search faster
- pros and cons of implementing different approaches
- RAM vs Storage


Now lets understand that why does SQL is there?
In real world, we have so many types of data. And that data can be stored in various file formats such a text file, images, csv, parquet files, video files etc. And storing data in various file formats has its own purposes.

For example:
- storing texts in text file is a good idea. It wount be a good idea to store text in images.


So, the important part is that everything is driven for some purpose/s.

Out of so many ways to store data, lets see if a subset of data can be represented in table like structure. what do i mean by table? see below

-----------------------------------------------------
| <Some info>| <Some info>| <Some info>| <Some info>| 
-----------------------------------------------------
| <Some info>| <Some info>| <Some info>| <Some info>| 
-----------------------------------------------------
| <Some info>| <Some info>| <Some info>| <Some info>| 
-----------------------------------------------------


So each table is going to have some rows and some columns.



Lets take an example. There is a storyteller (name = storyteller_x) from India (Country), who write a story. So, proably, I will store story in a text file (I don't think there is a way to store it in table like format. <Think about it and try to prove me wrong>). But I can store, storyteller's name, storyteller's country and name of the story in a table like structure;

-----------------------------------------------------
| Author Name   | Author Country| Story name        | 
-----------------------------------------------------
| storyteller_x | India         | story_x_1         | 
-----------------------------------------------------

If there is another story written by `storyteller_x` then I can just add one more row.

-----------------------------------------------------
| Author Name   | Author Country| Story name        | 
-----------------------------------------------------
| storyteller_x | India         | story_x_1         | 
-----------------------------------------------------
| storyteller_x | India         | story_x_2         | 
-----------------------------------------------------

If there is another story written by `storyteller_y` then I can just add one more row.

-----------------------------------------------------
| Author Name   | Author Country| Story name        | 
-----------------------------------------------------
| storyteller_x | India         | story_x_1         | 
-----------------------------------------------------
| storyteller_x | India         | story_x_2         | 
-----------------------------------------------------
| storyteller_y | India         | story_y_1         | 
-----------------------------------------------------

So basically - 
- a row gives us some information that are related to each other
- a column - tell us the significane of that data (Confusing way to explina, but understand it in own language)


Data in table can be appened, deleted, updated etc.




Internet has its own history, <read on internet if you are more interesed>
Around, 1978, IBM developed compute programs to store, retrive and process data in table like structure.
Here, we define structure of table and do operation on this table. We can create more than one table and each table is going to have some name. Those table can be related to each other (we will understand it later).

So, what is SQL?
It stands to Structured Query Langaue. It is just like any other programming languare which is used to do some operation on these tables.

Now you should ask, where will these tables be stored?
These table will be stored in Database which is manged by Server (SQL Server) and SQL Language will be used to do operations on these table. SQL Server will mange these table in a smarter, opetimized way (that we will understand later).
PS: if i say, SQL Server, don't assume that it will be a big machine with larges CPU and RAM. Its just a program that is used to created files and store table's data in them. Even, anyone can download the SQL libraries and run SQL server in their local compute.


So its like

```markdown

+-------------------------------------------------------------+
|                         SQL SERVER                          |
|                                                             |
|   +-------------+     +-------------+     +-------------+   |
|   |   Table 1   |     |   Table 2   | ... |   Table N   |   |
|   +-------------+     +-------------+     +-------------+   |
|                                                             |
+-------------------------------------------------------------+
                ▲
                │  (SQL commands act on the database)
                │
+-------------------------------------------------------------+
|                    SQL LANGUAGE (SQL)                       |
|  e.g., SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, etc.   |
|  → Instructions that tell SQL Server what to do              |
+-------------------------------------------------------------+


````

This is basic of SQL and Server. Also, remember that whenever a system's design reach certain level, that system will start rolling out additional features to tackle user's problem (that we will see later).
