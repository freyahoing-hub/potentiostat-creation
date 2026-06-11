from machine import Pin, SPI, ADC
import time

# Define SPI pins for MCP4822
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs = Pin(17, Pin.OUT)

# ADC pin for reading current
adc = ADC(Pin(26))

# Function to set voltage using MCP4822 DAC
def set_voltage(channel, voltage):
    cs.low()
    value = int((voltage / 3.3) * 4095)  # Convert voltage to 12-bit value
    buf = bytearray(2)
    buf[0] = (channel << 7) | (0b011 << 4) | (value >> 8)
    buf[1] = value & 0xFF
    spi.write(buf)
    cs.high()

# Parameters for cyclic voltammetry
start_voltage = -1.0  # Start voltage in volts
end_voltage = 1.0  # End voltage in volts
scan_rate = 0.01  # Scan rate in V/s
voltage_step = 0.001  # Voltage step in volts

# Calculate the time step based on the scan rate and voltage step
time_step = voltage_step / scan_rate

# Open a file to save the data
file = open("voltammetry_data.csv", "w")
file.write("Voltage,Current\n")  # Write header

# Main loop for cyclic voltammetry
while True:
    voltage = start_voltage
    
    # Forward scan
    while voltage <= end_voltage:
        set_voltage(0, voltage)
        adc_value = adc.read_u16()
        current = adc_value / 65535 * 3.3  # Convert ADC value to current
        print("Voltage:", voltage, "Current:", current)
        file.write("{},{}\n".format(voltage, current))  # Save data to file
        voltage += voltage_step
        time.sleep(time_step)
    
    # Reverse scan
    while voltage >= start_voltage:
        set_voltage(0, voltage)
        adc_value = adc.read_u16()
        current = adc_value / 65535 * 3.3  # Convert ADC value to current
        print("Voltage:", voltage, "Current:", current)
        file.write("{},{}\n".format(voltage, current))  # Save data to file
        voltage -= voltage_step
        time.sleep(time_step)
    
    # Message indicating the end of the voltammetry cycle
    print("Cyclic Voltammetry cycle completed")
    file.write("Cyclic Voltammetry cycle completed\n")  # Log completion

    # Pause before starting the next cycle
    time.sleep(1)
