# Python examples

## Requirements for the Python examples

They use the hidapi, so please install that.

```pip install hidapi```

In Python you can find at least two HID implementations.
Therefore you might need to uninstall the other HID module as well if you had that installed earlier.

```pip uninstall hid```

Need to install the [udev](../../udev/README.md) rules as well to allow non-root access.


## [RunLight.py](RunLight.py)
Shows a moving light from left to right and vice versa. Quite similar to my very first mockup.


## [SimpleReceiver.py](SimpleReceiver.py)
A very simple receiver, just enough to show the basics.
After starting it, send some IR-Remote commands from the Remote and you can see the data printed.
Read the data in endless loop
```
0x15 0xf 0x423 0x0 rc_core:  0x800f0423
0x15 0xf 0x423 0x1 rc_core:  0x800f0423
```
## [ReceiveAndSend.py](ReceiveAndSend.py)
Still a simple receiver, but at certein keys it send sweeps to the Neopixels.

# USB Sniffer tool
This free RP2040 based [USB sniffer](https://github.com/ataradov/usb-sniffer-lite) helped me with debugging. Thanks to Alex Taradov for providing this wonderfull tool.