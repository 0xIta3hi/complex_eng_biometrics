architectural glitches : if one server is compromised then what will happen, if we are basically sharing between 3 servers and if one server is compromised i get that the template won't be of any use to the hacker, but it also won't be of any use to me as well? or is there a way to keep the process going even if one part of the template is compromised.

Answer:

This depends on the sharing scheme and the threshold.

In a strict 3-of-3 additive secret-sharing scheme, the secret x is split as:

x = s1 + s2 + s3 (mod p)

Each server gets only one share. If one server is compromised, the attacker learns only one share, which is random-looking and by itself reveals no useful information about the biometric template. So confidentiality is preserved against a single compromise.

However, availability is affected: if one share is lost, corrupted, or unavailable, the complete template cannot be reconstructed unless all 3 shares are available. So the system may stop working or become unusable if one party goes offline. This is a tradeoff between privacy and fault tolerance.

This is why real systems usually use threshold secret sharing, such as 2-of-3 or 3-of-5 schemes. In a 2-of-3 design, any two shares can reconstruct the secret, while any one share alone reveals nothing. Then if one server is compromised, the attacker still learns nothing useful, and the system can continue using the remaining honest servers.

So the key point is:
- one compromised server does not reveal the full biometric
- but a 3-of-3 scheme does not tolerate server loss or failure well
- threshold schemes are used to preserve both privacy and service continuity

A single compromised server is not necessarily catastrophic for confidentiality, but it is a serious issue for availability and integrity unless the protocol includes fault-tolerance and malicious-server defenses.



- what about database security won't i have to manage 3 different database, if i am storing the template in 3 different servers on 3 different dbs.

Answer:

Usually yes, in a realistic multi-party design you do maintain separate storage per party, and that is a good security design rather than a flaw.

The important idea is that the biometric template should not exist in plaintext in one central database. Instead, each party stores only its own share. For example:

- Party 1 stores s1
- Party 2 stores s2
- Party 3 stores s3

If one database is leaked, the attacker gets only one share, not the full template.

This gives you a clean trust boundary:
- each party is responsible for its own database and access control
- each server should have independent credentials, keys, and auditing
- the databases should not be colocated in the same trust domain if you want real isolation

You do not necessarily need three different database vendors. You may use:
- three separate PostgreSQL databases
- three separate SQLite files
- three isolated storage partitions
- three machines each with their own local database

The important requirement is not the specific technology; it is that the shares are stored in separate trust domains and access is independently controlled.

So in a serious design, yes, you do expect multiple storage systems, and that is normal. The real architectural design goal is not to centralize the template, but to distribute trust.

A simple rule:
- one shared plaintext template = bad
- one share per party = good
- full reconstruction only when the required threshold of parties cooperate = correct design

This is the main reason multi-party biometric systems are more complex than single-server biometric storage: they trade central convenience for distributed trust and fault-tolerance.

