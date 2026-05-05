from __future__ import annotations

import argparse
import csv
import gzip
import json
import socket
import struct
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterator


DEFAULT_INPUT = Path("data/external/wannaCry_15052017.pcap.gz")
DEFAULT_OUTPUT = Path("data/processed/wannacry_flows.csv")
DEFAULT_SUMMARY = Path("data/processed/wannacry_pcap_summary.json")

TCP_FLAG_NAMES = {
    0x01: "fin",
    0x02: "syn",
    0x04: "rst",
    0x08: "psh",
    0x10: "ack",
    0x20: "urg",
}


@dataclass(frozen=True)
class ParsedPacket:
    timestamp: float
    src_ip: str
    dst_ip: str
    protocol: str
    src_port: int | None
    dst_port: int | None
    length: int
    tcp_flags: int = 0


def _open_capture(path: Path) -> BinaryIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rb")
    return path.open("rb")


def _read_exact(handle: BinaryIO, size: int) -> bytes | None:
    data = handle.read(size)
    if len(data) != size:
        return None
    return data


def _pcap_endian_and_header(handle: BinaryIO) -> tuple[str, int]:
    header = _read_exact(handle, 24)
    if header is None:
        raise ValueError("El archivo PCAP esta incompleto o vacio.")

    magic = header[:4]
    if magic == b"\xd4\xc3\xb2\xa1":
        endian = "<"
    elif magic == b"\xa1\xb2\xc3\xd4":
        endian = ">"
    else:
        raise ValueError(f"Formato no soportado. Magic bytes: {magic.hex()}")

    linktype = struct.unpack(f"{endian}I", header[20:24])[0]
    return endian, linktype


def _ipv4_address(raw: bytes) -> str:
    return socket.inet_ntoa(raw)


def _parse_ethernet_ipv4(payload: bytes, timestamp: float) -> ParsedPacket | None:
    if len(payload) < 14:
        return None

    offset = 14
    ethertype = struct.unpack("!H", payload[12:14])[0]

    # 802.1Q VLAN tag.
    if ethertype == 0x8100 and len(payload) >= 18:
        ethertype = struct.unpack("!H", payload[16:18])[0]
        offset = 18

    if ethertype != 0x0800 or len(payload) < offset + 20:
        return None

    version_ihl = payload[offset]
    version = version_ihl >> 4
    ihl = (version_ihl & 0x0F) * 4
    if version != 4 or ihl < 20 or len(payload) < offset + ihl:
        return None

    total_length = struct.unpack("!H", payload[offset + 2 : offset + 4])[0]
    protocol_number = payload[offset + 9]
    src_ip = _ipv4_address(payload[offset + 12 : offset + 16])
    dst_ip = _ipv4_address(payload[offset + 16 : offset + 20])

    transport_offset = offset + ihl
    src_port = None
    dst_port = None
    tcp_flags = 0

    if protocol_number == 6 and len(payload) >= transport_offset + 20:
        protocol = "TCP"
        src_port, dst_port = struct.unpack("!HH", payload[transport_offset : transport_offset + 4])
        tcp_flags = payload[transport_offset + 13]
    elif protocol_number == 17 and len(payload) >= transport_offset + 8:
        protocol = "UDP"
        src_port, dst_port = struct.unpack("!HH", payload[transport_offset : transport_offset + 4])
    elif protocol_number == 1:
        protocol = "ICMP"
    else:
        protocol = f"IP_{protocol_number}"

    return ParsedPacket(
        timestamp=timestamp,
        src_ip=src_ip,
        dst_ip=dst_ip,
        protocol=protocol,
        src_port=src_port,
        dst_port=dst_port,
        length=total_length,
        tcp_flags=tcp_flags,
    )


def iter_packets(path: Path, max_packets: int | None = None) -> Iterator[ParsedPacket]:
    with _open_capture(path) as handle:
        endian, linktype = _pcap_endian_and_header(handle)
        if linktype != 1:
            raise ValueError(f"Solo se soporta Ethernet/linktype 1. Linktype encontrado: {linktype}")

        seen = 0
        while True:
            packet_header = _read_exact(handle, 16)
            if packet_header is None:
                break

            ts_sec, ts_usec, included_len, _original_len = struct.unpack(f"{endian}IIII", packet_header)
            packet_data = _read_exact(handle, included_len)
            if packet_data is None:
                break

            seen += 1
            parsed = _parse_ethernet_ipv4(packet_data, ts_sec + (ts_usec / 1_000_000))
            if parsed is not None:
                yield parsed

            if max_packets is not None and seen >= max_packets:
                break


def _empty_flow(packet: ParsedPacket) -> dict[str, object]:
    return {
        "src_ip": packet.src_ip,
        "dst_ip": packet.dst_ip,
        "protocol": packet.protocol,
        "src_port": packet.src_port or "",
        "dst_port": packet.dst_port or "",
        "first_seen": packet.timestamp,
        "last_seen": packet.timestamp,
        "packets": 0,
        "bytes": 0,
        "tcp_syn": 0,
        "tcp_ack": 0,
        "tcp_rst": 0,
        "tcp_fin": 0,
    }


def aggregate_packets(path: Path, max_packets: int | None = None) -> tuple[list[dict[str, object]], dict[str, object]]:
    flows: dict[tuple[str, str, str, int | None, int | None], dict[str, object]] = {}
    protocol_counts: Counter[str] = Counter()
    dst_port_counts: Counter[str] = Counter()
    src_ips: set[str] = set()
    dst_ips: set[str] = set()
    first_seen: float | None = None
    last_seen: float | None = None
    parsed_packets = 0
    total_bytes = 0

    for packet in iter_packets(path, max_packets=max_packets):
        parsed_packets += 1
        total_bytes += packet.length
        protocol_counts[packet.protocol] += 1
        src_ips.add(packet.src_ip)
        dst_ips.add(packet.dst_ip)
        if packet.dst_port is not None:
            dst_port_counts[str(packet.dst_port)] += 1

        first_seen = packet.timestamp if first_seen is None else min(first_seen, packet.timestamp)
        last_seen = packet.timestamp if last_seen is None else max(last_seen, packet.timestamp)

        key = (packet.src_ip, packet.dst_ip, packet.protocol, packet.src_port, packet.dst_port)
        flow = flows.setdefault(key, _empty_flow(packet))
        flow["packets"] = int(flow["packets"]) + 1
        flow["bytes"] = int(flow["bytes"]) + packet.length
        flow["first_seen"] = min(float(flow["first_seen"]), packet.timestamp)
        flow["last_seen"] = max(float(flow["last_seen"]), packet.timestamp)

        if packet.protocol == "TCP":
            for flag, name in TCP_FLAG_NAMES.items():
                if packet.tcp_flags & flag:
                    column = f"tcp_{name}"
                    if column in flow:
                        flow[column] = int(flow[column]) + 1

    flow_rows = list(flows.values())
    flow_rows.sort(key=lambda row: (int(row["packets"]), int(row["bytes"])), reverse=True)

    summary = {
        "source_file": str(path),
        "parsed_ipv4_packets": parsed_packets,
        "unique_flows": len(flow_rows),
        "unique_src_ips": len(src_ips),
        "unique_dst_ips": len(dst_ips),
        "total_ip_bytes": total_bytes,
        "first_seen_utc": _format_timestamp(first_seen),
        "last_seen_utc": _format_timestamp(last_seen),
        "duration_seconds": None if first_seen is None or last_seen is None else round(last_seen - first_seen, 6),
        "protocol_counts": dict(protocol_counts.most_common()),
        "top_dst_ports": dict(dst_port_counts.most_common(20)),
    }
    return flow_rows, summary


def _format_timestamp(value: float | None) -> str | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def write_flows(rows: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "src_ip",
        "dst_ip",
        "protocol",
        "src_port",
        "dst_port",
        "first_seen",
        "last_seen",
        "packets",
        "bytes",
        "tcp_syn",
        "tcp_ack",
        "tcp_rst",
        "tcp_fin",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(summary: dict[str, object], summary_path: Path) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae flujos agregados desde el PCAP de WannaCry.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--max-packets", type=int, default=None, help="Limita paquetes leidos para pruebas rapidas.")
    args = parser.parse_args()

    rows, summary = aggregate_packets(args.input, max_packets=args.max_packets)
    write_flows(rows, args.output)
    write_summary(summary, args.summary)

    print(f"Flujos guardados: {args.output} ({len(rows)} filas)")
    print(f"Resumen guardado: {args.summary}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
