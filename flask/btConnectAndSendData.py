import bluetooth
# https://github.com/huberf/Computer-to-Arduino-Bluetooth/blob/master/LightGUI.py
bd_addr = '00:20:10:08:19:FF'
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, 1))
sock.send("1")
sock.send("5")
sock.close()

#python3 -m pip install pybluez

nearby_devices = bluetooth.discover_devices()
