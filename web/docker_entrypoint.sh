#!/bin/bash

./wait_for_it.sh -t 100 elasticsearch:9200 
./provision_clusters.sh
exec "$@"
