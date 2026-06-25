# Dockerfile for the tasks-app: a reproducible environment you can build, run, and throw away.
#
# Build it:   docker build -t tasks-app .
# Run it:     docker run --rm tasks-app list
#             docker run --rm tasks-app add "containerize the app"
#
# The same image runs identically on your laptop, on the CI runner (Module 14), and on a deploy
# target (Module 18), because the environment travels *inside the image* instead of living only
# in your head. (Docker is the worked example here; this is a standard OCI image, so `podman build`
# / `nerdctl build` read the same file.)

# --- Base image -------------------------------------------------------------
# Pin the language version so the container matches what your CI pins (Module 14 used 3.12).
# "-slim" is a smaller Debian-based image: enough to run Python, without a full OS toolchain.
# For bit-for-bit reproducibility, pin the digest too (see "Where it breaks" in the README):
#   FROM python:3.12-slim@sha256:<digest>
FROM python:3.12-slim

# Small, sane defaults: don't litter .pyc files, don't buffer stdout (so logs appear immediately).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- App --------------------------------------------------------------------
# Everything lives in /app inside the image. This path is identical on every machine that runs it;
# that sameness is the whole point.
WORKDIR /app

# Copy the app in. .dockerignore (see dockerignore-starter in this folder) keeps junk (caches,
# runtime state, the .git dir) out of the build and out of the image.
COPY tasks.py cli.py ./

# Run as a non-root user. This is hygiene, NOT a security boundary on its own; see the README's
# "Where it breaks." We also hand /app to that user so the app can write tasks.json at runtime.
RUN useradd --create-home appuser && chown appuser /app
USER appuser

# What runs when the container starts. ENTRYPOINT is the fixed command; CMD is the default
# argument, overridable at `docker run` time:
#   docker run --rm tasks-app list        ->  python cli.py list
#   docker run --rm tasks-app add "x"     ->  python cli.py add x
ENTRYPOINT ["python", "cli.py"]
CMD ["list"]
