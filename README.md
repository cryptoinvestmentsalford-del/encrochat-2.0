# Platinum Secure Flasher

A secure device flashing tool with hardening and license management for Pixel devices 6+ and GrapheneOS.

## Features

- **Device Flashing**: Flash GrapheneOS to supported Pixel devices
- **License Management**: UUID-based licensing system
- **Device Hardening**: Apply security configurations and anti-debugging measures
- **Pixel Support**: All Pixel models 6 and up
- **GrapheneOS Compatible**: Optimized for GrapheneOS images

## Supported Devices

- Google Pixel 6 (oriole)
- Google Pixel 6 Pro (raven)
- Google Pixel 6a (bluejay)
- Google Pixel 7 (panther)
- Google Pixel 7 Pro (cheetah)
- Google Pixel 7a (lynx)
- Google Pixel 8 (shiba)
- Google Pixel 8 Pro (husky)
- Google Pixel 8a (akita)

## Requirements

- Python 3.8+
- Android SDK Platform Tools (ADB/Fastboot)
- Windows 10/11
- USB Debugging enabled on target device
- Unlocked bootloader

## Installation

1. Run `setup.bat` to configure the environment
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run `python platinum_secure_flasher.py` to start the application

## Building Executable

Run `build.bat` to create a standalone executable using PyInstaller.

## Usage

### Flash Device
1. Connect your Pixel device with USB debugging enabled
2. Select "Flash Device" tab
3. Choose GrapheneOS image or custom ROM
4. Click "Start Flash" to begin the process

### License Management
1. Go to "License" tab
2. Generate new UUID licenses
3. Import/export license files
4. View license database

### Device Hardening
1. Select "Hardening" tab
2. Apply anti-debugging measures
3. Enable lockdown scripts
4. Configure security settings

## Security Features

- UUID-based device licensing
- Anti-debugging protection
- Emergency lockdown scripts
- Secure boot verification
- Root detection
- Developer options lockdown

## License

This software is licensed under a proprietary license. Unauthorized distribution is prohibited.

## Support

For technical support and updates, contact the development team.

## Changelog

### v1.0.0
- Initial release
- Basic flashing functionality
- License management system
- Device hardening features
- Support for Pixel 6+ devices
- GrapheneOS compatibility