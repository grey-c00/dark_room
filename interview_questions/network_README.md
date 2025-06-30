## Basic terminology that we use during
- development cycle
- deployment cycle
- architecture design


### what is latency?
Latency refers to the delay between a request and its response — in simple terms, it's how long you wait for something to happen.

It is typically measured in milliseconds (ms) or microseconds (µs).

Simple Example (Real Life):
- You click a link in a browser. 
- It takes 300 ms before the page starts loading. 
- That 300 ms is latency.

Types of Latency in Computing:

| Type                    | What It Refers To                                         | Example                                  |
| ----------------------- | --------------------------------------------------------- | ---------------------------------------- |
| **Network latency**     | Delay in sending data over a network                      | Time taken for a packet to reach server  |
| **Database latency**    | Time taken for a query to return a result                 | SELECT query takes 200 ms to respond     |
| **Disk I/O latency**    | Delay in reading/writing data to disk                     | SSD latency \~0.1 ms; HDD much higher    |
| **UI latency**          | Delay between user action and interface response          | Button click shows response after 500 ms |
| **Application latency** | Time between user request and response (end-to-end delay) | API call takes 1 second                  |


### What is throughput?
Throughput is the amount of work done in a given time period. It measures how many tasks or operations can be completed in a specific timeframe.

Throughput is the number of operations (requests, transactions, queries, etc.) successfully processed per unit of time.

It’s usually measured in:
- Requests per second (RPS)
- Transactions per second (TPS)
- Rows processed per second 
- MB/s or GB/s (for data transfer or disk I/O)

Example Scenario:

| System             | Throughput Metric               | Example                  |
| ------------------ | ------------------------------- | ------------------------ |
| Web server         | Requests per second (RPS)       | 10,000 HTTP requests/sec |
| Database           | Queries or transactions per sec | 1,200 SQL queries/sec    |
| Network            | Data rate (MB/s)                | 500 MB/s transfer speed  |
| Manufacturing line | Units per hour                  | 300 products/hour        |
| Streaming service  | Packets per second              | 20,000 video packets/sec |


### what is bandwidth?
Bandwidth is the maximum amount of data that can be transferred over a network (or channel) in a given period of time.

It’s typically measured in:
- Bits per second (bps) — or more commonly:
  - Mbps – megabits per second 
  - Gbps – gigabits per second

More bandwidth = more data can flow simultaneously.
But remember:
- This is the maximum capacity, not the actual performance. 
- Actual speed may be lower due to latency, congestion, packet loss, etc.


### will latency go down if bandwidth goes up?
Bandwidth = how much data can flow per second
Latency = how long it takes one piece of data to go from source to destination

- Scenario 1: Low Bandwidth & High Latency 
  - You upgrade to higher bandwidth (say from 10 Mbps to 100 Mbps). 
  - Now more data can flow, so large downloads are faster ✅ 
  - But if latency was caused by distance (say you're pinging a server in the US from India), latency doesn't change ❌
- Scenario 2: Congestion-Related Latency
  - If your network was clogged, increasing bandwidth might reduce queueing delay, and so latency drops a bit ✅
  - But again, this is indirect and not always guaranteed

When Latency and Bandwidth Are Related:

| Situation                          | Bandwidth↑ Helps Latency? |
| ---------------------------------- | ------------------------- |
| Downloading large files            | ✅ Yes (completes faster)  |
| Real-time ping or small API calls  | ❌ No                      |
| Video buffering (reducing stalls)  | ✅ Sometimes               |
| High latency due to long distances | ❌ No                      |
| High latency due to congestion     | ✅ Maybe (if queues clear) |


### latency vs throughput
Latency and throughput are two important metrics in networking and computing, but they measure different aspects of performance.

Latency shows how fast each request is:
- Useful when measuring user experience 
- Low latency = faster page loads, snappier UIs
-  Example: A banking API that returns your balance in 50ms feels fast.

Throughput shows how much the system can handle
- Useful when testing scalability 
- High throughput = handles more users, more data
- Example: During a sale, your e-commerce site needs to process 1,000 orders/sec.

So, latency is about speed of individual requests, while throughput is about volume of requests handled over time.

So, if throughput is low then latency can go high.


### What is a CDN?
A CDN (Content Delivery Network) is a network of distributed servers that deliver web content (like images, videos, scripts) to users based on their geographic location. The goal is to improve the performance, reliability, and speed of content delivery.


### How does a CDN work?
1. **Content Replication**: The CDN replicates and caches content across multiple servers located in various geographic locations (edge servers).
2. **User Request**: When a user requests content (like an image or video), the CDN routes the request to the nearest edge server based on the user's location.
3. **Content Delivery**: The edge server delivers the cached content to the user, reducing latency and improving load times.
4. **Dynamic Content**: For dynamic content (like API calls), the CDN can still optimize delivery by caching static parts and routing requests efficiently.

### What happens when you type a URL in a browser and press Enter?
1. The browser checks DNS cache or queries a DNS server to resolve the domain to an IP. 
2. It establishes a TCP connection with the server via a three-way handshake. 
3. Sends an HTTP/HTTPS request to the server. 
4. The server processes the request and sends back an HTTP response. 
5. The browser renders the webpage. 
6. The connection is closed or kept alive for further requests.

### Explain the difference between TCP and UDP.
- TCP is connection-oriented, reliable, guarantees order and delivery of packets, and uses flow control. 
- UDP is connectionless, unreliable, faster, with no guarantee of packet order or delivery. 
- TCP is used for web pages, emails; UDP for video streaming, gaming where speed matters.

### What is an IP address? What is the difference between IPv4 and IPv6?
An IP address is a unique identifier assigned to each device on a network. 
- IPv4 is 32-bit, expressed in four decimal numbers (e.g., 192.168.1.1). 
- IPv6 is 128-bit, expressed in hexadecimal, to support a vastly larger number of addresses.

### Explain subnetting and CIDR.
- Subnetting divides a larger network into smaller subnetworks to improve management and security. 
- CIDR (Classless Inter-Domain Routing) represents IP addresses with a suffix indicating the network prefix length (e.g., 192.168.1.0/24). 
- It allows flexible allocation of IP addresses.

### What is DNS and how does it work?
- DNS (Domain Name System) translates human-readable domain names to IP addresses.
- When you request a domain, the browser queries DNS servers to resolve the domain to an IP.
- This allows browsers to connect to the correct web servers.

### What is the OSI model? Describe the layers.
The OSI model has 7 layers describing network functions:
1. Physical – hardware and transmission media. 
2. Data Link – MAC addressing, error detection. 
3. Network – IP addressing and routing. 
4. Transport – TCP/UDP, reliability. 
5. Session – managing sessions. 
6. Presentation – data formatting, encryption. 
7. Application – user services (HTTP, FTP).

### What is HTTP and HTTPS? How does SSL/TLS work?
- HTTP is a protocol for transferring web pages. 
- HTTPS is HTTP over SSL/TLS, providing encrypted and secure communication. 
- SSL/TLS uses certificates to establish a secure, encrypted connection between client and server.

### What is NAT? Why is it used?
- NAT (Network Address Translation) translates private IP addresses to a public IP to enable devices in a private network to access the internet. 
- It helps conserve IPv4 addresses and provides security by hiding internal IPs.


### Difference between a switch and a router.
- A switch connects devices within the same network, forwarding data based on MAC addresses. 
- A router connects multiple networks and forwards data based on IP addresses, routing packets between networks.

### Explain a three-way TCP handshake.
It establishes a reliable connection:
- [first] Client sends SYN to server . 
- [Second] Server responds with SYN-ACK. 
- [Third] Client replies with ACK.

- Connection is now established.


### How do you troubleshoot network issues like latency or packet loss?
- Use tools like ping and traceroute to check latency and path. 
- Check for network congestion, faulty hardware, or misconfiguration. 
- Analyze packet loss via packet capture tools (Wireshark). 
- Verify firewall or routing rules.

### What are common HTTP methods, and how are they used in RESTful APIs?
Common HTTP Methods:
- GET: Retrieve data from the server (read-only). Example: Get user details. 
- POST: Send data to the server to create a new resource. Example: Create a new user. 
- PUT: Update an existing resource or create it if it doesn’t exist. Example: Update user info. 
- DELETE: Remove a resource. Example: Delete a user. 
- PATCH: Partially update a resource. 
- OPTIONS: Check supported HTTP methods for a resource.

In RESTful APIs, these methods correspond to CRUD operations:
- Create → POST 
- Read → GET 
- Update → PUT/PATCH 
- Delete → DELETE

###  How does a firewall protect a network?
A firewall acts as a security barrier between a trusted internal network and untrusted external networks (like the internet). It monitors and filters incoming and outgoing network traffic based on predefined security rules.

How it protects:
- Blocks unauthorized access. 
- Allows only legitimate traffic based on rules (IP addresses, ports, protocols). 
- Can prevent malware and attacks by blocking suspicious traffic. 
- Types include hardware, software, and cloud firewalls.


### What is a VLAN, and why would an organization use VLANs?
VLAN (Virtual Local Area Network) is a logical grouping of devices within a physical network, segmented into separate broadcast domains.

Why use VLANs:
- Improve security by isolating sensitive data traffic. 
- Reduce broadcast traffic and improve network performance. 
- Simplify network management by grouping users/departments regardless of physical location. 
- Enable better control over network resources and policies.

### What is VPN?
A VPN (Virtual Private Network) creates a secure, encrypted tunnel between your device and a remote network over the internet.

Purpose:
- Protects data from interception (encryption). 
- Enables secure remote access to internal company resources. 
- Masks the user’s IP address for privacy. 
- Useful for connecting remote employees securely to a company’s network.

How does a VPN work?
1. Encryption: When you connect to a VPN, your data is encrypted on your device before it even leaves. This means anyone intercepting the data cannot read it without the encryption key. 
2. Tunnel: The encrypted data travels through a secure tunnel, established between your device and the VPN server. 
3. VPN Server: The VPN server decrypts your data and sends it to the intended destination (like a website or internal company server). Responses from that destination go back to the VPN server, get encrypted, and travel back through the tunnel to your device, where they are decrypted. 
4. IP Masking: While connected, your IP address appears as the VPN server’s IP, hiding your real location and identity.

Why do people use VPNs?
- Security: Protect sensitive data from hackers, especially on public Wi-Fi. 
- Privacy: Hide your browsing activity from ISPs, governments, or trackers. 
- Access Control: Employees can securely access company resources from anywhere. 
- Bypass Geo-Restrictions: Access content or websites restricted by location. 
- Avoid Censorship: Access blocked websites in restrictive regions.

### What are ARP and its purpose in networking?
ARP (Address Resolution Protocol) is a protocol used to map an IP address to its corresponding MAC (hardware) address on a local network.

Purpose:
- When a device wants to communicate with another device on the same LAN, it uses ARP to find the MAC address associated with the target IP address. 
- Enables proper delivery of packets on Ethernet networks by resolving IP addresses to physical hardware addresses.


### what different protocols are used in a e-commerce website?
1. **HTTP/HTTPS**: For web page requests and secure transactions.
2. **TCP/IP**: For reliable data transmission over the internet.
3. **FTP/SFTP**: For file transfers (e.g., product images, backups).
4. **SMTP/IMAP/POP3**: For email communication (order confirmations, notifications).
5. **OAuth**: For secure user authentication and authorization.
6. **WebSockets**: For real-time updates (e.g., live chat, notifications).
7. **RESTful APIs**: For communication between frontend and backend services.
8. **GraphQL**: For flexible data queries and interactions.
9. **Payment Gateway Protocols**: For secure payment processing (e.g., Stripe, PayPal).
10. **CDN Protocols**: For content delivery (e.g., caching images, scripts).
11. **DNS**: For resolving domain names to IP addresses.
12. **Webhooks**: For real-time event notifications (e.g., order status updates).
13. **Caching Protocols**: For improving performance (e.g., Redis, Memcached).
14. **Analytics Protocols**: For tracking user behavior (e.g., Google Analytics, Mixpanel).

