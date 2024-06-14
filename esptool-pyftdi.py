from pyftdi.ftdi import Ftdi
from pyftdi.serialext.protocol_ftdi import Serial as FtdiSerialFinalClass
import sys

# FTDI AN_184
IO_MAPPING = {
    "TXD": 0b00000001,  # D0
    "RXD": 0b00000010,  # D1
    "RTS": 0b00000100,  # D2
    "CTS": 0b00001000,  # D3
    "DTR": 0b00010000,  # D4
    "DSR": 0b00100000,  # D5
    "DCD": 0b01000000,  # D6
    "RI": 0b10000000,  # D7
}

# GPIO0
MAP_DTR_TO = IO_MAPPING["CTS"]

# EN
MAP_RTS_TO = IO_MAPPING["DTR"]

# URL scheme: ftdi://[vendor[:product[:index|:serial]]]/interface
OVERRIDE_URL = "ftdi:///1"

# (True) esptool-pyftdi.py esptool chip_id
# (False) esptool-pyftdi.py chip_id
# Has to be True if ESPTOOL_WRAPPER is set
SKIP_FIRST_ARG = True


class CustomMappedFtdiSerial(FtdiSerialFinalClass):
    def _update_rts_state(self):
        self._update_gpio_state()

    def _update_dtr_state(self):
        self._update_gpio_state()

    def _update_gpio_state(self):
        if not self.is_open:
            return
        self._ensure_mode(Ftdi.BitMode.BITBANG)
        val = IO_MAPPING["TXD"]
        if not self._dtr_state:
            val |= MAP_DTR_TO
        if not self._rts_state:
            val |= MAP_RTS_TO
        self.udev.write_data(val.to_bytes(1))

    def _ensure_mode(self, new_mode: Ftdi.BitMode):
        if not self.is_open or self.udev._bitmode == new_mode:
            return
        if new_mode == Ftdi.BitMode.BITBANG:
            direction_mask = IO_MAPPING["TXD"] | MAP_DTR_TO | MAP_RTS_TO
            self.udev.set_bitmode(direction_mask, new_mode)
        elif new_mode == Ftdi.BitMode.RESET:
            self.udev.set_bitmode(0, new_mode)
            self.udev.set_flowctrl("")
            self.udev.set_rts(False)

    def read(self, size=1):
        self._ensure_mode(Ftdi.BitMode.RESET)
        if size == 0:
            # If in_waiting i.e. 0 was passed to this function, read the whole buffer
            buf = b""
            while True:
                read_bytes = self.udev.read_data(1)
                if read_bytes == b"":
                    break
                buf += read_bytes
        else:
            buf = super().read(size)
        return buf

    def write(self, data):
        self._ensure_mode(Ftdi.BitMode.RESET)
        return super().write(data)

    def reset_input_buffer(self):
        self._ensure_mode(Ftdi.BitMode.RESET)
        super().reset_input_buffer()

    def reset_output_buffer(self):
        self._ensure_mode(Ftdi.BitMode.RESET)
        super().reset_output_buffer()

    def send_break(self, duration=0.25):
        self._ensure_mode(Ftdi.BitMode.RESET)
        super().send_break(duration)

    def _update_break_state(self):
        self._ensure_mode(Ftdi.BitMode.RESET)
        super()._update_break_state()

    @property
    def cts(self):
        self._ensure_mode(Ftdi.BitMode.RESET)
        return super().cts

    @property
    def dsr(self):
        self._ensure_mode(Ftdi.BitMode.RESET)
        return super().dsr

    @property
    def ri(self):
        self._ensure_mode(Ftdi.BitMode.RESET)
        return super().ri

    @property
    def cd(self):
        self._ensure_mode(Ftdi.BitMode.RESET)
        return super().cd


def serial_for_url(url, *args, **kwargs):
    do_open = not kwargs.pop("do_not_open", False)
    instance = CustomMappedFtdiSerial(None, *args, **kwargs)
    instance.port = OVERRIDE_URL
    if do_open:
        instance.open()
    return instance


def win32_ensure_usb_backend():
    # Add script directory to PATH on Windows so that ctypes can find libusb
    import os
    import usb.backend.libusb1

    os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.abspath(__file__))
    if usb.backend.libusb1.get_backend() == None:
        sys.exit(
            f"Libusb1 backend was not found! Make sure that libusb-1.0.dll is in the script's directory."
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} <esptool> [args...]")
    print("esptool-pyftdi wrapper")

    if sys.platform == "win32":
        win32_ensure_usb_backend()

    try:
        import esptool
    except:
        sys.exit(
            "Esptool module could not be found. Make sure that the environment is correct."
        )

    if SKIP_FIRST_ARG:
        sys.argv[1:] = sys.argv[2:]
    esptool.loader.serial.serial_for_url = serial_for_url
    esptool._main()
