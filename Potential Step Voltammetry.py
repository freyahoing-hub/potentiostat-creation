from machine import Pin, SPI, ADC
import time

# Define the SPI pins for the MCP4822 DAC
spi_sck = machine.Pin(10)  # SCK (Serial Clock)
spi_mosi = machine.Pin(11)  # MOSI (Master Out Slave In)
spi_miso = machine.Pin(12)  # MISO (Master In Slave Out) - Not used here
spi_cs = machine.Pin(15, machine.Pin.OUT)  # CS (Chip Select)

# Setup SPI interface
spi = machine.SPI(1, baudrate=500000, polarity=0, phase=0, sck=spi_sck, mosi=spi_mosi, miso=spi_miso)

# Setup ADC
adc = machine.ADC(machine.Pin(27, machine.Pin.IN))  # Connect to the current output of your potentiostat

# Function to write to MCP4822 DAC
def write_dac(channel, value):
    spi_cs.value(0)
    config = 0x3000 | (channel << 15) | (value & 0x0FFF)
    spi.write(bytearray([(config >> 8) & 0xFF, config & 0xFF]))
    spi_cs.value(1)

# Parameters for potential step voltammetry
step_voltages = [0.9222175]  # List of step voltages in volts
step_duration = 5  # Duration at each step in seconds

# Open a file to save the data
file = open("potential_step_data(Orange (600)).csv", "w")
file.write("Time,Voltage,Current\n")  # Write header

# Function to perform potential step voltammetry
def potential_step_voltammetry(start_voltage, end_voltage, step_duration, steps):
    time.sleep(5)
    voltage_values = step_voltages #[start_voltage + i * (end_voltage - start_voltage) / (steps - 1) for i in range(steps)]
    for voltage in voltage_values:
        write_dac(0, int((voltage*1.62) * 4096 / 3.3)) # Assuming channel 0 is used for the DAC
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < step_duration * 1000:
            current = adc.read_u16() >> 4 # Convert to 12-bit by right-shifting 4 bits
            elapsed_time = time.ticks_diff(time.ticks_ms(), start_time) / 1000 # Convert to seconds
            print(f"Time: {elapsed_time:.2f} s, Voltage: {voltage:.2f} V, Current: {current} μA")
            file.write("{},{},{}\n".format(elapsed_time, voltage, current))

    file.close()  # Ensure the file is closed properly
    
# Define your experiment parameters here
start_voltage = 0.0 # Starting voltage
end_voltage = 0.5 # Ending voltage
step_duration = 5.0 # Duration of each step in seconds
steps = 10 # Number of steps
# Run the experiment
potential_step_voltammetry(start_voltage, end_voltage, step_duration, steps)