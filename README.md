Dockerfiles k https://hub.docker.com/u/developmentrunsk

Názvová konvencia je nasledovná (`Dockerfile.<image_label>_<image_tag>`):
- ak `<image_label>` začína `fajn` alebo `dev-` tak ide o Dockerfile určené pre vývoj projektu v devcontainer-i.
- ak `<image_label>` začína `prod-` tak ide pre produkčné spúšťanie projektu

Obrazy sa buildujú a tlačia na hub.docker.com automaticky pomocou github actions (workflows). Táto automatizácia je nakonfigurovaná v `.github/workflows/docker-publish.yml`:

- Súbor `Dockerfile.<image_label>_<image_tag>` sa vybuilduje do obrazu `<image_label>:<image_tag>`. Napríklad `Dockerfile.fajnlamp_7.3` sa vybuilduje do obrazu `fajnlamp:7.3`.
- Súbor, ktorého tag končí na  `.test`, sa nebuilduje.
- Súbor, ktorý má za tagom príponu `.amd64`, sa builduje len pre `amd64`. Táto prípona sa nepočíta za súčasť tagu, napr. súbor `Dockerfile.fajnlamp_7.3.amd64` sa vybuilduje do obrazu `fajnlamp:7.3`.
