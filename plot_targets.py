import serial_protocol

import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import queue


def serial_reader():
    ser = serial.Serial('/dev/ttyUSB0', 256000, timeout=1)
    while True:
        serial_port_line = ser.read_until(b'\xF8\xF7\xF6\xF5')
        data_queue.put(serial_port_line)
   
def update_plot(frame):
    # Check if there is data in the queue
    while not data_queue.empty():
        serial_port_line = data_queue.get()

        target_values = serial_protocol.read_basic_mode(serial_port_line)
        
        # if line is corrupted, skip it
        if target_values is None:
            continue

        target_state, \
        moving_target_dist, moving_target_energy, \
        static_target_dist, static_target_energy, \
        distance \
            = target_values

        print(distance)
        measured_distance.append(distance)
        
        measured_time.append(int(time.time_ns()))

        # Update the scatter plot
        line.set_data(measured_time[-50:], measured_distance[-50:])
        ax.relim()
        ax.autoscale_view()
    return line,

# Create a thread-safe queue to communicate between threads
data_queue = queue.Queue()

# Create and start the serial reader thread
serial_thread = threading.Thread(target=serial_reader)
serial_thread.daemon = True
serial_thread.start()

# Initialize empty lists to store all target information 
measured_time = []
global time_iterate
time_iterate = 0
measured_distance = []

# Set up the plot
fig, ax = plt.subplots()
line, = ax.plot(measured_time, measured_distance, marker='o')
ax.set_ylim(0, 200)

# Create an animation
ani = FuncAnimation(fig, update_plot, blit=True)

plt.xlabel('t [s]')
plt.ylabel('distance [cm]')
plt.grid()
plt.show()

