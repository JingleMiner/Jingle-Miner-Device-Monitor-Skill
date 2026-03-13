#!/usr/bin/env python3
"""Fetch and format Jingle Miner remote monitor telemetry."""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any


API_URL = "https://jingleminer.com/api/remote-monitor"
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/134.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

FIELD_META: dict[str, dict[str, str]] = {
    "ASICModel": {"label": "ASIC model", "meaning": "ASIC chip model"},
    "algorithm": {"label": "Algorithm", "meaning": "Current mining algorithm"},
    "bestDiff": {"label": "Best difficulty", "meaning": "Best share difficulty reported by the miner"},
    "bestSessionDiff": {
        "label": "Best session difficulty",
        "meaning": "Best share difficulty during the current session",
    },
    "coreVoltageActual": {
        "label": "Core voltage raw reading",
        "meaning": "Firmware telemetry reading for core voltage; unit is not guaranteed by the API",
    },
    "current": {"label": "Input current", "meaning": "Power input current reading"},
    "deviceModel": {"label": "Device model", "meaning": "Device or controller board model"},
    "fallbackStratumPort": {"label": "Fallback pool port", "meaning": "Fallback pool port"},
    "fallbackStratumURL": {"label": "Fallback pool URL", "meaning": "Fallback pool hostname or address"},
    "fallbackStratumUser": {"label": "Fallback pool user", "meaning": "Fallback pool worker name or wallet"},
    "fanrpm": {"label": "Fan RPM", "meaning": "Current fan speed in revolutions per minute"},
    "fanspeed": {"label": "Fan speed percent", "meaning": "Fan control duty percentage"},
    "frequency": {"label": "Frequency", "meaning": "Working frequency reading"},
    "hashRate": {"label": "Hashrate", "meaning": "Raw hashrate value"},
    "hostip": {"label": "LAN IP", "meaning": "Current LAN IP address"},
    "hostname": {"label": "Hostname", "meaning": "Miner hostname"},
    "isStratumConnected": {"label": "Pool connected", "meaning": "Whether the miner is connected to stratum"},
    "isUsingFallbackStratum": {
        "label": "Using fallback pool",
        "meaning": "Whether the miner has switched to the fallback pool",
    },
    "jobInterval": {"label": "Job interval", "meaning": "Pool job refresh interval"},
    "macAddr": {"label": "MAC address", "meaning": "Network MAC address"},
    "poolDifficulty": {"label": "Pool difficulty", "meaning": "Pool-side job difficulty"},
    "power": {"label": "Power", "meaning": "Current device power draw"},
    "runningPartition": {"label": "Running partition", "meaning": "Currently active firmware partition"},
    "sharesAccepted": {"label": "Accepted shares", "meaning": "Number of accepted shares"},
    "sharesRejected": {"label": "Rejected shares", "meaning": "Number of rejected shares"},
    "stratumDifficulty": {"label": "Stratum difficulty", "meaning": "Current stratum session difficulty"},
    "stratumPort": {"label": "Primary pool port", "meaning": "Primary pool port"},
    "stratumURL": {"label": "Primary pool URL", "meaning": "Primary pool hostname or address"},
    "stratumUser": {"label": "Primary pool user", "meaning": "Primary pool worker name or wallet"},
    "temp": {"label": "Chip temperature", "meaning": "Main temperature reading"},
    "timestamp": {"label": "Timestamp", "meaning": "Telemetry sample time"},
    "uuid": {"label": "Device UUID", "meaning": "Device unique identifier"},
    "version": {"label": "Firmware version", "meaning": "Current firmware version"},
    "voltage": {"label": "Input voltage", "meaning": "Power input voltage reading"},
    "vrTemp": {"label": "VR temperature", "meaning": "Voltage regulator or power stage temperature"},
}

FIELD_ORDER = [
    "deviceModel",
    "ASICModel",
    "algorithm",
    "hashRate",
    "power",
    "temp",
    "vrTemp",
    "fanrpm",
    "fanspeed",
    "frequency",
    "isStratumConnected",
    "isUsingFallbackStratum",
    "stratumURL",
    "stratumPort",
    "stratumUser",
    "fallbackStratumURL",
    "fallbackStratumPort",
    "fallbackStratumUser",
    "poolDifficulty",
    "stratumDifficulty",
    "sharesAccepted",
    "sharesRejected",
    "bestDiff",
    "bestSessionDiff",
    "jobInterval",
    "hostip",
    "hostname",
    "macAddr",
    "runningPartition",
    "version",
    "uuid",
    "timestamp",
    "voltage",
    "current",
    "coreVoltageActual",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query the Jingle Miner remote monitor API and format the result."
    )
    parser.add_argument("--uuid", required=True, help="Device UUID")
    parser.add_argument("--secret", required=True, help="Device secret")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP timeout in seconds",
    )
    return parser.parse_args()


def request_payload(uuid: str, secret: str, timeout: float) -> tuple[int, dict[str, Any]]:
    query = urllib.parse.urlencode({"uuid": uuid, "secret": secret})
    url = f"{API_URL}?{query}"
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            payload = json.loads(body)
            return response.status, payload
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        payload: dict[str, Any] = {"error": body}
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            pass
        return exc.code, payload


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, str):
        try:
            number = float(value.strip())
        except ValueError:
            return None
        return number if math.isfinite(number) else None
    return None


def format_hashrate(value: Any) -> str:
    number = as_number(value)
    if number is None:
        return "Unavailable"

    units = ["H/s", "KH/s", "MH/s", "GH/s", "TH/s", "PH/s"]
    index = 0
    while number >= 1000 and index < len(units) - 1:
        number /= 1000
        index += 1
    return f"{number:.2f} {units[index]}"


def format_watts(value: Any) -> str:
    number = as_number(value)
    if number is None:
        return "Unavailable"
    return f"{number:.2f} W"


def format_temp(value: Any) -> str:
    number = as_number(value)
    if number is None:
        return "Unavailable"
    return f"{number:.0f} C"


def format_percent(value: Any) -> str:
    number = as_number(value)
    if number is None:
        return "Unavailable"
    return f"{number:.0f}%"


def format_rpm(value: Any) -> str:
    number = as_number(value)
    if number is None:
        return "Unavailable"
    return f"{number:.0f} RPM"


def format_timestamp(value: Any) -> str:
    number = as_number(value)
    if number is None:
        return "Unavailable"

    if number < 1_000_000_000_000:
        number *= 1000

    dt = datetime.fromtimestamp(number / 1000).astimezone()
    return dt.isoformat(timespec="seconds")


def format_bool(value: Any) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Unavailable"


def format_raw(value: Any) -> str:
    if value is None:
        return "Unavailable"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def summarize(data: dict[str, Any], telemetry_error: Any) -> dict[str, Any]:
    accepted = as_number(data.get("sharesAccepted")) or 0
    rejected = as_number(data.get("sharesRejected")) or 0
    total_shares = accepted + rejected
    reject_rate = f"{(rejected / total_shares) * 100:.2f}%" if total_shares else "Unavailable"

    job_interval = as_number(data.get("jobInterval"))

    return {
        "overview": {
            "device_model": format_raw(data.get("deviceModel")),
            "asic_model": format_raw(data.get("ASICModel")),
            "hostname": format_raw(data.get("hostname")),
            "host_ip": format_raw(data.get("hostip")),
            "mac_address": format_raw(data.get("macAddr")),
            "firmware_version": format_raw(data.get("version")),
            "uuid": format_raw(data.get("uuid")),
            "timestamp": format_timestamp(data.get("timestamp")),
        },
        "status": {
            "pool_connected": "Connected" if data.get("isStratumConnected") is True else "Disconnected",
            "using_fallback_pool": format_bool(data.get("isUsingFallbackStratum")),
            "algorithm": format_raw(data.get("algorithm")),
            "hash_rate": format_hashrate(data.get("hashRate")),
            "shares_accepted": int(accepted),
            "shares_rejected": int(rejected),
            "rejected_ratio": reject_rate,
            "best_diff": format_raw(data.get("bestDiff")),
            "best_session_diff": format_raw(data.get("bestSessionDiff")),
        },
        "pool": {
            "primary_url": format_raw(data.get("stratumURL")),
            "primary_port": format_raw(data.get("stratumPort")),
            "primary_user": format_raw(data.get("stratumUser")),
            "fallback_url": format_raw(data.get("fallbackStratumURL")),
            "fallback_port": format_raw(data.get("fallbackStratumPort")),
            "fallback_user": format_raw(data.get("fallbackStratumUser")),
            "pool_difficulty": format_raw(data.get("poolDifficulty")),
            "stratum_difficulty": format_raw(data.get("stratumDifficulty")),
            "job_interval": f"{job_interval:.0f} ms" if job_interval is not None else "Unavailable",
        },
        "thermal_power": {
            "chip_temp": format_temp(data.get("temp")),
            "vr_temp": format_temp(data.get("vrTemp")),
            "fan_rpm": format_rpm(data.get("fanrpm")),
            "fan_speed": format_percent(data.get("fanspeed")),
            "power": format_watts(data.get("power")),
            "voltage_raw": format_raw(data.get("voltage")),
            "current_raw": format_raw(data.get("current")),
            "core_voltage_actual_raw": format_raw(data.get("coreVoltageActual")),
            "frequency_raw": format_raw(data.get("frequency")),
        },
        "telemetry_warning": telemetry_error,
    }


def build_field_rows(data: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for key in FIELD_ORDER:
        if key not in data:
            continue
        meta = FIELD_META.get(key, {"label": key, "meaning": "Undefined field"})
        rows.append(
            {
                "field": key,
                "label": meta["label"],
                "meaning": meta["meaning"],
                "value": format_raw(data.get(key)),
            }
        )

    for key in sorted(data.keys()):
        if key in FIELD_ORDER:
            continue
        rows.append(
            {
                "field": key,
                "label": key,
                "meaning": "Field not defined in the local dictionary; interpret from raw response.",
                "value": format_raw(data.get(key)),
            }
        )

    return rows


def to_markdown(status_code: int, payload: dict[str, Any]) -> str:
    if status_code != 200 or "error" in payload:
        error_message = payload.get("error", "Request failed")
        return "\n".join(
            [
                "# Jingle Miner Remote Monitor",
                "",
                f"- Request status: {status_code}",
                f"- Error: {error_message}",
            ]
        )

    data = payload.get("data")
    if not isinstance(data, dict):
        return "# Jingle Miner Remote Monitor\n\n- Request succeeded, but no parseable data payload was returned."

    summary = summarize(data, payload.get("telemetryError"))
    rows = build_field_rows(data)

    lines = [
        "# Jingle Miner Remote Monitor",
        "",
        "## Overview",
        f"- Device model: {summary['overview']['device_model']}",
        f"- ASIC model: {summary['overview']['asic_model']}",
        f"- Hostname: {summary['overview']['hostname']}",
        f"- LAN IP: {summary['overview']['host_ip']}",
        f"- MAC address: {summary['overview']['mac_address']}",
        f"- Firmware version: {summary['overview']['firmware_version']}",
        f"- Device UUID: {summary['overview']['uuid']}",
        f"- Timestamp: {summary['overview']['timestamp']}",
        "",
        "## Mining Status",
        f"- Pool connection: {summary['status']['pool_connected']}",
        f"- Using fallback pool: {summary['status']['using_fallback_pool']}",
        f"- Algorithm: {summary['status']['algorithm']}",
        f"- Hashrate: {summary['status']['hash_rate']}",
        f"- Accepted shares: {summary['status']['shares_accepted']}",
        f"- Rejected shares: {summary['status']['shares_rejected']}",
        f"- Reject ratio: {summary['status']['rejected_ratio']}",
        f"- Best difficulty: {summary['status']['best_diff']}",
        f"- Best session difficulty: {summary['status']['best_session_diff']}",
        "",
        "## Pool Configuration",
        f"- Primary pool: {summary['pool']['primary_url']}:{summary['pool']['primary_port']}",
        f"- Primary user: {summary['pool']['primary_user']}",
        f"- Fallback pool: {summary['pool']['fallback_url']}:{summary['pool']['fallback_port']}",
        f"- Fallback user: {summary['pool']['fallback_user']}",
        f"- Pool difficulty: {summary['pool']['pool_difficulty']}",
        f"- Stratum difficulty: {summary['pool']['stratum_difficulty']}",
        f"- Job interval: {summary['pool']['job_interval']}",
        "",
        "## Thermal and Power",
        f"- Chip temperature: {summary['thermal_power']['chip_temp']}",
        f"- VR temperature: {summary['thermal_power']['vr_temp']}",
        f"- Fan RPM: {summary['thermal_power']['fan_rpm']}",
        f"- Fan speed: {summary['thermal_power']['fan_speed']}",
        f"- Power: {summary['thermal_power']['power']}",
        f"- Input voltage raw: {summary['thermal_power']['voltage_raw']}",
        f"- Input current raw: {summary['thermal_power']['current_raw']}",
        f"- Core voltage raw: {summary['thermal_power']['core_voltage_actual_raw']}",
        f"- Frequency raw: {summary['thermal_power']['frequency_raw']}",
    ]

    warning = summary["telemetry_warning"]
    if warning:
        lines.extend(["", "## Telemetry Warning", f"- {warning}"])

    lines.extend(["", "## Field Reference", "| Field | Label | Value | Meaning |", "| --- | --- | --- | --- |"])
    for row in rows:
        lines.append(f"| `{row['field']}` | {row['label']} | {row['value']} | {row['meaning']} |")

    return "\n".join(lines)


def to_json_output(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    human_readable = None
    field_rows: list[dict[str, str]] = []

    if isinstance(data, dict):
        human_readable = summarize(data, payload.get("telemetryError"))
        field_rows = build_field_rows(data)

    return {
        "request": {
            "method": "GET",
            "url": API_URL,
        },
        "status_code": status_code,
        "success": status_code == 200 and "error" not in payload,
        "api_response": payload,
        "human_readable": human_readable,
        "field_reference": field_rows,
    }


def main() -> int:
    args = parse_args()
    status_code, payload = request_payload(args.uuid, args.secret, args.timeout)

    if args.format == "json":
        print(json.dumps(to_json_output(status_code, payload), ensure_ascii=False, indent=2))
    else:
        print(to_markdown(status_code, payload))

    return 0 if status_code == 200 and "error" not in payload else 1


if __name__ == "__main__":
    sys.exit(main())
