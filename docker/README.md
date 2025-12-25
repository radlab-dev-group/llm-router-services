# LLM‑Router Services – Docker Build & Run Guide  

## Overview  
This repository contains everything needed to containerise the **LLM‑Router** services with GPU support:

| Component | File | Purpose |
|-----------|------|---------|
| **Base image** | `Dockerfile.base` | Builds a CUDA‑enabled Ubuntu image with common utilities and PyTorch. |
| **Application image** | `Dockerfile` | Extends the base image, pulls the service source code, installs Python dependencies, creates a non‑root user, and sets the entrypoint. |
| **Entrypoint script** | `entrypoint.sh` | Handles optional debug mode and launches the main service script (`run_servcices.sh`). |

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
# From the repository root (where Dockerfile.base lives)
docker build -t gpu-base:cuda-12.2.2-ubuntu22.04 -f Dockerfile.base .
```


> **Tip** – If you want to reuse the image across multiple projects, push it to a private registry:

```shell script
docker tag gpu-base:cuda-12.2.2-ubuntu22.04 my-registry.example.com/gpu-base:cuda-12.2.2-ubuntu22.04
docker push my-registry.example.com/gpu-base:cuda-12.2.2-ubuntu22.04
```


---  

## 2. Build the Application Image  

The application image is based on the **gpu‑base** image you just built (or on any image you
specify via the `BASE_IMAGE` build‑arg). It clones the service repository, installs the
Python package, creates a dedicated user, and sets the entrypoint.

```shell script
# From the repository root (where Dockerfile lives)
docker build \
  --build-arg version=prod \               # optional: override the image label
  --build-arg GIT_REF=main \               # optional: checkout a different git branch/tag
  --build-arg USER_ID=5000 \               # optional: custom UID for the runtime user
  --build-arg GROUP_ID=5000 \              # optional: custom GID for the runtime group
  --build-arg BASE_IMAGE=gpu-base:cuda-12.2.2-ubuntu22.04 \  # optional: custom base image
  -t llm-router-services:prod .
```


### Common build‑time arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `version` | `prod` | Image label used for documentation / versioning. |
| `GIT_REF` | `main` | Git reference (branch, tag, or commit) to checkout. |
| `USER_ID` / `GROUP_ID` | `5000` | UID/GID for the non‑root `llm-router` user inside the container. |
| `BASE_IMAGE` | `gpu-base:cuda-12.2.2-ubuntu22.04` | Base image for the application; can be any compatible CUDA image. |

---  

## 3. Run the Container  

The container expects the `entrypoint.sh` script (included in the repository) to be present at
`/srv/llm-router-services/entrypoint.sh` inside the image. It will launch `run_servcices.sh`
(the service starter) unless you enable debug mode.

```shell script
docker run -it --rm \
  --gpus all \                         # expose GPU(s) to the container
  -p 5000:5000 \                       # map the service port (adjust if needed)
  -e HF_TOKEN=YOUR_HF_TOKEN \          # **required** HuggingFace access token
  llm-router-services:prod
```


### Debug / Interactive Mode  

If you need to poke around inside the container (e.g., inspect logs, run ad‑hoc commands), start it with the `--debug` flag:

```shell script
docker run -it --rm \
  --gpus all \
  -p 5000:5000 \
  -e HF_TOKEN=YOUR_HF_TOKEN \
  llm-router-services:prod --debug
```


The entrypoint will pause indefinitely (`sleep infinity`) allowing you to
`docker exec -it <container-id> bash` and explore.

---  

## 4. Customising Runtime Behaviour  

| Variable | Where to set | Description |
|----------|--------------|-------------|
| `HF_HOME` (set in the image) | Not required at run‑time | Directory used by Hugging Face libraries for model caches (`/srv/cache`). |
| `HF_TOKEN` | `docker run -e HF_TOKEN=…` | **Mandatory** token for authenticating with the Hugging Face Hub. |
| Additional environment variables | `docker run -e VAR=value …` | Pass any configuration needed by your service (e.g., API keys, model names). |
| Port mapping | `-p host:container` | Change the exposed port if your service listens on a different one. |
| Cache volume | `-v /local/path:/srv/cache` | Mount a host directory to `/srv/cache` to persist Hugging Face model downloads across container restarts. |


---  

## 5. Cleaning Up  

```shell script
# Remove stopped containers (if any)
docker container prune -f

# Remove images
docker image rm gpu-base:cuda-12.2.2-ubuntu22.04 llm-router-services:prod
```


If you pushed the images to a registry, delete them there as well.

---  

## 6. Troubleshooting  

| Symptom | Likely Cause | Fix                                                                                                                           |
|---------|--------------|-------------------------------------------------------------------------------------------------------------------------------|
| `docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]]` | NVIDIA runtime not enabled | Install the NVIDIA Container Toolkit and add `"default-runtime": "nvidia"` to `/etc/docker/daemon.json`, then restart Docker. |
| `Unable to locate package python3-pip` during build | Out‑of‑date `apt` cache | Ensure the `apt-get update` line runs before installing packages (the base Dockerfile already does this).                     |
| `ImportError: No module named torch` at runtime | PyTorch not installed or mismatched CUDA version | Re‑build the base image; the base Dockerfile installs `torch` from PyPI, which pulls the CUDA‑compatible wheel.               |
| Container exits immediately after start | `run_servcices.sh` missing or not executable | Verify the script is mounted correctly (`-v …:ro`) and has executable permissions (`chmod +x`).                               |
| Debug mode does not pause | Wrong argument spelling | Use `--debug`, `debug`, `--shell`, or `shell` (any of these activate debug mode).                                             |
| Hugging Face authentication fails | `HF_TOKEN` not set or invalid | Supply a valid token via `-e HF_TOKEN=…` when running the container and check if you have confirmed the licenses for the models used                                                |
| Model files are re‑downloaded on each start | No persistent cache volume | Mount a host directory to `/srv/cache` (see **Cache volume** above).                                                          |

---  

## 7. Quick One‑Liner (for developers)  

```shell script
docker build -t gpu-base:cuda-12.2.2-ubuntu22.04 -f Dockerfile.base . && \
docker build -t llm-router-services:prod . && \
docker run -it --rm --gpus all -p 5000:5000 \
  -e HF_TOKEN=YOUR_HF_TOKEN \
  -v "$HOME/hf_cache":/srv/cache \
  llm-router-services:prod
```


That’s it! You now have a reproducible, GPU‑enabled container ready to serve the LLM‑Router services. 🚀