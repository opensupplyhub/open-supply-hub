#!/bin/bash

function error_exit() {
  echo "$1" 1>&2
  exit 1
}

function check_deps() {
  test -f $(which jq) || error_exit "jq command not detected in path, please install it"
  test -f $(which aws) || error_exit "aws cli not detected in path, please install it"
}

function parse_input() {
  eval "$(jq -r '@sh "export DB_INSTANCE_IDENTIFIER=\(.db_instance_identifier)"')"
  if [[ -z "${DB_INSTANCE_IDENTIFIER}" ]]; then export DB_INSTANCE_IDENTIFIER=none; fi
}

function get_latest_snapshot_id() {
  instance_identifier="${DB_INSTANCE_IDENTIFIER}"
  export SNAPSHOT_ID=$(aws rds describe-db-snapshots --include-shared | jq --arg instance_identifier "$instance_identifier" '[.DBSnapshots[] | select(.DBInstanceIdentifier == $instance_identifier)][-1]' | jq '.DBSnapshotArn' |  tr -d '"\\')
}

function produce_output() {
  jq -n \
    --arg snapshot_id "${SNAPSHOT_ID}" \
    '{"id":$snapshot_id}'
}

check_deps
parse_input
get_latest_snapshot_id
produce_output
