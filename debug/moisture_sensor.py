#!/usr/bin/env python3
import spidev
import time

# === Configuration ===
SPI_BUS        = 0        # SPI bus (0 or 1 on Pi)
SPI_DEVICE     = 0        # SPI device (0 for CE0, 1 for CE1)
SPI_MAX_SPEED  = 1_350_000  # 1.35 MHz (safe for MCP3008)
VREF           = 3.3      # Reference voltage for ADC (use 3.3V rail)
SENSOR_CHANNEL = 0        # MCP3008 CH0

RAW_DRY        = 920      # Manually measured in air
RAW_WET        = 90      # Manually measured in water

# === SPI Initialization ===
def init_spi(bus=SPI_BUS, device=SPI_DEVICE, speed=SPI_MAX_SPEED):
    """Return an spidev object configured for the MCP3008."""
    spi = spidev.SpiDev()
    spi.open(bus, device)
    spi.max_speed_hz = speed
    return spi

# === ADC Read ===
def read_adc(spi, channel):
    """
    Perform a single read from the MCP3008.
    Returns an integer 0–1023 corresponding to the analog voltage.
    """
    if not 0 <= channel <= 7:
        raise ValueError("ADC channel must be between 0 and 7")
    # MCP3008 protocol: [start=1][SGL/DIFF + channel (bits 6–4)][don't care]
    cmd = [1, (8 + channel) << 4, 0]
    resp = spi.xfer2(cmd)
    # Assemble 10-bit result from the last two bytes
    raw = ((resp[1] & 0x03) << 8) | resp[2]
    return raw

def raw_to_voltage(raw, vref=VREF):
    """Convert raw ADC reading to voltage."""
    return (raw / 1023.0) * vref

# === Main Loop ===
def main():
    spi = init_spi()
    try:
        print(f"Reading moisture on CH{SENSOR_CHANNEL} (CTRL+C to quit)")
        while True:
            raw = read_adc(spi, SENSOR_CHANNEL)
            voltage = raw_to_voltage(raw)
            # Normalize to 0.0–1.0 wetness ratio
            # wetness = (VREF - voltage) / VREF
            wetness = (RAW_DRY - raw) / (RAW_DRY - RAW_WET)
            wetness = max(0.0, min(1.0, wetness))
            print(f"Raw: {raw:4d} | Voltage: {voltage:.2f} V | Wetness: {wetness:.0%}")
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nInterrupted, closing SPI.")
    finally:
        spi.close()

if __name__ == "__main__":
    main()
