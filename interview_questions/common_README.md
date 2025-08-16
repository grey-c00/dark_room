## what are RESTFULL vs RESTless apis?

### RESTFull APIs:
These are APIs that follow the REST (Representational State Transfer) architectural style properly and completely.

#### Characteristics of RESTful APIs:
- Use HTTP methods correctly: GET, POST, PUT, DELETE

- Use stateless communication (no server-side memory of previous requests)

- Follow resource-based URLs (e.g. /products/123)

- Return data typically in JSON or XML

- Use standard status codes (200 OK, 404 Not Found, etc.)



### RESTless APIs (not a formal term but commonly used)
This usually refers to APIs that do not fully follow REST principles — either intentionally or due to poor implementation.

#### Characteristics of RESTless APIs:
- Mis use HTTP verbs (e.g., using GET to delete)
- Non-resourceful endpoints (e.g., /getUser?id=101)
- May be stateful
- Might mix in RPC-like behavior (/doSomethingNow)
- Often less standardized, harder to scale or maintain


### A usecase where RESTless APIs are better:



## why parquet is better than csv?
its a columnar format, which means it stores data in columns rather than rows. This has several advantages: such as compression, efficient while reading and inserting column.
While CSV does not have compression, everything is a string.



## How are you going to generate ids for new users (and other attribute) ?
We can use uuid4 to generate unique ids for new users. This will ensure that the ids are unique across the system and can be used as primary keys in the database.

```python
import uuid

user_id = str(uuid.uuid4())
print(user_id)  # e.g., '3d0e2b6a-d845-4d2b-8e97-bcb7c53f1169'
```
✅ Globally unique

✅ No setup required

✅ Works across any number of services/machines

❌ Not ordered

❌ Slightly large (36 characters)

Best for: General-purpose ID generation



```python
import ulid

user_id = str(ulid.new())
print(user_id)  # e.g., '01HZZWYB91WXT5ZAY1R2BMF9EZ'

```

✅ Lexicographically sortable

✅ 26 characters

✅ Great for logs, databases, event tracking

✅ No central coordination

✅ Built-in timestamp component

Best for: Ordered inserts, logs, analytics, user IDs




```python
from nanoid import generate

user_id = generate()
print(user_id)  # e.g., 'V1StGXR8_Z5jdHi6B-myT'

```
✅ Short and URL-safe

✅ Cryptographically secure

✅ Configurable alphabet/length

❌ Not sortable

❌ Slightly less standardized than UUID/ULID

Best for: Public-facing URLs, shareable tokens


```python
from snowflake_id import SnowflakeIDGenerator

generator = SnowflakeIDGenerator(node_id=1)

user_id = generator.generate()
print(user_id)  # e.g., 1587542056042844160

```

✅ Unique

✅ Time-sortable

✅ Uses timestamp + machine ID + sequence

❌ Must configure machine/node ID correctly

❌ Slightly more setup, but very efficient

Best for: High-throughput, time-ordered inserts
