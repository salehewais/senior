# Software Engineering Master Roadmap
## A structured roadmap for Backend Engineering and Senior Software Engineering

> **تنظيم وتوسيع للمنهج الأصلي.** تم الحفاظ على المحاور والموضوعات الأصلية، مع إعادة ترتيبها، وتصحيح بعض التسميات الواضحة، وإضافة موضوعات مكملة. لم يتم حذف قوائم المسائل أو الأنماط الموجودة في الملف الأصلي.

---

# Roadmap Overview

## Phase 1 — Engineering Foundations
1. Problem Solving & Data Structures & Algorithms (DSA)
2. DBMS & Data Management
3. Object-Oriented Design (OOD)

## Phase 2 — Software Design & Architecture
4. Application Architecture
5. Presentation Architecture
6. Patterns of Enterprise Application Architecture (PoEAA)
7. Domain-Driven Design (DDD)

## Phase 3 — Concurrency & Integration
8. Concurrency Patterns
9. Enterprise Integration Patterns (EIP)

## Phase 4 — Distributed Systems & System Architecture
10. System Design

## Supporting Foundations (study alongside the roadmap)
- Software Engineering Practices
- Operating Systems Fundamentals
- Computer Networking Fundamentals

> ترتيب المراحل تعليمي وليس Dependency Graph صارمًا. يمكن دراسة بعض المحاور بالتوازي، كما يمكن البدء بأساسيات System Design مبكرًا ثم التعمق فيها بعد دراسة المحاور السابقة.

---

# 01 — Problem Solving & Data Structures & Algorithms (DSA)

## 1.1 Complexity Analysis
- Time Complexity & Space Complexity
  - Big O, Big Omega, Big Theta
- Amortized Analysis

## 1.2 Fundamental Data Structures
- Arrays & Strings
  - Prefix Sums
  - Matrix Manipulation
- Linked Lists
  - Singly Linked Lists
  - Doubly Linked Lists
  - Circular Linked Lists
- Stacks & Queues
  - Monotonic Stack
  - Monotonic Queue
- Hash Tables / Hash Maps / Hash Sets
- Heaps / Priority Queues

## 1.3 Advanced Data Structures
- Trees
  - Binary Trees
  - Binary Search Trees
  - AVL / Self-Balancing Trees
  - Tries
- Graphs
  - Adjacency Matrix / Adjacency List
  - Directed / Undirected
  - Weighted / Unweighted
- Disjoint Set Union (Union-Find / DSU)
- Segment Trees
- Fenwick Trees (Binary Indexed Tree)

## 1.4 Core Problem-Solving Patterns & Techniques
- Two Pointers
- Sliding Window
- Fast & Slow Pointers (Tortoise & Hare)
- Prefix Sum
- Merge Intervals
- Cyclic Sort
- In-place Reversal of a Linked List
- Binary Search & Modified Binary Search
- Tree Breadth-First Search (BFS) & Depth-First Search (DFS)
- Graph Traversal
- Shortest Path
  - Dijkstra
  - Bellman-Ford
  - Floyd-Warshall
- Topological Sort
  - Kahn's Algorithm
  - DFS-based
- Backtracking & Recursion
- Dynamic Programming
  - Memoization
  - Tabulation
  - 1D / 2D DP
  - Knapsack
  - LCS
  - LIS
- Greedy Algorithms
- Divide and Conquer
- Bit Manipulation
- Mathematical Algorithms

## 1.5 Recursion Roadmap & Problem Tracker

### A. Recursion (العودية)

#### Common Problems
- 509 — Fibonacci Number (Easy)
- 344 — Reverse String (Easy)
- 21 — Merge Two Sorted Lists (Easy)
- 50 — Pow(x, n) (Medium)
- 118 — Pascal's Triangle (Easy)
- 24 — Swap Nodes in Pairs (Medium)
- 779 — K-th Symbol in Grammar (Medium)
- 2 — Add Two Numbers (Medium)
- 95 — Unique Binary Search Trees II (Medium)
- 394 — Decode String (Medium)

#### Training Path
- 206 — Reverse Linked List (Easy): Recursive reversal of a linked list
- 203 — Remove Linked List Elements (Easy): Recursive removal with a base case
- 231 — Power of Two (Easy): Recursive halving until the base
- 326 — Power of Three (Easy): Recursive division and base cases
- 342 — Power of Four (Easy): Recursive division by four
- 234 — Palindrome Linked List (Easy): Recursion to the end, then compare
- 3304 — Find the K-th Character in String Game I (Easy): Recursive string growth
- 390 — Elimination Game (Medium): A recurrence that shrinks the problem
- 1545 — Find Kth Bit in Nth Binary String (Medium): A string defined by recursion
- 1823 — Find the Winner of the Circular Game (Medium): Josephus recurrence

### B. Trees (الأشجار)

#### Common Problems
- 104 — Maximum Depth of Binary Tree (Easy)
- 226 — Invert Binary Tree (Easy)
- 100 — Same Tree (Easy)
- 102 — Binary Tree Level Order Traversal (Medium)
- 98 — Validate Binary Search Tree (Medium)
- 236 — Lowest Common Ancestor of a Binary Tree (Medium)
- 572 — Subtree of Another Tree (Easy)
- 543 — Diameter of Binary Tree (Easy)
- 124 — Binary Tree Maximum Path Sum (Hard)
- 105 — Construct Binary Tree from Preorder and Inorder Traversal (Medium)

### C. Backtracking (التراجع)

#### Core Problems
- 78 — Subsets (Medium)
- 90 — Subsets II (Medium)
- 46 — Permutations (Medium)
- 47 — Permutations II (Medium)
- 39 — Combination Sum (Medium)
- 40 — Combination Sum II (Medium)
- 131 — Palindrome Partitioning (Medium)
- 51 — N-Queens (Hard)
- 79 — Word Search (Medium)
- 37 — Sudoku Solver (Hard)

#### Additional Problems
- 17 — Letter Combinations of a Phone Number (Medium)
- 216 — Combination Sum III (Medium)
- 93 — Restore IP Addresses (Medium)
- 698 — Partition to K Equal Sum Subsets (Medium)
- 212 — Word Search II (Hard)
- 473 — Matchsticks to Square (Medium)
- 52 — N-Queens II (Hard)
- 491 — Non-decreasing Subsequences (Medium)
- 526 — Beautiful Arrangement (Medium)
- 1849 — Splitting a String Into Descending Consecutive Values (Medium)

### D. Dynamic Programming (البرمجة الديناميكية)

#### Common Problems
- 70 — Climbing Stairs (Easy)
- 198 — House Robber (Medium)
- 213 — House Robber II (Medium)
- 5 — Longest Palindromic Substring (Medium)
- 322 — Coin Change (Medium)
- 300 — Longest Increasing Subsequence (Medium)
- 416 — Partition Equal Subset Sum (Medium)
- 62 — Unique Paths (Medium)
- 72 — Edit Distance (Hard)
- 1143 — Longest Common Subsequence (Medium)

### E. Graphs (الرسوم البيانية)

#### Common Problems
- 200 — Number of Islands (Medium)
- 133 — Clone Graph (Medium)
- 695 — Max Area of Island (Medium)
- 207 — Course Schedule (Medium)
- 417 — Pacific Atlantic Water Flow (Medium)
- 994 — Rotting Oranges (Medium)
- 261 — Graph Valid Tree (Medium, Premium)
- 127 — Word Ladder (Hard)
- 743 — Network Delay Time (Medium)
- 787 — Cheapest Flights Within K Stops (Medium)

---

# 02 — DBMS & Data Management

## 2.1 Core Concepts & Architecture
- DBMS vs RDBMS
- Database Architecture
- Relational Model
- Tables, Rows, Columns
- Data Types
- SQL vs NoSQL
- ACID Properties
  - Atomicity
  - Consistency
  - Isolation
  - Durability

## 2.2 Relational Database Design
- Keys
  - Primary Key
  - Foreign Key
  - Candidate Key
  - Composite Key
  - Unique Key
- Relationships
  - One-to-One
  - One-to-Many
  - Many-to-Many
- Normalization
  - 1NF
  - 2NF
  - 3NF
  - BCNF
- Denormalization
- Schema Design
- Data Modeling

## 2.3 Transactions & Concurrency Control
- Transactions
- Transaction Isolation Levels
  - Read Uncommitted
  - Read Committed
  - Repeatable Read
  - Serializable
- Concurrency Phenomena
  - Dirty Reads
  - Non-repeatable Reads
  - Phantom Reads
  - Lost Updates
  - Write Skew
- Locks
  - Shared Locks
  - Exclusive Locks
  - Intent Locks
- Deadlocks
- MVCC (Multi-Version Concurrency Control)
- Optimistic Concurrency Control
- Pessimistic Concurrency Control
- WAL (Write-Ahead Logging)
- Savepoints

## 2.4 Storage, Indexing & Query Performance
- Indexing
  - B-Tree
  - B+Tree
  - Hash Index
  - Clustered vs Non-Clustered
  - Bitmap Index
- Query Processing
- Query Planner / Optimizer
- Query Execution Plans
- Database Caching
- Buffer Pool Management
- Storage Engines
- Vacuuming and Maintenance

## 2.5 Distributed Databases & Scaling
- Replication
  - Primary-Replica (Master-Slave)
  - Multi-Primary (Master-Master)
  - Synchronous vs Asynchronous
- Read Replicas
- Sharding
- Horizontal / Vertical Partitioning
- CAP Theorem
  - Consistency
  - Availability
  - Partition Tolerance
- ACID vs BASE
- Distributed Transactions (overview)

## 2.6 Database Types & Engines

### Relational Databases (SQL)
- MySQL
- PostgreSQL
- Microsoft SQL Server
- SQLite
- Oracle Database

### Non-Relational Databases (NoSQL)
- Document Stores
  - MongoDB
  - CouchDB
- Key-Value Stores
  - Redis
  - Amazon DynamoDB
- Graph Databases
  - Neo4j
  - Amazon Neptune
- Time-Series Databases
  - InfluxDB
  - TimescaleDB
- Column-Family / Wide-Column Stores
  - Apache Cassandra
  - HBase
- Object-Oriented DBMS
  - db4o
  - ObjectDB

---

# 03 — Object-Oriented Design (OOD)

## 3.1 OOP Fundamentals
- Encapsulation
- Abstraction
- Inheritance
  - Single
  - Multiple
  - Multilevel
  - Hierarchical
  - Hybrid
- Polymorphism
  - Runtime Polymorphism
  - Overriding
  - Compile-Time Polymorphism
  - Method Overloading
  - Operator Overloading
- Access Modifiers
  - Public
  - Private
  - Protected
  - Protocol / Interface concepts
- Classes and Objects
- Composition

## 3.2 Object Relationships
- Association
- Aggregation
- Composition
- Inheritance
- Realization
- Dependency

## 3.3 Design Principles

### SOLID Principles
- Single Responsibility Principle
- Open/Closed Principle
- Liskov Substitution Principle
- Interface Segregation Principle
- Dependency Inversion Principle

### General Principles
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple, Stupid)
- YAGNI (You Aren't Gonna Need It)
- Separation of Concerns
- Encapsulate What Varies
- Favor Composition Over Inheritance
- Law of Demeter (Principle of Least Knowledge)
- POLA (Principle of Least Astonishment)
- Cohesion & Coupling
  - High Cohesion
  - Low Coupling

## 3.4 GoF Design Patterns

### Creational Patterns (5)
- Singleton
- Factory Method
- Abstract Factory
- Builder
- Prototype

### Structural Patterns (7)
- Adapter
- Bridge
- Composite
- Decorator
- Facade
- Flyweight
- Proxy

### Behavioral Patterns (11)
- Chain of Responsibility
- Command
- Interpreter
- Iterator
- Mediator
- Memento
- Observer
- State
- Strategy
- Template Method
- Visitor

## 3.5 UML & Object Modeling
- Class Diagram
- Use Case Diagram
- Sequence Diagram
- Activity Diagram
- State Machine Diagram
- Object / Domain Modeling

---

# 04 — Application Architecture

## 4.1 Architectural Styles
- Layered Architecture (N-Tier)
- Monolithic Architecture
- Modular Monolith
- Client-Server Architecture
- Microservices Architecture
- Service-Oriented Architecture (SOA)
- Event-Driven Architecture (EDA)
- Serverless Architecture / FaaS
- Pipe-and-Filter Architecture
- Microkernel / Plugin Architecture

## 4.2 Architectural Patterns
- Clean Architecture (Uncle Bob)
- Hexagonal Architecture (Ports and Adapters)
- Onion Architecture
- Model-View-Controller (MVC)
- Model-View-Presenter (MVP)
- Model-View-ViewModel (MVVM)

## 4.3 Core Concepts & Principles
- Separation of Concerns (SoC)
- Domain-Driven Design (DDD) Integration
- Inversion of Control (IoC)
- Dependency Injection (DI)
- Dependency Inversion
- Ports and Adapters (Interfaces and Implementations)
- Boundary Management
- Dependency Rules
- Data Transfer Objects (DTOs)
- Mappers
- Decoupling Business Logic from Infrastructure
  - Databases
  - Frameworks
  - External APIs
- High Cohesion / Low Coupling
- Testability and Modifiability
- Architectural Trade-offs

## 4.4 Application Organization
- Modularization
- Module Boundaries
- Package by Layer
- Package by Feature
- Component-Based Design
- Plugin Architecture
- Internal vs External Interfaces

## 4.5 Integration Architecture
- API Integration
- Synchronous vs Asynchronous Communication
- Point-to-Point Integration
- Hub-and-Spoke
- Enterprise Service Bus (ESB)
- API-Led Connectivity
- Event-Driven Integration
- Canonical Data Model

---

# 05 — Presentation Architecture

## 5.1 Core Architectural Patterns
- MVC (Model-View-Controller)
- MVP (Model-View-Presenter)
- MVVM (Model-View-ViewModel)

## 5.2 Advanced & Mobile-Specific Patterns
- VIPER (View-Interactor-Presenter-Entity-Router)
- MVI (Model-View-Intent)

## 5.3 Modern Frontend & Component Architectures
- Component-Based Architecture
  - React
  - Vue
  - Svelte
  - Angular
- Container / Presentational Components
- Smart / Dumb Components
- Unidirectional Data Flow
- Flux Pattern
  - Redux
  - NgRx
  - Pinia

## 5.4 State Management & Reactive Patterns
- Local State
- Global State
- State Management
- Reactive State
- Observable
- Immutable State
- BLoC
- Provider
- Riverpod
- Signals

## 5.5 Core Concepts & Mechanisms
- Data Binding
  - One-Way Binding
  - Two-Way Binding
- Event Handling
- State Management & Reactivity
- Separation of UI Rendering from Business Logic
- Navigation
- UI State
- Rendering Lifecycle

---

# 06 — Patterns of Enterprise Application Architecture (PoEAA)

> Reference classification: Martin Fowler's Patterns of Enterprise Application Architecture. Pattern names are retained, with spelling and grouping normalized. Some patterns have relationships or subtypes; those are noted below.

## 6.1 Domain Logic Patterns (4)
- Transaction Script
- Domain Model
- Table Module
- Service Layer

## 6.2 Data Source Architectural Patterns (4)
- Table Data Gateway
- Row Data Gateway
- Active Record
- Data Mapper

## 6.3 Object-Relational Behavioral Patterns (3)
- Unit of Work
- Identity Map
- Lazy Load

## 6.4 Object-Relational Structural Patterns
- Identity Field
- Foreign Key Mapping
- Association Table Mapping
- Dependent Mapping
- Embedded Value
- Serialized LOB
- Inheritance Mappers
  - Single Table Inheritance
  - Class Table Inheritance
  - Concrete Table Inheritance

## 6.5 Object-Relational Metadata Mapping Patterns (3)
- Metadata Mapping
- Query Object
- Repository

## 6.6 Web Presentation Patterns (7)
- Model View Controller
- Page Controller
- Front Controller
- Template View
- Transform View
- Two-Step View
- Application Controller

## 6.7 Distribution Patterns (2)
- Remote Facade
- Data Transfer Object (DTO)

## 6.8 Offline Concurrency Patterns (4)
- Optimistic Offline Lock
- Pessimistic Offline Lock
- Coarse-Grained Lock
- Implicit Lock

## 6.9 Session State Patterns (3)
- Client Session State
- Server Session State
- Database Session State

## 6.10 Base Patterns (11)
- Gateway
- Service Stub
- Mapper
- Layer Supertype
- Separated Interface
- Registry
- Value Object
- Money
- Special Case
- Plugin
- Record Set

---

# 07 — Domain-Driven Design (DDD)

## 7.1 Strategic DDD

### Domain Understanding
- Domain
- Subdomains
  - Core Domain
  - Supporting Subdomain
  - Generic Subdomain
- Ubiquitous Language

### Model Boundaries
- Bounded Context
- Context Map

### Context Mapping Patterns
- Partnership
- Shared Kernel
- Customer-Supplier
- Conformist
- Anti-Corruption Layer
- Open Host Service
- Published Language
- Separate Ways
- Big Ball of Mud

## 7.2 Tactical DDD
- Entity
- Value Object
- Aggregate
- Aggregate Root
- Repository
- Domain Service
- Domain Event
- Factory
- Application Service

## 7.3 DDD Implementation & Modeling Concepts
- Domain Model
- Domain Layer
- Application Layer
- Infrastructure Layer
- Invariants
- Aggregate Boundaries
- Transaction Boundaries
- Domain Event vs Integration Event
- Eventual Consistency
- Anti-Corruption Layer Implementation

---

# 08 — Concurrency Patterns

> This section intentionally includes design patterns, concurrency primitives, algorithms, and implementation techniques. They are related, but they are not all patterns in the strict GoF sense.

## 8.1 Task Execution & Scheduling
**السؤال: إزاي أشغّل الـTasks وأوزعها على الـWorkers؟**
- Thread-per-Task — Thread لكل مهمة
- Thread Pool — مجموعة Threads يعاد استخدامها
- Worker Thread — Worker يستقبل وينفذ المهام
- Producer–Consumer — فصل الإنتاج عن الاستهلاك
- Master–Worker — Master يوزع العمل
- Task Farm — مجموعة Workers تنفذ مهام مستقلة
- Thread-per-Request — Thread لكل Request
- Thread-per-Session — Thread لكل Session
- Work Stealing — سرقة المهام من Workers مشغولين
- Fork–Join — تقسيم المهمة وتجميع النتائج
- Task Scheduling — جدولة المهام
- Future / Promise — تمثيل نتيجة مستقبلية
- Task Cancellation — إلغاء المهام
- Timeout — تحديد وقت أقصى للتنفيذ
- Executor Pattern
- Structured Concurrency

## 8.2 Synchronization Patterns
**السؤال: إزاي أنظم الوصول إلى الموارد المشتركة وأمنع التضارب؟**
- Monitor Object — حماية حالة Object وتنظيم الوصول
- Scoped Locking — تحديد نطاق القفل
- Strategized Locking — اختيار استراتيجية القفل
- Read–Write Lock — تعدد القراءات وانفراد الكتابة
- Lock Splitting — تقسيم القفل الكبير
- Lock Striping — توزيع الأقفال على مجموعات
- Double-Checked Locking — تقليل تكلفة التهيئة المقفولة
- Fixed Lock Ordering — ترتيب اكتساب الأقفال
- Guarded Suspension — الانتظار حتى تحقق شرط
- Balking — رفض العملية عند عدم ملاءمة الحالة

## 8.3 Coordination & Synchronization Primitives
**السؤال: إزاي أخلي مجموعة Threads تتعاون وتنتظر بعضها؟**
- Mutex — السماح لمشارك واحد بالدخول
- Semaphore — تحديد عدد المشاركين
- Condition Variable — انتظار تحقق شرط
- Barrier — انتظار وصول الجميع
- CountDown Latch — انتظار اكتمال عدد أحداث
- Event — الإشارة لحدوث حدث
- Rendezvous — التقاء المشاركين عند نقطة مشتركة
- Thread Join — انتظار انتهاء Thread
- Message Passing — تبادل الرسائل
- Blocking Queue — Queue تدعم الانتظار

## 8.4 Event Handling & Asynchronous Architecture
**السؤال: إزاي أتعامل مع الأحداث والطلبات دون حجز Thread لكل عملية؟**
- Active Object — فصل الطلب عن التنفيذ
- Reactor — استقبال الأحداث وتوجيهها للمعالجات
- Proactor — التعامل مع نتائج العمليات غير المتزامنة
- Half-Sync / Half-Async — فصل المعالجة المتزامنة عن غير المتزامنة
- Leader / Followers — تنظيم استقبال الأحداث ومعالجتها
- Acceptor–Connector — فصل إنشاء الاتصالات عن الخدمات
- Callback — استدعاء دالة عند اكتمال حدث
- Asynchronous Completion Token — ربط العملية بسياقها عند اكتمالها
- Actor Model — وحدات مستقلة تتواصل بالرسائل
- Event Loop

## 8.5 Parallel Computing Patterns
**السؤال: إزاي أقسم المشكلة الحسابية لتتنفذ بالتوازي؟**
- Task Parallelism — مهام مختلفة بالتوازي
- Data Parallelism — نفس العملية على بيانات مختلفة
- Divide and Conquer — تقسيم المشكلة لمشكلات أصغر
- Fork–Join — تشغيل الأجزاء وتجميعها
- Pipeline — توزيع المعالجة على مراحل
- Map–Reduce — تحويل البيانات وتجميع النتائج
- Loop Parallelism — تقسيم دورات التكرار
- Geometric Decomposition — تقسيم البيانات مكانيًا
- Stencil — الحساب بالاعتماد على العناصر المجاورة
- Speculative Execution — تنفيذ احتمالات مسبقًا
- Reduction — تجميع النتائج الجزئية

## 8.6 Shared State & Thread Safety
**السؤال: إزاي أحافظ على سلامة البيانات مع وجود عدة Threads؟**
- Thread Confinement — تخصيص البيانات لـThread واحد
- Thread-Specific Storage — بيانات مستقلة لكل Thread
- Immutable Objects — كائنات غير قابلة للتعديل
- Safe Publication — نشر الكائن بطريقة آمنة
- Copy-on-Write — النسخ عند التعديل
- Atomic Operations — عمليات ذرية
- Lock-Free Algorithms — خوارزميات دون أقفال تقليدية
- Wait-Free Algorithms — ضمان تقدم كل عملية خلال خطوات محدودة
- Optimistic Concurrency Control — اكتشاف التعارض بدل القفل المسبق
- Versioned State — تتبع إصدارات الحالة

## 8.7 Flow Control & Performance
**السؤال: إزاي أتحكم في تدفق المهام وأقلل التكلفة؟**
- Batching / Bulking — تجميع العمليات
- Buffering — التخزين المؤقت
- Bounded Queue — تحديد سعة قائمة الانتظار
- Backpressure — إبطاء المنتج عند زيادة الحمل
- Rate Limiting — تحديد معدل الطلبات
- Load Balancing — توزيع الأحمال
- Throttling — التحكم في سرعة التنفيذ
- Debouncing — دمج الأحداث المتقاربة زمنيًا
- Coalescing — دمج العمليات المتشابهة
- Caching — تقليل تكرار العمل
- Work Stealing — تحسين استغلال الـWorkers

## 8.8 Distributed Concurrency Patterns
**السؤال: إزاي أطبق مفاهيم التزامن على Nodes وخدمات مختلفة؟**
- Leader Election — انتخاب قائد
- Distributed Lock — قفل موزع
- Distributed Semaphore — Semaphore موزع
- Lease — امتلاك مورد لفترة
- Fencing Token — منع الكتابة من مالك قديم
- Distributed Coordination — تنسيق بين Nodes
- Consensus — الوصول لاتفاق بين المشاركين
- Idempotency — أمان إعادة تنفيذ العملية
- Saga — تنسيق معاملات موزعة
- Competing Consumers — استهلاك الرسائل بالتنافس
- Message Ordering — ضمان ترتيب الرسائل
- Duplicate Detection — اكتشاف الرسائل المكررة

---

# 09 — Enterprise Integration Patterns (EIP)

> The original EIP catalog is organized into seven groups. The core catalog is listed first. A separate section contains complementary patterns and modern integration practices that are useful in real systems but are not all entries in the original EIP catalog.

## 9.1 Messaging Systems
- Message
- Message Channel
- Pipes and Filters
- Message Router
- Message Translator
- Message Endpoint
- Messaging Bridge
- Message Bus

## 9.2 Messaging Channels
- Point-to-Point Channel
- Publish-Subscribe Channel
- Datatype Channel
- Invalid Message Channel
- Dead Letter Channel
- Guaranteed Delivery
- Channel Adapter
- Messaging Bridge
- Message Bus

## 9.3 Message Construction
- Command Message
- Document Message
- Event Message
- Request-Reply
- Return Address
- Correlation Identifier
- Message Sequence
- Message Expiration
- Format Indicator

## 9.4 Message Routing
- Content-Based Router
- Message Filter
- Dynamic Router
- Recipient List
- Splitter
- Aggregator
- Resequencer
- Routing Slip
- Process Manager
- Message Broker

## 9.5 Message Transformation
- Envelope Wrapper
- Content Enricher
- Content Filter
- Claim Check
- Normalizer
- Canonical Data Model

## 9.6 Messaging Endpoints
- Messaging Gateway
- Messaging Mapper
- Transactional Client
- Polling Consumer
- Event-Driven Consumer
- Competing Consumers
- Message Dispatcher
- Selective Consumer
- Durable Subscriber
- Idempotent Receiver
- Service Activator
- Business Delegate
- Request-Reply
- Sync/Async Bridge

## 9.7 System Management
- Control Bus
- Wire Tap
- Message History
- Message Store
- Smart Proxy
- Test Message
- Channel Purger

## 9.8 Complementary Integration & Messaging Patterns
> These are complementary patterns and practices. Do not treat this list as an extension of the original seven-group EIP catalog without qualification.

### Reliability & Delivery
- Transactional Outbox
- Transactional Inbox
- Idempotent Consumer
- Retry Pattern
- Delayed Retry
- Exponential Backoff
- Dead Letter Queue Processing
- Poison Message Handling
- Duplicate Message Detection
- Message Deduplication
- Message Ordering
- At-most-once Delivery
- At-least-once Delivery
- Exactly-once Processing Semantics

### Event-Driven Integration
- Event Notification
- Event-Carried State Transfer
- Event Sourcing
- Event Streaming
- Event Collaboration
- Domain Event vs Integration Event

### Distributed Workflow & Coordination
- Saga
- Choreography
- Orchestration
- Process Manager
- CQRS
- Request-Reply Messaging

### Observability & Operations
- Distributed Tracing
- Correlation ID Propagation
- Message Auditing
- Replay / Reprocessing
- Backpressure
- Rate Limiting
- Circuit Breaker (integration resilience)
- Timeout and Bulkhead (integration resilience)

## 9.9 Integration Concepts to Understand
- Synchronous vs Asynchronous Messaging
- Queue vs Topic
- Broker vs Brokerless Messaging
- Message Schema / Schema Evolution
- Serialization / Deserialization
- Message Contract
- Consumer Groups
- Delivery Guarantees
- Ordering Guarantees
- Retry Policies
- Dead Letter Queues
- Idempotency
- Eventual Consistency

---

# 10 — System Design

## 10.1 System Design Fundamentals
- What is System Design?
- Functional vs Non-Functional Requirements
- Scalability
- Reliability
- Availability
- Maintainability
- Performance
- Consistency
- Latency vs Throughput
- Capacity Estimation
- Load Estimation
- Back-of-the-Envelope Calculations
- Quality Attributes and Trade-offs
  - Modifiability
  - Testability
  - Extensibility
  - Portability
  - Interoperability
  - Security

## 10.2 Networking & Communication
- OSI Model
- TCP/IP Model
- HTTP / HTTPS
- TCP vs UDP
- TCP Handshake
- Connection Lifecycle
- REST vs SOAP
- gRPC
- WebSockets
- Long Polling
- DNS
- CDN
- Reverse Proxy
- Forward Proxy
- NAT
- API Gateway
- Connection Pooling
- Rate Limiting
- Throttling
- TLS

## 10.3 Data Storage (Databases)

### Relational Databases
- MySQL / PostgreSQL
- ACID
- Indexes
- Transactions
- Normalization vs Denormalization
- Read Replicas
- Sharding

### NoSQL Databases
- Key-Value (Redis, DynamoDB)
- Document (MongoDB)
- Column Family (Cassandra)
- Graph DB (Neo4j)

### CAP Theorem
- Consistency
- Availability
- Partition Tolerance

### Database Design
- Schema Design
- Data Modeling
- Hot Partitions
- Data Migration
- OLTP vs OLAP
- Data Warehouse
- Read Models

## 10.4 Caching
- What is Caching?
- Cache vs DB
- Cache Hit / Miss
- Cache Eviction Policies
  - LRU
  - LFU
  - FIFO
- Cache-Aside
- Read-Through
- Write-Through
- Write-Back
- Write-Around
- Redis
- Memcached
- CDN Caching
- Cache Invalidation

## 10.5 Scalability Patterns
- Vertical Scaling
- Horizontal Scaling
- Stateless Services
- Stateful Services
- Load Balancing
  - Round Robin
  - Least Connections
  - Hash-based
  - Consistent Hashing
- Auto Scaling
- Sharding Strategies
- Partitioning

## 10.6 Distributed Systems Concepts
- Distributed Systems Basics
- Consistency Models
  - Strong Consistency
  - Eventual Consistency
  - Causal Consistency
- Leader Election
- Consensus Algorithms
  - Paxos
  - Raft
- Clock Synchronization
- Logical Clocks
- Vector Clocks
- Distributed Locks
- Idempotency
- Split Brain
- Quorum
- Failure Detection

## 10.7 Messaging & Async Processing
- Message Queues
- Kafka
- RabbitMQ
- SQS
- Pub/Sub
- Event-Driven Architecture
- At-most-once Delivery
- At-least-once Delivery
- Exactly-once Semantics
- Dead Letter Queues
- Backpressure
- Message Ordering
- Consumer Groups
- Transactional Outbox / Inbox

## 10.8 Microservices Architecture
- Monolith vs Microservices
- Modular Monolith
- Service Discovery
- Inter-Service Communication
- API Gateway
- Backend for Frontend (BFF)
- Circuit Breaker
- Retry & Timeout
- Bulkhead
- Saga Pattern
- Choreography vs Orchestration
- Data per Service
- Database per Service
- Microservices Anti-Patterns
- Strangler Fig Pattern
- Service Mesh
- Anti-Corruption Layer

## 10.9 Security
- Authentication
- Authorization
- OAuth 2.0
- OpenID Connect (OIDC)
- JWT
- SSO
- HTTPS / TLS
- Encryption at Rest / In Transit
- Rate Limiting
- DDoS Protection
- Secrets Management
- RBAC
- ABAC
- Least Privilege

## 10.10 High Availability & Reliability
- Single Point of Failure
- Replication
- Failover
- Health Checks
- Heartbeats
- Graceful Degradation
- Disaster Recovery
- Backup Strategies
- RTO / RPO
- Fault Tolerance
- Redundancy
- Retry and Timeout
- Failure Isolation

## 10.11 Observability & Monitoring
- Logging
- Metrics
- Monitoring
- Distributed Tracing
- Alerting
- SLIs / SLOs / SLAs
- Prometheus
- Grafana
- ELK Stack
- OpenTelemetry

## 10.12 Design Patterns (System Level)
- Singleton
- Factory
- Observer
- CQRS
- Event Sourcing
- Bulkhead
- Sidecar
- Ambassador
- Strangler Fig Pattern
- API Composition
- Cell-Based Architecture

## 10.13 Data Processing
- Batch Processing
- Stream Processing
- ETL
- ELT
- MapReduce
- Spark
- Flink
- Data Pipelines
- Data Warehouse

## 10.14 Cloud & Infrastructure
- IaaS / PaaS / SaaS
- AWS / GCP / Azure Concepts
- Containers (Docker)
- Kubernetes
- CI / CD
- Infrastructure as Code
- Terraform
- Service Mesh
- Container Orchestration

## 10.15 Common System Design Interview Problems
- Design URL Shortener
- Design WhatsApp
- Design Twitter
- Design Instagram
- Design YouTube
- Design Netflix
- Design Uber
- Design Payment System
- Design Notification System
- Design Search Engine
- Design File Storage (Google Drive)
- Design E-commerce System
- Design Ticket Booking System
- Design Rate Limiter
- Design Distributed Job Scheduler
- Design Logging System

---

# Supporting Foundations

These topics support multiple roadmap pillars. They are not replacements for the ten main sections.

## A. Software Engineering Practices
- Clean Code
- Refactoring
- Code Smells
- Technical Debt
- Defensive Programming
- Error Handling
- Logging
- Unit Testing
- Integration Testing
- End-to-End Testing
- Test-Driven Development (TDD)
- Behavior-Driven Development (BDD)
- Test Doubles
  - Mocks
  - Stubs
  - Fakes
- Code Review
- Version Control (Git)
- CI / CD

## B. Operating Systems Fundamentals
- Process vs Thread
- Process Scheduling
- Context Switching
- User Mode vs Kernel Mode
- Memory Management
- Virtual Memory
- Stack vs Heap
- Mutex / Semaphore
- Inter-Process Communication (IPC)
- CPU-bound vs I/O-bound
- Deadlocks
- Race Conditions
- File Descriptors
- System Calls

## C. Computer Networking Fundamentals
- OSI Model
- TCP/IP Model
- IP Addressing
- Subnetting
- TCP Handshake
- Connection Lifecycle
- DNS
- TLS
- HTTP Internals
- Keep-Alive
- Connection Pooling
- Socket Programming
- Routing Basics

---

# Cross-Topic Relationships & Study Notes

## OOD vs PoEAA vs DDD
- **OOD** focuses on designing objects, responsibilities, relationships, and reusable design.
- **PoEAA** provides patterns for implementing enterprise application logic, persistence, presentation, distribution, and concurrency.
- **DDD** focuses on understanding and modeling complex business domains and defining meaningful domain boundaries.
- These areas complement one another; none is a direct replacement for the others.

## Application Architecture vs Presentation Architecture
- **Application Architecture** organizes the application as a whole: modules, layers, dependencies, boundaries, and infrastructure.
- **Presentation Architecture** organizes the UI layer: views, presenters, view models, state, rendering, and user interaction.
- MVC can appear in both discussions because it can be studied at different levels and for different concerns.

## Concurrency vs EIP
- **Concurrency** concerns coordinating tasks and accessing shared resources safely, within a process or across distributed nodes.
- **EIP** concerns communication and integration between independent applications or services through messages.
- Related ideas can appear in both areas, but the concepts are not interchangeable.

## EIP vs System Design
- **EIP** focuses on message-based integration patterns and the mechanics of routing, transforming, constructing, and consuming messages.
- **System Design** uses messaging and integration as part of a larger system, alongside storage, networking, scaling, reliability, security, and operations.

## Suggested Practical Project
Use one evolving E-commerce / Order Management System to connect the roadmap:
- DSA: search, filtering, and data-processing problems.
- OOD: Product, Order, Payment, Inventory objects and responsibilities.
- DBMS: schema, transactions, indexes, and concurrency.
- Application Architecture: modules, layers, boundaries, and dependencies.
- Presentation Architecture: UI state and presentation flow.
- PoEAA: Repository, Unit of Work, Service Layer, Data Mapper.
- DDD: Order Aggregate, bounded contexts, domain events.
- Concurrency: inventory race conditions and safe task execution.
- EIP: Order, Payment, and Inventory message flows.
- System Design: scaling, availability, observability, and distributed deployment.

---

# Recommended Study Strategy

For every topic or pattern, document:
1. **What is it?**
2. **What problem does it solve?**
3. **Why does that problem happen?**
4. **How does the solution work?**
5. **When should it be used?**
6. **When should it not be used?**
7. **What are its trade-offs?**
8. **What is it similar to, and how is it different?**
9. **How can it be implemented in Python?**
10. **Where can it appear in a real backend system?**

> Keep the original topic tracker and problem lists as the source of study progress. Add practical implementation and trade-off analysis as a second layer, rather than turning the roadmap into a list of definitions to memorize.
