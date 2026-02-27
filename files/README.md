In this doc, we are going to discuss about 
1. files and processing them
2. Processing real big files
3. Processing different formats
4. Processing different formats in chunks 


## Introduction about files

What is a File at the OS level?:
- A file is an abstract container for storing data persistently on a storage device (like HDD, SSD).
- The OS presents files as a linear sequence of bytes.
- Physically, the file’s data is stored in blocks/sectors on the disk.


**File System:**
- The OS uses a file system (e.g., NTFS, ext4, FAT32) to organize files on storage.
- The file system manages:
    - Metadata: filename, permissions, timestamps, size, etc.
    - Data blocks: where the actual content bytes are stored.
    - Directories: mappings of filenames to inodes or file control blocks.


**Key file system concepts:**
1. Inode (Index Node): A data structure storing metadata and pointers to data blocks.
2. Directories: Special files mapping filenames to inodes.
3. Superblock: Describes the filesystem layout.


**Opening a File:**

When you open a file, what happens inside the OS?

Step-by-step:
1. System call: Your program calls open("file.txt", flags) (e.g., in Linux).
2. The OS checks:
    - Does the file exist?
    - Do you have permission?
3. The OS reads the file’s inode from disk (metadata).
4. The OS creates a file descriptor (an integer) in the process’s file descriptor table.
5. The file descriptor points to an entry in the OS's open file table, which tracks:
    - Current file position (cursor).
    - File status flags (read, write, append).
    - Pointer to the inode.


**Reading a File: When you read data:**

- You call read(fd, buffer, size) system call.
- OS checks the file descriptor.
- OS looks up the file’s inode to find the data block locations.
- OS reads the necessary blocks from disk into kernel buffers (using caching).
- OS copies data from kernel space buffers into your program’s memory.
- OS updates the file cursor (offset) in the open file table.
- Returns the number of bytes read.

Note: Disks are slow, so OS uses buffer cache and read-ahead to optimize.


**Writing a File: When writing:**

- You call write(fd, buffer, size).
- OS copies data from user memory to kernel buffer cache.
- Marks the file dirty (needs to flush to disk).
- Updates file size and metadata if needed.
- Actual physical write to disk happens later asynchronously (to improve performance).
- Cursor moves forward by number of bytes written.


**File Cursor / File Offset:**

- Each open file descriptor has a cursor (offset) indicating where next read/write happens.
- Initially at 0.
- Moves forward with every read/write.
- Can be changed with lseek() system call (equivalent of Python’s seek()).


**Closing a File:**

- When close(fd) is called:
    - The file descriptor is removed from the process’s table.
    - Kernel flushes any remaining dirty buffers for that file.
    - OS releases resources.


**Buffering and Caching:**

- OS maintains buffer cache in RAM — holds recently accessed disk blocks.
- Reading from buffer cache is much faster than disk.
- Writing can be delayed and flushed later (write-back caching).
- This is why sometimes data is not immediately persisted to disk until flushed.


**Permissions & Security:**
- File metadata includes:
    - Owner, group.
    - Read, write, execute permissions.
- OS enforces access based on current user credentials.


**File Locks:**

- OS supports locking mechanisms to prevent race conditions:
    - Advisory locks (flock)
    - Mandatory locks (less common)

**File Types:**

- Regular files, directories, symbolic links, device files, FIFOs, sockets.
- Each has different semantics and handling by OS.

**File Descriptor Table (per process):**

- Each process has a table mapping integers (fds) to open files.
- Common fds: 0 = stdin, 1 = stdout, 2 = stderr.
- Max number of open files per process is limited.


### is socket I/O is also consider to be a file?
Yes — in Unix-like operating systems (like Linux and macOS), sockets are considered files.

It means you can use the same system calls to operate on a socket that you would use for files:

So, even though you don’t open() a socket like a file, once you create a socket, it gets assigned a file descriptor (int) just like files do.

```python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("example.com", 80))

fd = s.fileno()
print(fd)  # 👉 prints a file descriptor, like 3 or 4

```
- fileno() returns the underlying file descriptor.
- This FD lives in your process’s file descriptor table, just like any file.


| Type         | Description                     | File Descriptor? |
| ------------ | ------------------------------- | ---------------- |
| Regular file | Text, binary files              | ✅ Yes            |
| Directory    | Special file with entries       | ✅ Yes            |
| Socket       | Network connection endpoint     | ✅ Yes            |
| Pipe/FIFO    | For inter-process communication | ✅ Yes            |
| Device file  | `/dev/null`, `/dev/tty`         | ✅ Yes            |
| Terminal     | Interactive shell               | ✅ Yes            |

This design makes the OS simpler and more composable — e.g., you can use select() to monitor both a file and a socket at once.


When you do:
```c
int sockfd = socket(AF_INET, SOCK_STREAM, 0);

```
The kernel:
- Allocates a socket structure
- Adds it to the open file table
- Returns a file descriptor to the process

You then use read(), write(), send(), recv() on that file descriptor — just like with files.

| Question                       | Answer                                                                                            |
| ------------------------------ | ------------------------------------------------------------------------------------------------- |
| Is a socket a file?            | ✅ **Yes — in Unix-like systems**, sockets are represented by file descriptors                     |
| Can you read/write like files? | ✅ Yes (using `read()`, `write()` or `recv()`, `send()`)                                           |
| Does this apply to Windows?    | ❌ Not exactly. Windows has a different I/O model — sockets and files are not unified the same way |


### what is OS's open file system and How can i check OS's open file system?

### how can you check process's file descriptor table?

### is data stored in continuous memory blocks?
The short answer is: No, file data is not necessarily stored in continuous (contiguous) memory or disk blocks.

- Disks (HDD/SSD) are divided into fixed-size blocks (e.g., 4 KB).
- When you save a file, the OS allocates enough blocks to hold the data.
- These blocks do not have to be adjacent.
- This technique is called fragmentation.


## why file I/O is not CPU intensive?

**What is "CPU-intensive"?:**

An operation is CPU-intensive when it requires a lot of processor time — like:
- Complex calculations (e.g. matrix multiplication)
- Image/video processing
- Encryption/decryption
- Parsing large documents

In contrast, I/O operations (like reading a file) are typically bound by the speed of external devices, not by how fast the CPU can process.

**What happens during File I/O?:**
Let’s say you write this:
```python
with open("data.txt") as f:
    content = f.read()

```
You might think the CPU is doing a lot of work — but it’s mostly waiting. Here's what really happens:

### File I/O Flow (System Level)
1. User program calls read()
    - Your code calls read() on a file.
    - This triggers a system call (read syscall) into the OS kernel.
2. Kernel prepares for disk access
    - Kernel checks file metadata (permissions, offset, etc.).
    - If the data is not already cached, the kernel needs to load it from disk.
3. Disk I/O is handed off to hardware
    - The OS issues a read request to the disk controller (via I/O scheduler).
    - The disk hardware (HDD or SSD) locates the data on disk. 🔧 This is the part that’s slow compared to CPU speed.
        - HDDs: Have mechanical heads that physically move.
        - SSDs: Have no moving parts, but still slower than RAM or CPU.
4. While disk is reading, CPU is free
    - The CPU is not doing the reading itself.
    - Instead, it either:
        - Waits (blocking I/O), or
        - Switches to another process/thread (non-blocking or async I/O).
5. Data arrives in memory (RAM)
    - Once the disk returns the data, it's placed in:
        - Kernel buffers (page cache)
        - Then copied to your program’s buffer
6. read() returns to your program
    - Now your program can use the data.
7. OS Optimizations to Reduce CPU Load
    1. Page Cache (Buffer Cache)
        - Frequently accessed file data is cached in RAM.
        - If it's in cache, no disk access is needed → instant read.
    2. DMA (Direct Memory Access)
        - Modern OS and hardware use DMA, where data goes from disk → RAM without CPU copying it.
        - This further reduces CPU involvement.
    3. Asynchronous I/O
        - With non-blocking I/O, the CPU doesn’t wait at all — it just moves on and gets a notification when data is ready.


While basic file I/O is not CPU-intensive, the CPU can still be busy if:

| Case                                | Why CPU is used                        |
| ----------------------------------- | -------------------------------------- |
| Decompressing files (zip, parquet)  | Requires CPU cycles                    |
| Parsing structured data (JSON, XML) | CPU reads/validates structure          |
| Handling millions of small files    | Metadata access can be CPU-heavy       |
| Encryption/Decryption               | Cryptographic operations are CPU-bound |


### Kernel buffer and programe buffer

*** What Are Buffers?***

A buffer is just a block of memory used to temporarily hold data while it’s being transferred from one place to another — such as:

- From disk to RAM
- From RAM to your program
- From your program to a file or socket

This buffering ensures that the system can handle differences in speed between devices (e.g., disk is slow, CPU is fast).


There Are Two Main Buffers in File I/O:
| Type              | Where It Exists       | Managed By              | Purpose                                      |
| ----------------- | --------------------- | ----------------------- | -------------------------------------------- |
| **Kernel Buffer** | Inside kernel memory  | OS (e.g., Linux kernel) | Temporarily stores data during I/O transfers |
| **User Buffer**   | Your program's memory | Your Python/C/Java code | Where your app reads from or writes to       |


**Kernel Buffer (Page Cache)**
- Resides in kernel space, not directly accessible by your app.
- Managed by the OS.
- Used for:
    - Disk read/write caching
    - Buffered I/O
    - Disk prefetching (read-ahead)

- Why it exists:
    - Disk access is slow; caching improves performance.
    - Allows multiple programs to share recently read data.

**User Buffer (Application Memory)**

- Resides in user space.
- This is where your Python or C variable (data, buffer, etc.) lives.
- After a read() call, data is copied from kernel buffer into this space.

## Best Practices
- if you are processing a file in chunk and transmitting it over network then make sure that 
    - total content lenght is know / transmitted to receiver.
    - each chunk is being tracked



