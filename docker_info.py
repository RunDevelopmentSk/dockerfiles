#!/usr/bin/env python3
"""Zobrazí prehľad Docker kontajnerov a volumes zoradených podľa veľkosti (od najväčších po najmenšie)."""

import subprocess
import re
import sys


def parse_size_to_bytes(size_str: str) -> int:
    """Prevedie textovú veľkosť (napr. '1.5GB', '500MB', '2kB') na bajty."""
    size_str = size_str.strip()
    units = {
        "B":   1,
        "KB":  1_000,
        "MB":  1_000_000,
        "GB":  1_000_000_000,
        "TB":  1_000_000_000_000,
        "KIB": 1_024,
        "MIB": 1_048_576,
        "GIB": 1_073_741_824,
        "TIB": 1_099_511_627_776,
    }
    match = re.fullmatch(r"([\d.]+)\s*([A-Za-z]+)", size_str)
    if match:
        value = float(match.group(1))
        unit = match.group(2).upper()
        return int(value * units.get(unit, 1))
    # Ak je číslo bez jednotky, predpokladáme bajty
    try:
        return int(float(size_str))
    except ValueError:
        return 0


def format_size(size_bytes: int) -> str:
    """Formátuje bajty do čitateľnej podoby."""
    for unit, threshold in [("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("KB", 1e3)]:
        if size_bytes >= threshold:
            return f"{size_bytes / threshold:.2f} {unit}"
    return f"{size_bytes} B"


def get_volumes_with_sizes() -> list[tuple[str, int, str]]:
    """
    Vráti zoznam (názov, veľkosť_v_bajtoch, veľkosť_text) pre všetky Docker volumes.
    Využíva 'docker system df -v' pre získanie veľkostí.
    """
    try:
        result = subprocess.run(
            ["docker", "system", "df", "-v"],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Chyba pri spustení docker: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Docker nie je nainštalovaný alebo nie je dostupný v PATH.", file=sys.stderr)
        sys.exit(1)

    volumes = []
    in_volumes_section = False
    header_found = False

    for line in result.stdout.splitlines():
        stripped = line.strip()

        # Detekcia začiatku sekcie volumes
        if re.match(r"local volumes", stripped, re.IGNORECASE):
            in_volumes_section = True
            header_found = False
            continue

        if not in_volumes_section:
            continue

        # Preskočiť hlavičku tabuľky a poznačiť si, že sme za ňou
        if re.match(r"VOLUME\s+NAME", stripped, re.IGNORECASE):
            header_found = True
            continue

        # Prázdny riadok pred hlavičkou preskočíme, za hlavičkou ukončíme sekciu
        if stripped == "":
            if header_found:
                in_volumes_section = False
                header_found = False
            continue

        # Riadky s dátami (až po nájdení hlavičky)
        if header_found:
            parts = stripped.split()
            if len(parts) >= 3:
                name = parts[0]
                size_str = parts[-1]
                size_bytes = parse_size_to_bytes(size_str)
                volumes.append((name, size_bytes, size_str))

    return volumes


def get_containers_with_sizes() -> list[tuple[str, int, int, str]]:
    """
    Vráti zoznam (názov, vlastná_veľkosť_bytes, virtuálna_veľkosť_bytes, status)
    pre všetky Docker kontajnery. Využíva 'docker ps -a --size'.
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--size",
             "--format", "{{.Names}}\t{{.Size}}\t{{.Status}}"],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Chyba pri spustení docker: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Docker nie je nainštalovaný alebo nie je dostupný v PATH.", file=sys.stderr)
        sys.exit(1)

    containers = []
    # Formát SIZE: "1.71GB (virtual 4.22GB)"
    size_pattern = re.compile(r"^([\d.]+\s*\S+)\s+\(virtual\s+([\d.]+\s*\S+)\)$", re.IGNORECASE)

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        name, size_str, status = parts[0], parts[1], parts[2]
        m = size_pattern.match(size_str.strip())
        if m:
            own_bytes = parse_size_to_bytes(m.group(1))
            virtual_bytes = parse_size_to_bytes(m.group(2))
        else:
            own_bytes = parse_size_to_bytes(size_str.strip())
            virtual_bytes = own_bytes
        containers.append((name, own_bytes, virtual_bytes, status))

    return containers


def print_section(title: str, rows: list, col_name: int, columns: list[tuple[str, int, str]]):
    """Vypíše zarovnanú sekciu tabuľky so zadanými stĺpcami."""
    # Zostav header
    header_parts = [f"{'NÁZOV':<{col_name}}"]
    for col_label, col_width, col_align in columns:
        if col_align == ">":
            header_parts.append(f"{col_label:>{col_width}}")
        else:
            header_parts.append(f"{col_label:<{col_width}}")
    header = "  ".join(header_parts)
    separator = "-" * len(header)

    print(f"\n{title}\n")
    print(header)
    print(separator)
    for row in rows:
        name = row[0]
        cells = [f"{name:<{col_name}}"]
        for i, (_, col_width, col_align) in enumerate(columns):
            val = row[i + 1]
            if col_align == ">":
                cells.append(f"{val:>{col_width}}")
            else:
                cells.append(f"{val:<{col_width}}")
        print("  ".join(cells))
    print(separator)


def main():
    # ── KONTAJNERY ──────────────────────────────────────────────────────────
    containers = get_containers_with_sizes()

    if not containers:
        print("\nNenašli sa žiadne Docker kontajnery.")
    else:
        containers.sort(key=lambda x: x[1], reverse=True)
        col_name = max(max(len(c[0]) for c in containers), 5)

        rows = [
            (name, format_size(own), format_size(virt), status.split(" ")[0])
            for name, own, virt, status in containers
        ]
        print_section(
            "Docker kontajnery zoradené podľa veľkosti:",
            rows, col_name,
            [("VLASTNÁ", 12, ">"), ("VIRTUÁLNA", 12, ">"), ("STATUS", 10, "<")],
        )
        total_own = sum(c[1] for c in containers)
        total_virt = sum(c[2] for c in containers)
        print(
            f"{'CELKOM':<{col_name}}  {format_size(total_own):>12}  {format_size(total_virt):>12}"
        )
        print(f"\nPočet kontajnerov: {len(containers)}")
        print("  VLASTNÁ   = dáta zapísané kontajnerom nad base image")
        print("  VIRTUÁLNA = vlastná + zdieľaný base image\n")

    # ── VOLUMES ──────────────────────────────────────────────────────────────
    volumes = get_volumes_with_sizes()

    if not volumes:
        print("\nNenašli sa žiadne Docker volumes.")
    else:
        volumes.sort(key=lambda x: x[1], reverse=True)
        col_name = max(max(len(v[0]) for v in volumes), 11)

        rows = [(name, format_size(size), raw) for name, size, raw in volumes]
        print_section(
            "Docker volumes zoradené podľa veľkosti:",
            rows, col_name,
            [("VEĽKOSŤ", 12, ">"), ("RAW", 15, ">")],
        )
        total = sum(v[1] for v in volumes)
        print(f"{'CELKOM':<{col_name}}  {format_size(total):>12}")
        print(f"\nPočet volumes: {len(volumes)}\n")


if __name__ == "__main__":
    main()
