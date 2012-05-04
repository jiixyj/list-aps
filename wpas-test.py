#!/usr/bin/env python

import dbus
import sys, os
import time

WPAS_DBUS_SERVICE = "fi.epitest.hostap.WPASupplicant"
WPAS_DBUS_INTERFACE = "fi.epitest.hostap.WPASupplicant"
WPAS_DBUS_OPATH = "/fi/epitest/hostap/WPASupplicant"

WPAS_DBUS_INTERFACES_INTERFACE = "fi.epitest.hostap.WPASupplicant.Interface"
WPAS_DBUS_INTERFACES_OPATH = "/fi/epitest/hostap/WPASupplicant/Interfaces"
WPAS_DBUS_BSSID_INTERFACE = "fi.epitest.hostap.WPASupplicant.BSSID"

def main():
	if len(sys.argv) != 2:
		print "Usage: wpas-test.py <interface>"
		os._exit(1)

	ifname = sys.argv[1]

	bus = dbus.SystemBus()
	wpas_obj = bus.get_object(WPAS_DBUS_SERVICE, WPAS_DBUS_OPATH)
	wpas = dbus.Interface(wpas_obj, WPAS_DBUS_INTERFACE)

	# See if wpa_supplicant already knows about this interface
	path = None
	try:
		path = wpas.getInterface(ifname)
	except dbus.dbus_bindings.DBusException, exc:
		if str(exc) != "wpa_supplicant knows nothing about this interface.":
			raise exc
		try:
			path = wpas.addInterface(ifname, {'driver': dbus.Variant('wext')})
		except dbus.dbus_bindings.DBusException, exc:
			if str(exc) != "wpa_supplicant already controls this interface.":
				raise exc

	if_obj = bus.get_object(WPAS_DBUS_SERVICE, path)
	iface = dbus.Interface(if_obj, WPAS_DBUS_INTERFACES_INTERFACE)
	iface.scan()
	# Should really wait for the "scanResults" signal instead of sleeping
	# time.sleep(5)
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

if __name__ == "__main__":
	main()
