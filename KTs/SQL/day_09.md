So far, we know
1. what is sql
2. why is it used
3. how to create a database
4. how to create a table in a database
5. some best practices around table creation
6. what is an index
7. why index is useful
8. what is drawback of using an index
9. how files are stored for a postgreSQL database
10. How indexs are helpful in faster searches, B+ tree

So far, good.


Lets take a step back and see overall picture.
Lets understand what all components are there.

1. A server (compute) with some VCPUs, some RAM and some storage.
2. A program that is responsible for maintaining SQL database
3. A program or interaface (client) that is interacting to database.
4. Server's resource VCPUs, RAM etc are used to server client's request.
   

Lets say that we have a compute with 8VCPus, 16GB RAM and 256GB of SSD. Lets call it server A.

Also, lets say that we have a table `Users` and it has 5 columns.

### Situation 1: 
At some point of time, we had just a few thousand records, size in MBs. I think it is very easy to accomodate and process this much data on Server A.


### Situation 2:
Now, our data has grown and it is of about 50GB. I think, its pretty much easy to accomodate and process this much data on Server B.



### Situation 3:
Now, our data has grown and it is of about 300GB. Now, we can't really fit it into Server A's SSD. 

So, what do we do.
Lets get a bigger SSD of 1TB. Copy all data from older SSD to into this new SSD and use it for storage. We are operational again.


### Situation 4:
Now, our data has grown beyound 1TB. Lets say 1.5 TB.

What do we do? We can't really have an SSD of bigger size then 1TB because no such SSD really exists. So what is the solution.


Lets do one thing - 

split data into 700 GB - 750 GB. And buy a Server B to keep this data.

Server A - will hold 0-700GB of data.
Server B - will hold 700-1600 GB of data.


But this create an additional problem then whenever a search query comes in, we will have to make search into both Servers.

#### Can we optimze this? 
Let say that any user whose's userId is even, is kept of Server A and Server B contains odd userIds.

Now, if we get a search query, then we will be able to decide which server will be containing the data.



** his stretegy of splitting data on multiple servers, is known as Horizontal scaling or sharing** 
Its very important concept because vertical scaling will always hit some limit but we have great scope in horizonatal scaling.

So, the way, sharing works is -
1. there is a master computer, which will tell us that out of `n` servers in cluster, which server is going to have data.
2. Slave servers or normal servers, that will actally be doing computation and containing data in their storage.

```markdown
           ┌──────────────┐
           │  App Server  │
           └──────┬───────┘
                  │
   ┌──────────────┼────────────────────────────┐
   │              │                            │
┌──────┐     ┌──────┐                    ┌──────----┐
│Shard1│     │Shard2│                    │Shard3    │
│users_us│   │users_eu│     .....        │users_asia│
└──────┘     └──────┘                    └──────----┘
```

We are done with the concept of sharding.