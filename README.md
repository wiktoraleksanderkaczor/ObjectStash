# Cluster-in-a-box (ephemeral and/or stateful)

You have a bunch of heterogenous computers you want to make into something resembling a highly-available cloud? You don't like centralized failure spots? You do like simple setup and scaling? This project is, hopefully, for you! It even comes with some odd use-case support, snoozing higher power computers when not in use. 

Features:
- Abstracted multiple-access storage (S3, NFS, etc.)
- Synchronization of data between nodes (replication, sharding etc.)
- Multi-paradigm database (relational, timeseries, document, graph, object etc.)

Roadmap (ranked):
- Compute (serverless, containers, [parallel] VMs, etc.)
- CI/CD service (container, local exec, etc.)
- Meshed high-utilization multi-adapter networking
- Device sharing (USB, display, audio etc.)
- Industry-standard adapters (SQL, REST, GraphQL, Redis, etc.)
- Enterprise services (Active Directory, proxies,  etc.)
- Authentication (private keys, certificates, etc.) and authorization (roles, permissions, etc.)
- Security (encryption, firewall, intrusion detection, overflow attacks, MFA etc.)
- Monitoring (metrics, logs, etc.)
- Backup and recovery (snapshots, etc.)
- Multi-tenancy (multiple users, organizations, etc.)
- Geographical location aware (multiple datacenters, etc.)
- Extensible (plugins, modules, etc.)
- Bootstraping (provisioning, configuration, network boot etc.)

Principles (biased):
- SOLID principles
- Keep it simple stupid (KISS)
- Do not repeat yourself (DRY)
- Transparent wrapping for additional functionality
- Human readable everything (if possible, storage, configuration, logs, etc.)
- Independence, autonomy, and self-sufficiency (anything required by the cluster should be provided by the cluster)
- Functionality not provided by the backend should be provided by the software or cluster (e.g. S3 locking or streams over FUSE)

Action: This is done by synchronising nodes over any network to work together, cooperatively, no masters, replicas etc. A single package of software and programming library. If you've got the authentication, you can do whatever the environment supports.

Reliability:
- This software is not magic, if all nodes go down, the cluster is down
- If any node is compromised, the entire cluster is compromised (at least right now)
- RAFT consensus... it still suffers from the CAP theorem
- Discovery of other instances for coordination of distributed object happens through ZeroConf

#### Developer setup
- Ensure Linux-based system with working Docker installation
- VSCode will take care of setup with 'devcontainers'
- Ensure pipeline passed before commit, checked on git hook

DISCLAIMER: The author takes no responsibility for costs incurred by the usage of this project, there is no explicit or implied warranty
