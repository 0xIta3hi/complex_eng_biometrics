# Essential Technical Concepts

## 1. Biometric Authentication

* Biometric authentication
* Biometric template vs raw biometric
* Feature extraction
* Feature vector
* Enrollment vs authentication
* Biometric matching
* FAR, FRR, EER
* Authentication threshold
* Euclidean distance

## 2. Mathematical Foundation

* Vectors and vector operations

* Squared Euclidean distance

  `D(x,y) = Σ(xᵢ − yᵢ)²`

* Modular arithmetic

* Finite fields / rings

* Basic computational complexity

* `O(n)` complexity

## 3. Secret Sharing

* What is secret sharing?
* Additive secret sharing
* Shares and reconstruction
* Secret sharing over a finite field/ring
* Why one share does not reveal the secret
* Collusion and reconstruction
* Threshold secret sharing
* Shamir's Secret Sharing — conceptually
* **Secret sharing vs SMPC**

## 4. Secure Multi-Party Computation

* What is SMPC?
* Parties and private inputs
* Computing on secret-shared data
* Privacy during computation
* What information is revealed
* Arithmetic circuits
* Communication rounds
* Computation vs communication cost

## 5. Secure Arithmetic

* Addition on secret shares
* Subtraction on secret shares
* Why multiplication is different
* Secure multiplication
* Beaver triples
* Offline/preprocessing phase
* Online computation phase

## 6. Private Biometric Matching

Understand exactly how this works:

**Input vectors**

* Query `x`
* Stored template `y`

**Computation**

* `x − y`
* `(x − y)²`
* Sum of squared differences

**Result**

* Secret-shared distance `D`

The team must understand how every step happens **without reconstructing `x` or `y`**.

## 7. Secure Comparison

* Why distance cannot simply be revealed
* Secret-shared threshold
* Comparison of secret-shared values
* Secure `<`, `>`, `≤` operations
* Secure decision bit
* Revealing only `ACCEPT/REJECT`
* Why comparison is harder than addition

## 8. Threat Model

* Honest-but-curious / semi-honest party
* Malicious party — basic concept
* Single-party compromise
* Collusion
* Number of parties that can be corrupted
* What our protocol protects against
* What our protocol does **not** protect against
* Availability / party failure

## 9. Distributed Architecture

* Distributed parties
* Independent processes
* Coordinator
* Party-to-party communication
* TCP/IP sockets
* Message passing
* Serialization
* Localhost distributed simulation
* Localhost vs physically distributed deployment

## 10. Communication Cost

This is particularly important because **communication efficiency is our research focus**.

* Communication rounds
* Number of messages
* Message size
* Total bytes transferred
* Network latency
* Bandwidth
* Round-trip time (RTT)
* Communication overhead
* Computation vs communication bottleneck
* Effect of feature-vector dimension
* Effect of number of parties

## 11. Performance Evaluation

* Authentication latency
* Throughput
* CPU usage
* Memory usage
* Communication volume
* Number of protocol rounds
* Feature-vector scalability
* Number-of-party scalability
* Concurrent authentication requests
* p50 / p95 / p99 latency
* Baseline vs SMPC performance

## 12. Experimental Evaluation

The team should understand why we perform:

* Centralized baseline
* Localhost SMPC experiment
* Feature-dimension scaling
* Party-count scaling
* Network-latency experiments
* Bandwidth-constrained experiments
* Concurrent-request experiments
* Party-failure experiments

And how to identify whether the bottleneck is:

**Computation → Communication → Network latency → Serialization → Protocol rounds**

## 13. Security & Privacy Boundaries

* What the client knows
* What Party 1 knows
* What Party 2 knows
* What Party 3 knows
* What the coordinator knows
* What information is never reconstructed
* What information is intentionally revealed
* Raw biometric privacy
* Feature-vector privacy
* Distance privacy
* Decision privacy

## 14. Protocol Flow

Everyone should be able to explain this without looking at the diagram:

**Enrollment**

`Biometric → Feature Extraction → Feature Vector → Secret Sharing → Parties`

**Authentication**

`Biometric → Feature Extraction → Query Vector → Secret Sharing → Parties`

**Matching**

`Secret-shared x,y → Secure Arithmetic → Secret-shared Distance`

**Decision**

`Secret-shared Distance + Secret-shared Threshold → Secure Comparison → ACCEPT/REJECT`

## 15. Critical Distinctions

These are highly likely professor questions:

| Concept                           | Must understand                                                                        |
| --------------------------------- | -------------------------------------------------------------------------------------- |
| Encryption vs Secret Sharing      | Encryption uses a key; secret sharing distributes information across shares            |
| Secret Sharing vs SMPC            | Secret sharing protects inputs; SMPC enables computation on those inputs               |
| Centralized vs SMPC               | One trusted server vs distributed trust                                                |
| Raw biometric vs feature vector   | Raw data is processed into a representation used for matching                          |
| Addition vs multiplication        | Addition can be performed locally on shares; multiplication requires a secure protocol |
| Distance vs decision              | Distance is sensitive intermediate information; decision is the required output        |
| Semi-honest vs malicious          | Follow protocol but inspect data vs actively deviate                                   |
| Latency vs throughput             | Time for an operation vs operations per unit time                                      |
| Computation vs communication cost | CPU work vs data exchanged between parties                                             |
| Localhost vs real distribution    | Same machine simulation vs real network deployment                                     |

## 16. Core Questions Every Team Member Must Answer

1. Why are we using SMPC for biometric authentication?
2. What exactly are we protecting?
3. What does each party receive?
4. Can one party reconstruct the biometric?
5. What happens if two parties collude?
6. Why isn't secret sharing alone enough?
7. How does additive secret sharing work?
8. How is addition performed on shares?
9. Why is multiplication harder?
10. What is a Beaver triple?
11. How do we calculate Euclidean distance privately?
12. Why shouldn't we reveal the distance?
13. How can we reveal only ACCEPT/REJECT?
14. Why is secure comparison difficult?
15. What is our threat model?
16. What happens if a party fails?
17. Where does communication occur?
18. What determines authentication latency?
19. Why does feature dimension matter?
20. What exactly makes our system **communication-efficient**?
21. What is our baseline?
22. What are our measurable metrics?
23. What is the project's actual research contribution?

## Minimum Knowledge Boundary

A team member does **not** need deep knowledge of:

* General malware analysis
* Web security
* OWASP
* General network security
* Deep learning
* Transformers
* General distributed-systems theory
* General cryptographic algorithms
* FHE
* Blockchain
* Zero Trust architecture
* General cloud architecture
* Advanced statistics
* Hardware/sensor engineering

They only need enough surrounding knowledge to understand the **SMPC biometric authentication pipeline** and defend the design decisions.

The core chain they should know is:

**Biometric → Feature Vector → Secret Sharing → Distributed Parties → Secure Arithmetic → Private Distance → Secure Comparison → ACCEPT/REJECT**

The research layer is:

**How do we minimize the communication and latency overhead introduced by this privacy-preserving computation?**
