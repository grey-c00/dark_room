Do a high level design of a WhatsApp-like messaging app that supports 
1. real-time messaging
2. media sharing - images, videos
3. group chats

Functional Requirements 
- User Registration and Authentication
- One to one chat
- Group creation 
- Group Chat
- Media Sharing - text, images, videos
- Read Receipts
  - Sent
  - Delivered
  - Read
- Last Seen
- Typing Indicator


Non-Functional Requirements
- Scalability
  - The system should be able to handle millions of users and messages.
  - 1 billion users
  - 1.6 Billion monthly active users
  - 65 Billion messages
- Low latency
- High Availability
- No lag

Questions
1. what all devices are we going to support?
2. What is the expected message size?
3. What is the expected media size?