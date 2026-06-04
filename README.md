Dockerfiles k https://hub.docker.com/u/developmentrunsk

Pravidlá fungovania `.github/workflows/docker-publish.yml`:

- Súbor `Dockerfile.<image_label>_<image_tag>` sa vybuilduje do obrazu `<image_label>:<image_tag>`, napríklad `Dockerfile.fajnlamp_7.3` sa vybuilduje do obrazu `fajnlamp:7.3`.
- Súbor, ktorého tag končí na  `.test`, sa nebuilduje.
- Súbor, ktorý má za tagom príponu `.amd64`, sa builduje len pre `amd64`. Táto prípona sa nepočíta za súčasť tagu, napr. súbor `Dockerfile.fajnlamp_7.3.amd64` sa vybuilduje do obrazu `fajnlamp:7.3`.
