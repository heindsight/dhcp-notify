# DHCP Notify

A script to send notifications of `dnsmasq` dhcp events via email.

This script is meant to be run by [dnsmasq](http://www.thekelleys.org.uk/dnsmasq/doc.html), using
the `dhcp-script` option. It will send notifications of new, changed or destroyed dhcp leases via
email (using using the [mailgun](https://www.mailgun.com/) rest api).

## Installation

Download and extract a tarball or clone the git repo and run

    $ make install

This will install the script to `/usr/local/bin/dhcp_notify` by default and put the configuration
file at `/etc/dhcp_notify`.

You will need [curl](https://curl.haxx.se/) installed for email sending to work.

## Configuration

Before you can use the script you need to edit `/etc/dhcp_notify` and provide mailgun credentials,
mailgun base URL, and sender and recipient email addresses. See the comments in the default
configuration file for guidance.

Next you need to configure `dnsmasq` to run the script when leases are created, destroyed or
changed.  You can do this by providing the `dhcp-script` option to `dnsmasq` with the path to the
`dhcp_notify` scrip. You can either provide this in the `dnsmasq` configuration file (usually at
`/etc/dnsmasq.conf`) eg:

    dhcp-script=/usr/local/bin/dhcp_notify

or by passing `--dhcp-script` on the command line.

## Notes

Note that this script is not intended to be used with the `leasefile-ro` option option to `dnsmasq`.
