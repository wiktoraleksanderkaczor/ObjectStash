# Cluster-in-a-box (ephemeral and/or stateful)
Motivation: I got tired of maintaining reliable compute, storage and service environments, either for personal use or development work. Multiple libraries used in software development are annoying to keep up-to-date, sometimes unavailable on different platforms, etc. I also do not want to pay for cloud services where it is not necessary, and I don't want to maintain the servers required. Configurability of how uptime is maintained and somewhat weird use cases are also a factor.

Solution: This project aims to provide a simple, easy to use, highly available and scalable but insecure by default (for simplicity, possible development later) environment for running your own cloud, everything from a single computer to highly distributed heterogenous networks of commodity computers. It is designed to be used as a personal cloud, or as a development environment, anything from personal storage to automatically clustered machine learning. All with the reliability of a cloud provider, but with the control of a local network.

What can it run on: Anything, hybrid, multi-cloud, multi-paradigm (machines, serverless, containers, VMs, etc.). Some features requiring specific backend capabilities like reliable storage, compute, networking, etc. will be disabled if no available backend supports them. For example, an external state store and at least one always-on manager is required for serverless functions.

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
- Human readable everything (if possible, storage, configuration, logs, etc.)
- Independence, autonomy, and self-sufficiency (anything required by the cluster should be provided by the cluster)
- Keep it simple stupid (KISS)
- Do not repeat yourself (DRY)
- Reinvent the wheel if necessary
- Over-engineer for future use
- Do not over-optimize (premature optimization is the root of all evil)
- Do not over-document (code should be self-documenting, or documentation should be generated from code and comments)
- Security as a second-class citizen (holes can be patched later, better to have a working [instead of a secure] system)
- Transparent wrapping for additional functionality
- Functionality not provided by the backend should be provided by the software or cluster (e.g. S3 locking or streams over FUSE)

Action: This is done by synchronising nodes over any network to work together, cooperatively, no masters, replicas etc. A single package of software and programming library. If you've got the authentication, you can do whatever the environment supports.

Reliability:
- This software is not magic, if all nodes go down, the cluster is down
- If any node is compromised, the entire cluster is compromised (at least right now)
- RAFT consensus... it still suffers from the CAP theorem
- Discovery of other instances for coordination of distributed object happens through ZeroConf
- Multiple instance lock consensus is handled by RAFT, simple.

Configuration:
- Centralized configuration with replication
- As simple as possible
- Sensible defaults but configurable
- Changeable at runtime

#### Developer setup
- Ensure Linux-based system with working Docker installation
- VSCode will take care of setup with 'devcontainers'
- Use 'drone exec' to run pipeline locally
- Ensure pipeline passed before commit, pipelines checked on git hook

DISCLAIMER: The author takes no responsibility for costs incurred by the usage of this project, there is no explicit or implied warranty
