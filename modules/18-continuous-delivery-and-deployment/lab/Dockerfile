# The Module 16 container image for the tasks-app, set to run the HTTP service from serve.py.
#
# This is *what you ship* (Module 16). Continuous delivery/deployment (this module) builds this
# once, tags it with the commit SHA, and runs that exact artifact everywhere.
#
# Note what is NOT here: no secrets, no environment-specific config. Those are injected at run time
# (Module 17), which is why the same image can run in staging and prod unchanged.

FROM python:3.12-slim

WORKDIR /app

# The app is dependency-free (stdlib only), so there is nothing to pip install. Copy the source.
COPY tasks.py cli.py serve.py ./

# Document the port the service listens on.
EXPOSE 8000

# A built-in container health check. The deploy step also checks /health from outside, but this
# lets the runtime itself know whether the container is healthy.
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["python", "serve.py"]
