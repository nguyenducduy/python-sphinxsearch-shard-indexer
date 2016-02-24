# python-sphinxsearch-shard-indexer

* Working Centos 6.x
* Xenforo_post index has been shard to 8 index. Because limit max index size is 4GB.
* Include threshold when index match maximum index size (4GB).
* Indexer Delta will ben ru when not any indexer processing running on system. Because runing multi stack indexer with Sphinxsearch is imposible.
