# JingleMiner Skills

This repository contains custom AI agents skills for working with Jingle Miner devices. At the moment, it includes a single production-focused skill: `jingleminer-remote-monitor`.

The skill is built to query the public Jingle Miner Solo remote monitor API, interpret the returned telemetry, and present it in a strict, human-readable format. The repository also ships a small Python helper script and local reference documents for the API contract and field meanings.

## Repository Scope

This is not a standalone application or web service. It is a skill repository organized around reusable agent instructions plus supporting assets.

Current contents:

- `skills/jingleminer-remote-monitor/SKILL.md`: the main skill definition and workflow instructions
- `skills/jingleminer-remote-monitor/scripts/fetch_remote_monitor.py`: a Python CLI for calling the remote monitor API
- `skills/jingleminer-remote-monitor/references/api-contract.md`: request/response contract for the API
- `skills/jingleminer-remote-monitor/references/field-reference.md`: field-by-field telemetry reference
- `skills/jingleminer-remote-monitor/agents/openai.yaml`: agent-facing metadata for the skill

## Included Skill

### `jingleminer-remote-monitor`

Purpose:

- Fetch live telemetry for a Jingle Miner Solo device
- Explain mining, pool, thermal, and power data
- Reuse session-scoped credentials through environment variables

Expected environment variables:

- `JINGLE_MINER_DEVICE_UUID`
- `JINGLE_MINER_DEVICE_SECRET`

When used as a skill, the preferred behavior is:

1. Read the stored credentials from the environment when available.
2. Ask for missing credentials only when needed.
3. Query `https://jingleminer.com/api/remote-monitor`.
4. Return a fixed four-section English summary unless the user explicitly asks for something else.

## Quick Start

### Use the helper script

The bundled script has no third-party Python dependencies.

```bash
python skills/jingleminer-remote-monitor/scripts/fetch_remote_monitor.py \
  --uuid "<device_uuid>" \
  --secret "<device_secret>"
```

JSON output is also supported:

```bash
python skills/jingleminer-remote-monitor/scripts/fetch_remote_monitor.py \
  --uuid "<device_uuid>" \
  --secret "<device_secret>" \
  --format json
```

### Reuse credentials with environment variables

PowerShell:

```powershell
$env:JINGLE_MINER_DEVICE_UUID="<device_uuid>"
$env:JINGLE_MINER_DEVICE_SECRET="<device_secret>"
```

Bash:

```bash
export JINGLE_MINER_DEVICE_UUID="<device_uuid>"
export JINGLE_MINER_DEVICE_SECRET="<device_secret>"
```

## How the Skill Works

The `jingleminer-remote-monitor` package combines three pieces:

- Instruction layer: `SKILL.md` defines when to use the skill, how to authenticate, how to call the API, and how the final answer must be formatted.
- Execution layer: `fetch_remote_monitor.py` performs the HTTP request, applies browser-like headers, and can emit either Markdown or JSON.
- Reference layer: the Markdown files under `references/` document the API contract and the meaning of known telemetry fields.

This separation keeps the runtime behavior explicit and makes the skill easier to audit or extend.

## API Notes

- Endpoint: `GET https://jingleminer.com/api/remote-monitor`
- Required query parameters: `uuid`, `secret`
- Response model: success payload with `data`, optional `telemetryError`, or an `error` payload
- Operational constraint: the endpoint may block default Python request signatures behind Cloudflare

For that reason, the helper script sends a browser-style header set, including a modern `User-Agent`, `Accept`, `Accept-Language`, `Cache-Control`, and `Pragma`.

## Output Behavior

When used through the skill, the intended default response is a strict plain-text summary with these sections:

1. `Pool information:`
2. `Operating metrics:`
3. `Temperature and power:`
4. `Power telemetry raw values:`

The local Python script is more verbose by default and can also emit structured JSON for downstream tooling.

## Development Notes

- Language: Python
- Dependency model: standard library only
- Repository status: currently contains one skill package
- Main extension point: add more skill folders under `skills/`

If you add a new skill, keep the same pattern:

- `SKILL.md` for behavior and workflow
- `references/` for local documentation
- `scripts/` for executable helpers
- `agents/` for agent metadata when needed

## Security

- Treat device `secret` values as sensitive credentials.
- Do not commit real device credentials into the repository.
- Avoid echoing full secrets in user-facing responses unless explicitly required.

---

# JingleMiner Skills 中文说明

这个仓库用于存放面向 AI agents 的自定义技能，目前主要服务于 Jingle Miner 设备相关场景。当前仓库只包含一个可直接使用的技能包：`jingleminer-remote-monitor`。

该技能用于调用 Jingle Miner Solo 的公开远程监控 API，解析返回的遥测数据，并按照固定的人类可读格式输出结果。仓库中同时提供了一个 Python 辅助脚本，以及 API 协议和字段含义的本地参考文档。

## 仓库定位

这不是一个独立应用，也不是一个 Web 服务项目。它本质上是一个“技能仓库”，由可复用的代理指令和配套资源组成。

当前包含的内容：

- `skills/jingleminer-remote-monitor/SKILL.md`：技能主定义与使用流程说明
- `skills/jingleminer-remote-monitor/scripts/fetch_remote_monitor.py`：用于调用远程监控 API 的 Python 命令行脚本
- `skills/jingleminer-remote-monitor/references/api-contract.md`：API 请求与响应协议说明
- `skills/jingleminer-remote-monitor/references/field-reference.md`：遥测字段含义参考
- `skills/jingleminer-remote-monitor/agents/openai.yaml`：面向代理系统的技能元数据

## 已包含技能

### `jingleminer-remote-monitor`

用途：

- 获取 Jingle Miner Solo 设备的实时遥测数据
- 解释矿机运行、矿池连接、温度和功耗信息
- 通过环境变量复用当前会话中的设备凭据

预期使用的环境变量：

- `JINGLE_MINER_DEVICE_UUID`
- `JINGLE_MINER_DEVICE_SECRET`

作为技能使用时，推荐行为如下：

1. 如果环境变量中已有凭据，优先直接复用。
2. 仅在缺少凭据时向用户询问。
3. 调用 `https://jingleminer.com/api/remote-monitor`。
4. 默认返回固定四段式英文摘要，除非用户明确要求其他格式。

## 快速开始

### 使用辅助脚本

仓库自带脚本仅依赖 Python 标准库，不需要额外安装第三方包。

```bash
python skills/jingleminer-remote-monitor/scripts/fetch_remote_monitor.py \
  --uuid "<device_uuid>" \
  --secret "<device_secret>"
```

也支持输出 JSON：

```bash
python skills/jingleminer-remote-monitor/scripts/fetch_remote_monitor.py \
  --uuid "<device_uuid>" \
  --secret "<device_secret>" \
  --format json
```

### 通过环境变量复用凭据

PowerShell：

```powershell
$env:JINGLE_MINER_DEVICE_UUID="<device_uuid>"
$env:JINGLE_MINER_DEVICE_SECRET="<device_secret>"
```

Bash：

```bash
export JINGLE_MINER_DEVICE_UUID="<device_uuid>"
export JINGLE_MINER_DEVICE_SECRET="<device_secret>"
```

## 技能工作方式

`jingleminer-remote-monitor` 由三部分组成：

- 指令层：`SKILL.md` 定义了技能适用场景、鉴权方式、API 调用流程以及最终输出格式要求。
- 执行层：`fetch_remote_monitor.py` 负责发起 HTTP 请求，附带浏览器风格请求头，并支持输出 Markdown 或 JSON。
- 参考层：`references/` 目录下的文档说明了 API 协议和已知字段含义。

这种拆分方式让技能行为更清晰，也更便于审查和扩展。

## API 说明

- 接口地址：`GET https://jingleminer.com/api/remote-monitor`
- 必填查询参数：`uuid`、`secret`
- 响应模型：成功时返回 `data`，可能附带 `telemetryError`；失败时返回 `error`
- 运行限制：接口可能会通过 Cloudflare 拦截 Python 默认请求特征

因此，辅助脚本会主动发送浏览器风格的请求头，包括较新的 `User-Agent`、`Accept`、`Accept-Language`、`Cache-Control` 和 `Pragma`。

## 输出行为

通过技能调用时，默认目标输出是固定的纯文本四段结构：

1. `Pool information:`
2. `Operating metrics:`
3. `Temperature and power:`
4. `Power telemetry raw values:`

而本地 Python 脚本默认会输出更完整的 Markdown 摘要，也可以输出结构化 JSON，方便后续集成到其他工具链中。

## 开发说明

- 语言：Python
- 依赖：仅使用标准库
- 仓库现状：当前只包含一个技能包
- 主要扩展方式：在 `skills/` 目录下新增更多技能子目录

如果你要新增技能，建议保持同样的组织方式：

- `SKILL.md`：定义行为和流程
- `references/`：存放本地参考文档
- `scripts/`：存放辅助执行脚本
- `agents/`：存放代理元数据（如需要）

## 安全说明

- 设备 `secret` 应视为敏感凭据。
- 不要把真实设备凭据提交到仓库。
- 除非用户明确要求，否则不要在面向用户的输出中回显完整 `secret`。

