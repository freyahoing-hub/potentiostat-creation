from machine import Pin, SPI, ADC
import time
import uos

Test_number = 'Scan Rate 0.01 2'

# Define the SPI pins for the MCP4822 DAC
spi_sck = Pin(10)  # SCK (Serial Clock)
spi_mosi = Pin(11)  # MOSI (Master Out Slave In)
spi_miso = Pin(12)  # MISO (Master In Slave Out) - Not used here
spi_cs = Pin(15, Pin.OUT)  # CS (Chip Select)

# Setup SPI interface
spi = SPI(1, baudrate=500000, polarity=0, phase=0, sck=spi_sck, mosi=spi_mosi, miso=spi_miso)

# Setup ADC
adc = ADC(Pin(27, Pin.IN))  # Connect to the current output of your potentiostat

# Function to write to MCP4822 DAC
def write_dac(channel, value):
    spi_cs.value(0)
    config = 0x3000 | (channel << 15) | (value & 0x0FFF)
    spi.write(bytearray([(config >> 8) & 0xFF, config & 0xFF]))
    spi_cs.value(1)
   
# Open a file to save the data
file = open("CV_Data" + Test_number + ".csv", "w")
file.write("Time,Voltage,Current\n")  # Write header

# Function to perform cyclic voltammetry with multiple cycles
def cyclic_voltammetry(start_voltage, mid_voltage, end_voltage, scan_rate, steps, cycles):
    voltage_range = list(range(int((start_voltage) * 4096 / 3.3), int((mid_voltage) * 4096 / 3.3), int(4096 * scan_rate / (3.3 * steps))))
    voltage_range.extend(reversed(voltage_range))
    voltage_range.extend(range(int((start_voltage) * 4096 / 3.3), int((end_voltage) * 4096 / 3.3), -int(4096 * scan_rate / (3.3 * steps))))
    voltage_range.extend(range(int((end_voltage) * 4096 / 3.3), int((start_voltage) * 4096 / 3.3), int(4096 * scan_rate / (3.3 * steps))))


    start_time = time.ticks_ms()
    time.sleep(5)
    
    for cycle in range(cycles):
        print(f"Cycle {cycle + 1} of {cycles}")
        file.write("{}.\n".format(cycle + 1 ,"of",cycles))
        for voltage in voltage_range:
            act_voltage = int(voltage)
            write_dac(0, act_voltage)  # Assuming channel 0 is used for the DAC
            time.sleep(1 / steps)
            adc_value = adc.read_u16() >> 4  # Convert to 12-bit by right-shifting 4 bits
            current = ((adc_value / 4095) * 3.3)
            elapsed_time = time.ticks_diff(time.ticks_ms(), start_time) / 1000  # Convert to seconds
            print(f"Time:{elapsed_time:.2f}, Voltage:{voltage * 3.3 / 4096:.2f}, Current:{current}")
            file.write("{},{},{}\n".format(elapsed_time, ((voltage * 3.3 )/ 4096), current))
            
# Parameters for cyclic voltammetry
start_voltage = 0.12  # Start voltage in volts
mid_voltage = 0.5  # Intermediate voltage in volts
end_voltage = 0.0  # End voltage in volts
scan_rate = 0.01  # Scan rate in V/s
steps = 10  # Steps in one sweep
cycles = 2  # Number of cycles

# Run the experiment
cyclic_voltammetry(start_voltage, mid_voltage, end_voltage, scan_rate, steps, cycles)
file.close()  # Ensure the file is closed properly
