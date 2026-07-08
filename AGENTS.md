---
type: "always_apply"
---

# General Project Description

The current project contains Dockerfile files of various Docker images that we use in other projects as:

- basis for .devcontainer in the VS Code environment. These are the files/images whose names start with `dev-` or `fanj`.
- basis for production containers. These are the files/images whose names start with `prod-`.

These images are published and shared on https://hub.docker.com/u/developmentrunsk. Individual Dockerfile files are independent, although sometimes quite similar, as they only update the Docker image for a newer version of the given technology. The naming convention is `Dockerfile.<image-label>_<image-tag>`, for example:

- `Dockerfile.dev-odoo_17.0-20240812`
- `Dockerfile.fajnlamp_7.3`
- `Dockerfile.prod-odoo_19.0-20251222`
