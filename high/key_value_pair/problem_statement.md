Design a distributed key-value pair store that can handle high read and write throughput with low latency. The system should support the following operations:


Functional Requirements:
- `PUT(key, value)`: Store the key-value pair in the system.
- `GET(key)`: Retrieve the value associated with the key.
- `DELETE(key)`: Remove the key-value pair from the system.
- `UPDATE(key, value)`: Update the value associated with the key.


Non-functional requirements:
- Scalability: The system should be able to scale horizontally to handle increased load.
- Availability: The system should be highly available, with minimal downtime.
- Consistency: The system should provide strong consistency for read and write operations.
- Latency: The system should have low latency for read and write operations.
- distributed in nature


