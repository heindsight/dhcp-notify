.PHONY: install uninstall

PREFIX?=/usr/local
BINDIR="$(PREFIX)/bin"
ETCDIR=/etc

SCRIPT=src/dhcp_notify
CONFIG=etc/dhcp_notify

install:
	install -t $(BINDIR) $(SCRIPT)
	install -t $(ETCDIR) -m 600 $(CONFIG)


uninstall:
	rm -f $(BINDIR)/dhcp_notify $(ETCDIR)/dhcp_notify
