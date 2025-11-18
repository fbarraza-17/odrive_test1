
"""
Example usage of the ODrive python library to monitor and control ODrive devices
"""

import math
import time
import odrive
import numpy 
from odrive.enums import AxisState, ControlMode, InputMode
from odrive.utils import dump_errors, request_state

# Find a connected ODrive (this will block until you connect one)
print("waiting for ODrive...")
odrv0 = odrive.find_any()
print(f"found ODrive {odrv0.serial_number}")

# --- ADDED: CLEAR EXISTING ERRORS ---
# This is good practice to clear errors from previous runs
print("Clearing pre-existing errors...")
odrv0.clear_errors()

# Get a handle to the motor axis
axis = odrv0.axis0


# --- CALIBRATION STEP ---
# The ODrive must be calibrated before it can enter closed-loop control
print("Running calibration...")
# WARNING: This will make the motor move!
request_state(axis, AxisState.FULL_CALIBRATION_SEQUENCE)

# --- ADDED: WAIT FOR CALIBRATION TO COMPLETE AND CHECK FOR SUCCESS ---
print("Waiting for calibration to finish...")
start_time = time.monotonic()
print("Checking for errors...")
dump_errors(odrv0)


time.sleep(15)
# Clear the "Calibrating..." line and print a newline
print("       hello little odrive                      \n")

print("Calibration successful.")
# --- END OF ADDED CHECK ---

# Enter closed loop control
print("Entering closed-loop control...")
axis.controller.config.input_mode = InputMode.PASSTHROUGH
axis.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
request_state(axis, AxisState.CLOSED_LOOP_CONTROL)
print("Closed-loop control activated.")

print("Closed-loop control activated.")

# Run a sine wave velocity function
try:
    print("Starting sine wave velocity control...")
    
    # --- Get User Input for Sine Wave Parameters ---
    amplitude = float(input("Enter amplitude (peak speed in turns/s): "))
    frequency_hz = float(input("Enter frequency (oscillations per second, in Hz): "))
    
    # Convert Hz (cycles/sec) to radians/sec for math.sin()
    # 1 Hz = 2*pi radians/s
    frequency_rad = frequency_hz * 2 * math.pi
    
    # Set the center velocity (turns/s)
    center_velocity = 0.0
    
    print(f"\nRunning sine wave: Amplitude={amplitude} t/s, Frequency={frequency_hz} Hz")
    
    # Get the start time
    t0 = time.monotonic()

    # This loop runs as long as the ODrive is in closed-loop mode
    while axis.current_state == AxisState.CLOSED_LOOP_CONTROL:
        # Calculate how much time has passed
        elapsed_time = time.monotonic() - t0
        
        # Calculate the sine wave setpoint
        setpoint = center_velocity + amplitude * math.sin(frequency_rad * elapsed_time)
        
        # Send the command to the ODrive
        axis.controller.input_vel = setpoint
        
        # Optional: print the current setpoint
        print(f"Velocity: {setpoint:0.2f}", end='\r')
        
        # Wait a small amount of time to not flood the USB bus
        time.sleep(0.01)


finally:
    # Put the axis back into IDLE state
    print("\nLoop exited. Returning to IDLE state.")
    request_state(axis, AxisState.IDLE)

# Show errors
print("Checking for errors...")
dump_errors(odrv0)
print("Script finished.")



