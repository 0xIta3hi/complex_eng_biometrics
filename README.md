# Communication-Efficient Distributed Biometric Authentication

This repository contains a first-principles, localhost prototype of a three-party
arithmetic MPC computation. It is intentionally small enough to inspect line by
line.

## What is implemented

- Three independent party processes listening on `127.0.0.1:8001-8003`.
- Additive secret sharing over a prime field.
- Secret-shared query and template feature vectors.
- Beaver-triple multiplication for each squared difference.
- TCP message and byte-count instrumentation.
- A runnable authentication demo and a small benchmark.
- Synthetic enrollment using 2-of-3 Shamir shares stored in one JSON file per party.

The computation is `distance = sum((query[i] - template[i]) ** 2)`.

The initial baseline opens the final distance to the coordinator and performs
the threshold comparison there. This protects feature vectors from any one
honest-but-curious party, but does not yet provide private comparison or
malicious security.

The synthetic enrollment API is in `src.enrollment`. It can persist and
reconstruct an enrolled template from any two party share files. The existing
three-party additive MPC computation is still used after template retrieval;
full Shamir-compatible MPC and private threshold comparison remain future work.

## Run

Requires Python 3.10+ and no third-party packages. Start three terminals:

```bash
python -m src.party --party-id 0 --port 8001
python -m src.party --party-id 1 --port 8002
python -m src.party --party-id 2 --port 8003
```

Then run the demo in a fourth terminal:

```bash
python -m src.demo
```

For a dimension/latency baseline:

```bash
python -m src.benchmark --dimensions 8 32 128 --runs 10
```

## Security boundary

The prototype assumes semi-honest parties and no collusion. Enrollment uses
2-of-3 Shamir shares for storage recovery, but all three parties are still
required by the current additive MPC computation. Each party sees only its
stored share and protocol messages. There is no malicious-security verification,
TLS, client authentication, replay protection, or fault-tolerant MPC. The
coordinator receives the final distance internally, while the enrollment
authentication wrapper returns only the decision to its caller. This remains an
educational synthetic baseline rather than a deployable biometric authenticator.
