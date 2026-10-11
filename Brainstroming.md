
The note for all the things in biometrics complex engineering problem that i find out about will be written here

# Brainstroming
1. what happens if one party is down?
2. If 3 parties are calculating the euclidian distance between X and Y via intercommunication, will they be in the same network or different networks work? also, if same network, one parties compromise will definately lead to other 2 parties compromise, cause the vulnerability would be the same in the same network. how will be prevent that, that's a threat.
3. When implementing a biometric system, the core worry is about latency and UX the system should not take lot of time (like 10seconds) to process the user input. what about the latency in this architecture.
4. If one share is corrupted when getting transfers, be it of user input or even worse, the template itself, what will happen?
5. How is CIA maintained in this architecture?
6. What about the DB security? If I am storing 3 different pieces of data in 3 different servers and 3 different databases, I have to deal with securing those databases as well, right?
7. at scale, handling this many biometric templates across 3 different servers- how computationally expensive will that get? I will need to add 3x whatever i am adding to a single database (if i am sizing 1 DB up, then i will need to size the other 2 as well)
8. Then how reliable is this system? if one server goes down, then how will the biometric calculations happen?

> 1.  What happens if one party is down?
>    It depends on the specific secret-sharing and SMPC protocol. If using additive secret-sharing, then all 3 parties are required to reconstruct the value. Using another method like shamir's secret sharing can prevent this. using it in a 2-of-3 configuration.
> 2. All party need not be in the same network. they can be in the same network, different networks/locations or have their own security domains. They just need network connectivity to exchange protocol messages.
> 3. Compromise of one party leading to compromise of other 2 party is a real threat. The defenses should be layered : 
> 	1. Network segmentation : restrict which party can communicate with which other party and on which ports.
> 	2. Mutual TLS, Least priviledge, Independent security controls, Hardened hosts and containers. These are some other layers of the security model. one last is
> 	3. SMPC security against collusion: select a protocol with explicit guarantees for the number of parties that may collude
> 4. Authentication latency depends on : time it takes to capture, extract, share, MPC, decision, network. It becomes an optimization problem from here.
> 5. if one share is corrupted there are 2 cases which can happen: 
> 	   1. Accidental corruption during transmission : TCP provides reliable, ordered byte-stream delivery and detects many transmission errors. It handles retransmission, but applications still need framing, timeouts and error handling. TCP alone is not a complete end-to-end security mechanism.
> 	   2. An attacker modifies a share or sends a false value :  A syntactically valid but incorrect share could cause the system to compute the wrong distance and potentially make an incorrect authentication decision. Encryption in transit does not, by itself, prevent an authorized but compromised party from sending malicious protocol messages.
> 6. Each DBs needs to be secured. this does not need additional maintainance to the company as there are multiple DBs which the company is assumed to maintain.
> 7. The Stoage overhead is a concern as it will surely require more storage comparing to storing a single template. But the computation requirement is not necessarily 3 times the original.
