#!/usr/bin/env bash
#
# OSDEV-3531: helpers for reaching private resources through the bastion
# with AWS Systems Manager (Session Manager) instead of SSH, so tcp/22 can
# stay closed on the bastion security group.
#
# Usage:
#   ssm_tunnel.sh bastion-id
#       Print the instance ID of the bastion.
#   ssm_tunnel.sh start <remote_host> <remote_port> <local_port>
#       Open a port forward localhost:<local_port> -> <remote_host>:<remote_port>
#       through the bastion and return once it accepts connections. The
#       session keeps running in the background until `stop` is called or
#       the job ends.
#   ssm_tunnel.sh stop <local_port>
#       Close the port forward started for <local_port>.
#
# Environment:
#   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_DEFAULT_REGION
#       Credentials for the AWS account that owns the bastion.
#   ENVIRONMENT
#       Value of the bastion's Environment tag (e.g. Test, Production).
#   BASTION_INSTANCE_ID (optional)
#       Skip the tag lookup and use this instance ID.

set -euo pipefail

STATE_DIR="${RUNNER_TEMP:-/tmp}"
READY_TIMEOUT_SECONDS=90

log() { echo "[ssm] $*" >&2; }

ensure_plugin() {
  if command -v session-manager-plugin >/dev/null 2>&1; then
    return
  fi

  log "Installing the Session Manager plugin"
  local arch_dir
  case "$(uname -m)" in
    aarch64 | arm64) arch_dir="ubuntu_arm64" ;;
    *) arch_dir="ubuntu_64bit" ;;
  esac

  local deb
  deb="$(mktemp --suffix=.deb)"
  curl -fsSL -o "$deb" \
    "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/${arch_dir}/session-manager-plugin.deb"

  local sudo=""
  if [ "$(id -u)" -ne 0 ]; then
    sudo="sudo"
  fi
  $sudo dpkg -i "$deb" >/dev/null
  rm -f "$deb"
}

bastion_id() {
  if [ -n "${BASTION_INSTANCE_ID:-}" ]; then
    echo "$BASTION_INSTANCE_ID"
    return
  fi

  : "${ENVIRONMENT:?ENVIRONMENT (the Environment tag of the bastion) is required}"

  local ids
  ids="$(aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=${ENVIRONMENT}" \
              "Name=tag:Name,Values=Bastion" \
              "Name=instance-state-name,Values=running" \
    --query 'Reservations[].Instances[].InstanceId' \
    --output text)"

  local count
  count="$(wc -w <<<"$ids")"
  if [ "$count" -ne 1 ]; then
    log "Expected exactly one running bastion tagged Environment=${ENVIRONMENT}, found ${count}: ${ids}"
    exit 1
  fi
  echo "$ids"
}

start_tunnel() {
  local remote_host="$1" remote_port="$2" local_port="$3"
  local pid_file="${STATE_DIR}/ssm-tunnel-${local_port}.pid"
  local log_file="${STATE_DIR}/ssm-tunnel-${local_port}.log"

  ensure_plugin

  local target
  target="$(bastion_id)"
  log "Forwarding localhost:${local_port} -> ${remote_host}:${remote_port} via ${target}"

  # setsid puts the CLI and the plugin it spawns in their own process
  # group, so `stop` can terminate both.
  setsid nohup aws ssm start-session \
    --target "$target" \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters "{\"host\":[\"${remote_host}\"],\"portNumber\":[\"${remote_port}\"],\"localPortNumber\":[\"${local_port}\"]}" \
    >"$log_file" 2>&1 &
  echo $! >"$pid_file"

  local waited=0
  until grep -q "Waiting for connections" "$log_file" 2>/dev/null; do
    if ! kill -0 "$(cat "$pid_file")" 2>/dev/null; then
      log "Session ended before the port forward was ready:"
      cat "$log_file" >&2
      exit 1
    fi
    if [ "$waited" -ge "$READY_TIMEOUT_SECONDS" ]; then
      log "Port forward not ready after ${READY_TIMEOUT_SECONDS}s:"
      cat "$log_file" >&2
      stop_tunnel "$local_port"
      exit 1
    fi
    sleep 2
    waited=$((waited + 2))
  done
  log "Port forward ready on localhost:${local_port}"
}

stop_tunnel() {
  local local_port="$1"
  local pid_file="${STATE_DIR}/ssm-tunnel-${local_port}.pid"

  if [ ! -f "$pid_file" ]; then
    return
  fi
  local pid
  pid="$(cat "$pid_file")"
  kill -TERM -- "-${pid}" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
  rm -f "$pid_file"
  log "Port forward on localhost:${local_port} closed"
}

case "${1:-}" in
  bastion-id) bastion_id ;;
  start)
    [ $# -eq 4 ] || { log "Usage: $0 start <remote_host> <remote_port> <local_port>"; exit 2; }
    start_tunnel "$2" "$3" "$4"
    ;;
  stop)
    [ $# -eq 2 ] || { log "Usage: $0 stop <local_port>"; exit 2; }
    stop_tunnel "$2"
    ;;
  *)
    log "Usage: $0 {bastion-id|start|stop} ..."
    exit 2
    ;;
esac
