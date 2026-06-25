#!/usr/bin/env bash
#
# deploy.sh: the deploy step of CD, simulated with a local container run.
#
# The five steps of any deploy, provider-neutral (see the module README):
#   1. build/pull the specific image tag        4. health-check before trusting it
#   2. inject runtime config + secrets          5. cut over if healthy, ROLL BACK if not
#   3. start the new version
#
# The *target* here is your own machine instead of a server, but the logic is the real thing.
#
# Usage:
#   ./deploy.sh <tag>        # e.g. ./deploy.sh $(git rev-parse --short HEAD)
#   BREAK=1 ./deploy.sh <tag># force the new version's health check to fail, to demo rollback
#
# Requires: docker (or `alias docker=podman`), curl.

set -euo pipefail

IMAGE="tasks-app"
CONTAINER="tasks-app"
PORT="8000"
STATE_FILE=".deploy-state"          # records the last good tag, for rollback
TAG="${1:-$(git rev-parse --short HEAD)}"

say() { printf '\n=== %s\n' "$*"; }

# --- Step 1: build the artifact for this tag (in real CD this was already built+pushed by CI) -----
say "Building ${IMAGE}:${TAG}"
docker build -t "${IMAGE}:${TAG}" .

# Remember what is currently running so we can roll back to it.
PREVIOUS=""
if [ -f "${STATE_FILE}" ]; then
  PREVIOUS="$(cat "${STATE_FILE}")"
fi

# --- Steps 2 + 3: start the new version with runtime config/secrets injected (Module 17) ----------
# Note: APP_VERSION is config supplied at run time, NOT baked into the image. A real deploy would
# also pass secrets here (e.g. --env-file, a mounted secret, or a secrets-manager lookup), never
# committed, never in the image.
start_version() {
  local tag="$1"
  docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
  docker run -d --name "${CONTAINER}" \
    -p "${PORT}:8000" \
    -e "APP_VERSION=${tag}" \
    ${BREAK:+-e "BREAK=${BREAK}"} \
    "${IMAGE}:${tag}" >/dev/null
}

say "Starting ${IMAGE}:${TAG}"
start_version "${TAG}"

# --- Step 4: health-check the new version before trusting it --------------------------------------
healthy() {
  for _ in $(seq 1 10); do
    if curl -fs "http://localhost:${PORT}/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

say "Health-checking http://localhost:${PORT}/health"
if healthy; then
  # --- Step 5a: cut over. Record this as the new known-good for the next deploy's rollback target.
  echo "${TAG}" > "${STATE_FILE}"
  say "DEPLOY OK: ${IMAGE}:${TAG} is live and healthy"
  curl -s "http://localhost:${PORT}/health"; echo
  exit 0
fi

# --- Step 5b: ROLLBACK. The new version failed its health check. ----------------------------------
say "HEALTH CHECK FAILED for ${IMAGE}:${TAG}, rolling back"
docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true

if [ -z "${PREVIOUS}" ]; then
  echo "No previous known-good version to roll back to. Service is DOWN." >&2
  echo "(Deploy a healthy version first, then re-run the BREAK=1 deploy to see rollback work.)" >&2
  exit 1
fi

# Rollback is trivial because we deploy immutable tags: just run the old one again. No rebuild.
say "Restoring previous good version ${IMAGE}:${PREVIOUS}"
BREAK="" start_version "${PREVIOUS}"     # clear BREAK so the good version comes up clean
if healthy; then
  say "ROLLED BACK: ${IMAGE}:${PREVIOUS} is live and healthy. The bad deploy reverted itself."
  curl -s "http://localhost:${PORT}/health"; echo
  exit 1   # exit non-zero: the deploy you asked for did NOT ship, even though service recovered
else
  echo "Rollback FAILED: service is DOWN. Investigate ${IMAGE}:${PREVIOUS}." >&2
  exit 2
fi
