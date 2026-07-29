# LLM‑Router Services – Docker Build & Run Guide  

## Overview  
This repository contains everything needed to containerise the **LLM‑Router** services with GPU support:

| Component | File                | Purpose                                                                                                                                |
|-----------|---------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **Base image** | `Dockerfile.base`   | Builds a CUDA‑enabled Ubuntu image with common utilities and PyTorch.                                                                  |
| **Application image** | `Dockerfile`        | Extends the base image, pulls the service source code, installs Python dependencies, creates a non‑root user, and sets the entrypoint. |
| **No-CUDA application image** | `Dockerfile.nocuda` | Standalone build image (Python + PyTorch, no NVIDIA/CUDA dependency). Useful for CPU-only deployment or when the CUDA base image is unavailable. |
| **Entrypoint script** | `entrypoint.sh`     | Handles optional debug mode and launches the main service script (`run_servcices.sh`).                                                 |

The steps below assume you have a recent Docker installation (Docker 20.10+ with the NVIDIA Container Toolkit for GPU access).

---  

## Prerequisites  

| Requirement | How to install |
|-------------|----------------|
| **Docker Engine** | Follow the official guide: <https://docs.docker.com/engine/install/> |
| **NVIDIA drivers** (host) | Install the latest driver for your GPU (e.g., `sudo apt install nvidia-driver-525`). |
| **NVIDIA Container Toolkit** | <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html> |
| **Git** (optional, for cloning the repo locally) | `sudo apt install git` |

Verify GPU visibility inside Docker:

```shell script
docker run --gpus all nvidia/cuda:12.2.2-runtime-ubuntu22.04 nvidia-smi
```


You should see a table with your GPU details.

---  

## 1. Build the Base Image  

The base image provides CUDA, Ubuntu, Python 3, `pip`, and a pre‑installed PyTorch wheel.  
It is built from **Dockerfile.base**, which accepts an optional `BASE_IMAGE` build‑arg (default:
`nvidia/cuda:12.2.2-runtime-ubuntu22.04`). After the build the image is tagged as
`gpu-base:cuda-12.2.2-ubuntu22.04` and can be used as a foundation for the application image.

```shell script
# From the project ROOT (not inside docker/)
docker build -f docker/Dockerfile.base \
  -t gpu-base:cuda-12.2.2-ubuntu22.04 .
```


> **Tip** – If you want to reuse the image across multiple projects, push it to a private registry:

```shell script
docker tag gpu-base:cuda-12.2.2-ubuntu22.04 my-registry.example.com/gpu-base:cuda-12.2.2-ubuntu22.04
docker push my-registry.example.com/gpu-base:cuda-12.2.2-ubuntu22.04
```


---  

## 2. Build the Application Image  

The application image is based on the **gpu‑base** image you just built (or on any image you
specify via the `BASE_IMAGE` build‑arg). It copies the service source code, installs the
Python package, creates a dedicated user, and sets the entrypoint.

> ⚠️ **Important:** The Docker build context must be the **project root** (where `setup.py` lives),
because `COPY .` copies everything from there — including the `llm_router_services/` package directory
and `setup.py`. The Docker file itself is passed via `-f`:

```shell script
# Run this from the project ROOT (not inside docker/)
docker build \
  -f docker/Dockerfile \
  --build-arg version=prod \               # optional: override the image label
  --build-arg USER_ID=5000 \               # optional: custom UID for the runtime user
  --build-arg GROUP_ID=5000 \              # optional: custom GID for the runtime group
  --build-arg BASE_IMAGE=gpu-base:cuda-12.2.2-ubuntu22.04 \  # optional: custom base image
  -t llm-router-services:prod .
```


### Common build‑time arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `version` | `prod` | Image label used for documentation / versioning. |
| `USER_ID` / `GROUP_ID` | `5000` | UID/GID for the non‑root `llm-router` user inside the container. |
| `BASE_IMAGE` | `gpu-base:cuda-12.2.2-ubuntu22.04` | Base image for the application; can be any compatible CUDA image. |

---  

## 3. Build the No-CUDA Application Image  

When you don't need GPU support (CPU-only deployment) or can't use the CUDA base image, use **Dockerfile.nocuda**.  
It is a fully standalone image based on `python:3.14.6-trixie` with Python 3, PyTorch, UTF-8 locale settings, and all required utilities baked in.

> ⚠️ Same as above — run from the **project root** with `-f docker/Dockerfile.nocuda`:

```shell script
# Run this from the project ROOT (not inside docker/)
docker build \
  -f docker/Dockerfile.nocuda \
  --build-arg version=prod \
  -t llm-router-services:prod-cpu .
```

> **Note** – This image is larger than a typical multi-stage CUDA build because PyTorch and all system dependencies are installed in a single stage.  
> It does **not** require the NVIDIA Container Toolkit to run.

---  

## 4. Run the Container  

The container expects the `entrypoint.sh` script (included in the repository) to be present at
`/srv/llm-router-services/entrypoint.sh` inside the image. It will launch `run_servcices.sh`
(the service starter) unless you enable debug mode.

### GPU build (`llm-router-services:prod`)

```shell script
docker run -it --rm \
  --gpus all \                         # expose GPU(s) to the container — required for CUDA builds
  -p 5000:5000 \                       # map the service port (adjust if needed)
  -e HF_TOKEN=YOUR_HF_TOKEN \          # **required** HuggingFace access token
  llm-router-services:prod
```

### CPU build (`llm-router-services:prod-cpu`)

> No `--gpus` flag needed — the nocuda image works on any host.

```shell script
docker run -it --rm \
  -p 5000:5000 \
  -e HF_TOKEN=YOUR_HF_TOKEN \
  llm-router-services:prod-cpu
```

### Debug / Interactive Mode

For either build, add the `--debug` flag to pause inside the container (allows `docker exec`):

```shell script
docker run -it --rm \
  -p 5000:5000 \
  -e HF_TOKEN=YOUR_HF_TOKEN \
  llm-router-services:prod --debug
```

The entrypoint will sleep indefinitely, so you can `docker exec -it <container-id> bash` and explore.

---  

## 5. Customising Runtime Behaviour  

| Variable | Where to set | Description |
|----------|--------------|-------------|
| `HF_HOME` (set in the image) | Not required at run‑time | Directory used by Hugging Face libraries for model caches (`/srv/cache`). |
| `HF_TOKEN` | `docker run -e HF_TOKEN=…` | **Mandatory** token for authenticating with the Hugging Face Hub. |
| Additional environment variables | `docker run -e VAR=value …` | Pass any configuration needed by your service (e.g., API keys, model names). |
| Port mapping | `-p host:container` | Change the exposed port if your service listens on a different one. |
| Cache volume | `-v /local/path:/srv/cache` | Mount a host directory to `/srv/cache` to persist Hugging Face model downloads across container restarts. |


---  

## 6. Cleaning Up  

```shell script
# Remove stopped containers (if any)
docker container prune -f

# Remove images
docker image rm gpu-base:cuda-12.2.2-ubuntu22.04 llm-router-services:prod llm-router-services:prod-cpu
```


If you pushed the images to a registry, delete them there as well.

---  

## 7. Troubleshooting  

| Symptom | Likely Cause | Fix                                                                                                                           |
|---------|--------------|-------------------------------------------------------------------------------------------------------------------------------|
| `docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]]` | NVIDIA runtime not enabled | Install the NVIDIA Container Toolkit and add `"default-runtime": "nvidia"` to `/etc/docker/daemon.json`, then restart Docker. |
| `Unable to locate package python3-pip` during build | Out‑of‑date `apt` cache | Ensure the `apt-get update` line runs before installing packages (the base Dockerfile already does this).                     |
| `ImportError: No module named torch` at runtime | PyTorch not installed or mismatched CUDA version | Re‑build the base image; the base Dockerfile installs `torch` from PyPI, which pulls the CUDA‑compatible wheel.               |
| Container exits immediately after start | `run_servcices.sh` missing or not executable | Verify the script is mounted correctly (`-v …:ro`) and has executable permissions (`chmod +x`).                               |
| Debug mode does not pause | Wrong argument spelling | Use `--debug`, `debug`, `--shell`, or `shell` (any of these activate debug mode).                                             |
| Hugging Face authentication fails | `HF_TOKEN` not set or invalid | Supply a valid token via `-e HF_TOKEN=…` when running the container and check if you have confirmed the licenses for the models used                                                |
| Model files are re‑downloaded on each start | No persistent cache volume | Mount a host directory to `/srv/cache` (see **Cache volume** above).                                                          |
| `torch` CUDA errors or missing GPU at runtime | Running nocuda image with `--gpus` flag | The nocuda build does not include NVIDIA support — remove the `--gpus` flag when running it.                                  |

---  

## 8. Quick One‑Liners (for developers)

### GPU (CUDA) build & run

```shell script
# Run from project ROOT (not inside docker/)
docker build -f docker/Dockerfile.base \
  -t gpu-base:cuda-12.2.2-ubuntu22.04 . && \
docker build -f docker/Dockerfile \
  --build-arg version=prod \
  -t llm-router-services:prod . && \
docker run -it --rm --gpus all -p 5000:5000 \
  -e HF_TOKEN=YOUR_HF_TOKEN \
  -v "$HOME/hf_cache":/srv/cache \
  llm-router-services:prod
```

### CPU-only build & run

```shell script
# Run from project ROOT (not inside docker/)
docker build -f docker/Dockerfile.nocuda \
  --build-arg version=prod \
  -t llm-router-services:prod-cpu . && \
docker run -it --rm -p 5000:5000 \
  -e HF_TOKEN=YOUR_HF_TOKEN \
  -v "$HOME/hf_cache":/srv/cache \
  llm-router-services:prod-cpu
```


That's it! You now have a reproducible, GPU‑enabled container ready to serve the LLM‑Router services. 🚀