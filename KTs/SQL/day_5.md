Alright, now lets focus on just one table.

collection of tables ====> Database [most simplified terms]

# Example One
Consider a table: `Users`
schema:
|----user_id: int
|----name: string
|----country: string
|----state: string
|----age: string
|----surname: string
|----father_name: string
|----date_of_birth: date


## Case1: Consider that we are just a small scale application with about just 1000 records in `Users` table.

How do we make sure that:
1. Writes in this table are fast (I hope you understand what I mean by write) : wirtes are pretty much fast because table size is too small.
2. Reads in this table are fast (I hope you understand what I mean by write): wirtes are pretty much fast because table size is too too small.

fyi: writes are insertion of row, deletion of a row, updation of row
reads: its reading and retrivel rows

## Case2: Consider that we have grown and application has grown 100 time. Now Users table contains about 100,000 records.

How do we make sure that:
1. Writes in this table are fast : wirtes are enough fast because table size is not too big.
2. Reads in this table are fast : wirtes are enough fast because table size is too fast.

## Case3: Again, our scale has grown by 100x. Now, `Users` table contains about 10 Million records.

How do we make sure that:
1. Writes in this table are fast : <lets ignore this for time being>
2. Reads in this table are fast : we can do indexing.

### Question? What is indexing
<Write here>
<pros>
<cons>
<How much index should we creat and on what all tables>
<How indexing is done, what is red black tree>
<What happens when you create index while creating table itself>
<What changes do happen when indexes are added later>


## Case4: Again, our scale has again grown by 100x. Now, `Users` table contains about 1 Billion records.

 How do we make sure that:
1. Writes in this table are fast : <lets ignore this for time being>
2. Reads in this table are fast : think what all things can we do?

<Write here>




# Setting up SQL in local 

Check if you have access.

1. Download docker desktop
2. Download SQL image
3. Run docker run command to start up DB.
4. Use tablePlus and any other mean to interact with DB
5. Create Users table with the defined schema and play around

