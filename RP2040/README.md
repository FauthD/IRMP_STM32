## IRMP on RP2040

For boards with the RP2040, e.g. the Raspberry Pi Pico and many others.  
This is additional information, basic information in https://github.com/j1rie/IRMP_STM32#readme.

## Flashing the firmware
Disconnect from USB.
Attach to USB while holding BOOTSEL button down, than release. The device will show up as a mass storage.
Drag and drop the firmware.uf2 file onto it. The device will reboot and start as an IRMP HID-Device.

Sending the "reboot" command brings device into mass storage state as well.

## First test
When you press the BOOTSEL button in suspend mode, the PC should wake up.  
For wiring see https://www.mikrocontroller.net/articles/IRMP_auf_STM32_-_Bauanleitung#Minimalistic_assembly_for_experienced_users  
https://www.mikrocontroller.net/articles/IRMP_auf_STM32_%E2%80%93_stark_vereinfachte_Bauanleitung#Solder_Cables  
https://www.mikrocontroller.net/articles/IRMP_auf_STM32_%E2%80%93_stark_vereinfachte_Bauanleitung#Connect_Cables

## Emulated Eeprom
Any configuration done by one of the configuration programs goes first into cache only. In order to save
those changes into flash permanently, you have to do an eeprom commit.
Exception: first wakeup is commited by firmware for backwards compability.

## Building from source
See [Getting Started with the Raspberry Pi Pico](https://rptl.io/pico-get-started)  
-> Get the SDK and examples  
-> Install the Toolchain  
->  Building "Blink"  
->  Load and run "Blink"  

## Details
- Clone the repo (e.g. gh repo clone FauthD/IRMP_STM32)
- Either
  - Install picoSDK, toolchain and create an environment variable PICO_SDK_PATH that points to the SDK (recommended).
  - Clone the pico SDK into the local clone of my repo.
- Navigate to RP2040 directory inside the local clone.
- Delete or rename the directory build.
- run bash make.sh (takes a while).
- Find the result in IRMP_STM32/RP2040/build/*.uf2
- Download to the pico with the known methods.

## Using Neopixel leds for all kinds of purposes
This is an extension to the original IRMP design and for the RP2040 only so far.

### Testing with existing tools

There is a nice tool to test hidraw devices called hidapitester. Unfortunatelly it is not in the repos of Ubuntu (Suse,Redhat, ... not tested).

[Prebuilt binaries can be found there](https://github.com/todbot/hidapitester/releases)

See how to build it in their README.me on [Github](https://github.com/todbot/hidapitester), it is a fairly simple process.

After building it is recommended to place it in the /usr/local/bin directory for easier use.

`sudo cp hidapitester /usr/local/bin/`

### Turn all 8 leds to blue
`hidapitester --vidpid 1209:4444 --open --send-output 3,11,8,0,0,200,0,0,0,200,0,0,0,200,0,0,0,200,0,0,0,200,0,0,0,200,0,0,0,200,0,0,0,200,0,0 `

The bove is one single line.

The payload consists of:
| Index | Description |
| :----: | :----: |
| 0 | Report ID (3) |
| 1 | CMD (0xb or dec 11) |
| 2 | pixel count (4 bytes each pixel) only 8 is tested |
| 3 | unused, ignored recommended is to send 0 |
| 4..63 | payload, 4 bytes per pixel |

#### Note: one pixel consists of 4 bytes.
| Index | Description |
| :----: | :----: |
| W | unused for RGB (actually BGR) leds like the WS2812 (B) |
| B | blue (0..255) |
| R | red (0..255) |
| G | green (0..255) |

So the "0,200,0,0" sequences in the above example are for one blue pixel.

### One more example
`hidapitester --vidpid 1209:4444 --open --send-output 3,11,8,0,0,0,100,0,0,0,0,100,0,100,0,0,0,100,100,0,0,100,100,100,0,10,10,10,0,0,30,30,0,0,20,0 `

It produces thesde colores: red,green,blue,magenta,white,dark wite, dark green-yellow, dark red

