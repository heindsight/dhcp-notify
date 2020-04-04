"""Send notifications of dnsmasq dhcp events via email."""
import sys

from . import config, email_notify


__version__ = "0.0.1.dev0"

CONFIG_PATH = "/etc/dhcp_notify.toml"


def main(args=None):
    args=args or sys.argv[1:]
    cfg = config.load(CONFIG_PATH)
    process_event(args, cfg)


def process_event(args, cfg):
    action, mac, *_ = args

    if mac.lower() in cfg.ignore_macs:
        print(f"Ignoring {action} event for MAC address {mac}", file=sys.stderr)
        return

    notify_text = " ".join(args)
    msg = email_notify.make_email(msg_config=cfg.message, msg_text=notify_text)
    email_notify.send_email(smtp_config=cfg.smtp, message=msg)
