# Remote Monitor API Contract

## Endpoint

- Method: `GET`
- URL: `https://jingleminer.com/api/remote-monitor`

## Query Parameters

| Parameter | Required | Type | Meaning |
| --- | --- | --- | --- |
| `uuid` | Yes | string | Device UUID |
| `secret` | Yes | string | Device secret used for remote monitor access |

## Example Request

```text
GET https://jingleminer.com/api/remote-monitor?uuid=a75629f7-ffc4-47f6-a131-f9321d049203&secret=<device_secret>
Accept: application/json
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cache-Control: no-cache
Pragma: no-cache
```

## Request Header Note

- In production use, this endpoint may be protected by Cloudflare.
- Python default request signatures may receive `403 Error 1010: Access denied`.
- Use browser-like headers, especially a modern `User-Agent`, instead of relying on runtime defaults.

## Success Response

Status code: `200 OK`

```json
{
  "data": {
    "ASICModel": "BM1370",
    "algorithm": "sha256d",
    "bestDiff": "328M",
    "bestSessionDiff": "43.7M",
    "coreVoltageActual": 3435,
    "current": 61937.5,
    "deviceModel": "JMBTCHashcard",
    "fallbackStratumPort": 1414,
    "fallbackStratumURL": "btcssl.solomining.xyz",
    "fallbackStratumUser": "bc1qczf783s87laaanl9rlxxf787r58qz8268grwqk",
    "fanrpm": 3207,
    "fanspeed": 60,
    "frequency": 700,
    "hashRate": 13390677946056.26,
    "hostip": "192.168.41.179",
    "hostname": "JingleMiner",
    "isStratumConnected": true,
    "isUsingFallbackStratum": false,
    "jobInterval": 500,
    "macAddr": "98:A3:16:D5:5F:80",
    "poolDifficulty": 4000,
    "power": 220.668212890625,
    "runningPartition": "ota_1",
    "sharesAccepted": 8164,
    "sharesRejected": 42,
    "stratumDifficulty": 4000,
    "stratumPort": 3014,
    "stratumURL": "mining.viabtc.io",
    "stratumUser": "super66.bg03",
    "temp": 60,
    "timestamp": 1773208954338,
    "uuid": "a75629f7-ffc4-47f6-a131-f9321d049203",
    "version": "V1.0.0",
    "voltage": 11968.75,
    "vrTemp": 54
  },
  "telemetryError": null
}
```

## Error Responses

### Missing UUID or secret

Status code: `400 Bad Request`

```json
{
  "error": "Device uuid and secret are required."
}
```

### UUID and secret do not match

Status code: `400 Bad Request`

```json
{
  "error": "Device UUID and secret do not match."
}
```

### Upstream telemetry temporarily unavailable

Status code: `502 Bad Gateway`

```json
{
  "error": "Unable to load miner telemetry right now."
}
```

### Internal server error

Status code: `500 Internal Server Error`

```json
{
  "error": "Unable to load remote monitor telemetry."
}
```

## Response Handling Rules

- If `data` exists, treat the request as successful even when `telemetryError` is not `null`.
- If `telemetryError` is not `null`, report the warning along with the data.
- If the response contains `error`, do not continue with field interpretation.
