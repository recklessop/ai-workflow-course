#!/usr/bin/env bash
# Module 19 lab: what a CI job could see if it ran on THIS machine.
#
# Run this on any machine you'd consider turning into a self-hosted runner (your laptop is fine for
# the exercise). It does NOT change anything; it only LOOKS. The point is to make concrete what is
# otherwise abstract: a "workflow step" is just a shell command, so whatever this read-only script
# can see, a malicious workflow step (e.g. from a pull request) running on this runner can see too.
#
#   bash inspect-runner.sh
#
# Then paste the output into your AI and ask it to rank, worst-first, what a malicious PR could
# steal or reach if this were your runner. That conversation IS the security tradeoff for this module.

set -u

line() { printf '\n=== %s ===\n' "$1"; }

# Try a TCP connect to host:port with a ~2s deadline, portably.
# GNU `timeout` (Linux) or Homebrew's `gtimeout` are used when present; otherwise a bash-native
# background-and-kill fallback keeps this working on stock macOS, which ships no GNU `timeout`.
tcp_probe() {
  host="$1"; port="$2"
  if command -v timeout >/dev/null 2>&1; then
    timeout 2 bash -c ">/dev/tcp/${host}/${port}" 2>/dev/null
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout 2 bash -c ">/dev/tcp/${host}/${port}" 2>/dev/null
  else
    bash -c ">/dev/tcp/${host}/${port}" 2>/dev/null &
    probe_pid=$!
    ( sleep 2; kill "$probe_pid" 2>/dev/null ) >/dev/null 2>&1 &
    killer_pid=$!
    rc=0; wait "$probe_pid" 2>/dev/null || rc=$?
    kill "$killer_pid" 2>/dev/null
    return "$rc"
  fi
}

line "WHO AND WHERE"
echo "hostname : $(hostname 2>/dev/null)"
echo "user     : $(whoami 2>/dev/null)  (root? $( [ "$(id -u 2>/dev/null)" = 0 ] && echo YES || echo no ))"
echo "os       : $(uname -srm 2>/dev/null)"
echo "  >> A runner should run as a dedicated low-privilege user, never root, never your login."

line "SECRETS SITTING IN THE ENVIRONMENT"
# Don't print values, just the names. Seeing the NAMES is enough to make the point.
env | grep -iE 'token|secret|key|password|passwd|credential|aws|gcp|azure|api' | cut -d= -f1 | sort -u \
  | sed 's/^/  exposed env var: /' || true
echo "  >> Any of these is readable by every job step. Scope runner secrets to the absolute minimum."

line "CREDENTIAL FILES ON DISK"
for p in \
  "$HOME/.aws/credentials" \
  "$HOME/.config/gcloud" \
  "$HOME/.azure" \
  "$HOME/.docker/config.json" \
  "$HOME/.kube/config" \
  "$HOME/.netrc" \
  "$HOME/.git-credentials" ; do
  [ -e "$p" ] && echo "  FOUND: $p"
done
echo "  (nothing listed above = none of those common credential stores are present here)"

line "SSH KEYS (pivot material)"
if [ -d "$HOME/.ssh" ]; then
  ls -1 "$HOME/.ssh" 2>/dev/null | sed 's/^/  ~\/.ssh\//'
  echo "  >> Private keys here let a compromised job hop to every host you can SSH to."
else
  echo "  no ~/.ssh directory"
fi

line "DOCKER SOCKET (root-equivalent if present)"
if [ -S /var/run/docker.sock ]; then
  echo "  /var/run/docker.sock EXISTS and is reachable."
  echo "  >> Access to the Docker socket is effectively root on the host. Big deal."
else
  echo "  no reachable docker socket"
fi

line "PRIVATE NETWORK REACH (the reason you self-host, and the reason it's dangerous)"
# Probe a few common private ranges' gateways and any hosts you care about.
# Edit these to match your network for a sharper result.
PROBES=( "192.168.0.1:80" "192.168.1.1:80" "10.0.0.1:80" )
for hp in "${PROBES[@]}"; do
  host="${hp%%:*}"; port="${hp##*:}"
  if tcp_probe "$host" "$port"; then
    echo "  REACHABLE: ${host}:${port}"
  fi
done
echo "  (edit the PROBES list above to test your real internal hosts: databases, deploy targets)"
echo "  >> Every reachable internal host is something a compromised runner can attack or exfiltrate."

line "BOTTOM LINE"
echo "Everything listed above is what a self-hosted runner on this box would hand to ANY job it runs,"
echo "including a job defined by a pull request you haven't merged. That is the tradeoff. Mitigate with:"
echo "  - ephemeral runners (fresh environment per job)"
echo "  - a dedicated low-priv user on an isolated network segment"
echo "  - least-privilege secrets, and NEVER attach this to a public repo without fork-PR approval"
