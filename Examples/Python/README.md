# Python examples

## Requirements for the Python examples

Need to install the [udev](../../udev/README.md) rules to allow non-root access.


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

## [Receiver.py](Receiver.py)
Still a simple receiver, but uses the irmplircd.map to translate keystrokes.

```
15000f042200 0 KEY_OK IRMP
15000f042200 1 KEY_OK IRMP
15000f040f00 0 KEY_INFO IRMP
15000f040f00 1 KEY_INFO IRMP
```

## [ReceiveAndSend.py](ReceiveAndSend.py)
Still a simple receiver, but at certein keys it send sweeps to the Neopixels.

## [IrmpSend.py](IrmpSend.py)
Sends IR codes via IRMP. This is not a full replacement of irsend, just a demonstrator.

Examples:
```
SEND_ONCE IRMP KEY_OK
```

Assumed there is a rc6.map file in the config directory, send the two codes with rc6.
```
SEND_ONCE rc6 KEY_OK KEY_ESC
```

## [Statusled.py](Statusled.py)
A simple status led changer for the IRMP.

Example: Change every 1 sec to red, off, yellow, off, green, off, green, off.
If there is no two color led connected (original project), you only see the green led blinking.

```
-t 1000 2 0 3 0 1 0 1 0
```

## [irmplircd.py](irmplircd.py)
An experimental daemon inspired by the original [irmplircd](https://github.com/realglotzi/irmplircd).

# USB Sniffer tool
This free RP2040 based [USB sniffer](https://github.com/ataradov/usb-sniffer-lite) helped me with debugging. Thanks to Alex Taradov for providing this wonderfull tool.