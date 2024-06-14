<h3 align="center">esptool-pyftdi</h3>

  <p align="center">
    esptool-pyftdi is a cross-platform alternative to <a href="https://github.com/jimparis/esptool-ftdi">esptool-ftdi</a>
    <br />
    <br />
    <a href="https://github.com/snake-4/esptool-pyftdi/issues">Report Bug</a>
    ·
    <a href="https://github.com/snake-4/esptool-pyftdi/issues">Request Feature</a>
    ·
    <a href="https://github.com/snake-4/esptool-pyftdi/releases">Latest Release</a>
  </p>
</div>


<!-- ABOUT THE PROJECT -->
## About The Project

This `esptool.py` wrapper allows you to map DTR and RTS used for resetting the ESP to any pin on your FTDI chip.
It also works on Windows, Linux and macOS.

The selected FTDI device and the pins that DTR or RTS are mapped to can be configured at the top of the `esptool-pyftdi.py` script.

### Requirements
- Windows: libusb-1.0.dll from [libusb.info](https://libusb.info/) alongside `esptool-pyftdi.py`
- Ubuntu, Debian: libusb-1.0-0
- Fedora: libusb1
- AUR: libusb
- `pip install -r requirements.txt`

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/FeatureName`)
3. Commit your Changes (`git commit -m 'Add some FeatureName'`)
4. Push to the Branch (`git push origin feature/FeatureName`)
5. Open a Pull Request

### Credits
- https://github.com/jimparis/esptool-ftdi
- https://github.com/eblot/pyftdi

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.