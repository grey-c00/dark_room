## string functions
stl: `#include <string>`


## vector stl
stl: `#include <vector>`

intialize: vector<int> arr (n, number)

functions: 
1. push_back(value) - adds value to the end of the vector
2. pop_back() - removes the last element from the vector
3. clear() - removes all elements from the vector
4. size() - returns the number of elements in the vector
5. emplace_back(value) - constructs an element in place at the end of the vector

## sort function
stl: `#include <algorithm>`

syntax: sort(begin_iterator, end_iterator, comparator_function)
    
here -
- end_iterator is exclusive, meaning the element at end_iterator is not included in the sort.
- end_iterator does not have to be end of it, it can be `begin_iterator + k`
- by default compare_function is `std::less<T>()` which sorts in ascending order.

### custom sorter

```
bool custom_sorter(const T& a, const T& b) {
    // return true if a should come before b
    return a < b; // for ascending order
}

sort(begin_iterator, end_iterator, custom_sorter)
```


## reverse function
stl: `#include <bits/stdc++.h>`

In C++, the reverse() is a built-in function used to reverse the order of elements in the given range of elements

syntax: `reverse(begin_iterator, end_iterator)`
- end_iterator does not have to be end of it, it can be `begin_iterator + k`

## pair
In C++, pair is used to combine together two values that may be of different data types or same data types as a single unit. The first element is stored as a data member with name 'first' and the second element as 'second'.

stl: `#include <utility>`

intialize: `pair<T1, T2> p1;`

where, 
- T1: Data type of the first element. 
- T2: Data type of the second element. 
- p: Name assigned to the pair.

```commandline
pair <T1, T2> p;
pair<T1, T2> p = {v1, v2};
pair<T1, T2> p = make_pair(v1, v2);
```

Basic Operations
- `make_pair(v1, v2)` - creates a pair with values v1 and v2
- `first` - access the first element of the pair
- `second` - access the second element of the pair
- `swap(p1, p2)` - swaps the values of two pairs p1 and p2
- 

## iterator
Iterators are used to access and iterate through elements of data structures (vectors, sets, etc.), by "pointing" to them.

stl: `#include <iterator>`

intialize: T::iterator itr

```commandline
vector<string>::iterator it;
auto itr = v.begin();  // for vector, supported after c++11
```


begin() and end() are functions that belong to data structures, such as vectors and lists. They do not belong to the iterator itself. Instead, they are used with iterators to access and iterate through the elements of these data structures.

- begin() returns an iterator that points to the first element of the data structure.
- end() returns an iterator that points to one position after the last element.

```commandline
// Point to the first element in the vector
it = cars.begin();

// Point to the second element
it = cars.begin() + 1;

// Point to the last element
it = cars.end() - 1;

```

- Use `std::distance(itr1, itr2)` to find the number of elements between two iterators.
  - Time complexity of this operation
    - For Random-Access Iterators (Used by: std::vector, std::deque, arrays), we can directly subtract the iterators, which is O(1).
    - For Bidirectional / Forward / Input Iterators (Used by: std::set, std::map, std::list, std::unordered_set, etc.), Cannot subtract directly, hence time complexity is O(n)

#### Why do we say "point"?

Iterators are like "pointers" in that they "point" to elements in a data structure rather than returning values from them. They refer to a specific position, providing a way to access and modify the value when needed, without making a copy of it. For example:
```

// Point to the first element in the vector
it = cars.begin();

// Modify the value of the first element
*it = "Tesla";

// Volvo is now Tesla
```

#### For-Each Loop vs. Iterators
When you are just reading the elements, and don't need to modify them, the for-each loop is much simpler and cleaner than iterators.

However, when you need to add, modify, or remove elements during iteration, iterate in reverse, or skip elements, you should use iterators:

## priority queue
stl: `#include <queue>`

initialization: `priority_queue<int> pq;`
```commandline
    // Creating priority queue from other container
    vector<int> v = {9, 8, 6, 10, 4, 2};
    priority_queue<int> pq2(v.begin(), v.end());  // time: O(n)
```

functions:
1. push(value) - adds value to the priority queue, time O(log n)
2. pop() - removes the top element from the priority queue, time O(log n)
3. top() - access the top element of the priority queue, time O(1)
4. empty() - checks if the priority queue is empty, time O(1)
5. size() - returns the number of elements in the priority queue, time O(1)
6. deletion can only be done at the top element of it, so only pop() function is supported
7. traversal can be done via deleting the top element and keep on accessing next one

### custom priority queue

```commandline
priority_queue<int, vector<int>, greater<int>> pq;
```


## set
In C++, sets are associative container which stores unique elements in some sorted order. By default, it is sorted ascending order of the keys, but this can be changed as per requirement. It provides fast insertion, deletion and search operations

stl: `#include<set>`

initialize: `set<T, comp> s;`
where,
- T: Data type of elements in the set.
- s: Name assigned to the set.
- comp: It is a binary predicate function that tells set how to compare two elements. It is used to sort set in custom order. It is optional and if not provided, set is sorted in increasing order.

```commandline
set<int> s1;
set<int> s2 = {5, 1, 3, 2, 4};
```

Functions - 
1. insert(value) - adds value to the set, time O(log n)
2. erase(value) - removes value from the set, time O(log n)
3. updating element - not supported
4. finding element - find(), time O(log n)
   - `find(value)` returns an iterator to the element if found, otherwise returns an iterator to end of the set.
   - `count(value)` returns the number of occurrences of value in the set (0 or 1 for sets).
5. traversing: Just like other containers, sets can be easily traversed using range-based for loop or using begin() and end() iterators.
6. size() - returns the number of elements in the set, time O(1)
7. empty() - checks if the set is empty, time O(1)
8. **lower_bound(val)** - returns an iterator pointing to the first element that is not less than n (>=n), This operation is `O(logn)` in std::set.
9. **upper_bound(val)** - Returns an iterator to the first element strictly greater than n (>n).


## map
In C++, maps are associative containers that store data in the form of key value pairs sorted on the basis of keys. No two mapped values can have the same keys. By default, it stores data in ascending order of the keys, but this can be changes as per requirement.

stl: `#include <map>`
initialize: `map<T1, T2, comp> m;`
where:
- T1: Data type of keys.
- T2: Data type of values.
- m: Name assigned to the map.
- comp: It is a binary predicate function that tells map how to compare two keys. It is used to sort map in custom order. It is optional and if not provided, map is sorted in increasing order of keys.

```commandline
    // Creating an empty map
    map<int, string> m1;

    // Initialze map with list
    map<int, string> m2 = {{1, "Geeks"},
              {2, "For"}, {3, "Geeks"}};
```

Basic Operations:
1. insert(key, value) - adds a key-value pair to the map, time O(log n)
2. erase(key) - removes the key-value pair with the given key, time O(log n)
3. updating element - `m[key] = value` or `m.insert({key, value})`, time O(log n)
4. finding element - `find(key)`, time O(log n)
   - `find(key)` returns an iterator to the key-value pair if found, otherwise returns an iterator to end of the map, time O(log n)
   - `count(key)` returns the number of occurrences of key in the map 
5. size() - returns the number of key-value pairs in the map, time O(1)
6. empty() - checks if the map is empty, time O(1)
7. at(key) - accesses the value associated with the given key, throws an exception if key is not found, time O(log n)


### unordered_map

stl: `#include <unordered_map>`

initialize: `unordered_map<T1, T2, hash_function, equal_function> m;`
where:
- T1: Data type of keys.
- T2: Data type of values.
- m: Name assigned to the unordered_map.
- hash_function: It is a function that computes the hash value of the keys. It is used to store the keys in a hash table.
- equal_function: It is a function that checks if two keys are equal. It is used to compare the keys in the hash table. It is optional and if not provided, unordered_map uses default hash function and equal function.

```commandline
    // Creating an empty unordered_map
    unordered_map<int, string> m1;

    // Initialze unordered_map with list
    unordered_map<int, string> m2 = {{1, "Geeks"},
              {2, "For"}, {3, "Geeks"}};
```

On average, insert, delete, update, find operation happen in O(1). And all functions are same as of map functions.



## deque
In C++, deque container provides fast insertion and deletion at both ends. Stands for Double Ended QUEue, it is a special type of queue where insertion and deletion operations are possible at both the ends in constant time complexity.

stl: `#include <deque>`

intialize: `deque<T> d;`
```commandline
    // Creating an empty deque
    deque<int> dq1;
    
    
    // Creating a deque with default size and value
    deque<int> dq2(3, 4);
    
    // Creating a deque of 5 elements
    deque<int> dq = {1, 4, 2, 3, 5};
```

Basic Operations:
1. push_front(value) - adds value to the front of the deque, time O(1)
2. push_back(value) - adds value to the back of the deque, time O(1)
3. pop_front() - removes the front element from the deque, time O(1)
4. pop_back() - removes the back element from the deque, time O(1)
5. front() - accesses the front element of the deque, time O(1)
6. back() - accesses the back element of the deque, time O(1)
7. size() - returns the number of elements in the deque, time O(1)
8. empty() - checks if the deque is empty, time O(1)
9. traversing: Just like other containers, deques can be easily traversed using range-based for loop or using begin() and end() iterators.
    ```
   deque<int> dq = {1, 4, 2, 3, 5};

    // Traversing using the for loop
    for (int i = 0; i < dq.size(); i++) 
        cout << dq[i] << " ";
   ```
   
10. insert(): Insertion at specific position, time O(n)
    ```commandline
    deque<int> dq = {1, 4, 2};

    // Inserting elements at back and front
    dq.push_back(5);
    dq.push_front(0);
    
    // Insert element at third position
    auto it = dq.begin() + 2;
    dq.insert(it, 11);
    ```
11. updating element: 
    ```commandline
    deque<int> dq = {1, 4, 2, 3, 5};

    // Updating element
    dq[2] = 8;
    
    cout << dq[2]; 
    ```
    
12. Deleting element: For removing element at specific index, the erase() method is used
    ```commandline
    deque<int> dq = {1, 4, 2, 3, 5};

    // Deleting from the back and front
    dq.pop_back();
    dq.pop_front();
    dq.erase(dq.begin());
    for (int i = 0; i < dq.size(); i++) 
        cout << dq[i] << " ";
    ```

## heap







