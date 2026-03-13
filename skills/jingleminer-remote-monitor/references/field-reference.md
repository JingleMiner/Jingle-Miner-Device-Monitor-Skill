# Remote Monitor Field Reference

## Field Meanings

| Field | Recommended Label | Meaning | Display Guidance |
| --- | --- | --- | --- |
| `ASICModel` | ASIC Model | ASIC chip model. | Display the raw value directly. |
| `algorithm` | Algorithm | Current mining algorithm. | Display directly, for example `sha256d`. |
| `bestDiff` | Best Difficulty | Highest share difficulty ever reported by the device. | Preserve the raw API format, for example `328M`. |
| `bestSessionDiff` | Best Session Difficulty | Highest share difficulty during the current runtime session. | Preserve the raw API format. |
| `coreVoltageActual` | Core Voltage Raw Reading | Firmware telemetry value for chip core voltage. | The unit is not guaranteed by the API contract, so display it as a raw reading. |
| `current` | Input Current | Power input current reading. | If conversion is needed, explain it is commonly interpreted as mA; otherwise keep the raw value. |
| `deviceModel` | Device Model | Device or control board model identifier. | Display the raw value directly. |
| `fallbackStratumPort` | Fallback Pool Port | Port of the fallback mining pool. | Display directly. |
| `fallbackStratumURL` | Fallback Pool URL | Hostname or address of the fallback mining pool. | Display directly. |
| `fallbackStratumUser` | Fallback Pool User | Mining username or wallet address for the fallback pool. | Display directly, and mask part of it only if privacy is required. |
| `fanrpm` | Fan RPM | Current fan speed in revolutions per minute. | Display as `3207 RPM`. |
| `fanspeed` | Fan Speed Percent | Fan control percentage. | Display as `60%`. |
| `frequency` | Frequency | Working frequency of the chip or board. | It can often be treated as MHz, but if uncertain, describe it as a raw frequency reading. |
| `hashRate` | Hashrate | Raw hashrate value. | Convert from H/s to GH/s, TH/s, or PH/s for display. |
| `hostip` | LAN IP | Current LAN IP address of the miner. | Display directly. |
| `hostname` | Hostname | Miner hostname. | Display directly. |
| `isStratumConnected` | Pool Connection Status | Whether the miner is currently connected to a stratum pool. | Display `true` as `Connected` and `false` as `Disconnected`. |
| `isUsingFallbackStratum` | Using Fallback Pool | Whether the miner has switched to the fallback pool. | Display `true` as `Yes` and mention that the primary pool may be unavailable. |
| `jobInterval` | Job Interval | Pool job refresh or work interval. | Display as milliseconds, for example `500 ms`. |
| `macAddr` | MAC Address | MAC address of the miner network interface. | Display directly. |
| `poolDifficulty` | Pool Difficulty | Pool-side job difficulty. | Display the raw value directly. |
| `power` | Power Draw | Current total device power draw. | Display as watts, for example `220.67 W`. |
| `runningPartition` | Running Partition | Currently active firmware partition. | Display directly, for example `ota_1`. |
| `sharesAccepted` | Accepted Shares | Number of shares accepted by the pool. | Display as an integer. |
| `sharesRejected` | Rejected Shares | Number of shares rejected by the pool. | Display as an integer, and calculate reject rate when useful. |
| `stratumDifficulty` | Stratum Difficulty | Difficulty used by the current stratum session. | Display the raw value directly. |
| `stratumPort` | Primary Pool Port | Port of the current primary pool. | Display directly. |
| `stratumURL` | Primary Pool URL | Hostname or address of the current primary pool. | Display directly. |
| `stratumUser` | Primary Pool User | Username, worker, or wallet address for the current primary pool. | Display directly, and mask part of it only if privacy is required. |
| `temp` | Chip Temperature | Main temperature reading. | Display in Celsius, for example `60 C`. |
| `timestamp` | Data Timestamp | Telemetry sample timestamp. | Convert the Unix millisecond timestamp into readable date and time. |
| `uuid` | Device UUID | Unique device identifier. | Display directly. |
| `version` | Firmware Version | Current firmware version of the device. | Display directly, for example `V1.0.0`. |
| `voltage` | Input Voltage | Power input voltage reading. | If conversion is needed, explain it is commonly interpreted as mV; otherwise keep the raw value. |
| `vrTemp` | VR Temperature | Temperature of the voltage regulation or power stage area. | Display in Celsius, for example `54 C`. |

## Recommended User-Facing Sections

1. Device Overview
2. Mining Status
3. Pool Configuration
4. Thermal and Power
5. Field Reference

## Interpretation Notes

- When the raw `hashRate` value is very large, prefer converting it to TH/s.
- `sharesRejected` can be combined with `sharesAccepted` to calculate a reject rate.
- `telemetryError` is not a field inside `data`; it is an extra warning returned by the API call.
- For fields such as `current`, `voltage`, `coreVoltageActual`, and `frequency`, avoid definitive diagnostic conclusions unless the API documentation explicitly guarantees the units.
