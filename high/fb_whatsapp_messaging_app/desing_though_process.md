First of all, we need to have a bi-directional communication between the client and server. This can be achieved using WebSockets or long polling.

We are going to use webSocket for real time communication and so that we can send and receive messages instantly, without refreshing the UI.


So, whenever a user comes online, we will establish a WebSocket connection between the client and server. This connection will remain open as long as the user is online. Since, there can be so many user online at the same time, we are going to use a websocket handler that will tell us that which user is connected to which websocket object. So that whenever, there is need for us to send message to the user, we can identify the corresponding websocket object and sent it to the corresponding user.

How are we going to handle the case, when - 
1. a user goes offline, what all things will be happening at backend side?
2. There can be so many users online at the time, how are we going to maintain that much information?
3. Is there going to be a central service that will handle all the websocket connections? if yes then where and how are we going to store the information about the users and their websocket connections?


### what all things are going to happen when a user comes online
1. makes websocket connection with the server
2. Sends any message that couldn't be sent due to offline status
3. Requests any pending messages 
4. Requests delivery/read receipts

### [Flow1] How things are going to work when, both users are online
1. U1 sends message to U2
2. App communicates with the server using WebSocket
3. Server receives the message and finds the corresponding WebSocket connection for U2
4. Server sends the message to U2's WebSocket connection
5. U2 receives the message and updates the UI
6. U2 sends the acknowledgement of receiving the message
7. Delivery receipt is sent back to U1's WebSocket connection
8. whenever, U2 reads the messages, read receipt is sent back to U1's WebSocket connection

### [Flow2] How things are going to work when, one user is online and other is offline
1. U1 sends message to U2
2. App communicates with the server using WebSocket
3. Server receives the message and finds the corresponding WebSocket connection for U2
4. Since, U2 is offline, no WebSocket connection is found
5. This message is stored in the database with a status of "pending"
6. when U2 comes online, [Flow1] is triggered


### [Flow3] How things are going to work when, both users are offline
1. U1 sends message to U2
2. Message is stored in local db
3. When U1 comes online, [Flow1] is triggered


### [Flow4] How things are going to work when, a user is sending message in group
1. U1 sends message to group G1
2. App communicates with the server using WebSocket
3. Group Service receives the message and finds all the members of the group
4. For each member of the group, it finds the corresponding WebSocket connection
5. For group members those who are offline, messages are stored in the database with a status of "pending"
6. Server sends the message to each member's WebSocket connection
7. There is need for us to setup a different service because additional functionalities such as who all have seen, whom all has message been deliverd and other could be build independently with the desired scale.
8.

### [Flow5] How things are going to work when, a user is sending media
1. U1 communicate with Asset Service to upload the media file
2. Asset Service stores the media file in a distributed file system (like S3) and returns an asset_id
3. this asset_id is sent to U2 
4. Whenever, U2 comes online, [Flow1] is triggered
5. Whenever, U2 clicks on the asset_id, Asset Service fetches the media file from the distributed file system and sends it to U2


### how are we going maintain last seen time
1. we can have an analytics service that is continuously listening to the events that are happening on the user's app. Based on that, we can deduce the time when the user went offline.

### How are we going to handle the Typing Indicator
1. Whenever, a user starts typing, we can send an event to the server using WebSocket
2. These events can be stored in a cache (like Redis) with a TTL (Time To Live) of 5 seconds
3. Whenever, the other user comes online, we can fetch the typing indicator from the cache and send it to the user



### Lets understand that how the websocket manager is going to work
If we just consider that there is going to be one geographical location then probably we can have a central cache that will store user and corresponding websocket's information.


If service is distributed across multiple geographical location then
1. based on the destination user we can route the request to the corresponding websocket manager. Example, if U1 is in US and U2 is in India then we can route the request to the websocket manager that is closest to U2.
2. we can use a centralised cache to store the entire information.

In approach 1, if user (lets say from India) is travelling to another country (lets say US) then probably, we can can still manage this connection in local websocket manager and in the India's local websocket manager as well.
