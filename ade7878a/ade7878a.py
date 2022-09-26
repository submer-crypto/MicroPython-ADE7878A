import time
from micropython import const

_AIGAIN = const(0x4380)
_AVGAIN = const(0x4381)
_BIGAIN = const(0x4382)
_CIGAIN = const(0x4384)
_AIRMSOS = const(0x4387)
_AVRMSOS = const(0x4388)
_BIRMSOS = const(0x4389)
_BVRMSOS = const(0x438A)
_HPFDIS = const(0x43B6)
_AIRMS = const(0x43C0)
_AVRMS = const(0x43C1)
_BIRMS = const(0x43C2)
_BVRMS = const(0x43C3)
_CIRMS = const(0x43C4)
_CVRMS = const(0x43C5)

_RUN = const(0xE228)

_STATUS0 = const(0xE502)
_STATUS1 = const(0xE503)
_OILVL = const(0xE507)
_OVLVL = const(0xE508)
_SAGLVL = const(0xE509)
_MASK0 = const(0xE50A)
_MASK1 = const(0xE50B)
_CHECKSUM = const(0xE51F)
_IARMS_LRIP = const(0xE530)
_VARMS_LRIP = const(0xE531)
_IBRMS_LRIP = const(0xE532)
_VBRMS_LRIP = const(0xE533)
_ICRMS_LRIP = const(0xE534)
_VCRMS_LRIP = const(0xE535)

_PERIOD = const(0xE607)
_COMPMODE = const(0xE60E)
_GAIN = const(0xE60F)
_CFMODE = const(0xE610)
_CONFIG = const(0xE618)

_MMODE = const(0xE700)
_ACCMODE = const(0xE701)
_LCYCMODE = const(0xE702)
_PEAKCYC = const(0xE703)
_SAGCYC = const(0xE704)

_LOCK = const(0xE7FE)
_WRITE = const(0xE7E3)

_DEFAULT_CHECKSUM = const(0xEEF4CB9A)

# +0.5 volts mapped to +5.928.256
# -0.5 volts mapped to -5.928.256
_ADE7878A_ADC_RANGE = const(5_928_256 * 2) # [1 / V]

class ADE7878A:
    _BUFFER_8 = bytearray(1)
    _BUFFER_16 = bytearray(2)
    _BUFFER_32 = bytearray(4)

    def __init__(self, i2c, ct_burden_resistor, ct_turns_ratio, voltage_resistor_1, voltage_resistor_2, address=0x38):
        self._i2c = i2c
        self._address = address

        self._current_scale = ct_turns_ratio / (_ADE7878A_ADC_RANGE * ct_burden_resistor)
        self._voltage_scale = (voltage_resistor_1 + voltage_resistor_2) / (_ADE7878A_ADC_RANGE * voltage_resistor_2)

        self.reset()
        time.sleep_ms(150)
        self._init()

        if (checksum := self.read_checksum()) != _DEFAULT_CHECKSUM:
            raise ValueError(f'Unexpected checksum {checksum:x}')

    def _init(self):
        self._write_u32(_AIGAIN, 0x00)
        self._write_u32(_AVGAIN, 0x00)
        self._write_u32(_BIGAIN, 0x00)
        self._write_u32(_CIGAIN, 0x00)
        self._write_u32(_AIRMSOS, 0x00)
        self._write_u32(_AVRMSOS, 0x00)
        self._write_u32(_BIRMSOS, 0x00)
        self._write_u32(_BVRMSOS, 0x00)
        self._write_u32(_OILVL, 0xFFFFFF)
        self._write_u32(_OVLVL, 0xFFFFFF)
        self._write_u32(_SAGLVL, 0x00)
        # self._write_u32(_MASK0, 0x00)
        # self._write_u32(_MASK1, 0x060000)
        # self._write_u16(_COMPMODE, 0x0111)
        self._write_u16(_GAIN, 0x00)
        # self._write_u16(_CFMODE, 0x00)
        self._write_u16(_CONFIG, 0x00)
        self._write_u8(_MMODE, 0x1C)
        self._write_u8(_ACCMODE, 0x00)
        self._write_u8(_LCYCMODE, 0x78)
        self._write_u8(_PEAKCYC, 0x0F)
        self._write_u8(_SAGCYC, 0x0F)

        # Write the last register three times to
        # ensure that its value was been written into the RAM
        self._write_u32(_HPFDIS, 0x00)
        self._write_u32(_HPFDIS, 0x00)
        self._write_u32(_HPFDIS, 0x00)

        # self._write_u8(_LOCK, 0xAD)
        # self._write_u8(_WRITE, 0x80)

    def _read_u16(self, memaddr):
        self._i2c.readfrom_mem_into(self._address, memaddr, self._BUFFER_16, addrsize=16)

        return ((self._BUFFER_16[0] << 8)
            | self._BUFFER_16[1])

    def _read_u32(self, memaddr):
        self._i2c.readfrom_mem_into(self._address, memaddr, self._BUFFER_32, addrsize=16)

        return ((self._BUFFER_32[0] << 24)
            | (self._BUFFER_32[1] << 16)
            | (self._BUFFER_32[2] << 8)
            | self._BUFFER_32[3])

    def _write_u8(self, memaddr, val):
        self._BUFFER_8[0] = val & 0xFF
        self._i2c.writeto_mem(self._address, memaddr, self._BUFFER_8, addrsize=16)

    def _write_u16(self, memaddr, val):
        self._BUFFER_16[0] = (val >> 8) & 0xFF
        self._BUFFER_16[1] = val & 0xFF
        self._i2c.writeto_mem(self._address, memaddr, self._BUFFER_16, addrsize=16)

    def _write_u32(self, memaddr, val):
        self._BUFFER_32[0] = (val >> 24) & 0xFF
        self._BUFFER_32[1] = (val >> 16) & 0xFF
        self._BUFFER_32[2] = (val >> 8) & 0xFF
        self._BUFFER_32[3] = val & 0xFF
        self._i2c.writeto_mem(self._address, memaddr, self._BUFFER_32, addrsize=16)

    def start(self):
        self._write_u32(_STATUS0, 0x0007FFFF)
        self._write_u32(_STATUS1, 0x03FFFFFF)
        self._write_u16(_RUN, 0x0001)

    def reset(self):
        self._write_u16(_CONFIG, 0x00F0)

    def read_checksum(self):
        return self._read_u32(_CHECKSUM)

    def read_phase_a_current(self):
        rms = self._read_u32(_AIRMS)
        return rms * self._current_scale

    def read_phase_a_current_average(self):
        rms = self._read_u32(_IARMS_LRIP)
        return rms * self._current_scale

    def read_phase_a_voltage(self):
        rms = self._read_u32(_AVRMS)
        return rms * self._voltage_scale

    def read_phase_a_voltage_average(self):
        rms = self._read_u32(_VARMS_LRIP)
        return rms * self._voltage_scale

    def read_phase_b_current(self):
        rms = self._read_u32(_BIRMS)
        return rms * self._current_scale

    def read_phase_b_current_average(self):
        rms = self._read_u32(_IBRMS_LRIP)
        return rms * self._current_scale

    def read_phase_b_voltage(self):
        rms = self._read_u32(_BVRMS)
        return rms * self._voltage_scale

    def read_phase_b_voltage_average(self):
        rms = self._read_u32(_VBRMS_LRIP)
        return rms * self._voltage_scale

    def read_phase_c_current(self):
        rms = self._read_u32(_CIRMS)
        return rms * self._current_scale

    def read_phase_c_current_average(self):
        rms = self._read_u32(_ICRMS_LRIP)
        return rms * self._current_scale

    def read_phase_c_voltage(self):
        rms = self._read_u32(_CVRMS)
        return rms * self._voltage_scale

    def read_phase_c_voltage_average(self):
        rms = self._read_u32(_VCRMS_LRIP)
        return rms * self._voltage_scale

    def read_voltage_frequency(self):
        period = self._read_u16(_PERIOD)
        return 256000 / (period + 1)
