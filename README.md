# service-template

![CI](https://github.com/sami-djouhri/service-template/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/hardened%20container-2496ED?logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

An opinionated Python microservice template. It is the base I use for dozens of
self-hosted services. Each of them inherits the same health checks, logging and
security defaults, so I stop rebuilding that part every time.

```mermaid
flowchart LR
  req[HTTP request] --> nginx[nginx proxy fragment]
  nginx --> auth[auth<br/>trusted-proxy identity check]
  auth --> app[your service logic]
  app --> health[/health → Docker HEALTHCHECK/]
  app -. opt-in .-> mqtt[(MQTT event bus)]
  app --> logs[structured logs]
  cfg[config.py<br/>env-driven defaults] --> app
```

## What it gives you
- **Config** via environment with sane defaults (`app/config.py`)
- **Health endpoint** (`/health`) wired to a Docker `HEALTHCHECK`
- **MQTT** publisher/subscriber scaffolding as an opt-in event bus
- **Auth** helper with trusted-proxy verification, so a forwarded identity
  cannot be spoofed by an untrusted peer
- **Structured logging**
- **Hardened Dockerfile** (non-root, minimal surface) plus an nginx
  reverse-proxy fragment
- `scripts/new-service.sh` to stamp out a new service from the template

## Philosophy
Stability and security come before features here, and the template stays small on
purpose. Config, auth, health and mqtt are scaffolding you switch on when you need
them. Nothing in the template forces you to keep them.

MIT licensed.

## About this snapshot

This repo sits closest to its private original, since a template has little to
hide. The publishing script still does the full pass over it: internal addresses
and paths become placeholders, and two secret scanners have to agree before
anything leaves the house.

The single commit is the same story as in my other repos here. This template is
what my own services are built on.
