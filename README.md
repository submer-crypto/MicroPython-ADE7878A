# MicroPython ADE7878A

MicroPython driver for [ADE7868A, ADE7878A and ADE7878](https://www.analog.com/en/products/ade7878a.html) energy metering microchips with input from a CT sensor for amperage readings and a resistor voltage divider for voltage readings for each phase.

## Usage

Initiate one of the `ADE78*` variants and pass the I2C instance and the appropriate physical values.

```python
from micropython import const
from machine import Pin, I2C
from ade7878a import ADE7878A

CT_BURDEN_RESISTOR = 16 # [Ohm]
CT_TURNS_RATIO = const(1000)

VOLTAGE_RESISTOR_1 = const(1650000) # [Ohm]
VOLTAGE_RESISTOR_2 = const(1000) # [Ohm]

i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)

ade = ADE7878A(i2c,
    ct_burden_resistor=CT_BURDEN_RESISTOR,
    ct_turns_ratio=CT_TURNS_RATIO,
    voltage_resistor_1=VOLTAGE_RESISTOR_1,
    voltage_resistor_2=VOLTAGE_RESISTOR_2)

ade.start()

# For each phase a, b and c it is possible to
# read the amperage and voltage values.
ade.read_phase_a_current()
ade.read_phase_a_voltage()

# The ADE78*A variants also support reading the
# average over one second.
ade.read_phase_a_current_average()
ade.read_phase_a_voltage_average()
```
