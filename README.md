Providing highly available database services on S3 or other compatible storage. This is done by synchronising nodes in a local network to work together with PubSub updates on DB modifications and distributed locking with the requirement of all participating nodes in a single repository having communication to each-other with zeroconf. S3 or other compatible storage must be strict read-after-write and list-after-write consistent.

Supported paradigms:
- Relational
- Timeseries
- Document
- Graph

Recommended setup; Local MinIO instance with replication to cloud S3 or other compatible storage for high availability, low latency and avoiding costs related to lots of IO operations. It might also be suited for low volume work directly directly on the cloud or even high volume depending on cost appetites.

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


Storage paths are as follows (from root):
- indexes/ -> Holds B-Tree and HashMap indexes for each partition
- partitions/ -> Where the data for each partition resides by prefix/filename.ext
- metadata/ (or put into a relational databases)-> Holds object metadata like the following:
    - version
    - sha256
    - last modified
    - creation time
    - is it latest


Additionally, the capability of mounting storage into a FUSE layer will be necessary, especially when running VMs. Caching large files will have to be worked out on the client side... and acknowledges of writes will likely not be synchronous... but that should be fine if the VM is a journaling file system?

Amusingly, I don't think S3 scaling capacity is the first bottleneck, it'll be sheer internet speed and latency, perhaps options can be had for using multiple internet connections simultaneously.

DISCLAIMER: The author takes no responsibility for costs incurred by the usage of this project, there is no explicit or implied warranty