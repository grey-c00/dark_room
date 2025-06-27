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
