---
type: "always_apply"
---

# Všeobecný popis projektu

Aktuálny projekt obsahuje Dockerfile súbory rôznych Docker obrazov, ktoré používame v iných projektoch ako základ pre .devcontainer vo VS Code prostredí. Tieto obrazy sú zverejnené a zdieľané na https://hub.docker.com/u/developmentrunsk. Jednotlivé Dockerfile súbory sú nezávislé, hoci niekedy dosť podobné, keďže len aktualizujú  Docker obraz pre novšiu verziu danej technológie. Názvová konvencia je `Dockerfile.<image_label_and_version>`, napríklad:

- `Dockerfile.dev-odoo17.0-20240812`
- `Dockerfile.dev-odoo18.0-20250123`
- `Dockerfile.dev-odoo19.0-20251222`
