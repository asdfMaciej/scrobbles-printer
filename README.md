# Print last.fm scrobbles in real time!

### Installation
The application has been tested under Windows 10 under Python 3.7.4. 

1. Install the required packages: ```pip install python-escpos requests```
2. Change the last.fm API key, USB serial port and usernames in the script.
3. Launch the script. Initial scrobbles should print even if no music is currently being played.

### Known issues

The application doesn't work under WSL2 due to [lack of support for access to USB devices](https://github.com/microsoft/WSL/issues/5158). It might work under Windows 11 due to a [recent update](https://devblogs.microsoft.com/commandline/connecting-usb-devices-to-wsl/).

[Install LibUsb](https://github.com/pyusb/pyusb/issues/120#issuecomment-324966927) if you're getting a "No backend available" error.

If you're getting the "NotImplementedError: detach_kernel_driver" error, follow [this blog post](https://nyorikakar.medium.com/printing-with-python-and-epson-pos-printer-fbd17e127b6c) to fix it.

### License

This project is licensed under Apache License 2.0.
