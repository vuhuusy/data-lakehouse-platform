#!/usr/bin/env bash

set -e

/opt/bootstrap.sh
/opt/hive-metastore/bin/start-metastore -p 9083
