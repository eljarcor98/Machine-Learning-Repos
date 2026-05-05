from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


DEFAULT_INPUT_GLOB = "data/external/Free Automated*.html"
DEFAULT_HOSTS_CSV = Path("data/processed/hybrid_analysis_contacted_hosts_geo.csv")
DEFAULT_COUNTRIES_CSV = Path("data/processed/hybrid_analysis_contacted_countries.csv")
DEFAULT_GRAPHML = Path("data/processed/hybrid_analysis_contacted_hosts_geo.graphml")
DEFAULT_SUMMARY = Path("data/processed/hybrid_analysis_contacted_hosts_summary.json")
DEFAULT_FIGURE = Path("reports/figures/hybrid_analysis_contacted_hosts_geo.png")

SOURCE_NODE = "mssecsvc.exe:3192"

# Approximate country centroids. These coordinates are for visualization and
# aggregation, not precise host geolocation.
COUNTRY_CENTROIDS = {
    "Australia": (-25.2744, 133.7751),
    "Austria": (47.5162, 14.5501),
    "Belgium": (50.5039, 4.4699),
    "Brazil": (-14.2350, -51.9253),
    "Canada": (56.1304, -106.3468),
    "Chile": (-35.6751, -71.5430),
    "China": (35.8617, 104.1954),
    "Colombia": (4.5709, -74.2973),
    "Denmark": (56.2639, 9.5018),
    "Dominican Republic": (18.7357, -70.1627),
    "Egypt": (26.8206, 30.8025),
    "France": (46.2276, 2.2137),
    "Germany": (51.1657, 10.4515),
    "Greece": (39.0742, 21.8243),
    "Hong Kong": (22.3193, 114.1694),
    "India": (20.5937, 78.9629),
    "Indonesia": (-0.7893, 113.9213),
    "Iran (ISLAMIC Republic Of)": (32.4279, 53.6880),
    "Ireland": (53.1424, -7.6921),
    "Israel": (31.0461, 34.8516),
    "Italy": (41.8719, 12.5674),
    "Japan": (36.2048, 138.2529),
    "Kazakhstan": (48.0196, 66.9237),
    "Korea Republic of": (35.9078, 127.7669),
    "Latvia": (56.8796, 24.6032),
    "Lithuania": (55.1694, 23.8813),
    "Mexico": (23.6345, -102.5528),
    "Moldova Republic of": (47.4116, 28.3699),
    "Netherlands": (52.1326, 5.2913),
    "New Zealand": (-40.9006, 174.8860),
    "Norway": (60.4720, 8.4689),
    "Russian Federation": (61.5240, 105.3188),
    "Saudi Arabia": (23.8859, 45.0792),
    "Serbia": (44.0165, 21.0059),
    "South Africa": (-30.5595, 22.9375),
    "Spain": (40.4637, -3.7492),
    "Sweden": (60.1282, 18.6435),
    "Taiwan; Republic of China (ROC)": (23.6978, 120.9605),
    "Thailand": (15.8700, 100.9925),
    "Turkey": (38.9637, 35.2433),
    "United Kingdom": (55.3781, -3.4360),
    "United States": (37.0902, -95.7129),
    "Venezuela": (6.4238, -66.5897),
    "Viet Nam": (14.0583, 108.2772),
}


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if value:
            self.parts.append(value)


def html_text_parts(html: str) -> list[str]:
    parser = TextExtractor()
    parser.feed(html)
    return parser.parts


def resolve_input(path_or_glob: str) -> Path:
    path = Path(path_or_glob)
    if path.exists():
        return path
    matches = sorted(Path(".").glob(path_or_glob))
    if not matches:
        raise FileNotFoundError(f"No se encontro HTML con patron: {path_or_glob}")
    return matches[0]


def parse_contacted_hosts(html_path: Path) -> list[dict[str, object]]:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    start = html.find('id="contacted-hosts"')
    end = html.find('id="contacted-countries"', start)
    if start == -1 or end == -1:
        raise ValueError("No se encontro la seccion contacted-hosts/contacted-countries.")

    section = html[start:end]
    rows = re.findall(r"<tr>\s*(.*?)\s*</tr>", section, flags=re.S)
    records: list[dict[str, object]] = []

    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)
        if len(cells) < 4:
            continue

        cell_parts = [html_text_parts(cell) for cell in cells]
        ip = next((part for part in cell_parts[0] if re.match(r"^\d+\.\d+\.\d+\.\d+$", part)), "")
        if not ip:
            continue

        port = next((part for part in cell_parts[1] if part.isdigit()), "")
        protocol = next((part for part in cell_parts[1] if part in {"TCP", "UDP", "ICMP"}), "")
        process = cell_parts[2][0] if cell_parts[2] else ""
        pid = ""
        for part in cell_parts[2]:
            match = re.search(r"PID:\s*(\d+)", part)
            if match:
                pid = match.group(1)

        detail = " ".join(cell_parts[3])
        country = cell_parts[3][0] if cell_parts[3] else ""
        asn = ""
        organization = ""
        asn_match = re.search(r"ASN:\s*(\d+)\s*\((.*?)\)", detail)
        if asn_match:
            asn = asn_match.group(1)
            organization = asn_match.group(2)

        latitude, longitude = COUNTRY_CENTROIDS.get(country, ("", ""))
        records.append(
            {
                "ip": ip,
                "port": port,
                "protocol": protocol,
                "process": process,
                "pid": pid,
                "country": country,
                "asn": asn,
                "organization": organization,
                "latitude": latitude,
                "longitude": longitude,
                "has_coordinates": bool(latitude != "" and longitude != ""),
            }
        )

    return records


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def country_summary(records: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(str(row["country"]) for row in records)
    rows = []
    for country, hosts in counts.most_common():
        latitude, longitude = COUNTRY_CENTROIDS.get(country, ("", ""))
        rows.append(
            {
                "country": country,
                "hosts": hosts,
                "latitude": latitude,
                "longitude": longitude,
                "has_coordinates": bool(latitude != "" and longitude != ""),
            }
        )
    return rows


def build_graph(records: list[dict[str, object]]) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node(
        SOURCE_NODE,
        node_type="process",
        process="mssecsvc.exe",
        pid="3192",
        latitude="",
        longitude="",
        country="Sandbox process",
    )

    for row in records:
        graph.add_node(
            row["ip"],
            node_type="contacted_host",
            country=row["country"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            asn=row["asn"],
            organization=row["organization"],
        )
        graph.add_edge(
            SOURCE_NODE,
            row["ip"],
            port=row["port"],
            protocol=row["protocol"],
            process=row["process"],
            pid=row["pid"],
        )
    return graph


def plot_country_map(country_rows: list[dict[str, object]], output_path: Path) -> None:
    plotted = [row for row in country_rows if row["has_coordinates"]]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title("Hybrid Analysis - hosts contactados por pais")
    ax.grid(alpha=0.25)

    longitudes = [float(row["longitude"]) for row in plotted]
    latitudes = [float(row["latitude"]) for row in plotted]
    sizes = [35 + (float(row["hosts"]) ** 0.75) * 35 for row in plotted]
    ax.scatter(longitudes, latitudes, s=sizes, color="#c43c3c", alpha=0.68, edgecolors="#263238")

    for row in plotted[:12]:
        ax.annotate(
            f"{row['country']} ({row['hosts']})",
            (float(row["longitude"]), float(row["latitude"])),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae Contacted Hosts desde un HTML de Hybrid Analysis.")
    parser.add_argument("--input", default=DEFAULT_INPUT_GLOB)
    parser.add_argument("--hosts-csv", type=Path, default=DEFAULT_HOSTS_CSV)
    parser.add_argument("--countries-csv", type=Path, default=DEFAULT_COUNTRIES_CSV)
    parser.add_argument("--graphml", type=Path, default=DEFAULT_GRAPHML)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    args = parser.parse_args()

    html_path = resolve_input(args.input)
    records = parse_contacted_hosts(html_path)
    countries = country_summary(records)
    graph = build_graph(records)

    host_fields = [
        "ip",
        "port",
        "protocol",
        "process",
        "pid",
        "country",
        "asn",
        "organization",
        "latitude",
        "longitude",
        "has_coordinates",
    ]
    write_csv(args.hosts_csv, records, host_fields)
    write_csv(args.countries_csv, countries, ["country", "hosts", "latitude", "longitude", "has_coordinates"])

    args.graphml.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, args.graphml)
    plot_country_map(countries, args.figure)

    summary = {
        "source_html": str(html_path),
        "hosts": len(records),
        "countries": len(countries),
        "hosts_with_coordinates": sum(1 for row in records if row["has_coordinates"]),
        "countries_without_coordinates": [row["country"] for row in countries if not row["has_coordinates"]],
        "top_countries": countries[:15],
        "outputs": {
            "hosts_csv": str(args.hosts_csv),
            "countries_csv": str(args.countries_csv),
            "graphml": str(args.graphml),
            "figure": str(args.figure),
        },
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    with args.summary.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
