# Network Watchdog / VPN Coffee Companion

Windows 10 / 11 desktop watchdog for checking whether the local machine can reach selected external websites over real HTTPS requests, while also tracking local CPU, memory, and C drive usage.

仅适用于 Windows 10 / 11 的桌面看门狗工具，第二名称为 `VPN 咖啡伴侣`。它会用真实 HTTPS 请求定期检测本机访问外部网站是否通畅，同时监控本机 CPU、内存和 C 盘占用率。

## Scope

This project is only intended for Windows 10 and Windows 11 local desktop monitoring.

The current notification path is intentionally narrow:

- Email notifications are currently designed for Mainland China usage
- QQ Mail SMTP is the supported notification mailbox path
- A QQ Mail authorization code is required to receive notifications

当前项目仅适用于 Windows 10 / 11 本机桌面监控。

目前的通知方案有明确范围：

- 邮件通知当前面向中国内地使用场景
- 通知邮箱链路当前支持 QQ 邮箱 SMTP
- 要收到通知，必须使用 QQ 邮箱授权码，而不是邮箱登录密码

## English Overview

`Network Watchdog`, also referred to as `VPN Coffee Companion`, is a lightweight local monitoring tool for users who want a visible desktop status panel instead of a full monitoring platform.

It is designed for this workflow:

- Probe Google, Amazon, AWS, YouTube, Cloudflare, or custom targets with real HTTPS requests
- Show current status, latency, and a friendly explanation of HTTP results
- Keep a 6-hour latency chart on the main screen
- Track CPU, memory, and C drive usage on the same refresh interval
- Send email alerts for degraded network status, outages, or high system resource usage
- Run as a Windows 10 / 11 desktop app with optional tray mode

## 中文说明

`Network Watchdog`，也就是 `VPN 咖啡伴侣`，是一个偏轻量、本机常驻的监控工具，适合希望直接在桌面看到状态，而不是搭一整套监控平台的场景。

它主要解决这类问题：

- 用真实 HTTPS 请求探测 Google、Amazon、AWS、YouTube、Cloudflare 或自定义目标
- 显示当前状态、延迟，以及对 HTTP 返回结果的简单说明
- 在主界面展示最近 6 小时的网络延迟曲线
- 按同一刷新周期同步监控 CPU、内存和 C 盘占用率
- 当网络异常或系统资源过高时通过邮件发送告警
- 作为 Windows 10 / 11 桌面程序运行，支持托盘常驻

## Features

- Manual refresh with visible in-progress and completed feedback
- Adjustable refresh interval and timeout
- Friendly HTTP detail text for common responses such as `200` and `204`
- Dashboard latency chart for the last 6 hours
- Full history chart for the last 6 hours
- CPU, memory, and C drive usage monitoring
- Email alerts for degraded network state, outages, and high system resource usage
- Daily email alert counter on the main screen
- English UI by default, with Chinese language switch
- Automatic SMTP path fallback between SSL `465` and STARTTLS `587`
- Environment self-check page for portable deployment on another machine
- Windows installer packaging with a directory-based runtime layout

## Screens and Modes

- `Dashboard`: network table, recent events, 6-hour mini chart, summary counters
- `Email`: SMTP settings, alert settings, test email, language switch, system alert threshold
- `History`: larger 6-hour chart
- `Environment`: dependency checks and portable setup hints

## Run From Source

```powershell
python -m pip install -r requirements.txt
python network_watchdog.py
```

You can also use:

```powershell
run_watchdog.bat
```

## Configuration

- `watchdog_targets.json`: probe targets
- `watchdog_settings.example.json`: public example settings file
- `watchdog_settings.json`: local private settings file, intentionally ignored by git
- `logs/network_watchdog_log.csv`: local runtime log, intentionally ignored by git

## Installer

Build the installer package:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_installer.ps1
```

Output files:

- `release/SetupNetworkWatchdog.exe`
- `release/NetworkWatchdogInstaller.zip`

The runtime package uses PyInstaller `onedir` mode instead of `onefile` mode to reduce antivirus false positives.

## Email Notes

For QQ Mail SMTP delivery:

- Host: `smtp.qq.com`
- Sender email: full mailbox address such as `name@qq.com`
- Auth code: mailbox authorization code, not the login password

The app automatically tries supported SMTP delivery paths in the background, but the intended public support target is Mainland China plus QQ Mail.

## Privacy and Publishing Notes

- Real mailbox credentials must never be committed
- `watchdog_settings.json` is ignored by git
- Build outputs and logs are ignored by git
- Public releases should be created from sanitized defaults only

## License

MIT
