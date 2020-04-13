from enum import Enum

import attr
import toml
from attr.converters import optional
from attr.validators import instance_of


DEFAULT_EMAIL_SUBJECT = "[dhcp-notify] DHCP Lease Notification"


class ConfigError(Exception):
    pass


class SMTPTLSConfig(Enum):
    tls = "tls"
    starttls = "starttls"
    off = "off"


class ConfigBase:
    @classmethod
    def from_dict(cls, cfg):
        config_values = {}
        missing = []

        for field in attr.fields(cls):
            if field.name in cfg:
                config_values[field.name] = cfg[field.name]
            elif field.default is attr.NOTHING:
                missing.append(field.name)

        if missing:
            missing = ", ".join(missing)
            raise ConfigError(
                f"{cls.__name__}: missing values for required fields: {missing}"
            )

        return cls(**config_values)


@attr.s(frozen=True)
class Credentials(ConfigBase):
    username = attr.ib(validator=instance_of(str))
    password = attr.ib(validator=instance_of(str))


@attr.s(frozen=True)
class SMTPConfig(ConfigBase):
    host = attr.ib(validator=instance_of(str))
    port = attr.ib(default="465", validator=instance_of(str))
    tls = attr.ib(converter=SMTPTLSConfig, default="tls")
    credentials = attr.ib(converter=optional(Credentials.from_dict), default=None)


@attr.s(frozen=True)
class MessageConfig(ConfigBase):
    from_addr = attr.ib(validator=instance_of(str))
    to_addr = attr.ib(validator=instance_of(str))
    subject = attr.ib(default=DEFAULT_EMAIL_SUBJECT, validator=instance_of(str))


@attr.s(frozen=True)
class Config(ConfigBase):
    smtp = attr.ib(converter=SMTPConfig.from_dict)
    message = attr.ib(converter=MessageConfig.from_dict)
    ignore_macs = attr.ib(
        factory=tuple, converter=lambda l: tuple(s.lower() for s in l)
    )
    ignore_actions = attr.ib(
        factory=tuple, converter=lambda l: tuple(s.lower() for s in l)
    )


def load(config_path):
    config = toml.load(config_path)
    return Config.from_dict(config)
