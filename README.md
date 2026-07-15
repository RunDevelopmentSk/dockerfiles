Dockerfiles for https://hub.docker.com/u/developmentrunsk

All build sources (the `Dockerfile.*` files and the `.sh` scripts) live in the `images/` directory, keeping the repository root reserved for documentation and tooling configuration.

The naming convention is as follows (`images/Dockerfile.<image_label>_<image_tag>`):
- if `<image_label>` starts with `fajn` or `dev-`, it is a Dockerfile intended for project development in a devcontainer.
- if `<image_label>` starts with `prod-`, it is for production project execution

Images are built and pushed to hub.docker.com automatically using github actions (workflows). This automation is configured in `.github/workflows/docker-publish.yml`:

- The `Dockerfile.<image_label>_<image_tag>` file is built into the image `<image_label>:<image_tag>`. For example, `Dockerfile.fajnlamp_7.3` is built into the image `fajnlamp:7.3`.
- A file whose tag ends with `.test` is not built.
- A file that has the `.amd64` suffix after the tag is built only for `amd64`. This suffix is not counted as part of the tag, e.g., the file `Dockerfile.fajnlamp_7.3.amd64` is built into the image `fajnlamp:7.3`.
