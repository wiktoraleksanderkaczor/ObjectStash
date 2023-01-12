Providing highly available database services on S3 or other compatible storage. This is done by synchronising nodes in a local network to work together with PubSub updates on DB modifications and distributed locking with the requirement of all participating nodes in a single repository having communication to each-other with zeroconf. S3 or other compatible storage must be strict read-after-write and list-after-write consistent.

Supported paradigms:
- Relational
- Timeseries
- Document
- Graph

Recommended setup; Local MinIO instance with replication to cloud S3 or other compatible storage for high availability, low latency and avoiding costs related to lots of IO operations. It might also be suited for low volume work directly directly on the cloud or even high volume depending on cost appetites. Finally, it has the ability to run in a serverless environment assuming an external synchronization store, since AWS lambdas would not have network communication with each other.

Additional info:
- Each instance runs and uses a replicated Python object with RAFT consensus... this shares indexes which saves on storage queries, allows pubsub and distributed locking as well as caching most used data.
- Discovery of other instances for coordination of distributed object happens through ZeroConf
- Multiple instance lock consensus is handled by RAFT, simple.

https://pypi.org/project/pysyncobj/

Database indexes are made using B-Tree or HashMap:
https://stackoverflow.com/questions/3909602/is-there-a-b-tree-database-or-framework-in-python
https://chartio.com/learn/databases/how-does-indexing-work/
https://en.wikipedia.org/wiki/Database_index
https://pypi.org/project/zeroconf/


Additionally, the capability of mounting storage into a FUSE layer will be necessary, especially when running VMs. Caching large files will have to be worked out on the client side... and acknowledges of writes will likely not be synchronous... but that should be fine if the VM is a journaling file system?

Streams will be implemented over PyFuse, too much bullshit otherwise...

DISCLAIMER: The author takes no responsibility for costs incurred by the usage of this project, there is no explicit or implied warranty