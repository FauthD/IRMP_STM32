# udev rules to allow access by non root users

Copy the rules file 70-irmp.rules to to /etc/udev/rules.d
```
sudo cp 70-irmp.rules /etc/udev/rules.d
sudo touch /etc/udev/rules.d/70-irmp.rules
```

Note: This file is different from Jörgs original file.
The reason is that my python code uses the HidApi which finally uses the libusb as a backend by default (though you can change to use the hidraw backend).

See the discussion [hidapi](https://github.com/libusb/hidapi/discussions/657).
