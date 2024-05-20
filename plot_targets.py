import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import queue

def interpret_target_basic_mode(target_data):
    if target_data[0] == 0x00:
        target_state = 'no_target'
    elif target_data[0] == 0x01:
        target_state = 'moving_target'
    elif target_data[0] == 0x02:
        target_state = 'static_target'
    elif target_data[0] == 0x03:
        target_state = 'both_targets'
    else:
        target_state = 'unknown'

    # DISCLAIMER: I am not sure if my interpretation of the moving target distance is correct
    moving_target_dist = int.from_bytes(target_data[1:3], byteorder='little', signed=True)
    moving_target_energy = int.from_bytes(target_data[3:4], byteorder='little', signed=True)
    moving_target_dist = moving_target_dist if moving_target_dist >= 0 else -2**15 - moving_target_dist
    moving_target_dist = abs(moving_target_dist)

    static_target_dist = int.from_bytes(target_data[4:6], byteorder='little', signed=True)
    static_target_energy = int.from_bytes(target_data[6:7], byteorder='little', signed=True)
    static_target_dist = static_target_dist if static_target_dist >= 0 else -2**15 - static_target_dist
    static_target_dist = abs(static_target_dist)

    # this should be correct and is the most important value
    distance = int.from_bytes(target_data[7:9], byteorder='little', signed=True)
    distance = distance if distance >= 0 else -2**15 - distance
    distance = abs(distance)

    return (target_state, 
            moving_target_dist, moving_target_energy, 
            static_target_dist, static_target_energy,
            distance)

def serial_reader():
    ser = serial.Serial('/dev/ttyUSB0', 256000, timeout=1)
    while True:
        data = ser.read_until(b'\xF8\xF7\xF6\xF5')
        data_queue.put(data)
   
def update_plot(frame):
    # Check if there is data in the queue
    while not data_queue.empty():
        data = data_queue.get()

        # Check if the frame header and tail are present
        if b'\xF4\xF3\xF2\xF1' in data and b'\xF8\xF7\xF6\xF5' in data:
            # Extract the objective information
            objective_data = data.split(b'\xF4\xF3\xF2\xF1')[1].split(b'\xF8\xF7\xF6\xF5')[0]
            target_data = objective_data[4:-2]

            # Interpret the target data if it has the correct length
            if len(target_data) == 9:
                target_state, \
                moving_target_dist, moving_target_energy, \
                static_target_dist, static_target_energy, \
                distance \
                    = interpret_target_basic_mode(target_data)

                print(distance)
                measure_distance.append(distance)
                
                measure_time.append(int(time.time_ns()))

                # Update the scatter plot
                line.set_data(measure_time[-50:], measure_distance[-50:])
                ax.relim()
                ax.autoscale_view()
            else:
                pass

    return line,

# Create a thread-safe queue to communicate between threads
data_queue = queue.Queue()

# Create and start the serial reader thread
serial_thread = threading.Thread(target=serial_reader)
serial_thread.daemon = True
serial_thread.start()

# Initialize empty lists to store all target information 
measure_time = []
global time_iterate
time_iterate = 0
measure_distance = []

# Set up the plot
fig, ax = plt.subplots()
line, = ax.plot(measure_time, measure_distance, marker='o')
ax.set_ylim(0, 200)

# Create an animation
ani = FuncAnimation(fig, update_plot, blit=True)

plt.xlabel('t [s]')
plt.ylabel('distance [cm]')
plt.grid()
plt.show()

