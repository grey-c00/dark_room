## Which DB to use?
This is decided based on -
1. structure of the data
   1. if data is pretty much structured then SQL DBs are preferred.
   2. else NoSQL DBs are preferred.
2. is there need for joins?
   1. if yes, then SQL DBs are preferred.
   2. else NoSQL DBs are preferred.
3. ACID properties
   1. Moder NoSQL DBs has started to support ACID properties, so this is not a big concern.
4. query patterns
   1. If the query pattern is on columns as well then columnar DB could be helpful.
   2. else if the retrieval can just be done based on keys then NoSQL are great.
5. scalability
   1. If the data is huge and needs to be scaled horizontally then NoSQL DBs are preferred.
6. Inserts/updates/append pattern [TODO]
7. read/write ratio [TODO]


## How data is stored in NoSQL DB vs SQL DB?