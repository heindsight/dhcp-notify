===========
DHCP Notify
===========

.. pull-quote::

    Email notifications of dnsmasq_ dhcp events.

.. image:: https://github.com/heindsight/dhcp-notify/workflows/Tests/badge.svg
    :target: https://github.com/heindsight/dhcp-notify/actions?query=workflow%3ATests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

Installation
------------

Download a zip archive from github and install using pip.  It is highly recommended to install
``dhcp-notify`` in a Python virtual environment. For example:

.. code-block:: shell

    $ sudo python3 -m venv /opt/dhcp-notify
    $ /opt/dhcp-notify/bin/pip install dhcp-notify.zip

Configuration
-------------

To configure the ``dhcp-notify`` script, make a copy of the `example
configuration file`_, edit it as needed and save it at ``/etc/dhcp_notify.toml``.

Next you need to configure ``dnsmasq`` to run the script when leases are
created, destroyed or changed.  You can do this by providing the ``dhcp-script``
option to ``dnsmasq`` with the path to the ``dhcp-notify`` script. You can
either provide this in the ``dnsmasq`` configuration file (usually at
``/etc/dnsmasq.conf``) e.g.:

.. code-block:: cfg

    dhcp-script=/opt/dhcp-notify/bin/dhcp-notify

or by passing ``--dhcp-script`` on the command line.

Notes
-----

Note that this script is not intended to be used with the ``leasefile-ro``
option option to ``dnsmasq``.

.. _dnsmasq: http://www.thekelleys.org.uk/dnsmasq/doc.html
.. _example configuration file: https://github.com/heindsight/dhcp-notify/blob/master/examples/dhcp_notify.toml
