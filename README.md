# Network Watchdog / VPN Coffee Companion

Windows 10 / 11 desktop watchdog for checking whether the local machine can reach selected external websites over real HTTPS requests, while also tracking local CPU, memory, and C drive usage.

浠呴€傜敤浜?Windows 10 / 11 鐨勬闈㈢湅闂ㄧ嫍宸ュ叿锛岀浜屽悕绉颁负 `VPN 鍜栧暋浼翠荆`銆傚畠浼氱敤鐪熷疄 HTTPS 璇锋眰瀹氭湡妫€娴嬫湰鏈鸿闂閮ㄧ綉绔欐槸鍚﹂€氱晠锛屽悓鏃剁洃鎺ф湰鏈?CPU銆佸唴瀛樺拰 C 鐩樺崰鐢ㄧ巼銆?
![Network Watchdog English UI](docs/network-watchdog-screenshot-en-cropped.png)

## Scope

This project is only intended for Windows 10 and Windows 11 local desktop monitoring.

The current notification path is intentionally narrow:

- Email notifications are currently designed for Mainland China usage
- QQ Mail SMTP is the supported notification mailbox path
- A QQ Mail authorization code is required to receive notifications

褰撳墠椤圭洰浠呴€傜敤浜?Windows 10 / 11 鏈満妗岄潰鐩戞帶銆?
鐩墠鐨勯€氱煡鏂规鏈夋槑纭寖鍥达細

- 閭欢閫氱煡褰撳墠闈㈠悜涓浗鍐呭湴浣跨敤鍦烘櫙
- 閫氱煡閭閾捐矾褰撳墠鏀寔 QQ 閭 SMTP
- 瑕佹敹鍒伴€氱煡锛屽繀椤讳娇鐢?QQ 閭鎺堟潈鐮侊紝鑰屼笉鏄偖绠辩櫥褰曞瘑鐮?
## English Overview

`Network Watchdog`, also referred to as `VPN Coffee Companion`, is a lightweight local monitoring tool for users who want a visible desktop status panel instead of a full monitoring platform.

It is designed for this workflow:

- Probe Google, Amazon, AWS, YouTube, Cloudflare, or custom targets with real HTTPS requests
- Show current status, latency, and a friendly explanation of HTTP results
- Keep a 6-hour latency chart on the main screen
- Track CPU, memory, and C drive usage on the same refresh interval
- Send email alerts for degraded network status, outages, or high system resource usage
- Run as a Windows 10 / 11 desktop app with optional tray mode

## 涓枃璇存槑

`Network Watchdog`锛屼篃灏辨槸 `VPN 鍜栧暋浼翠荆`锛屾槸涓€涓亸杞婚噺銆佹湰鏈哄父椹荤殑鐩戞帶宸ュ叿锛岄€傚悎甯屾湜鐩存帴鍦ㄦ闈㈢湅鍒扮姸鎬侊紝鑰屼笉鏄惌涓€鏁村鐩戞帶骞冲彴鐨勫満鏅€?
瀹冧富瑕佽В鍐宠繖绫婚棶棰橈細

- 鐢ㄧ湡瀹?HTTPS 璇锋眰鎺㈡祴 Google銆丄mazon銆丄WS銆乊ouTube銆丆loudflare 鎴栬嚜瀹氫箟鐩爣
- 鏄剧ず褰撳墠鐘舵€併€佸欢杩燂紝浠ュ強瀵?HTTP 杩斿洖缁撴灉鐨勭畝鍗曡鏄?- 鍦ㄤ富鐣岄潰灞曠ず鏈€杩?6 灏忔椂鐨勭綉缁滃欢杩熸洸绾?- 鎸夊悓涓€鍒锋柊鍛ㄦ湡鍚屾鐩戞帶 CPU銆佸唴瀛樺拰 C 鐩樺崰鐢ㄧ巼
- 褰撶綉缁滃紓甯告垨绯荤粺璧勬簮杩囬珮鏃堕€氳繃閭欢鍙戦€佸憡璀?- 浣滀负 Windows 10 / 11 妗岄潰绋嬪簭杩愯锛屾敮鎸佹墭鐩樺父椹?
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
