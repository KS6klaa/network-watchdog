from __future__ import annotations

import csv
import ctypes
import importlib
import importlib.util
import json
import queue
import smtplib
import ssl
import platform
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from datetime import date, datetime
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path
from urllib import error, request

try:
    import winreg
except Exception:
    winreg = None

try:
    import certifi
except Exception:
    certifi = None

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except Exception as exc:
    tk = None
    ttk = None
    messagebox = None
    TK_IMPORT_ERROR = exc
else:
    TK_IMPORT_ERROR = None

try:
    import winsound
except Exception:
    winsound = None

try:
    import psutil
except Exception as exc:
    psutil = None
    PSUTIL_IMPORT_ERROR = exc
else:
    PSUTIL_IMPORT_ERROR = None

try:
    from PIL import Image, ImageDraw
except Exception as exc:
    Image = None
    ImageDraw = None
    PIL_IMPORT_ERROR = exc
else:
    PIL_IMPORT_ERROR = None

try:
    import pystray
except Exception as exc:
    pystray = None
    PYSTRAY_IMPORT_ERROR = exc
else:
    PYSTRAY_IMPORT_ERROR = None


APP_TITLE = "Network Watchdog / VPN Coffee Companion"
APP_VERSION = "1.2.0"
APP_MUTEX_NAME = "Global\\NetworkWatchdogSingleInstance"
GITHUB_REPO = "KS6klaa/network-watchdog"
LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO}/releases"
DEFAULT_INTERVAL_SECONDS = 180
DEFAULT_TIMEOUT_SECONDS = 12
DEFAULT_DEGRADED_LATENCY_MS = 1500
DEFAULT_MINIMUM_OK_TARGETS = 2
DEFAULT_SYSTEM_ALERT_THRESHOLD = 95
DEFAULT_SLOW_AVG_LATENCY_ALERT_MS = 2000
DEFAULT_DOWN_ALERT_STREAK = 2
DEFAULT_SLOW_ALERT_STREAK = 3
DEFAULT_SYSTEM_ALERT_STREAK = 2
DEFAULT_DAILY_SUMMARY_TIME = "21:00"
HISTORY_WINDOW_SECONDS = 6 * 60 * 60
DEFAULT_SMTP_HOST = "smtp.qq.com"
DEFAULT_SMTP_PORT = 465
ROOT_PATH = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
TARGETS_PATH = ROOT_PATH / "watchdog_targets.json"
SETTINGS_PATH = ROOT_PATH / "watchdog_settings.json"
LOG_DIR = ROOT_PATH / "logs"
LOG_PATH = LOG_DIR / "network_watchdog_log.csv"
MIN_PYTHON_VERSION = (3, 10)
SYSTEM_THEME_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
THEME_LIGHT = "light"
THEME_DARK = "dark"
STATE_NORMAL = "NORMAL"
STATE_SLOW = "SLOW"
STATE_OFFLINE = "OFFLINE"
TRAY_STATE_COLORS = {
    STATE_NORMAL: "#12b76a",
    STATE_SLOW: "#f79009",
    STATE_OFFLINE: "#f04438",
}
COUNTRY_NAME_CACHE: dict[tuple[str, str], str] = {}


TEXT = {
    "en": {
        "language_name": "English",
        "refresh_s": "Refresh (s)",
        "timeout_s": "Timeout (s)",
        "degraded_ms": "Degraded latency (ms)",
        "minimum_ok": "Minimum OK targets",
        "language": "Language",
        "apply": "Apply",
        "refresh_now": "Refresh now",
        "test_sound": "Test sound",
        "test_email": "Test email",
        "hide_to_tray": "Hide to tray",
        "dashboard": "Dashboard",
        "email": "Email",
        "history": "History",
        "environment": "Environment",
        "updates": "Updates",
        "target": "Target",
        "status": "Status",
        "latency": "Latency",
        "detail": "Detail",
        "checked_at": "Checked at",
        "pending": "Pending",
        "waiting_probe": "Waiting for first probe result",
        "checking": "Checking...",
        "network_summary": "Network",
        "system_summary": "System",
        "today_alerts": "Email alerts today",
        "external_ip": "External IP",
        "power_summary": "Power",
        "manual_idle": "Manual refresh: idle",
        "manual_requested": "Manual refresh requested. Waiting for latency update...",
        "manual_running": "Manual refresh running: {seconds}s elapsed",
        "manual_done": "Manual refresh completed at {time}. Latency updated.",
        "next_not_scheduled": "Next update: not scheduled",
        "next_in": "Next update: in {seconds} seconds",
        "already_running": "Network Watchdog is already running.",
        "popup_skipped": "Popup alert skipped because another alert window is already open.",
        "last_not_started": "Last update: not started",
        "last_update": "Last update: {time}",
        "avg_latency": "avg latency",
        "success": "success",
        "cpu": "CPU",
        "memory": "Memory",
        "c_drive": "C drive",
        "small_chart": "Latency trend, last 6 hours",
        "recent_events": "Recent events",
        "sound_alert": "Sound alert",
        "popup_alert": "Popup alert",
        "email_alert": "Email alert",
        "daily_summary_email": "Daily summary email",
        "daily_summary_time": "Daily summary time",
        "recovery_email": "Recovery email",
        "slow_latency_alert_ms": "Slow latency alert (ms)",
        "close_to_tray": "Close button hides to tray",
        "smtp_host": "SMTP host",
        "sender_email": "Sender email",
        "sender_name": "Sender name",
        "smtp_auth": "SMTP auth code",
        "recipient_1": "Recipient 1",
        "recipient_2": "Recipient 2",
        "recipient_3": "Recipient 3",
        "save_settings": "Save settings",
        "email_note": (
            "Outbound alerts automatically try SSL 465 and STARTTLS 587. "
            "Current notification delivery is intended for Mainland China users with QQ Mail SMTP and a mailbox authorization code."
        ),
        "env_recheck": "Recheck environment",
        "env_note": "Missing optional items only disable the related feature.",
        "check_updates_now": "Check updates now",
        "open_release_page": "Open release page",
        "update_open_download": "Open selected download",
        "auto_update_check": "Check updates on startup",
        "current_version": "Current version",
        "latest_version": "Latest version",
        "published_at": "Published at",
        "update_status": "Update status",
        "asset_name": "Package",
        "asset_size": "Size",
        "asset_url": "Download",
        "update_idle": "Update check has not run yet.",
        "update_checking": "Checking GitHub release...",
        "update_up_to_date": "You are using the latest version.",
        "update_available": "Update available: {version}",
        "update_failed": "Update check failed: {error}",
        "update_no_selection": "Select a package first.",
        "portable_commands": "Portable setup commands",
        "item": "Item",
        "required": "Required",
        "install_hint": "Install hint",
        "yes": "Yes",
        "no": "No",
        "env_good": "Environment looks good. All checked features are available.",
        "settings_saved": "Settings saved",
        "manual_refresh_event": "Manual refresh requested",
        "sound_test": "Alert sound test played",
        "no_recipient": "Status: no recipient email configured",
        "mail_missing": "Status: SMTP host, sender email, and auth code are required",
        "sender_invalid": "Status: sender email must be a full email address",
        "email_sent": "Status: email sent to {recipients}",
        "email_failed": "Status: email send failed: {error}",
        "tray_missing": "Status: tray is unavailable. Install pillow and pystray to enable it.",
        "tray_notice": "App is still running in the tray.",
        "optional_missing_title": "Some optional features are unavailable on this machine.",
        "optional_missing_body": "The core network watchdog will continue running.",
        "http_200": "HTTP 200 OK - page is reachable.",
        "http_204": "HTTP 204 No Content - lightweight probe succeeded.",
        "http_other": "HTTP {code} - server responded.",
        "http_error": "HTTP error {code} - server rejected the request.",
        "state_normal": "Normal",
        "state_slow": "Slow",
        "state_offline": "Offline",
        "country_unknown": "Unknown",
        "power_battery": "Battery",
        "power_ac": "AC power",
        "power_not_supported": "No battery",
        "daily_summary_subject": "DAILY_SUMMARY",
        "daily_summary_message": (
            "Daily network summary\n"
            "Date: {date}\n"
            "Checks: {checks}\n"
            "Normal: {normal}\n"
            "Slow: {slow}\n"
            "Offline: {offline}\n"
            "Average latency: {avg_latency} ms\n"
            "Min latency: {min_latency} ms\n"
            "Max latency: {max_latency} ms\n"
            "Email alerts sent today: {alert_count}\n"
            "External IP: {external_ip}\n"
            "Country: {country}\n"
        ),
        "power_alert_subject": "POWER_ALERT",
        "power_alert_message": "Device switched to battery power. Battery {battery}%.",
        "abnormal_shutdown_subject": "ABNORMAL_SHUTDOWN",
        "abnormal_shutdown_message": "The previous run did not exit cleanly. This may indicate power loss or an unexpected shutdown.",
        "system_alert_subject": "SYSTEM_RESOURCE",
        "system_alert_message": "System resource threshold reached: {items}",
        "slow_network_subject": "SLOW_NETWORK",
        "slow_network_message": "Network speed is slow / 网速速度变慢. Average latency {latency} ms for 2 consecutive checks.",
        "recovery_subject": "RECOVERY",
        "recovery_message": "Connectivity recovered to the configured threshold. OK targets {ok_count}/{total_count}, minimum required {minimum_ok}, success rate {success_rate}%, average latency {latency} ms.",
    },
    "zh": {
        "language_name": "\u4e2d\u6587",
        "refresh_s": "\u5237\u65b0\u79d2\u6570",
        "timeout_s": "\u8d85\u65f6\u79d2\u6570",
        "degraded_ms": "\u5ef6\u8fdf\u9608\u503c(ms)",
        "minimum_ok": "\u6700\u5c11\u6b63\u5e38\u76ee\u6807\u6570",
        "language": "\u8bed\u8a00",
        "apply": "\u5e94\u7528",
        "refresh_now": "\u7acb\u5373\u5237\u65b0",
        "test_sound": "\u6d4b\u8bd5\u58f0\u97f3",
        "test_email": "\u6d4b\u8bd5\u90ae\u4ef6",
        "hide_to_tray": "\u9690\u85cf\u5230\u6258\u76d8",
        "dashboard": "\u4e3b\u9762\u677f",
        "email": "\u90ae\u4ef6",
        "history": "\u5386\u53f2",
        "environment": "\u73af\u5883",
        "updates": "\u66f4\u65b0",
        "target": "\u76ee\u6807",
        "status": "\u72b6\u6001",
        "latency": "\u5ef6\u8fdf",
        "detail": "\u8bf4\u660e",
        "checked_at": "\u68c0\u6d4b\u65f6\u95f4",
        "pending": "\u7b49\u5f85",
        "waiting_probe": "\u7b49\u5f85\u9996\u6b21\u68c0\u6d4b",
        "checking": "\u68c0\u6d4b\u4e2d...",
        "network_summary": "\u7f51\u7edc",
        "system_summary": "\u7cfb\u7edf",
        "today_alerts": "\u4eca\u65e5\u90ae\u4ef6\u8b66\u62a5",
        "external_ip": "\u5916\u7f51IP",
        "power_summary": "\u7535\u6e90",
        "manual_idle": "\u624b\u52a8\u5237\u65b0\uff1a\u7a7a\u95f2",
        "manual_requested": "\u5df2\u8bf7\u6c42\u624b\u52a8\u5237\u65b0\uff0c\u6b63\u5728\u7b49\u5f85\u5ef6\u8fdf\u66f4\u65b0...",
        "manual_running": "\u624b\u52a8\u5237\u65b0\u4e2d\uff1a\u5df2\u8fd0\u884c {seconds} \u79d2",
        "manual_done": "\u624b\u52a8\u5237\u65b0\u5df2\u5b8c\u6210\uff1a{time}\uff0c\u5ef6\u8fdf\u5df2\u66f4\u65b0\u3002",
        "next_not_scheduled": "\u4e0b\u6b21\u5237\u65b0\uff1a\u672a\u5b89\u6392",
        "next_in": "\u4e0b\u6b21\u5237\u65b0\uff1a{seconds} \u79d2\u540e",
        "already_running": "\u7f51\u7edc\u770b\u95e8\u72d7\u5df2\u7ecf\u5728\u8fd0\u884c\u3002",
        "popup_skipped": "\u7531\u4e8e\u53e6\u4e00\u4e2a\u544a\u8b66\u7a97\u53e3\u5df2\u6253\u5f00\uff0c\u672c\u6b21\u5f39\u7a97\u5df2\u8df3\u8fc7\u3002",
        "last_not_started": "\u4e0a\u6b21\u5237\u65b0\uff1a\u672a\u5f00\u59cb",
        "last_update": "\u4e0a\u6b21\u5237\u65b0\uff1a{time}",
        "avg_latency": "\u5e73\u5747\u5ef6\u8fdf",
        "success": "\u6b63\u5e38",
        "cpu": "CPU",
        "memory": "\u5185\u5b58",
        "c_drive": "C\u76d8",
        "small_chart": "\u6700\u8fd16\u5c0f\u65f6\u5ef6\u8fdf\u66f2\u7ebf",
        "recent_events": "\u6700\u8fd1\u4e8b\u4ef6",
        "sound_alert": "\u58f0\u97f3\u8b66\u62a5",
        "popup_alert": "\u5f39\u7a97\u8b66\u62a5",
        "email_alert": "\u90ae\u4ef6\u8b66\u62a5",
        "daily_summary_email": "\u6bcf\u65e5\u6c47\u603b\u90ae\u4ef6",
        "daily_summary_time": "\u6bcf\u65e5\u6c47\u603b\u65f6\u95f4",
        "recovery_email": "\u6062\u590d\u90ae\u4ef6",
        "slow_latency_alert_ms": "\u6162\u901f\u5ef6\u8fdf\u544a\u8b66(ms)",
        "close_to_tray": "\u5173\u95ed\u6309\u94ae\u9690\u85cf\u5230\u6258\u76d8",
        "smtp_host": "SMTP\u4e3b\u673a",
        "sender_email": "\u53d1\u4ef6\u90ae\u7bb1",
        "sender_name": "\u53d1\u4ef6\u540d\u79f0",
        "smtp_auth": "SMTP\u6388\u6743\u7801",
        "recipient_1": "\u6536\u4ef6\u4eba1",
        "recipient_2": "\u6536\u4ef6\u4eba2",
        "recipient_3": "\u6536\u4ef6\u4eba3",
        "save_settings": "\u4fdd\u5b58\u8bbe\u7f6e",
        "email_note": (
            "\u90ae\u4ef6\u8b66\u62a5\u4f1a\u81ea\u52a8\u5c1d\u8bd5 SSL 465 \u548c STARTTLS 587\u3002"
            "\u5f53\u524d\u901a\u77e5\u65b9\u6848\u9762\u5411\u4e2d\u56fd\u5185\u5730 QQ\u90ae\u7bb1 SMTP\uff0c\u9700\u8981\u90ae\u7bb1\u6388\u6743\u7801\u3002"
        ),
        "env_recheck": "\u91cd\u65b0\u68c0\u67e5\u73af\u5883",
        "env_note": "\u7f3a\u5c11\u53ef\u9009\u9879\u53ea\u4f1a\u7981\u7528\u76f8\u5173\u529f\u80fd\u3002",
        "check_updates_now": "\u7acb\u5373\u68c0\u67e5\u66f4\u65b0",
        "open_release_page": "\u6253\u5f00\u53d1\u5e03\u9875",
        "update_open_download": "\u6253\u5f00\u6240\u9009\u4e0b\u8f7d",
        "auto_update_check": "\u542f\u52a8\u65f6\u81ea\u52a8\u68c0\u67e5\u66f4\u65b0",
        "current_version": "\u5f53\u524d\u7248\u672c",
        "latest_version": "\u6700\u65b0\u7248\u672c",
        "published_at": "\u53d1\u5e03\u65f6\u95f4",
        "update_status": "\u66f4\u65b0\u72b6\u6001",
        "asset_name": "\u5305\u540d",
        "asset_size": "\u5927\u5c0f",
        "asset_url": "\u4e0b\u8f7d",
        "update_idle": "\u8fd8\u672a\u6267\u884c\u66f4\u65b0\u68c0\u67e5\u3002",
        "update_checking": "\u6b63\u5728\u68c0\u67e5 GitHub \u6700\u65b0\u7248\u672c...",
        "update_up_to_date": "\u5f53\u524d\u5df2\u662f\u6700\u65b0\u7248\u672c\u3002",
        "update_available": "\u53d1\u73b0\u65b0\u7248\u672c\uff1a{version}",
        "update_failed": "\u66f4\u65b0\u68c0\u67e5\u5931\u8d25\uff1a{error}",
        "update_no_selection": "\u8bf7\u5148\u9009\u62e9\u4e00\u4e2a\u5b89\u88c5\u5305\u3002",
        "portable_commands": "\u79fb\u52a8\u90e8\u7f72\u547d\u4ee4",
        "item": "\u9879\u76ee",
        "required": "\u5fc5\u9700",
        "install_hint": "\u5b89\u88c5\u63d0\u793a",
        "yes": "\u662f",
        "no": "\u5426",
        "env_good": "\u73af\u5883\u6b63\u5e38\uff0c\u6240\u6709\u68c0\u67e5\u9879\u53ef\u7528\u3002",
        "settings_saved": "\u8bbe\u7f6e\u5df2\u4fdd\u5b58",
        "manual_refresh_event": "\u5df2\u8bf7\u6c42\u624b\u52a8\u5237\u65b0",
        "sound_test": "\u5df2\u64ad\u653e\u8b66\u62a5\u58f0",
        "no_recipient": "\u72b6\u6001\uff1a\u672a\u914d\u7f6e\u6536\u4ef6\u4eba",
        "mail_missing": "\u72b6\u6001\uff1aSMTP\u4e3b\u673a\u3001\u53d1\u4ef6\u90ae\u7bb1\u548c\u6388\u6743\u7801\u5fc5\u586b",
        "sender_invalid": "\u72b6\u6001\uff1a\u53d1\u4ef6\u90ae\u7bb1\u5fc5\u987b\u662f\u5b8c\u6574\u90ae\u7bb1\u5730\u5740",
        "email_sent": "\u72b6\u6001\uff1a\u90ae\u4ef6\u5df2\u53d1\u9001\u81f3 {recipients}",
        "email_failed": "\u72b6\u6001\uff1a\u90ae\u4ef6\u53d1\u9001\u5931\u8d25\uff1a{error}",
        "tray_missing": "\u72b6\u6001\uff1a\u6258\u76d8\u4e0d\u53ef\u7528\uff0c\u8bf7\u5b89\u88c5 pillow \u548c pystray\u3002",
        "tray_notice": "\u7a0b\u5e8f\u6b63\u5728\u6258\u76d8\u7ee7\u7eed\u8fd0\u884c\u3002",
        "optional_missing_title": "\u672c\u673a\u90e8\u5206\u53ef\u9009\u529f\u80fd\u4e0d\u53ef\u7528\u3002",
        "optional_missing_body": "\u6838\u5fc3\u7f51\u7edc\u770b\u95e8\u72d7\u4f1a\u7ee7\u7eed\u8fd0\u884c\u3002",
        "http_200": "HTTP 200 OK - \u9875\u9762\u53ef\u8bbf\u95ee\u3002",
        "http_204": "HTTP 204 No Content - \u8f7b\u91cf\u63a2\u6d4b\u6210\u529f\u3002",
        "http_other": "HTTP {code} - \u670d\u52a1\u5668\u5df2\u54cd\u5e94\u3002",
        "http_error": "HTTP \u9519\u8bef {code} - \u670d\u52a1\u5668\u62d2\u7edd\u8bf7\u6c42\u3002",
        "state_normal": "\u6b63\u5e38",
        "state_slow": "\u5ef6\u8fdf",
        "state_offline": "\u79bb\u7ebf",
        "country_unknown": "\u672a\u77e5",
        "power_battery": "\u7535\u6c60\u4f9b\u7535",
        "power_ac": "\u63a5\u5165\u7535\u6e90",
        "power_not_supported": "\u65e0\u7535\u6c60",
        "daily_summary_subject": "\u6bcf\u65e5\u7f51\u7edc\u6c47\u603b",
        "daily_summary_message": (
            "\u6bcf\u65e5\u7f51\u7edc\u6c47\u603b\n"
            "\u65e5\u671f\uff1a{date}\n"
            "\u68c0\u6d4b\u6b21\u6570\uff1a{checks}\n"
            "\u6b63\u5e38\uff1a{normal}\n"
            "\u5ef6\u8fdf\uff1a{slow}\n"
            "\u79bb\u7ebf\uff1a{offline}\n"
            "\u5e73\u5747\u5ef6\u8fdf\uff1a{avg_latency} ms\n"
            "\u6700\u4f4e\u5ef6\u8fdf\uff1a{min_latency} ms\n"
            "\u6700\u9ad8\u5ef6\u8fdf\uff1a{max_latency} ms\n"
            "\u4eca\u65e5\u5df2\u53d1\u90ae\u4ef6\u8b66\u62a5\uff1a{alert_count}\n"
            "\u5916\u7f51 IP\uff1a{external_ip}\n"
            "\u6240\u5c5e\u56fd\u5bb6\uff1a{country}\n"
        ),
        "power_alert_subject": "\u7535\u6e90\u8b66\u62a5",
        "power_alert_message": "\u8bbe\u5907\u5df2\u5207\u6362\u5230\u7535\u6c60\u4f9b\u7535\u3002\u7535\u91cf {battery}%\u3002",
        "abnormal_shutdown_subject": "\u5f02\u5e38\u4e2d\u65ad",
        "abnormal_shutdown_message": "\u4e0a\u4e00\u6b21\u8fd0\u884c\u672a\u6b63\u5e38\u9000\u51fa\uff0c\u53ef\u80fd\u51fa\u73b0\u4e86\u65ad\u7535\u6216\u5f02\u5e38\u5173\u673a\u3002",
        "system_alert_subject": "\u7cfb\u7edf\u8d44\u6e90\u8b66\u62a5",
        "system_alert_message": "\u7cfb\u7edf\u8d44\u6e90\u8fbe\u5230\u9608\u503c\uff1a{items}",
        "slow_network_subject": "\u7f51\u901f\u53d8\u6162",
        "slow_network_message": "\u7f51\u901f\u901f\u5ea6\u53d8\u6162 / Network speed is slow\u3002\u5e73\u5747\u5ef6\u8fdf {latency} ms\uff0c\u5df2\u8fde\u7eed 2 \u6b21\u89e6\u53d1\u9608\u503c\u3002",
        "recovery_subject": "\u6062\u590d",
        "recovery_message": "\u7f51\u7edc\u5df2\u6062\u590d\u5230\u4f60\u914d\u7f6e\u7684\u9608\u503c\u3002\u6b63\u5e38\u76ee\u6807 {ok_count}/{total_count}\uff0c\u6700\u5c11\u8981\u6c42 {minimum_ok}\uff0c\u6210\u529f\u7387 {success_rate}%\uff0c\u5e73\u5747\u5ef6\u8fdf {latency} ms\u3002",
    },
}


@dataclass(frozen=True)
class ProbeTarget:
    name: str
    url: str


@dataclass(frozen=True)
class DependencyCheck:
    name: str
    status: str
    required: bool
    detail: str
    install_hint: str


DEFAULT_TARGETS = [
    ProbeTarget("Google", "https://www.google.com/generate_204"),
    ProbeTarget("Amazon", "https://www.amazon.com/"),
    ProbeTarget("AWS", "https://aws.amazon.com/"),
    ProbeTarget("YouTube", "https://www.youtube.com/generate_204"),
    ProbeTarget("Cloudflare", "https://www.cloudflare.com/cdn-cgi/trace"),
]


def tr(language: str, key: str, **kwargs: object) -> str:
    template = TEXT.get(language, TEXT["en"]).get(key, TEXT["en"].get(key, key))
    return template.format(**kwargs)


def load_targets() -> list[ProbeTarget]:
    if not TARGETS_PATH.exists():
        TARGETS_PATH.write_text(
            json.dumps(
                [{"name": target.name, "url": target.url} for target in DEFAULT_TARGETS],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return DEFAULT_TARGETS

    try:
        raw_items = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
        targets: list[ProbeTarget] = []
        for item in raw_items:
            name = str(item.get("name", "")).strip()
            url = str(item.get("url", "")).strip()
            if name and url:
                targets.append(ProbeTarget(name=name, url=url))
        return targets or DEFAULT_TARGETS
    except Exception:
        return DEFAULT_TARGETS


def default_settings() -> dict:
    return {
        "interval_seconds": DEFAULT_INTERVAL_SECONDS,
        "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
        "degraded_latency_ms": DEFAULT_DEGRADED_LATENCY_MS,
        "minimum_ok_targets": DEFAULT_MINIMUM_OK_TARGETS,
        "system_alert_threshold": DEFAULT_SYSTEM_ALERT_THRESHOLD,
        "slow_avg_latency_alert_ms": DEFAULT_SLOW_AVG_LATENCY_ALERT_MS,
        "sound_alert_enabled": True,
        "popup_alert_enabled": False,
        "email_alert_enabled": False,
        "recovery_email_enabled": False,
        "daily_summary_enabled": False,
        "daily_summary_time": DEFAULT_DAILY_SUMMARY_TIME,
        "auto_check_updates_enabled": True,
        "minimize_to_tray_on_close": True,
        "language": "en",
        "smtp_host": DEFAULT_SMTP_HOST,
        "smtp_port": DEFAULT_SMTP_PORT,
        "sender_email": "",
        "sender_name": "Network Watchdog",
        "auth_code": "",
        "recipient_1": "",
        "recipient_2": "",
        "recipient_3": "",
        "email_alert_count_date": date.today().isoformat(),
        "email_alert_count_today": 0,
        "last_daily_summary_sent_date": "",
        "last_shutdown_clean": True,
    }


def load_settings() -> dict:
    settings = default_settings()
    should_save = False
    if not SETTINGS_PATH.exists():
        save_settings(settings)
        return settings
    try:
        saved = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            settings.update(saved)
            if "minimum_ok_targets" not in saved:
                settings["minimum_ok_targets"] = DEFAULT_MINIMUM_OK_TARGETS
                should_save = True
            if "auto_check_updates_enabled" not in saved:
                settings["auto_check_updates_enabled"] = True
                should_save = True
            if "daily_summary_enabled" not in saved:
                settings["daily_summary_enabled"] = False
                should_save = True
            if "daily_summary_time" not in saved:
                settings["daily_summary_time"] = DEFAULT_DAILY_SUMMARY_TIME
                should_save = True
            if "last_daily_summary_sent_date" not in saved:
                settings["last_daily_summary_sent_date"] = ""
                should_save = True
            if "last_shutdown_clean" not in saved:
                settings["last_shutdown_clean"] = True
                should_save = True
            if saved.get("recovery_email_enabled") is True:
                settings["recovery_email_enabled"] = False
                should_save = True
            if saved.get("popup_alert_enabled") is True:
                settings["popup_alert_enabled"] = False
                should_save = True
    except Exception:
        pass
    if should_save:
        save_settings(settings)
    return settings


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def refresh_optional_dependencies() -> None:
    global winsound, psutil, PSUTIL_IMPORT_ERROR
    global Image, ImageDraw, PIL_IMPORT_ERROR, pystray, PYSTRAY_IMPORT_ERROR

    if winsound is None:
        try:
            winsound = importlib.import_module("winsound")
        except Exception:
            winsound = None

    if psutil is None:
        try:
            psutil = importlib.import_module("psutil")
        except Exception as exc:
            psutil = None
            PSUTIL_IMPORT_ERROR = exc
        else:
            PSUTIL_IMPORT_ERROR = None

    if Image is None or ImageDraw is None:
        try:
            pil_image = importlib.import_module("PIL.Image")
            pil_image_draw = importlib.import_module("PIL.ImageDraw")
        except Exception as exc:
            Image = None
            ImageDraw = None
            PIL_IMPORT_ERROR = exc
        else:
            Image = pil_image
            ImageDraw = pil_image_draw
            PIL_IMPORT_ERROR = None

    if pystray is None:
        try:
            pystray = importlib.import_module("pystray")
        except Exception as exc:
            pystray = None
            PYSTRAY_IMPORT_ERROR = exc
        else:
            PYSTRAY_IMPORT_ERROR = None


def check_environment() -> list[DependencyCheck]:
    refresh_optional_dependencies()
    is_supported_windows = platform.system() == "Windows"
    checks = [
        DependencyCheck(
            "Supported OS",
            "OK" if is_supported_windows else "MISSING",
            True,
            "Windows 10 / 11 supported." if is_supported_windows else f"Current OS is {platform.system()} {platform.release()}. Windows 10 / 11 is required.",
            "Run this project on Windows 10 or Windows 11.",
        ),
        DependencyCheck(
            "Python",
            "OK" if sys.version_info >= MIN_PYTHON_VERSION else "MISSING",
            True,
            (
                f"{sys.version_info.major}.{sys.version_info.minor}."
                f"{sys.version_info.micro}; requires "
                f"{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+"
            ),
            "Install Python 3.10 or newer from python.org.",
        ),
        DependencyCheck(
            "Tkinter",
            "OK" if tk is not None else "MISSING",
            True,
            "Desktop UI support" if tk is not None else f"Desktop UI cannot start: {TK_IMPORT_ERROR}",
            "Reinstall Python and include Tcl/Tk and IDLE.",
        ),
        DependencyCheck(
            "SMTP/SSL/email",
            "OK" if all(module_available(name) for name in ("smtplib", "ssl", "email")) else "MISSING",
            True,
            "Standard library mail support for alert delivery.",
            "Use a complete CPython installation.",
        ),
        DependencyCheck(
            "HTTPS probing",
            "OK" if all(module_available(name) for name in ("urllib.request", "ssl")) else "MISSING",
            True,
            "Standard library HTTPS request support.",
            "Use a complete CPython installation.",
        ),
        DependencyCheck(
            "psutil",
            "OK" if psutil is not None else "MISSING",
            False,
            "CPU, memory, and disk usage monitoring." if psutil is not None else f"System metrics unavailable: {PSUTIL_IMPORT_ERROR}",
            "python -m pip install psutil",
        ),
        DependencyCheck(
            "Sound alert",
            "OK" if winsound is not None else "MISSING",
            False,
            "Windows sound API for local alert beeps." if winsound is not None else "Sound alert will be disabled.",
            "Run on Windows or keep sound alert disabled.",
        ),
        DependencyCheck(
            "Pillow",
            "OK" if Image is not None and ImageDraw is not None else "MISSING",
            False,
            "Tray icon image support." if Image is not None and ImageDraw is not None else f"Tray icon unavailable: {PIL_IMPORT_ERROR}",
            "python -m pip install pillow",
        ),
        DependencyCheck(
            "pystray",
            "OK" if pystray is not None else "MISSING",
            False,
            "System tray integration." if pystray is not None else f"Tray integration unavailable: {PYSTRAY_IMPORT_ERROR}",
            "python -m pip install pystray",
        ),
    ]
    return checks


def missing_required_dependencies(checks: list[DependencyCheck]) -> list[DependencyCheck]:
    return [check for check in checks if check.required and check.status != "OK"]


def is_valid_email_address(value: str) -> bool:
    parsed = parseaddr(value.strip())[1]
    return "@" in parsed and "." in parsed.rsplit("@", 1)[-1]


def login_smtp_with_auth_code(
    server: smtplib.SMTP | smtplib.SMTP_SSL, sender_email: str, auth_code: str
) -> None:
    server.user = sender_email
    server.password = auth_code
    server.auth("LOGIN", server.auth_login)


def create_https_ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def parse_version_tag(value: str) -> tuple[int, ...]:
    cleaned = value.strip().lower().lstrip("v")
    parts = []
    for piece in cleaned.split("."):
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def format_size_bytes(size: int | None) -> str:
    if not isinstance(size, int) or size < 0:
        return "-"
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def acquire_single_instance_mutex() -> object | None:
    if platform.system() != "Windows":
        return object()
    try:
        kernel32 = ctypes.windll.kernel32
        mutex = kernel32.CreateMutexW(None, False, APP_MUTEX_NAME)
        if not mutex:
            return object()
        if kernel32.GetLastError() == 183:
            kernel32.CloseHandle(mutex)
            return None
        return mutex
    except Exception:
        return object()


def describe_http_status(code: int, language: str) -> str:
    if code == 200:
        return tr(language, "http_200")
    if code == 204:
        return tr(language, "http_204")
    return tr(language, "http_other", code=code)


def collect_system_metrics() -> dict:
    if psutil is None:
        return {"available": False, "cpu": None, "memory": None, "disk_c": None}
    try:
        disk_path = "C:\\" if sys.platform.startswith("win") else "/"
        return {
            "available": True,
            "cpu": round(psutil.cpu_percent(interval=0.1), 1),
            "memory": round(psutil.virtual_memory().percent, 1),
            "disk_c": round(psutil.disk_usage(disk_path).percent, 1),
        }
    except Exception:
        return {"available": False, "cpu": None, "memory": None, "disk_c": None}


def collect_power_metrics() -> dict:
    battery_func = getattr(psutil, "sensors_battery", None) if psutil is not None else None
    if battery_func is None:
        return {"supported": False, "has_battery": False, "on_battery": False, "percent": None}
    try:
        battery = battery_func()
    except Exception:
        battery = None
    if battery is None:
        return {"supported": True, "has_battery": False, "on_battery": False, "percent": None}
    percent = getattr(battery, "percent", None)
    plugged = bool(getattr(battery, "power_plugged", False))
    return {
        "supported": True,
        "has_battery": True,
        "on_battery": not plugged,
        "percent": round(percent, 1) if isinstance(percent, (int, float)) else None,
    }


def current_system_theme() -> str:
    if platform.system() != "Windows" or winreg is None:
        return THEME_LIGHT
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, SYSTEM_THEME_REG_PATH) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return THEME_LIGHT if int(value) == 1 else THEME_DARK
    except Exception:
        return THEME_LIGHT


def parse_daily_summary_time(raw_value: str) -> tuple[int, int]:
    try:
        hour_text, minute_text = str(raw_value).strip().split(":", 1)
        hour = max(0, min(23, int(hour_text)))
        minute = max(0, min(59, int(minute_text)))
        return hour, minute
    except Exception:
        return 21, 0


def localize_country_name(country_name: str | None, country_code: str | None, language: str) -> str:
    fallback_name = (country_name or "").strip() or tr(language, "country_unknown")
    code = (country_code or "").strip().upper()
    if language == "en" or not code:
        return fallback_name

    cache_key = (code, language)
    if cache_key in COUNTRY_NAME_CACHE:
        return COUNTRY_NAME_CACHE[cache_key]

    req = request.Request(
        f"https://restcountries.com/v3.1/alpha/{code}?fields=translations,name",
        headers={"User-Agent": f"network-watchdog/{APP_VERSION}"},
    )
    try:
        context = create_https_ssl_context()
        with request.urlopen(req, timeout=6, context=context) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if isinstance(payload, list) and payload:
            payload = payload[0]
        translations = payload.get("translations", {}) if isinstance(payload, dict) else {}
        translated = ""
        if language == "zh":
            translated = (
                translations.get("zho", {}).get("common")
                or translations.get("zht", {}).get("common")
                or ""
            )
        if not translated and isinstance(payload, dict):
            translated = payload.get("name", {}).get("common", "")
        if translated:
            COUNTRY_NAME_CACHE[cache_key] = translated
            return translated
    except Exception:
        pass
    COUNTRY_NAME_CACHE[cache_key] = fallback_name
    return fallback_name


def fetch_external_ip_info(timeout: int, language: str) -> dict:
    sources = [
        (
            "ipwho.is",
            "https://ipwho.is/",
            lambda payload: {
                "ip": payload.get("ip"),
                "country": payload.get("country"),
                "country_code": payload.get("country_code"),
            },
        ),
        (
            "api.ip.sb",
            "https://api.ip.sb/geoip",
            lambda payload: {
                "ip": payload.get("ip"),
                "country": payload.get("country"),
                "country_code": payload.get("country_code"),
            },
        ),
        (
            "ipapi.co",
            "https://ipapi.co/json/",
            lambda payload: {
                "ip": payload.get("ip"),
                "country": payload.get("country_name"),
                "country_code": payload.get("country_code"),
            },
        ),
        (
            "ifconfig.co",
            "https://ifconfig.co/json",
            lambda payload: {
                "ip": payload.get("ip"),
                "country": payload.get("country"),
                "country_code": payload.get("country_iso"),
            },
        ),
    ]
    context = create_https_ssl_context()
    for source_name, url, parser in sources:
        try:
            req = request.Request(
                url,
                headers={
                    "User-Agent": f"network-watchdog/{APP_VERSION}",
                    "Accept": "application/json",
                },
            )
            with request.urlopen(req, timeout=max(4, timeout), context=context) as response:
                payload = json.loads(response.read().decode("utf-8"))
            parsed = parser(payload)
            ip_value = str(parsed.get("ip") or "").strip()
            if not ip_value:
                continue
            country_code = str(parsed.get("country_code") or "").strip().upper()
            country_name = localize_country_name(parsed.get("country"), country_code, language)
            return {
                "ip": ip_value,
                "country": country_name,
                "country_raw": str(parsed.get("country") or "").strip(),
                "country_code": country_code or "",
                "source": source_name,
                "ok": True,
            }
        except Exception:
            continue
    return {
        "ip": "-",
        "country": tr(language, "country_unknown"),
        "country_raw": "",
        "country_code": "",
        "source": "-",
        "ok": False,
    }


class NetworkWatchdogApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.geometry("1080x720")
        self.root.minsize(960, 640)

        self.targets = load_targets()
        self.settings = load_settings()
        self._normalize_daily_counter()
        self.language = str(self.settings.get("language", "en"))
        if self.language not in TEXT:
            self.language = "en"
        self.dependency_checks = check_environment()
        self.tray_available = pystray is not None and Image is not None and ImageDraw is not None

        self.command_queue: queue.Queue[str] = queue.Queue()
        self.results_queue: queue.Queue[dict] = queue.Queue()
        self.update_queue: queue.Queue[dict] = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread: threading.Thread | None = None
        self.tray_icon = None
        self.closing = False
        self.startup_complete = False
        self.window_hidden = False
        self.next_run_ts: float | None = None
        self.latest_batch: dict | None = None
        self.last_alert_state = "INIT"
        self.last_system_alert_active = False
        self.last_power_alert_active = False
        self.history_points: list[dict] = []
        self.rows: dict[str, str] = {}
        self.event_lines: list[str] = []
        self.manual_refresh_started_at: float | None = None
        self.manual_refresh_pending = False
        self.popup_alert_open = False
        self.down_alert_streak = 0
        self.down_alert_active = False
        self.system_alert_streak = 0
        self.slow_latency_alert_streak = 0
        self.slow_latency_alert_active = False
        self.update_check_in_progress = False
        self.latest_release_info: dict | None = None
        self.current_theme = current_system_theme()
        self.external_ip_info = {
            "ip": "-",
            "country": self._t("country_unknown") if hasattr(self, "language") else "Unknown",
            "country_raw": "",
            "country_code": "",
            "source": "-",
            "ok": False,
        }
        self.power_metrics = collect_power_metrics()

        self.widgets: dict[str, object] = {}
        self.labels: dict[str, tk.StringVar] = {}
        self.notebook_tabs: list[tuple[ttk.Frame, str]] = []
        self.nav_buttons: list[tk.Button] = []

        self.interval_var = tk.StringVar(value=str(self.settings["interval_seconds"]))
        self.timeout_var = tk.StringVar(value=str(self.settings["timeout_seconds"]))
        self.threshold_var = tk.StringVar(value=str(self.settings["degraded_latency_ms"]))
        self.min_ok_var = tk.StringVar(value=str(self.settings["minimum_ok_targets"]))
        self.system_threshold_var = tk.StringVar(value=str(self.settings["system_alert_threshold"]))
        self.slow_latency_alert_var = tk.StringVar(value=str(self.settings["slow_avg_latency_alert_ms"]))
        self.language_var = tk.StringVar(value="English" if self.language == "en" else TEXT["zh"]["language_name"])
        self.status_var = tk.StringVar()
        self.last_update_var = tk.StringVar()
        self.next_update_var = tk.StringVar()
        self.manual_refresh_var = tk.StringVar()
        self.system_status_var = tk.StringVar()
        self.email_alert_count_var = tk.StringVar()
        self.external_ip_var = tk.StringVar()
        self.current_version_var = tk.StringVar(value=f"v{APP_VERSION}")
        self.latest_version_var = tk.StringVar(value="-")
        self.update_published_var = tk.StringVar(value="-")
        self.update_status_var = tk.StringVar()

        self.sound_alert_var = tk.BooleanVar(value=bool(self.settings["sound_alert_enabled"]))
        self.popup_alert_var = tk.BooleanVar(value=bool(self.settings["popup_alert_enabled"]))
        self.email_alert_var = tk.BooleanVar(value=bool(self.settings["email_alert_enabled"]))
        self.daily_summary_var = tk.BooleanVar(value=bool(self.settings.get("daily_summary_enabled", False)))
        self.recovery_email_var = tk.BooleanVar(value=bool(self.settings["recovery_email_enabled"]))
        self.auto_update_check_var = tk.BooleanVar(value=bool(self.settings["auto_check_updates_enabled"]))
        self.minimize_on_close_var = tk.BooleanVar(
            value=bool(self.settings["minimize_to_tray_on_close"]) and self.tray_available
        )
        self.daily_summary_time_var = tk.StringVar(value=str(self.settings.get("daily_summary_time", DEFAULT_DAILY_SUMMARY_TIME)))
        self.smtp_host_var = tk.StringVar(value=str(self.settings["smtp_host"]))
        self.sender_email_var = tk.StringVar(value=str(self.settings["sender_email"]))
        self.sender_name_var = tk.StringVar(value=str(self.settings["sender_name"]))
        self.auth_code_var = tk.StringVar(value=str(self.settings["auth_code"]))
        self.recipient_vars = [
            tk.StringVar(value=str(self.settings["recipient_1"])),
            tk.StringVar(value=str(self.settings["recipient_2"])),
            tk.StringVar(value=str(self.settings["recipient_3"])),
        ]

        self._ensure_log_file()
        self._build_ui()
        self._apply_theme()
        self._refresh_language_text()
        self._setup_tray()
        self.startup_complete = True
        self._refresh_environment_checks()
        self._mark_run_started()
        self._start_worker()
        self._poll_results()
        self._tick_clock()
        self._tick_theme()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_request)
        self.root.bind("<Unmap>", self._on_minimize_event)
        self.root.after(800, self._show_environment_startup_notice)
        self.update_status_var.set(self._t("update_idle"))
        if self.auto_update_check_var.get():
            self.root.after(1800, self._check_updates_now)

    def _t(self, key: str, **kwargs: object) -> str:
        return tr(self.language, key, **kwargs)

    def _normalize_daily_counter(self) -> None:
        today = date.today().isoformat()
        if self.settings.get("email_alert_count_date") != today:
            self.settings["email_alert_count_date"] = today
            self.settings["email_alert_count_today"] = 0
            save_settings(self.settings)

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=(10, 8))
        top.pack(fill=tk.X)
        for column in range(10):
            top.columnconfigure(column, weight=0)

        self.widgets["refresh_label"] = ttk.Label(top)
        self.widgets["refresh_label"].grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.interval_var, width=7).grid(row=0, column=1, padx=(4, 14))

        self.widgets["timeout_label"] = ttk.Label(top)
        self.widgets["timeout_label"].grid(row=0, column=2, sticky="w")
        ttk.Entry(top, textvariable=self.timeout_var, width=7).grid(row=0, column=3, padx=(4, 14))

        self.widgets["degraded_label"] = ttk.Label(top)
        self.widgets["degraded_label"].grid(row=0, column=4, sticky="w")
        ttk.Entry(top, textvariable=self.threshold_var, width=8).grid(row=0, column=5, padx=(4, 14))

        self.widgets["min_ok_label"] = ttk.Label(top)
        self.widgets["min_ok_label"].grid(row=0, column=6, sticky="w")
        ttk.Entry(top, textvariable=self.min_ok_var, width=6).grid(row=0, column=7, padx=(4, 14))

        self.widgets["language_label"] = ttk.Label(top)
        self.widgets["language_label"].grid(row=0, column=8, sticky="w")
        language_box = ttk.Combobox(
            top,
            textvariable=self.language_var,
            values=("English", TEXT["zh"]["language_name"]),
            state="readonly",
            width=10,
        )
        language_box.grid(row=0, column=9, padx=(4, 0))
        language_box.bind("<<ComboboxSelected>>", self._on_language_changed)

        self.widgets["apply_button"] = ttk.Button(top, command=self._apply_settings)
        self.widgets["apply_button"].grid(row=1, column=0, pady=(8, 0), sticky="ew")
        self.widgets["refresh_button"] = ttk.Button(top, command=self._trigger_manual_refresh)
        self.widgets["refresh_button"].grid(row=1, column=1, padx=(6, 0), pady=(8, 0), sticky="ew")
        self.widgets["test_email_button"] = ttk.Button(top, command=self._send_test_email)
        self.widgets["test_email_button"].grid(row=1, column=2, padx=(6, 0), pady=(8, 0), sticky="ew")
        self.widgets["tray_button"] = ttk.Button(top, command=self._hide_to_tray)
        self.widgets["tray_button"].grid(row=1, column=3, padx=(6, 0), pady=(8, 0), sticky="ew")
        if not self.tray_available:
            self.widgets["tray_button"].state(["disabled"])

        summary = ttk.Frame(self.root, padding=(10, 0, 10, 8))
        summary.pack(fill=tk.X)
        self.widgets["status_summary_label"] = ttk.Label(summary, textvariable=self.status_var)
        self.widgets["status_summary_label"].grid(row=0, column=0, sticky="w")
        ttk.Label(summary, textvariable=self.system_status_var).grid(row=1, column=0, sticky="w")
        ttk.Label(summary, textvariable=self.email_alert_count_var).grid(row=2, column=0, sticky="w")
        ttk.Label(summary, textvariable=self.external_ip_var).grid(row=3, column=0, sticky="w")
        ttk.Label(summary, textvariable=self.manual_refresh_var, foreground="#1570ef").grid(row=0, column=1, sticky="e")
        ttk.Label(summary, textvariable=self.last_update_var).grid(row=1, column=1, sticky="e")
        ttk.Label(summary, textvariable=self.next_update_var).grid(row=2, column=1, sticky="e")
        daily_summary_frame = ttk.Frame(summary)
        daily_summary_frame.grid(row=3, column=1, sticky="e")
        self.widgets["daily_summary_check"] = ttk.Checkbutton(daily_summary_frame, variable=self.daily_summary_var)
        self.widgets["daily_summary_check"].pack(side=tk.LEFT)
        self.widgets["daily_summary_time_label"] = ttk.Label(daily_summary_frame)
        self.widgets["daily_summary_time_label"].pack(side=tk.LEFT, padx=(8, 4))
        ttk.Entry(daily_summary_frame, textvariable=self.daily_summary_time_var, width=6).pack(side=tk.LEFT)
        summary.columnconfigure(0, weight=1)
        summary.columnconfigure(1, weight=1)

        nav = tk.Frame(self.root, padx=10, pady=4, bg="#eef2f6")
        nav.pack(fill=tk.X)
        self.widgets["nav_frame"] = nav
        self.nav_buttons = []
        for index, key in enumerate(("dashboard", "email", "history", "environment", "updates")):
            button = tk.Button(
                nav,
                relief=tk.FLAT,
                bd=0,
                padx=16,
                pady=7,
                cursor="hand2",
                command=lambda selected=index: self._select_tab(selected),
            )
            button.pack(side=tk.LEFT, padx=(0, 6))
            self.nav_buttons.append(button)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_notebook_tab_changed)

        dashboard_tab = ttk.Frame(self.notebook, padding=8)
        email_tab = ttk.Frame(self.notebook, padding=8)
        history_tab = ttk.Frame(self.notebook, padding=8)
        environment_tab = ttk.Frame(self.notebook, padding=8)
        updates_tab = ttk.Frame(self.notebook, padding=8)
        self.notebook_tabs = [
            (dashboard_tab, "dashboard"),
            (email_tab, "email"),
            (history_tab, "history"),
            (environment_tab, "environment"),
            (updates_tab, "updates"),
        ]
        for tab, key in self.notebook_tabs:
            self.notebook.add(tab, text=self._t(key))

        self._build_dashboard_tab(dashboard_tab)
        self._build_email_tab(email_tab)
        self._build_history_tab(history_tab)
        self._build_environment_tab(environment_tab)
        self._build_updates_tab(updates_tab)
        self._update_nav_state()

    def _build_dashboard_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=3)
        parent.columnconfigure(1, weight=2)
        parent.rowconfigure(0, weight=1)

        columns = ("site", "status", "latency", "detail", "checked_at")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.tree.column("site", width=120, anchor=tk.W)
        self.tree.column("status", width=80, anchor=tk.CENTER)
        self.tree.column("latency", width=95, anchor=tk.CENTER)
        self.tree.column("detail", width=300, anchor=tk.W)
        self.tree.column("checked_at", width=140, anchor=tk.CENTER)
        self.tree.tag_configure("ok", foreground="#12783d")
        self.tree.tag_configure("warn", foreground="#b54708")
        self.tree.tag_configure("fail", foreground="#b42318")

        for target in self.targets:
            item_id = self.tree.insert(
                "",
                tk.END,
                values=(target.name, self._t("pending"), "-", self._t("waiting_probe"), "-"),
            )
            self.rows[target.name] = item_id

        side = ttk.Frame(parent)
        side.grid(row=0, column=1, sticky="nsew")
        side.rowconfigure(1, weight=1)
        self.widgets["small_chart_label"] = ttk.Label(side)
        self.widgets["small_chart_label"].grid(row=0, column=0, sticky="w")
        self.small_chart_canvas = tk.Canvas(
            side,
            bg="#fcfcfd",
            height=210,
            highlightthickness=1,
            highlightbackground="#d0d5dd",
        )
        self.small_chart_canvas.grid(row=1, column=0, sticky="nsew", pady=(4, 8))
        self.small_chart_canvas.bind("<Configure>", lambda _event: self._draw_history_charts())

        self.widgets["recent_events_label"] = ttk.Label(side)
        self.widgets["recent_events_label"].grid(row=2, column=0, sticky="w")
        self.event_list = tk.Listbox(side, height=8)
        self.event_list.grid(row=3, column=0, sticky="nsew", pady=(4, 0))
        side.columnconfigure(0, weight=1)

    def _build_email_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)

        self.widgets["sound_check"] = ttk.Checkbutton(parent, variable=self.sound_alert_var)
        self.widgets["sound_check"].grid(row=0, column=0, sticky="w", pady=3)
        self.widgets["popup_check"] = ttk.Checkbutton(parent, variable=self.popup_alert_var)
        self.widgets["popup_check"].grid(row=0, column=1, sticky="w", pady=3)
        self.widgets["email_check"] = ttk.Checkbutton(parent, variable=self.email_alert_var)
        self.widgets["email_check"].grid(row=0, column=2, sticky="w", pady=3)
        self.widgets["recovery_check"] = ttk.Checkbutton(parent, variable=self.recovery_email_var)
        self.widgets["recovery_check"].grid(row=0, column=3, sticky="w", pady=3)
        self.widgets["recovery_check"].state(["disabled"])

        self.widgets["daily_summary_email_check"] = ttk.Checkbutton(parent, variable=self.daily_summary_var)
        self.widgets["daily_summary_email_check"].grid(row=1, column=0, sticky="w", pady=3)
        self.widgets["daily_summary_time_email_label"] = ttk.Label(parent)
        self.widgets["daily_summary_time_email_label"].grid(row=1, column=1, sticky="e", pady=3, padx=(0, 6))
        ttk.Entry(parent, textvariable=self.daily_summary_time_var, width=6).grid(row=1, column=2, sticky="w", pady=3)

        self.widgets["tray_check"] = ttk.Checkbutton(parent, variable=self.minimize_on_close_var)
        self.widgets["tray_check"].grid(row=2, column=0, columnspan=2, sticky="w", pady=3)
        if not self.tray_available:
            self.widgets["tray_check"].state(["disabled"])

        self.widgets["system_threshold_label"] = ttk.Label(parent)
        self.widgets["system_threshold_label"].grid(row=2, column=2, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.system_threshold_var, width=8).grid(row=2, column=3, sticky="w", pady=3)

        self.widgets["slow_latency_alert_label"] = ttk.Label(parent)
        self.widgets["slow_latency_alert_label"].grid(row=3, column=2, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.slow_latency_alert_var, width=8).grid(row=3, column=3, sticky="w", pady=3)

        self.widgets["smtp_host_label"] = ttk.Label(parent)
        self.widgets["smtp_host_label"].grid(row=4, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.smtp_host_var).grid(row=4, column=1, sticky="ew", pady=3, padx=(0, 10))

        self.widgets["sender_email_label"] = ttk.Label(parent)
        self.widgets["sender_email_label"].grid(row=5, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.sender_email_var).grid(row=5, column=1, sticky="ew", pady=3, padx=(0, 10))
        self.widgets["sender_name_label"] = ttk.Label(parent)
        self.widgets["sender_name_label"].grid(row=5, column=2, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.sender_name_var).grid(row=5, column=3, sticky="ew", pady=3)

        self.widgets["smtp_auth_label"] = ttk.Label(parent)
        self.widgets["smtp_auth_label"].grid(row=6, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.auth_code_var, show="*").grid(row=6, column=1, sticky="ew", pady=3, padx=(0, 10))

        for index, var in enumerate(self.recipient_vars):
            row = 7 + index
            label_key = f"recipient_{index + 1}"
            self.widgets[f"{label_key}_label"] = ttk.Label(parent)
            self.widgets[f"{label_key}_label"].grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(parent, textvariable=var).grid(row=row, column=1, columnspan=3, sticky="ew", pady=3)

        self.widgets["save_button"] = ttk.Button(parent, command=self._apply_settings)
        self.widgets["save_button"].grid(row=10, column=0, sticky="w", pady=(10, 0))
        self.widgets["test_sound_button"] = ttk.Button(parent, command=self._play_test_sound)
        self.widgets["test_sound_button"].grid(row=10, column=1, sticky="w", pady=(10, 0))
        self.widgets["email_note"] = ttk.Label(parent, wraplength=840, foreground="#475467")
        self.widgets["email_note"].grid(row=11, column=0, columnspan=4, sticky="w", pady=(10, 0))

    def _build_history_tab(self, parent: ttk.Frame) -> None:
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)
        self.widgets["history_chart_label"] = ttk.Label(parent)
        self.widgets["history_chart_label"].grid(row=0, column=0, sticky="w")
        self.history_chart_canvas = tk.Canvas(
            parent,
            bg="#fcfcfd",
            height=320,
            highlightthickness=1,
            highlightbackground="#d0d5dd",
        )
        self.history_chart_canvas.grid(row=1, column=0, sticky="nsew", pady=(4, 8))
        self.history_chart_canvas.bind("<Configure>", lambda _event: self._draw_history_charts())

    def _build_environment_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        top = ttk.Frame(parent)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.widgets["env_recheck_button"] = ttk.Button(top, command=self._refresh_environment_checks)
        self.widgets["env_recheck_button"].pack(side=tk.LEFT)
        self.widgets["env_note"] = ttk.Label(top, foreground="#475467")
        self.widgets["env_note"].pack(side=tk.LEFT, padx=(10, 0))

        columns = ("name", "status", "required", "detail", "install_hint")
        self.environment_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        self.environment_tree.grid(row=1, column=0, sticky="nsew")
        parent.rowconfigure(1, weight=1)
        self.environment_tree.column("name", width=130, anchor=tk.W)
        self.environment_tree.column("status", width=80, anchor=tk.CENTER)
        self.environment_tree.column("required", width=80, anchor=tk.CENTER)
        self.environment_tree.column("detail", width=350, anchor=tk.W)
        self.environment_tree.column("install_hint", width=280, anchor=tk.W)
        self.environment_tree.tag_configure("ok", foreground="#12783d")
        self.environment_tree.tag_configure("missing_required", foreground="#b42318")
        self.environment_tree.tag_configure("missing_optional", foreground="#b54708")

        install_box = ttk.LabelFrame(parent, padding=8)
        install_box.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.widgets["install_box"] = install_box
        self.install_hint_var = tk.StringVar()
        ttk.Label(install_box, textvariable=self.install_hint_var, wraplength=860, foreground="#344054").pack(anchor=tk.W)

    def _build_updates_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(4, weight=1)

        self.widgets["current_version_label"] = ttk.Label(parent)
        self.widgets["current_version_label"].grid(row=0, column=0, sticky="w", pady=3)
        ttk.Label(parent, textvariable=self.current_version_var).grid(row=0, column=1, sticky="w", pady=3)

        self.widgets["latest_version_label"] = ttk.Label(parent)
        self.widgets["latest_version_label"].grid(row=1, column=0, sticky="w", pady=3)
        ttk.Label(parent, textvariable=self.latest_version_var).grid(row=1, column=1, sticky="w", pady=3)

        self.widgets["published_at_label"] = ttk.Label(parent)
        self.widgets["published_at_label"].grid(row=2, column=0, sticky="w", pady=3)
        ttk.Label(parent, textvariable=self.update_published_var).grid(row=2, column=1, sticky="w", pady=3)

        self.widgets["update_status_label"] = ttk.Label(parent)
        self.widgets["update_status_label"].grid(row=3, column=0, sticky="w", pady=3)
        ttk.Label(parent, textvariable=self.update_status_var, foreground="#175cd3").grid(
            row=3, column=1, sticky="w", pady=3
        )

        self.update_assets_tree = ttk.Treeview(
            parent,
            columns=("name", "size", "url"),
            show="headings",
            height=8,
        )
        self.update_assets_tree.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(6, 8))
        self.update_assets_tree.column("name", width=260, anchor=tk.W)
        self.update_assets_tree.column("size", width=90, anchor=tk.CENTER)
        self.update_assets_tree.column("url", width=420, anchor=tk.W)

        actions = ttk.Frame(parent)
        actions.grid(row=5, column=0, columnspan=2, sticky="w", pady=(2, 0))
        self.widgets["check_updates_button"] = ttk.Button(actions, command=self._check_updates_now)
        self.widgets["check_updates_button"].pack(side=tk.LEFT)
        self.widgets["open_release_button"] = ttk.Button(actions, command=lambda: webbrowser.open(RELEASES_PAGE_URL))
        self.widgets["open_release_button"].pack(side=tk.LEFT, padx=(8, 0))
        self.widgets["open_update_download_button"] = ttk.Button(actions, command=self._open_selected_update_download)
        self.widgets["open_update_download_button"].pack(side=tk.LEFT, padx=(8, 0))

        self.widgets["auto_update_check_box"] = ttk.Checkbutton(
            parent,
            variable=self.auto_update_check_var,
            command=self._apply_settings,
        )
        self.widgets["auto_update_check_box"].grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

    def _refresh_language_text(self) -> None:
        text_map = {
            "refresh_label": "refresh_s",
            "timeout_label": "timeout_s",
            "degraded_label": "degraded_ms",
            "min_ok_label": "minimum_ok",
            "language_label": "language",
            "apply_button": "apply",
            "refresh_button": "refresh_now",
            "test_email_button": "test_email",
            "tray_button": "hide_to_tray",
            "small_chart_label": "small_chart",
            "recent_events_label": "recent_events",
            "sound_check": "sound_alert",
            "popup_check": "popup_alert",
            "email_check": "email_alert",
            "daily_summary_check": "daily_summary_email",
            "daily_summary_time_label": "daily_summary_time",
            "daily_summary_email_check": "daily_summary_email",
            "daily_summary_time_email_label": "daily_summary_time",
            "recovery_check": "recovery_email",
            "tray_check": "close_to_tray",
            "system_threshold_label": "system_summary",
            "slow_latency_alert_label": "slow_latency_alert_ms",
            "smtp_host_label": "smtp_host",
            "sender_email_label": "sender_email",
            "sender_name_label": "sender_name",
            "smtp_auth_label": "smtp_auth",
            "recipient_1_label": "recipient_1",
            "recipient_2_label": "recipient_2",
            "recipient_3_label": "recipient_3",
            "save_button": "save_settings",
            "test_sound_button": "test_sound",
            "email_note": "email_note",
            "history_chart_label": "small_chart",
            "env_recheck_button": "env_recheck",
            "env_note": "env_note",
            "current_version_label": "current_version",
            "latest_version_label": "latest_version",
            "published_at_label": "published_at",
            "update_status_label": "update_status",
            "check_updates_button": "check_updates_now",
            "open_release_button": "open_release_page",
            "open_update_download_button": "update_open_download",
            "auto_update_check_box": "auto_update_check",
        }
        for widget_key, text_key in text_map.items():
            widget = self.widgets.get(widget_key)
            if widget is not None:
                widget.configure(text=self._t(text_key))

        install_box = self.widgets.get("install_box")
        if install_box is not None:
            install_box.configure(text=self._t("portable_commands"))

        for index, (tab, key) in enumerate(self.notebook_tabs):
            self.notebook.tab(index, text=self._t(key))
        for index, button in enumerate(self.nav_buttons):
            if index < len(self.notebook_tabs):
                button.configure(text=self._t(self.notebook_tabs[index][1]))
        self._update_nav_state()

        if hasattr(self, "tree"):
            headings = {
                "site": "target",
                "status": "status",
                "latency": "latency",
                "detail": "detail",
                "checked_at": "checked_at",
            }
            for column, key in headings.items():
                self.tree.heading(column, text=self._t(key))

        if hasattr(self, "environment_tree"):
            headings = {
                "name": "item",
                "status": "status",
                "required": "required",
                "detail": "detail",
                "install_hint": "install_hint",
            }
            for column, key in headings.items():
                self.environment_tree.heading(column, text=self._t(key))

        if hasattr(self, "update_assets_tree"):
            headings = {
                "name": "asset_name",
                "size": "asset_size",
                "url": "asset_url",
            }
            for column, key in headings.items():
                self.update_assets_tree.heading(column, text=self._t(key))

        if self.latest_batch:
            self._update_summary_labels(self.latest_batch)
        else:
            self.status_var.set(f"{self._t('network_summary')}: {self._t('waiting_probe')}")
            self.system_status_var.set(f"{self._t('system_summary')}: -")
            self.external_ip_var.set(f"{self._t('external_ip')}: - | {self._t('country_unknown')}")
            self.last_update_var.set(self._t("last_not_started"))
            self.next_update_var.set(self._t("next_not_scheduled"))
        self.manual_refresh_var.set(self._t("manual_idle"))
        self._refresh_email_alert_count_label()
        self._refresh_environment_checks()
        self._draw_history_charts()

    def _select_tab(self, index: int) -> None:
        self.notebook.select(index)
        self._update_nav_state()

    def _on_notebook_tab_changed(self, _event: object = None) -> None:
        self._update_nav_state()

    def _update_nav_state(self) -> None:
        if not hasattr(self, "notebook") or not self.nav_buttons:
            return
        if self.current_theme == THEME_DARK:
            active_bg, active_fg = "#175cd3", "#ffffff"
            idle_bg, idle_fg = "#182230", "#d0d5dd"
            idle_active_bg, idle_active_fg = "#344054", "#ffffff"
        else:
            active_bg, active_fg = "#1570ef", "#ffffff"
            idle_bg, idle_fg = "#ffffff", "#344054"
            idle_active_bg, idle_active_fg = "#d0d5dd", "#101828"
        current_tab = self.notebook.index(self.notebook.select())
        for index, button in enumerate(self.nav_buttons):
            if index == current_tab:
                button.configure(
                    bg=active_bg,
                    fg=active_fg,
                    activebackground=active_bg,
                    activeforeground=active_fg,
                    font=("Segoe UI", 10, "bold"),
                )
            else:
                button.configure(
                    bg=idle_bg,
                    fg=idle_fg,
                    activebackground=idle_active_bg,
                    activeforeground=idle_active_fg,
                    font=("Segoe UI", 10, "normal"),
                )

    def _ensure_log_file(self) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if not LOG_PATH.exists():
            with LOG_PATH.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        "timestamp",
                        "site",
                        "status",
                        "latency_ms",
                        "detail",
                        "summary_state",
                        "success_rate",
                        "cpu_percent",
                        "memory_percent",
                        "disk_c_percent",
                    ]
                )

    def _setup_tray(self) -> None:
        if not self.tray_available:
            self.tray_icon = None
            self._add_event_line("System tray disabled: install pillow and pystray")
            return

        menu = pystray.Menu(
            pystray.MenuItem("Show", self._tray_show_window),
            pystray.MenuItem("Refresh now", self._tray_refresh_now),
            pystray.MenuItem("Exit", self._tray_exit_app),
        )
        self.tray_icon = pystray.Icon(
            "network_watchdog",
            self._build_tray_image(self.last_alert_state if self.last_alert_state != "INIT" else STATE_NORMAL),
            APP_TITLE,
            menu,
        )
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _start_worker(self) -> None:
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def _worker_loop(self) -> None:
        trigger = "startup"
        self.next_run_ts = time.time()
        while not self.stop_event.is_set():
            interval = self._current_interval()
            timeout = self._current_timeout()
            threshold = self._current_threshold()
            minimum_ok = self._current_min_ok_targets()
            slow_threshold = self._current_slow_state_threshold()
            results = []
            ok_count = 0
            latency_values = []

            for target in self.targets:
                result = self._probe_target(target, timeout)
                if result["status"] == "OK":
                    ok_count += 1
                if result["latency_ms"] is not None:
                    latency_values.append(result["latency_ms"])
                results.append(result)

            avg_latency = int(sum(latency_values) / len(latency_values)) if latency_values else None
            success_rate = round(ok_count / len(self.targets) * 100, 1)
            summary_state = self._classify_state(
                ok_count,
                len(self.targets),
                avg_latency,
                slow_threshold,
                minimum_ok,
            )
            system_metrics = collect_system_metrics()
            power_metrics = collect_power_metrics()
            external_ip = fetch_external_ip_info(timeout, self.language)

            payload = {
                "type": "batch",
                "trigger": trigger,
                "results": results,
                "ok_count": ok_count,
                "total_count": len(self.targets),
                "interval": interval,
                "avg_latency_ms": avg_latency,
                "success_rate": success_rate,
                "summary_state": summary_state,
                "system_metrics": system_metrics,
                "power_metrics": power_metrics,
                "external_ip": external_ip,
                "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time.time(),
            }
            self.results_queue.put(payload)
            self._append_csv_log(payload)

            self.next_run_ts = time.time() + interval
            trigger = self._wait_for_next_run(interval)

    def _wait_for_next_run(self, interval: int) -> str:
        waited = 0.0
        while waited < interval and not self.stop_event.is_set():
            time.sleep(0.2)
            waited += 0.2
            try:
                message = self.command_queue.get_nowait()
            except queue.Empty:
                continue
            if message == "manual_refresh":
                return "manual"
        return "scheduled"

    def _probe_target(self, target: ProbeTarget, timeout: int) -> dict:
        started = time.perf_counter()
        checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        req = request.Request(
            target.url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0 Safari/537.36"
                )
            },
        )
        try:
            ssl_context = create_https_ssl_context()
            with request.urlopen(req, timeout=timeout, context=ssl_context) as response:
                latency_ms = int((time.perf_counter() - started) * 1000)
                code = getattr(response, "status", None) or response.getcode()
                return {
                    "site": target.name,
                    "status": "OK",
                    "latency": f"{latency_ms} ms",
                    "latency_ms": latency_ms,
                    "detail_code": code,
                    "detail": describe_http_status(code, self.language),
                    "checked_at": checked_at,
                    "tag": "ok",
                }
        except error.HTTPError as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            return {
                "site": target.name,
                "status": "FAIL",
                "latency": f"{latency_ms} ms",
                "latency_ms": latency_ms,
                "detail_code": exc.code,
                "detail": self._t("http_error", code=exc.code),
                "checked_at": checked_at,
                "tag": "fail",
            }
        except ssl.SSLCertVerificationError:
            return {
                "site": target.name,
                "status": "FAIL",
                "latency": "-",
                "latency_ms": None,
                "detail_code": None,
                "detail": "SSL certificate verification failed on this machine.",
                "checked_at": checked_at,
                "tag": "fail",
            }
        except Exception as exc:
            return {
                "site": target.name,
                "status": "FAIL",
                "latency": "-",
                "latency_ms": None,
                "detail_code": None,
                "detail": str(exc),
                "checked_at": checked_at,
                "tag": "fail",
            }

    def _poll_results(self) -> None:
        while True:
            try:
                payload = self.results_queue.get_nowait()
            except queue.Empty:
                break
            if payload.get("type") != "batch":
                continue

            self.latest_batch = payload
            self.external_ip_info = payload.get("external_ip", self.external_ip_info)
            self.power_metrics = payload.get("power_metrics", self.power_metrics)
            for result in payload["results"]:
                self.tree.item(
                    self.rows[result["site"]],
                    values=(
                        result["site"],
                        result["status"],
                        result["latency"],
                        self._localized_result_detail(result),
                        result["checked_at"],
                    ),
                    tags=(result["tag"],),
                )
            self._update_summary_labels(payload)
            self.next_run_ts = time.time() + payload["interval"]
            self._record_history_point(payload)
            self._handle_alert_transition(payload)
            self._handle_down_alert(payload)
            self._handle_system_alert(payload)
            self._handle_slow_latency_alert(payload)
            self._handle_power_alert(payload)
            self._check_daily_summary(payload)
            self._refresh_tray_icon_state(payload["summary_state"])

            if payload.get("trigger") == "manual":
                self.manual_refresh_pending = False
                self.manual_refresh_started_at = None
                self.manual_refresh_var.set(
                    self._t("manual_done", time=datetime.now().strftime("%H:%M:%S"))
                )
                self._add_event_line(self.manual_refresh_var.get())

        while True:
            try:
                update_payload = self.update_queue.get_nowait()
            except queue.Empty:
                break
            self._apply_update_payload(update_payload)

        self.root.after(300, self._poll_results)

    def _localized_result_detail(self, result: dict) -> str:
        code = result.get("detail_code")
        if isinstance(code, int):
            if result["status"] == "OK":
                return describe_http_status(code, self.language)
            return self._t("http_error", code=code)
        return str(result.get("detail", ""))

    def _update_summary_labels(self, payload: dict) -> None:
        state = payload["summary_state"]
        avg_latency = payload["avg_latency_ms"]
        success_rate = payload["success_rate"]
        state_text = self._state_text(state)
        self.status_var.set(
            f"{self._t('network_summary')}: {state_text} | "
            f"{self._t('success')} {payload['ok_count']}/{payload['total_count']} "
            f"({success_rate}%) | {self._t('avg_latency')} "
            f"{avg_latency if avg_latency is not None else '-'} ms"
        )
        status_label = self.widgets.get("status_summary_label")
        if status_label is not None:
            status_label.configure(foreground=TRAY_STATE_COLORS.get(state, "#12b76a"))
        metrics = payload.get("system_metrics", {})
        power_metrics = payload.get("power_metrics", {})
        if metrics.get("available"):
            self.system_status_var.set(
                f"{self._t('system_summary')}: "
                f"{self._t('cpu')} {metrics['cpu']}% | "
                f"{self._t('memory')} {metrics['memory']}% | "
                f"{self._t('c_drive')} {metrics['disk_c']}% | "
                f"{self._t('power_summary')} {self._power_status_text(power_metrics)}"
            )
        else:
            self.system_status_var.set(f"{self._t('system_summary')}: psutil unavailable")
        external_ip = payload.get("external_ip", {})
        country_text = localize_country_name(
            external_ip.get("country_raw") or external_ip.get("country"),
            external_ip.get("country_code"),
            self.language,
        )
        self.external_ip_var.set(
            f"{self._t('external_ip')}: {external_ip.get('ip', '-')} | {country_text}"
        )
        self.last_update_var.set(self._t("last_update", time=payload["checked_at"]))
        self._refresh_email_alert_count_label()

    def _tick_clock(self) -> None:
        if self.manual_refresh_pending and self.manual_refresh_started_at is not None:
            elapsed = int(time.time() - self.manual_refresh_started_at)
            self.manual_refresh_var.set(self._t("manual_running", seconds=elapsed))
            self.next_update_var.set(self._t("manual_requested"))
        elif self.next_run_ts is None:
            self.next_update_var.set(self._t("next_not_scheduled"))
        else:
            remain = max(0, int(self.next_run_ts - time.time()))
            self.next_update_var.set(self._t("next_in", seconds=remain))
        self.root.after(1000, self._tick_clock)

    def _apply_settings(self) -> None:
        self.settings.update(
            {
                "interval_seconds": self._current_interval(),
                "timeout_seconds": self._current_timeout(),
                "degraded_latency_ms": self._current_threshold(),
                "minimum_ok_targets": self._current_min_ok_targets(),
                "system_alert_threshold": self._current_system_threshold(),
                "slow_avg_latency_alert_ms": self._current_slow_latency_alert_threshold(),
                "sound_alert_enabled": self.sound_alert_var.get(),
                "popup_alert_enabled": self.popup_alert_var.get(),
                "email_alert_enabled": self.email_alert_var.get(),
                "daily_summary_enabled": self.daily_summary_var.get(),
                "daily_summary_time": self._current_daily_summary_time(),
                "recovery_email_enabled": self.recovery_email_var.get(),
                "auto_check_updates_enabled": self.auto_update_check_var.get(),
                "minimize_to_tray_on_close": self.minimize_on_close_var.get(),
                "language": self.language,
                "smtp_host": self.smtp_host_var.get().strip() or DEFAULT_SMTP_HOST,
                "sender_email": self.sender_email_var.get().strip(),
                "sender_name": self.sender_name_var.get().strip() or "Network Watchdog",
                "auth_code": self.auth_code_var.get().strip(),
                "recipient_1": self.recipient_vars[0].get().strip(),
                "recipient_2": self.recipient_vars[1].get().strip(),
                "recipient_3": self.recipient_vars[2].get().strip(),
                "email_alert_count_date": self.settings.get("email_alert_count_date", date.today().isoformat()),
                "email_alert_count_today": self.settings.get("email_alert_count_today", 0),
                "last_daily_summary_sent_date": self.settings.get("last_daily_summary_sent_date", ""),
                "last_shutdown_clean": self.settings.get("last_shutdown_clean", False),
            }
        )
        self.interval_var.set(str(self.settings["interval_seconds"]))
        self.timeout_var.set(str(self.settings["timeout_seconds"]))
        self.threshold_var.set(str(self.settings["degraded_latency_ms"]))
        self.min_ok_var.set(str(self.settings["minimum_ok_targets"]))
        self.system_threshold_var.set(str(self.settings["system_alert_threshold"]))
        self.slow_latency_alert_var.set(str(self.settings["slow_avg_latency_alert_ms"]))
        self.daily_summary_time_var.set(str(self.settings["daily_summary_time"]))
        save_settings(self.settings)
        self.next_run_ts = time.time() + self.settings["interval_seconds"]
        self._add_event_line(self._t("settings_saved"))
        self.status_var.set(f"{self._t('status')}: {self._t('settings_saved')}")

    def _trigger_manual_refresh(self) -> None:
        self.manual_refresh_pending = True
        self.manual_refresh_started_at = time.time()
        self.command_queue.put("manual_refresh")
        self.manual_refresh_var.set(self._t("manual_requested"))
        self.next_update_var.set(self._t("manual_requested"))
        self._add_event_line(self._t("manual_refresh_event"))
        for site, item_id in self.rows.items():
            current = self.tree.item(item_id, "values")
            self.tree.item(
                item_id,
                values=(site, self._t("checking"), current[2], current[3], current[4]),
                tags=("warn",),
            )

    def _play_test_sound(self) -> None:
        self._play_alert_sound()
        self._add_event_line(self._t("sound_test"))

    def _send_test_email(self) -> None:
        self._apply_settings()
        threading.Thread(
            target=self._send_email_worker,
            args=("TEST", "This is a test email from Network Watchdog.", False),
            daemon=True,
        ).start()

    def _play_alert_sound(self) -> None:
        if winsound is None:
            self._add_event_line("Sound alert skipped: winsound is unavailable")
            return
        try:
            winsound.Beep(1200, 300)
            winsound.Beep(900, 500)
        except RuntimeError:
            winsound.MessageBeep()

    def _classify_state(
        self,
        ok_count: int,
        total_count: int,
        avg_latency: int | None,
        slow_threshold: int,
        minimum_ok_targets: int,
    ) -> str:
        if ok_count == 0:
            return STATE_OFFLINE
        minimum_ok_targets = max(1, min(minimum_ok_targets, total_count))
        if ok_count < minimum_ok_targets:
            return STATE_SLOW
        if avg_latency is not None and avg_latency >= slow_threshold:
            return STATE_SLOW
        return STATE_NORMAL

    def _record_history_point(self, payload: dict) -> None:
        self.history_points.append(
            {
                "timestamp": payload["timestamp"],
                "label": datetime.fromtimestamp(payload["timestamp"]).strftime("%H:%M"),
                "avg_latency_ms": payload["avg_latency_ms"],
                "summary_state": payload["summary_state"],
            }
        )
        cutoff = time.time() - HISTORY_WINDOW_SECONDS
        self.history_points = [point for point in self.history_points if point["timestamp"] >= cutoff]
        self._draw_history_charts()

    def _draw_history_charts(self) -> None:
        for canvas in (getattr(self, "small_chart_canvas", None), getattr(self, "history_chart_canvas", None)):
            if canvas is not None:
                self._draw_history_chart(canvas)

    def _draw_history_chart(self, canvas: tk.Canvas) -> None:
        dark_mode = self.current_theme == THEME_DARK
        background = "#1d2939" if dark_mode else "#fcfcfd"
        border = "#344054" if dark_mode else "#d0d5dd"
        axis = "#98a2b3"
        grid = "#344054" if dark_mode else "#eaecf0"
        muted = "#d0d5dd" if dark_mode else "#667085"
        width = max(260, canvas.winfo_width())
        height = max(160, canvas.winfo_height())
        canvas.delete("all")
        canvas.create_rectangle(0, 0, width, height, fill=background, outline=border)
        left, right, top, bottom = 44, 16, 16, 32
        plot_width = width - left - right
        plot_height = height - top - bottom
        canvas.create_line(left, top, left, height - bottom, fill=axis)
        canvas.create_line(left, height - bottom, width - right, height - bottom, fill=axis)
        points = [p for p in self.history_points if p["avg_latency_ms"] is not None]
        if not points:
            canvas.create_text(width / 2, height / 2, text="No history yet", fill=muted, font=("Segoe UI", 10))
            return

        max_latency = max([p["avg_latency_ms"] for p in points] + [self._current_slow_state_threshold(), 100])
        start_ts = time.time() - HISTORY_WINDOW_SECONDS
        end_ts = time.time()
        for i in range(4):
            y = top + i * (plot_height / 3)
            value = int(max_latency - (max_latency * i / 3))
            canvas.create_line(left, y, width - right, y, fill=grid)
            canvas.create_text(24, y, text=str(value), fill=muted, font=("Segoe UI", 8))

        threshold_y = top + plot_height - (min(self._current_slow_state_threshold(), max_latency) / max_latency * plot_height)
        canvas.create_line(left, threshold_y, width - right, threshold_y, fill="#f79009", dash=(4, 3))
        canvas.create_text(width - right - 48, max(top + 10, threshold_y - 8), text=self._t("state_slow"), fill="#b54708", font=("Segoe UI", 8))

        line_points = []
        for point in points:
            x = left + (point["timestamp"] - start_ts) / (end_ts - start_ts) * plot_width
            y = top + plot_height - (point["avg_latency_ms"] / max_latency * plot_height)
            line_points.extend([x, y])
            fill = "#12b76a"
            if point["summary_state"] == STATE_SLOW:
                fill = "#f79009"
            elif point["summary_state"] == STATE_OFFLINE:
                fill = "#f04438"
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=fill, outline=fill)
        if len(line_points) >= 4:
            canvas.create_line(*line_points, fill="#1570ef", width=2, smooth=True)
        canvas.create_text(left, height - 14, text="-6h", fill=muted, font=("Segoe UI", 8))
        canvas.create_text(width - right - 18, height - 14, text="now", fill=muted, font=("Segoe UI", 8))

    def _handle_alert_transition(self, payload: dict) -> None:
        current_state = payload["summary_state"]
        initial_transition = False
        if self.last_alert_state == "INIT":
            if current_state == STATE_NORMAL:
                self.last_alert_state = current_state
                self._add_event_line(f"Initial state: {current_state}")
                return
            initial_transition = True
            self._add_event_line(f"Initial state alert: {current_state}")
        if not initial_transition and current_state == self.last_alert_state:
            return

        avg_latency = payload["avg_latency_ms"]
        latency_text = avg_latency if avg_latency is not None else "-"
        message = (
            f"State changed to {self._state_text(current_state)}. Success rate {payload['success_rate']}%, "
            f"average latency {latency_text} ms."
        )
        self._add_event_line(message)

        if current_state in {STATE_SLOW, STATE_OFFLINE}:
            if self.sound_alert_var.get():
                self._play_alert_sound()
            if self.popup_alert_var.get():
                self.root.after(0, lambda: self._show_alert_popup(message))
            if self.tray_icon is not None:
                try:
                    self.tray_icon.notify(message, APP_TITLE)
                except Exception:
                    pass
        self.last_alert_state = current_state

    def _show_alert_popup(self, message: str) -> None:
        if messagebox is None:
            return
        if self.popup_alert_open:
            self._add_event_line(self._t("popup_skipped"))
            return
        self.popup_alert_open = True
        try:
            messagebox.showwarning(APP_TITLE, message)
        finally:
            self.popup_alert_open = False

    def _handle_down_alert(self, payload: dict) -> None:
        if payload.get("summary_state") == STATE_OFFLINE:
            self.down_alert_streak += 1
        else:
            self.down_alert_streak = 0
            self.down_alert_active = False
            return

        if self.down_alert_streak < DEFAULT_DOWN_ALERT_STREAK or self.down_alert_active:
            return
        if not self.email_alert_var.get():
            return

        message = (
            f"All configured targets are unreachable. "
            f"Down streak {self.down_alert_streak}, success rate {payload['success_rate']}%, "
            f"average latency {payload['avg_latency_ms'] if payload['avg_latency_ms'] is not None else '-'} ms."
        )
        threading.Thread(
            target=self._send_email_worker,
            args=(STATE_OFFLINE, message, True),
            daemon=True,
        ).start()
        self._add_event_line(message)
        self.down_alert_active = True

    def _handle_system_alert(self, payload: dict) -> None:
        metrics = payload.get("system_metrics", {})
        if not metrics.get("available"):
            return
        threshold = self._current_system_threshold()
        high_items = []
        if metrics["cpu"] >= threshold:
            high_items.append(f"CPU {metrics['cpu']}%")
        if metrics["memory"] >= threshold:
            high_items.append(f"Memory {metrics['memory']}%")
        if metrics["disk_c"] >= threshold:
            high_items.append(f"C drive {metrics['disk_c']}%")
        active = bool(high_items)
        if active:
            self.system_alert_streak += 1
        else:
            self.system_alert_streak = 0
            self.last_system_alert_active = False
            return

        if (
            active
            and not self.last_system_alert_active
            and self.system_alert_streak >= DEFAULT_SYSTEM_ALERT_STREAK
            and self.email_alert_var.get()
        ):
            message = self._t("system_alert_message", items=", ".join(high_items))
            threading.Thread(
                target=self._send_email_worker,
                args=(self._t("system_alert_subject"), message, True),
                daemon=True,
            ).start()
            self._add_event_line(message)
        self.last_system_alert_active = active

    def _handle_slow_latency_alert(self, payload: dict) -> None:
        avg_latency = payload.get("avg_latency_ms")
        threshold = self._current_slow_latency_alert_threshold()
        if avg_latency is not None and avg_latency >= threshold:
            self.slow_latency_alert_streak += 1
        else:
            self.slow_latency_alert_streak = 0
            self.slow_latency_alert_active = False
            return

        if self.slow_latency_alert_streak < DEFAULT_SLOW_ALERT_STREAK or self.slow_latency_alert_active:
            return
        if not self.email_alert_var.get():
            return

        message = self._t("slow_network_message", latency=avg_latency)
        threading.Thread(
            target=self._send_email_worker,
            args=(self._t("slow_network_subject"), message, True),
            daemon=True,
        ).start()
        self._add_event_line(message)
        self.slow_latency_alert_active = True

    def _check_updates_now(self) -> None:
        if self.update_check_in_progress:
            return
        self.update_check_in_progress = True
        self.update_status_var.set(self._t("update_checking"))
        threading.Thread(target=self._update_check_worker, daemon=True).start()

    def _update_check_worker(self) -> None:
        req = request.Request(
            LATEST_RELEASE_API,
            headers={
                "User-Agent": f"network-watchdog/{APP_VERSION}",
                "Accept": "application/vnd.github+json",
            },
        )
        try:
            context = create_https_ssl_context()
            with request.urlopen(req, timeout=15, context=context) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.update_queue.put({"type": "release", "ok": True, "payload": payload})
        except Exception as exc:
            self.update_queue.put({"type": "release", "ok": False, "error": str(exc)})

    def _apply_update_payload(self, payload: dict) -> None:
        self.update_check_in_progress = False
        if not payload.get("ok"):
            self.update_status_var.set(self._t("update_failed", error=payload.get("error", "unknown error")))
            return

        release = payload["payload"]
        self.latest_release_info = release
        tag_name = str(release.get("tag_name", "")).strip() or "-"
        self.latest_version_var.set(tag_name)
        self.update_published_var.set(str(release.get("published_at", "-")))

        current_version = parse_version_tag(APP_VERSION)
        latest_version = parse_version_tag(tag_name)
        if latest_version > current_version:
            self.update_status_var.set(self._t("update_available", version=tag_name))
            self._add_event_line(f"Update available: {tag_name}")
        else:
            self.update_status_var.set(self._t("update_up_to_date"))

        if hasattr(self, "update_assets_tree"):
            for item_id in self.update_assets_tree.get_children():
                self.update_assets_tree.delete(item_id)
            for asset in release.get("assets", []):
                self.update_assets_tree.insert(
                    "",
                    tk.END,
                    values=(
                        asset.get("name", "-"),
                        format_size_bytes(asset.get("size")),
                        asset.get("browser_download_url", "-"),
                    ),
                )

    def _open_selected_update_download(self) -> None:
        if not hasattr(self, "update_assets_tree"):
            return
        selected = self.update_assets_tree.selection()
        if not selected:
            self.status_var.set(self._t("update_no_selection"))
            return
        values = self.update_assets_tree.item(selected[0], "values")
        if len(values) < 3:
            return
        url = str(values[2]).strip()
        if url and url != "-":
            webbrowser.open(url)

    def _send_email_worker(self, alert_type: str, message: str, count_as_alert: bool) -> None:
        recipients = self._recipients()
        if not recipients:
            self.root.after(0, lambda: self.status_var.set(self._t("no_recipient")))
            return

        smtp_host = self.smtp_host_var.get().strip() or DEFAULT_SMTP_HOST
        sender_email = self.sender_email_var.get().strip()
        auth_code = self.auth_code_var.get().strip()
        if not smtp_host or not sender_email or not auth_code:
            self.root.after(0, lambda: self.status_var.set(self._t("mail_missing")))
            return
        if not is_valid_email_address(sender_email):
            self.root.after(0, lambda: self.status_var.set(self._t("sender_invalid")))
            return

        try:
            email_message = EmailMessage()
            email_message["Subject"] = f"[{APP_TITLE}] {alert_type}"
            email_message["From"] = f"{self.sender_name_var.get().strip() or APP_TITLE} <{sender_email}>"
            email_message["To"] = ", ".join(recipients)
            email_message.set_content(
                "\n".join(
                    [
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        f"Alert type: {alert_type}",
                        message,
                    ]
                )
            )
            used_route = self._send_message_via_auto_smtp(
                smtp_host, sender_email, auth_code, email_message
            )
            if count_as_alert:
                self.root.after(0, self._increment_email_alert_counter)
            self.root.after(
                0,
                lambda: self.status_var.set(
                    self._t("email_sent", recipients=", ".join(recipients))
                ),
            )
            self.root.after(0, lambda: self._add_event_line(f"Email sent: {alert_type} via {used_route}"))
        except Exception as exc:
            error_message = str(exc)
            self.root.after(0, lambda: self.status_var.set(self._t("email_failed", error=error_message)))
            self.root.after(0, lambda: self._add_event_line(f"Email failed: {error_message}"))

    def _send_message_via_auto_smtp(
        self,
        smtp_host: str,
        sender_email: str,
        auth_code: str,
        email_message: EmailMessage,
    ) -> str:
        routes = []
        configured_port = self._parse_positive_int(str(self.settings.get("smtp_port", DEFAULT_SMTP_PORT)), DEFAULT_SMTP_PORT)
        routes.append((smtp_host, configured_port))
        for port in (465, 587):
            if (smtp_host, port) not in routes:
                routes.append((smtp_host, port))
        for port in (465, 587):
            if (DEFAULT_SMTP_HOST, port) not in routes:
                routes.append((DEFAULT_SMTP_HOST, port))

        context = create_https_ssl_context()
        errors = []
        for host, port in routes:
            try:
                if port == 465:
                    with smtplib.SMTP_SSL(host, port, context=context, timeout=20) as server:
                        server.ehlo()
                        login_smtp_with_auth_code(server, sender_email, auth_code)
                        server.send_message(email_message)
                else:
                    with smtplib.SMTP(host, port, timeout=20) as server:
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        login_smtp_with_auth_code(server, sender_email, auth_code)
                        server.send_message(email_message)
                self.settings["smtp_host"] = host
                self.settings["smtp_port"] = port
                save_settings(self.settings)
                return f"{host}:{port}"
            except Exception as exc:
                errors.append(f"{host}:{port} {type(exc).__name__}: {exc}")
        raise RuntimeError(" | ".join(errors[-3:]))

    def _append_csv_log(self, payload: dict) -> None:
        metrics = payload.get("system_metrics", {})
        timestamp = payload["checked_at"]
        with LOG_PATH.open("a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            for result in payload["results"]:
                writer.writerow(
                    [
                        timestamp,
                        result["site"],
                        result["status"],
                        result["latency_ms"] if result["latency_ms"] is not None else "",
                        result["detail"],
                        payload["summary_state"],
                        payload["success_rate"],
                        metrics.get("cpu", ""),
                        metrics.get("memory", ""),
                        metrics.get("disk_c", ""),
                    ]
                )

    def _add_event_line(self, text: str) -> None:
        line = f"{datetime.now().strftime('%H:%M:%S')}  {text}"
        self.event_lines.append(line)
        self.event_lines = self.event_lines[-120:]
        if hasattr(self, "event_list"):
            self.event_list.delete(0, tk.END)
            for item in reversed(self.event_lines[-18:]):
                self.event_list.insert(tk.END, item)

    def _refresh_email_alert_count_label(self) -> None:
        self._normalize_daily_counter()
        count = int(self.settings.get("email_alert_count_today", 0))
        self.email_alert_count_var.set(f"{self._t('today_alerts')}: {count}")

    def _increment_email_alert_counter(self) -> None:
        self._normalize_daily_counter()
        self.settings["email_alert_count_today"] = int(self.settings.get("email_alert_count_today", 0)) + 1
        save_settings(self.settings)
        self._refresh_email_alert_count_label()

    def _refresh_environment_checks(self) -> None:
        self.dependency_checks = check_environment()
        self.tray_available = pystray is not None and Image is not None and ImageDraw is not None
        if self.tray_available and self.tray_icon is None and self.startup_complete:
            self._setup_tray()

        if hasattr(self, "environment_tree"):
            self.environment_tree.delete(*self.environment_tree.get_children())
            for check in self.dependency_checks:
                tag = "ok"
                if check.status != "OK" and check.required:
                    tag = "missing_required"
                elif check.status != "OK":
                    tag = "missing_optional"
                self.environment_tree.insert(
                    "",
                    tk.END,
                    values=(
                        check.name,
                        check.status,
                        self._t("yes") if check.required else self._t("no"),
                        check.detail,
                        check.install_hint,
                    ),
                    tags=(tag,),
                )

        optional_missing = [c for c in self.dependency_checks if not c.required and c.status != "OK"]
        required_missing = missing_required_dependencies(self.dependency_checks)
        hints = []
        if optional_missing:
            hints.append("Optional install: python -m pip install -r requirements.txt")
        if required_missing:
            hints.append("Required fix: install Python 3.10+ with Tcl/Tk enabled.")
        if not hints:
            hints.append(self._t("env_good"))
        self.install_hint_var.set(" | ".join(hints))

        if "tray_button" in self.widgets:
            self.widgets["tray_button"].state(["!disabled"] if self.tray_available else ["disabled"])
        if "tray_check" in self.widgets:
            self.widgets["tray_check"].state(["!disabled"] if self.tray_available else ["disabled"])
            if not self.tray_available:
                self.minimize_on_close_var.set(False)

    def _show_environment_startup_notice(self) -> None:
        optional_missing = [c for c in self.dependency_checks if not c.required and c.status != "OK"]
        if not optional_missing:
            return
        summary = "\n".join(f"- {check.name}: {check.install_hint}" for check in optional_missing)
        messagebox.showinfo(
            APP_TITLE,
            f"{self._t('optional_missing_title')}\n\n{summary}\n\n{self._t('optional_missing_body')}",
        )

    def _recipients(self) -> list[str]:
        return [var.get().strip() for var in self.recipient_vars if var.get().strip()]

    def _parse_positive_int(self, raw_value: str, fallback: int) -> int:
        try:
            value = int(str(raw_value).strip())
            return value if value > 0 else fallback
        except ValueError:
            return fallback

    def _current_interval(self) -> int:
        return self._parse_positive_int(self.interval_var.get(), DEFAULT_INTERVAL_SECONDS)

    def _current_timeout(self) -> int:
        return self._parse_positive_int(self.timeout_var.get(), DEFAULT_TIMEOUT_SECONDS)

    def _current_threshold(self) -> int:
        return self._parse_positive_int(self.threshold_var.get(), DEFAULT_DEGRADED_LATENCY_MS)

    def _current_slow_state_threshold(self) -> int:
        return max(1, int(self._current_threshold() * 0.3))

    def _current_min_ok_targets(self) -> int:
        value = self._parse_positive_int(self.min_ok_var.get(), DEFAULT_MINIMUM_OK_TARGETS)
        return max(1, min(value, len(self.targets)))

    def _current_system_threshold(self) -> int:
        return self._parse_positive_int(self.system_threshold_var.get(), DEFAULT_SYSTEM_ALERT_THRESHOLD)

    def _current_slow_latency_alert_threshold(self) -> int:
        return self._parse_positive_int(
            self.slow_latency_alert_var.get(),
            DEFAULT_SLOW_AVG_LATENCY_ALERT_MS,
        )

    def _current_daily_summary_time(self) -> str:
        hour, minute = parse_daily_summary_time(self.daily_summary_time_var.get())
        return f"{hour:02d}:{minute:02d}"

    def _state_text(self, state: str) -> str:
        mapping = {
            STATE_NORMAL: self._t("state_normal"),
            STATE_SLOW: self._t("state_slow"),
            STATE_OFFLINE: self._t("state_offline"),
        }
        return mapping.get(state, state)

    def _power_status_text(self, power_metrics: dict | None = None) -> str:
        metrics = power_metrics or self.power_metrics
        if not metrics.get("supported"):
            return self._t("power_not_supported")
        if not metrics.get("has_battery"):
            return self._t("power_not_supported")
        if metrics.get("on_battery"):
            percent = metrics.get("percent")
            return f"{self._t('power_battery')} {percent if percent is not None else '-'}%"
        return self._t("power_ac")

    def _build_tray_image(self, state: str):
        color = TRAY_STATE_COLORS.get(state, TRAY_STATE_COLORS[STATE_NORMAL])
        image = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill=color)
        draw.ellipse((22, 22, 42, 42), fill="#ffffff")
        return image

    def _refresh_tray_icon_state(self, state: str) -> None:
        if self.tray_icon is None or not self.tray_available:
            return
        try:
            self.tray_icon.icon = self._build_tray_image(state)
            self.tray_icon.title = f"{APP_TITLE} - {self._state_text(state)}"
            self.tray_icon.update_menu()
        except Exception:
            pass

    def _mark_run_started(self) -> None:
        abnormal_shutdown = not bool(self.settings.get("last_shutdown_clean", True))
        self.settings["last_shutdown_clean"] = False
        save_settings(self.settings)
        if abnormal_shutdown and self.email_alert_var.get() and self.power_metrics.get("has_battery"):
            threading.Thread(
                target=self._send_email_worker,
                args=(self._t("abnormal_shutdown_subject"), self._t("abnormal_shutdown_message"), True),
                daemon=True,
            ).start()

    def _mark_run_clean_exit(self) -> None:
        self.settings["last_shutdown_clean"] = True
        save_settings(self.settings)

    def _handle_power_alert(self, payload: dict) -> None:
        power_metrics = payload.get("power_metrics", {})
        active = bool(power_metrics.get("has_battery")) and bool(power_metrics.get("on_battery"))
        if not active:
            self.last_power_alert_active = False
            return
        if self.last_power_alert_active or not self.email_alert_var.get():
            return
        battery_value = power_metrics.get("percent")
        message = self._t("power_alert_message", battery=battery_value if battery_value is not None else "-")
        threading.Thread(
            target=self._send_email_worker,
            args=(self._t("power_alert_subject"), message, True),
            daemon=True,
        ).start()
        self._add_event_line(message)
        self.last_power_alert_active = True

    def _check_daily_summary(self, payload: dict) -> None:
        if not self.daily_summary_var.get():
            return
        now = datetime.now()
        target_hour, target_minute = parse_daily_summary_time(self.daily_summary_time_var.get())
        if (now.hour, now.minute) < (target_hour, target_minute):
            return
        today_key = now.date().isoformat()
        if self.settings.get("last_daily_summary_sent_date") == today_key:
            return
        message = self._build_daily_summary_message(today_key, payload)
        threading.Thread(
            target=self._send_email_worker,
            args=(self._t("daily_summary_subject"), message, False),
            daemon=True,
        ).start()
        self.settings["last_daily_summary_sent_date"] = today_key
        save_settings(self.settings)
        self._add_event_line(f"Daily summary email queued for {today_key}")

    def _build_daily_summary_message(self, day_text: str, payload: dict | None = None) -> str:
        checks = 0
        state_counts = {STATE_NORMAL: 0, STATE_SLOW: 0, STATE_OFFLINE: 0}
        avg_values: list[float] = []
        min_latency: int | None = None
        max_latency: int | None = None
        if LOG_PATH.exists():
            try:
                with LOG_PATH.open("r", encoding="utf-8", newline="") as file:
                    reader = csv.DictReader(file)
                    grouped: dict[str, dict] = {}
                    for row in reader:
                        timestamp = str(row.get("timestamp", "")).strip()
                        if not timestamp.startswith(day_text):
                            continue
                        summary_state = str(row.get("summary_state", "")).strip() or STATE_NORMAL
                        if summary_state == "DEGRADED":
                            summary_state = STATE_SLOW
                        elif summary_state == "DOWN":
                            summary_state = STATE_OFFLINE
                        latency_raw = str(row.get("latency_ms", "")).strip()
                        grouped.setdefault(timestamp, {"state": summary_state, "latencies": []})
                        if latency_raw:
                            try:
                                latency_value = int(float(latency_raw))
                                grouped[timestamp]["latencies"].append(latency_value)
                            except ValueError:
                                pass
                    checks = len(grouped)
                    for item in grouped.values():
                        state = item["state"]
                        if state in state_counts:
                            state_counts[state] += 1
                        latencies = item["latencies"]
                        if latencies:
                            batch_avg = sum(latencies) / len(latencies)
                            avg_values.append(batch_avg)
                            batch_min = min(latencies)
                            batch_max = max(latencies)
                            min_latency = batch_min if min_latency is None else min(min_latency, batch_min)
                            max_latency = batch_max if max_latency is None else max(max_latency, batch_max)
            except Exception:
                pass
        external_ip = (payload or {}).get("external_ip", self.external_ip_info)
        country_text = localize_country_name(
            external_ip.get("country_raw") or external_ip.get("country"),
            external_ip.get("country_code"),
            self.language,
        )
        average_latency = int(sum(avg_values) / len(avg_values)) if avg_values else "-"
        return self._t(
            "daily_summary_message",
            date=day_text,
            checks=checks,
            normal=state_counts[STATE_NORMAL],
            slow=state_counts[STATE_SLOW],
            offline=state_counts[STATE_OFFLINE],
            avg_latency=average_latency,
            min_latency=min_latency if min_latency is not None else "-",
            max_latency=max_latency if max_latency is not None else "-",
            alert_count=int(self.settings.get("email_alert_count_today", 0)),
            external_ip=external_ip.get("ip", "-"),
            country=country_text,
        )

    def _on_language_changed(self, _event: object = None) -> None:
        selected = self.language_var.get()
        self.language = "zh" if selected == TEXT["zh"]["language_name"] else "en"
        self.settings["language"] = self.language
        save_settings(self.settings)
        if self.external_ip_info:
            self.external_ip_info["country"] = localize_country_name(
                self.external_ip_info.get("country_raw") or self.external_ip_info.get("country"),
                self.external_ip_info.get("country_code"),
                self.language,
            )
        self._refresh_language_text()

    def _apply_theme(self) -> None:
        palette = {
            THEME_LIGHT: {
                "root_bg": "#f5f7fb",
                "panel_bg": "#eef2f6",
                "card_bg": "#fcfcfd",
                "text": "#101828",
                "muted": "#667085",
                "border": "#d0d5dd",
                "nav_active_bg": "#1570ef",
                "nav_active_fg": "#ffffff",
                "nav_idle_bg": "#ffffff",
                "nav_idle_fg": "#344054",
                "list_bg": "#ffffff",
            },
            THEME_DARK: {
                "root_bg": "#101828",
                "panel_bg": "#182230",
                "card_bg": "#1d2939",
                "text": "#f8fafc",
                "muted": "#98a2b3",
                "border": "#344054",
                "nav_active_bg": "#175cd3",
                "nav_active_fg": "#ffffff",
                "nav_idle_bg": "#182230",
                "nav_idle_fg": "#d0d5dd",
                "list_bg": "#1d2939",
            },
        }[self.current_theme]
        style = ttk.Style()
        if self.current_theme == THEME_DARK and "clam" in style.theme_names():
            style.theme_use("clam")
        elif self.current_theme == THEME_LIGHT and "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure(".", background=palette["root_bg"], foreground=palette["text"])
        style.configure("TFrame", background=palette["root_bg"])
        style.configure("TLabel", background=palette["root_bg"], foreground=palette["text"])
        style.configure("TCheckbutton", background=palette["root_bg"], foreground=palette["text"])
        style.configure("TNotebook", background=palette["root_bg"])
        style.configure("TNotebook.Tab", padding=(18, 8), font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", background=palette["card_bg"], fieldbackground=palette["card_bg"], foreground=palette["text"])
        style.configure("Treeview.Heading", background=palette["panel_bg"], foreground=palette["text"])
        self.root.configure(bg=palette["root_bg"])
        nav = self.widgets.get("nav_frame")
        if nav is not None:
            nav.configure(bg=palette["panel_bg"])
        for canvas_name in ("small_chart_canvas", "history_chart_canvas"):
            canvas = getattr(self, canvas_name, None)
            if canvas is not None:
                canvas.configure(bg=palette["card_bg"], highlightbackground=palette["border"])
        if hasattr(self, "event_list"):
            self.event_list.configure(
                bg=palette["list_bg"],
                fg=palette["text"],
                highlightbackground=palette["border"],
                selectbackground=palette["nav_active_bg"],
                selectforeground=palette["nav_active_fg"],
            )
        self._draw_history_charts()
        self._update_nav_state()

    def _tick_theme(self) -> None:
        detected_theme = current_system_theme()
        if detected_theme != self.current_theme:
            self.current_theme = detected_theme
            self._apply_theme()
        self.root.after(5000, self._tick_theme)

    def _hide_to_tray(self) -> None:
        if not self.tray_available or self.tray_icon is None:
            self.window_hidden = False
            self.status_var.set(self._t("tray_missing"))
            self._add_event_line("Hide to tray skipped: tray dependencies missing")
            return
        self.window_hidden = True
        self.root.withdraw()
        try:
            self.tray_icon.notify(self._t("tray_notice"), APP_TITLE)
        except Exception:
            pass

    def _show_from_tray(self) -> None:
        self.window_hidden = False
        self.root.after(0, self._show_window)

    def _show_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _on_minimize_event(self, _event: tk.Event) -> None:
        if self.closing:
            return
        if self.root.state() == "iconic" and self.tray_available:
            self._hide_to_tray()

    def _on_close_request(self) -> None:
        if self.minimize_on_close_var.get() and self.tray_available:
            self._hide_to_tray()
            return
        self._exit_app()

    def _tray_show_window(self, _icon: object, _item: object) -> None:
        self._show_from_tray()

    def _tray_refresh_now(self, _icon: object, _item: object) -> None:
        self.root.after(0, self._trigger_manual_refresh)

    def _tray_exit_app(self, _icon: object, _item: object) -> None:
        self.root.after(0, self._exit_app)

    def _exit_app(self) -> None:
        self.closing = True
        self.stop_event.set()
        self._mark_run_clean_exit()
        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.destroy()


def main() -> None:
    checks = check_environment()
    required_missing = missing_required_dependencies(checks)
    if required_missing:
        print(f"{APP_TITLE} cannot start because required environment items are missing.")
        for check in required_missing:
            print(f"- {check.name}: {check.detail}")
            print(f"  Fix: {check.install_hint}")
        input("Press Enter to exit...")
        return

    mutex_handle = acquire_single_instance_mutex()
    if mutex_handle is None:
        if tk is not None and messagebox is not None:
            temp_root = tk.Tk()
            temp_root.withdraw()
            try:
                messagebox.showinfo(APP_TITLE, tr("en", "already_running"))
            finally:
                temp_root.destroy()
        else:
            print("Network Watchdog is already running.")
        return

    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    style.configure("TNotebook.Tab", padding=(18, 8), font=("Segoe UI", 10, "bold"))
    NetworkWatchdogApp(root)
    try:
        root.mainloop()
    finally:
        if platform.system() == "Windows" and isinstance(mutex_handle, int):
            try:
                ctypes.windll.kernel32.CloseHandle(mutex_handle)
            except Exception:
                pass


if __name__ == "__main__":
    main()
