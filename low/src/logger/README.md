## Log Writer
1. We can write to log file, messaging queue or anything which is configurable. And there can be latency as well. So we need to 
   1. Create a buffer to store recent logs instead of writing each log into destination
   2. Write should be async, non-blocking
2. Write in logs file
   1. make sure data is not corrupted because of too many threads.
   2. We need to use thread safe mechanism - [TODO]
3. Writing in messaging queue
   1. No need to consider data corruption and data loss because it has to be handled by the messaging queue itself.


## Prevention of data loss
1. Keep the buffer size small - optimum
2. write logs of calls in a permanent storage and delete them after a while and reprocess them if failure occurres
3. Same call can be replicated across multiple servers


## Supporting various log levels
1. DEBUG, INFO, WAR, ERROR, CRITICAL
2. Log level should be configurable
3. This will be implement via using **chain-of-responsibility** design pattern
    -> https://refactoring.guru/design-patterns/chain-of-responsibility