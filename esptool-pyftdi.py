from pyftdi.ftdi import Ftdi
from pyftdi.serialext.protocol_ftdi import Serial as FtdiSerialFinalClass
import sys
import runpy
import serial

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


def ensure_usb_backend_on_windows():
    import os
    import usb.backend.libusb1

    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.environ["PATH"] += os.pathsep + script_directory
    if usb.backend.libusb1.get_backend() is None:
        raise Exception(
            "Libusb1 backend not found! Ensure libusb-1.0.dll is in the script's directory."
        )


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path to tool> [args...]")
        return

    tool_path = sys.argv[1]
    if "idf_monitor" in tool_path:
        module_name = "esp_idf_monitor"
    elif "esptool" in tool_path:
        module_name = "esptool"
    else:
        raise Exception(f'Unable to determine the module name for "{tool_path}"')

    print("esptool-pyftdi wrapper")

    if sys.platform == "win32":
        ensure_usb_backend_on_windows()

    sys.argv[1:] = sys.argv[2:]
    serial.serial_for_url = serial_for_url
    runpy.run_module(module_name, run_name="__main__")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
