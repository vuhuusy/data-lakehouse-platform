#!/usr/bin/env bash

set -ex

SCRIPT_NAME="$(basename ${BASH_SOURCE[0]})"
CORE_SITE="/opt/hadoop/etc/hadoop/core-site.xml"
METASTORE_SITE="/opt/hive-metastore/conf/metastore-site.xml"

function info {
    echo "${SCRIPT_NAME} - [INFO]: $(date +"%Y-%m-%d_%T") - ${1}"
}

_bootstrap_config() {
    local config_file="$1"  # Get the filename from the argument
    if [ -f "$config_file" ]; then
        info "Processing $config_file"
        envsubst < "$config_file" > "$config_file.tmp"
        mv "$config_file.tmp" "$config_file"
    fi
}

_bootstrap_config "$CORE_SITE"
_bootstrap_config "$METASTORE_SITE"
