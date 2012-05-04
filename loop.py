#!/usr/bin/env python

import dbus
import sys
try:
    import gobject
except ImportError:
    from gi.repository import GObject
    gobject = GObject
import functools
from dbus.mainloop.glib import DBusGMainLoop


WPAS_DBUS_SERVICE = "fi.epitest.hostap.WPASupplicant"
WPAS_DBUS_INTERFACE = "fi.epitest.hostap.WPASupplicant"
WPAS_DBUS_OPATH = "/fi/epitest/hostap/WPASupplicant"

WPAS_DBUS_INTERFACES_INTERFACE = "fi.epitest.hostap.WPASupplicant.Interface"
WPAS_DBUS_INTERFACES_OPATH = "/fi/epitest/hostap/WPASupplicant/Interfaces"
WPAS_DBUS_BSSID_INTERFACE = "fi.epitest.hostap.WPASupplicant.BSSID"

def scan_results_handler(bus, iface):
	res = iface.scanResults()

	print "Scanned wireless networks:"
	for opath in res:
		net_obj = bus.get_object(WPAS_DBUS_SERVICE, opath)
		net = dbus.Interface(net_obj, WPAS_DBUS_BSSID_INTERFACE)
		props = net.properties()

		# Convert the byte-array for SSID and BSSID to printable strings
		bssid = ""
		for item in props["bssid"]:
			bssid = bssid + ":%02x" % item
		bssid = bssid[1:]
		qual = props["quality"]

		print "%s quality=%d%%" % (bssid, qual)

	print
	iface.scan()


def main():
	if len(sys.argv) != 2:
		print "Usage: wpas-test.py <interface>"
		sys.exit(1)

	ifname = sys.argv[1]

	DBusGMainLoop(set_as_default=True)
	bus = dbus.SystemBus()
	wpas_obj = bus.get_object(WPAS_DBUS_SERVICE, WPAS_DBUS_OPATH)
	wpas = dbus.Interface(wpas_obj, WPAS_DBUS_INTERFACE)

	# See if wpa_supplicant already knows about this interface
	path = wpas.getInterface(ifname)

	if_obj = bus.get_object(WPAS_DBUS_SERVICE, path)
	iface = dbus.Interface(if_obj, WPAS_DBUS_INTERFACES_INTERFACE)

	bus.add_signal_receiver(
			functools.partial(scan_results_handler, bus, iface),
			signal_name='ScanResultsAvailable',
			dbus_interface=WPAS_DBUS_INTERFACES_INTERFACE,
			path=path)

	def start_mainloop():
		iface.scan()
		return False # start_mainloop should only be called once

	gobject.idle_add(start_mainloop)
	gobject.MainLoop().run()

if __name__ == "__main__":
	main()
