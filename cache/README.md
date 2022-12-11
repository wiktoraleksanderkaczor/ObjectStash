This module defines a caching wrapper for database and storage clients. Essentially, whatever function is defined in the wrapper will take priority over what is defined in the actual client, consequently, existing wrappers can be modified by adding/replacing functions. 

Additional configuration options exist in the distribution of the cache, replacement policy for cache items and where it is persisted.

Cache persistence is handled by a storage client, side stepping the issue of a separate implementation. Consequently, a memory client is implemented for caching.

