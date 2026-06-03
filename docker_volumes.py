#!/usr/bin/env python3
"""Zobrazí zoznam Docker volumes zoradený podľa veľkosti (od najväčších po najmenšie)."""

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


def main():
    volumes = get_volumes_with_sizes()

    if not volumes:
        print("Nenašli sa žiadne Docker volumes.")
        return

    # Zoradenie od najväčších po najmenšie
    volumes.sort(key=lambda x: x[1], reverse=True)

    # Výpočet šírky stĺpcov pre zarovnanie
    max_name_len = max(len(v[0]) for v in volumes)
    col_name = max(max_name_len, 11)  # min. šírka "VOLUME NAME"

    header = f"{'VOLUME NAME':<{col_name}}  {'VEĽKOSŤ':>12}  {'VEĽKOSŤ (raw)':>15}"
    separator = "-" * len(header)

    print(f"\nDocker volumes zoradené podľa veľkosti:\n")
    print(header)
    print(separator)

    for name, size_bytes, size_raw in volumes:
        print(f"{name:<{col_name}}  {format_size(size_bytes):>12}  {size_raw:>15}")

    print(separator)
    total = sum(v[1] for v in volumes)
    print(f"{'CELKOM':<{col_name}}  {format_size(total):>12}")
    print(f"\nPočet volumes: {len(volumes)}\n")


if __name__ == "__main__":
    main()
