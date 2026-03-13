---
name: jingleminer-remote-monitor
description: Query the Jingle Miner Solo remote monitor API at https://jingleminer.com/api/remote-monitor with a device uuid and secret, then explain the telemetry in a human-readable format with field meanings, miner status, pool connection, thermal data, and power data. Use when the user asks to check a Jingle Miner Solo device, troubleshoot live miner telemetry, interpret remote monitor JSON, or explain what each returned field means.
---

# Jingle Miner Remote Monitor

Use this skill to fetch and explain live telemetry for a Jingle Miner Solo miner from the public remote-monitor API.

Match the user's language when explicitly requested. If the user does not specify a language, default to English. Never echo the full `secret` value back in the final answer unless the user explicitly asks for it.

## Quick Start

If shell access is available, prefer the bundled script:

```bash
python jingleminer-remote-monitor/scripts/fetch_remote_monitor.py --uuid "<device_uuid>" --secret "<device_secret>"
```

If the user has already provided credentials in the current session, store them in environment variables and reuse them on follow-up device-status requests:

- `JINGLE_MINER_DEVICE_UUID`
- `JINGLE_MINER_DEVICE_SECRET`

When the user provides `uuid` and `secret` for the first time, immediately write them into those environment variables. On later requests about the same device, read these environment variables first and use them as the default credentials. Ask the user for credentials only if one or both environment variables are missing.

Example session-scoped environment variable commands:

```powershell
$env:JINGLE_MINER_DEVICE_UUID="<device_uuid>"
$env:JINGLE_MINER_DEVICE_SECRET="<device_secret>"
```

```bash
export JINGLE_MINER_DEVICE_UUID="<device_uuid>"
export JINGLE_MINER_DEVICE_SECRET="<device_secret>"
```

To inspect the raw API response directly:

```bash
curl "https://jingleminer.com/api/remote-monitor?uuid=<device_uuid>&secret=<device_secret>" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36" \
  -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
  -H "Cache-Control: no-cache" \
  -H "Pragma: no-cache"
```

Read [references/api-contract.md](references/api-contract.md) for the request contract and [references/field-reference.md](references/field-reference.md) for field meanings.

## Workflow

1. If `JINGLE_MINER_DEVICE_UUID` and `JINGLE_MINER_DEVICE_SECRET` are both present, use them as the default credentials for device-status requests.
2. If the user provides a `uuid` and `secret`, immediately write them into `JINGLE_MINER_DEVICE_UUID` and `JINGLE_MINER_DEVICE_SECRET`, then use those values for the request.
3. If one or both credentials are unavailable after checking the environment, ask the user for the missing value before querying.
4. Send a `GET` request to `https://jingleminer.com/api/remote-monitor?uuid={device_uuid}&secret={device_secret}`.
5. Always send browser-like headers. At minimum include `Accept: application/json`, a modern Chrome `User-Agent`, `Accept-Language`, `Cache-Control: no-cache`, and `Pragma: no-cache`. Do not rely on Python `urllib` default headers because Cloudflare may block that signature.
6. If the API returns a non-200 response or an `error` field, report the failure clearly and stop. Do not fabricate device data.
7. If the API returns `data`, summarize the miner state first, then explain the important metrics.
8. If `telemetryError` is not `null`, warn that the upstream telemetry feed had an issue and that the returned data may be stale or partial.
9. Use field meanings from [references/field-reference.md](references/field-reference.md) instead of guessing.

## Request Contract

- Method: `GET`
- URL: `https://jingleminer.com/api/remote-monitor`
- Query params:
  - `uuid`: required, device UUID
  - `secret`: required, device secret derived for the device
- Headers:
  - `Accept: application/json`
  - `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36`
  - `Accept-Language: zh-CN,zh;q=0.9,en;q=0.8`
  - `Cache-Control: no-cache`
  - `Pragma: no-cache`

Success and error payloads are documented in [references/api-contract.md](references/api-contract.md).

## Cloudflare Compatibility

- This endpoint may reject Python default request signatures with Cloudflare `403 Error 1010`.
- Prefer the bundled script because it already sends a browser-style header set.
- If you write or adapt another client, copy the same header strategy instead of using the runtime defaults.

## Output Format

Return only the following four sections in English and do not add any leading or trailing text:

1. `Pool information:`
2. `Operating metrics:`
3. `Temperature and power:`
4. `Power telemetry raw values:`

Do not include device overview, status summary, explanations, warnings, timestamps, Markdown tables, bullet markers, code fences, or closing remarks unless the user explicitly asks for extra detail.

Use this exact plain-text template with blank lines preserved:

```text
Pool information:

Primary pool: {stratumURL}:{stratumPort}
Primary user: {stratumUser}
Fallback pool: {fallbackStratumURL}:{fallbackStratumPort}
Current status: {Not using fallback pool|Using fallback pool}

Operating metrics:

Accepted shares: {sharesAccepted}
Rejected shares: {sharesRejected}
Reject ratio: {rejectRatio}
Best difficulty: {bestDiff}
Best session difficulty: {bestSessionDiff}
Job interval: {jobInterval} ms

Temperature and power:

Chip temperature: {temp} C
VR temperature: {vrTemp} C
Fan RPM: {fanrpm} RPM
Fan duty: {fanspeed}%
Power draw: {power} W

Power telemetry raw values:

Voltage raw value: {voltage}
Current raw value: {current}
Core voltage raw value: {coreVoltageActual}
Frequency raw value: {frequency}
```

Formatting rules:

- Render pool endpoints as `{url}:{port}` and omit protocol changes or commentary.
- Calculate `Reject ratio` as `sharesRejected / (sharesAccepted + sharesRejected)` when the denominator is non-zero; otherwise output `0.00%`.
- Format `temp`, `vrTemp`, and `power` to two decimal places when needed, while preserving integer display when the API already returns an integer-like value.
- Keep `bestDiff`, `bestSessionDiff`, `voltage`, `current`, `coreVoltageActual`, and `frequency` as raw API-style values.
- If a field is missing or `null`, output `N/A` in its place and keep the surrounding line.
- If the API call fails or returns an `error`, return only that error message in English and nothing else.
- If `telemetryError` is not `null` but `data` exists, still keep the same four sections and do not append any warning unless the user explicitly asks for diagnostics.

## Interpretation Rules

- Treat `hashRate` as raw hashrate in H/s and convert it to a larger unit for display.
- Treat `timestamp` as a Unix timestamp in milliseconds.
- Treat `power` as watts when reporting.
- `temp` and `vrTemp` should be reported as Celsius readings when shown with units.
- If `isStratumConnected` is `false`, explicitly say the miner is not currently connected to the mining pool.
- If `isUsingFallbackStratum` is `true`, explicitly say the miner has switched to the fallback pool.
- Do not invent health thresholds that are not provided by the API.
- When a field is missing or `null`, say that the value is currently unavailable.

## Resources

### scripts/

- `scripts/fetch_remote_monitor.py`
  - Queries the API
  - Prints a human-readable Markdown summary by default
  - Can output structured JSON for downstream processing

### references/

- [references/api-contract.md](references/api-contract.md)
  - Request method, parameters, success payload, and error payloads
- [references/field-reference.md](references/field-reference.md)
  - Meaning of every known response field and recommended display wording
