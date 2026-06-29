---
type: "always_apply"
---

# Všeobecný popis projektu

Aktuálny projekt obsahuje Dockerfile súbory rôznych Docker obrazov, ktoré používame v iných projektoch ako:

- základ pre .devcontainer vo VS Code prostredí. Sú to tie súbory/obrazy, ktorých názvy začínajú `dev-` alebo `fanj`.
- základ pre produkčné kontajnere. Sú to tie súbory/obrazy, ktorých názvy začínajú `prod-`.

Tieto obrazy sú zverejnené a zdieľané na https://hub.docker.com/u/developmentrunsk. Jednotlivé Dockerfile súbory sú nezávislé, hoci niekedy dosť podobné, keďže len aktualizujú  Docker obraz pre novšiu verziu danej technológie. Názvová konvencia je `Dockerfile.<image-label>_<image-tag>`, napríklad:

- `Dockerfile.dev-odoo_17.0-20240812`
- `Dockerfile.fajnlamp_7.3`
- `Dockerfile.prod-odoo_19.0-20251222`
