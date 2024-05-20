import serial
import time

def interpret_target_basic_mode(target_data):
    '''
    Interpret the target data in basic mode
    Parameters:
    - target_data (bytes): the target data as descibed in table 11
    Returns:
    - target_state (str): the state of the target
    - moving_target_dist (int): the distance resolution to the moving target
    - moving_target_energy (int): the energy of the moving target
    - static_target_dist (int): the distance to the static target
    - static_target_energy (int): the energy of the static target
    - distance (int): the distance to the target
    '''
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

# Open the serial port
ser = serial.Serial('/dev/ttyUSB0', 256000, timeout=1)

# set radar to configuration mode
# ser.write(bytes.fromhex('FD FC FB FA 04 00 FF 00 01 00 04 03 02 01'))

# read the current configuration
# ser.write(bytes.fromhex('FD FC FB FA 02 00 61 00 04 03 02 01'))

# enable engineering mode
# ser.write(bytes.fromhex('FD FC FB FA 02 00 62 00 04 03 02 01'))
engineering_mode = False # set true when uncommenting the line above

# end configuration mode
# ser.write(bytes.fromhex('FD FC FB FA 02 00 FE 00 04 03 02 01'))

# read the response
# time.sleep(0.1)
# response = ser.read_until(bytes.fromhex('04 03 02 01'))
# hex_response = ' '.join(format(byte, '02X') for byte in response)
# print(hex_response)

try:
    while True:
        # Read a line from the serial port
        data = ser.read_until(b'\xF8\xF7\xF6\xF5')

        # Check if the frame header and tail are present
        if b'\xF4\xF3\xF2\xF1' in data and b'\xF8\xF7\xF6\xF5' in data:
            # Extract the objective information
            objective_data = data.split(b'\xF4\xF3\xF2\xF1')[1].split(b'\xF8\xF7\xF6\xF5')[0]
            target_data = objective_data[4:-2]

            # Interpret the target data
            if len(target_data) == 9:
                target_state, \
                moving_target_dist, moving_target_energy, \
                static_target_dist, static_target_energy, \
                distance \
                    = interpret_target_basic_mode(target_data)               
            else:
                continue
            
            print('Target State:', target_state)
            print('Moving Target Distance:', moving_target_dist)
            print('Moving Target Energy:', moving_target_energy)
            print('Static Target Distance:', static_target_dist)
            print('Static Target Energy:', static_target_energy)
            print('Distance:', distance)
            print()
            print(30*'-')
            print()

            # uncomment for debugging serial port
            # print(data)
            # for i, byte in enumerate(target_data):
            #     # print byte as hex
            #     print(format(byte, '02X'), end=' ')
            # print(i)  
            # print(len(target_data))

        
        
except KeyboardInterrupt:
    # Close the serial port on keyboard interrupt
    ser.close()
    print("Serial port closed.")