#!/bin/bash
docker cp . wvi_database:/utils
docker exec -it wvi_database cqlsh -f utils/setup_keyspace.cql