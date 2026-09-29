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

The computation is `distance = sum((query[i] - template[i]) ** 2)`.

The initial baseline opens the final distance to the coordinator and performs
the threshold comparison there. This protects feature vectors from any one
honest-but-curious party, but does not yet provide private comparison or
malicious security.

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

The prototype assumes semi-honest parties and no collusion. Each party sees
only additive shares and Beaver-round masks. All three parties can reconstruct
the inputs if they collude. There is no malicious-security verification, TLS,
client authentication, replay protection, or fault tolerance. The coordinator
receives the final distance, so this is an educational MPC baseline rather than
a deployable biometric authenticator.
