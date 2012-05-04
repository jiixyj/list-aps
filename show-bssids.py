#!/usr/bin/env python
import dbus

bus = dbus.SystemBus()

proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
manager = dbus.Interface(proxy, "org.freedesktop.NetworkManager")

devices = manager.GetDevices()
for d in devices:
    dev_proxy = bus.get_object("org.freedesktop.NetworkManager", d)
    prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")

    # Make sure the device is enabled before we try to use it
    state = prop_iface.Get("org.freedesktop.NetworkManager.Device", "State")
    if state <= 2:
        continue

    # Get device's type; we only want wifi devices
    iface = prop_iface.Get("org.freedesktop.NetworkManager.Device", "Interface")
    dtype = prop_iface.Get("org.freedesktop.NetworkManager.Device", "DeviceType")
    if dtype == 2:   # WiFi
        # Get a proxy for the wifi interface
        wifi_iface = dbus.Interface(dev_proxy, "org.freedesktop.NetworkManager.Device.Wireless")
        wifi_prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")

        # Get all APs the card can see
        aps = wifi_iface.GetAccessPoints()
        for path in aps:
            ap_proxy = bus.get_object("org.freedesktop.NetworkManager", path)
            ap_prop_iface = dbus.Interface(ap_proxy, "org.freedesktop.DBus.Properties")

            bssid = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "HwAddress")
            strength = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "Strength")

            print bssid, int(strength)
