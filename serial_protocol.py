import serial


def read_basic_mode(serial_port_line:bytes)->tuple[6]:
    '''
    Read the basic mode data from the serial port line
    Parameters:
    - serial_port_line (bytes): the serial port line
    Returns:
    - target_state (str): the state of the target
    - moving_target_dist (int): the distance of the moving target
    - moving_target_energy (int): the energy of the moving target
    - static_target_dist (int): the distance of the static target
    - static_target_energy (int): the energy of the static target
    - distance (int): the distance of the target
    '''
    
    # Check if the frame header and tail are present
    if b'\xF4\xF3\xF2\xF1' in serial_port_line and b'\xF8\xF7\xF6\xF5' in serial_port_line:
        # cut out the header, tail and other checksum bytes
        target_data = serial_port_line[8:-6]

        # Interpret the target data
        if len(target_data) == 9:
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
            # moving_target_dist = moving_target_dist if moving_target_dist >= 0 else -2**15 - moving_target_dist
            # moving_target_dist = abs(moving_target_dist)

            static_target_dist = int.from_bytes(target_data[4:6], byteorder='little', signed=True)
            static_target_energy = int.from_bytes(target_data[6:7], byteorder='little', signed=True)
            # static_target_dist = static_target_dist if static_target_dist >= 0 else -2**15 - static_target_dist
            # static_target_dist = abs(static_target_dist)

            # this should be correct and is the most important value
            distance = int.from_bytes(target_data[7:9], byteorder='little', signed=True)
            distance = distance if distance >= 0 else -2**15 - distance
            distance = abs(distance)

            return (target_state, 
                    moving_target_dist, moving_target_energy, 
                    static_target_dist, static_target_energy,
                    distance)
        
        # if the target data is not 17 bytes long the line is corrupted
        else:
            return None
    # if the header and tail are not present the line is corrupted
    else: 
        return None

def enable_configuration_mode(ser:serial.Serial)->bool:
    '''
    Set the radar to configuration mode
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the configuration mode was successfully enabled, False otherwise
    '''
    ser.write(bytes.fromhex('FD FC FB FA 04 00 FF 00 01 00 04 03 02 01'))

    response = ser.read_until(bytes.fromhex('04 03 02 01'))
    if int.from_bytes(response[8:10], byteorder='little', signed=False)==0:
        return True
    else:
        return False
    
def end_configuration_mode(ser:serial.Serial)->bool:
    '''
    End the configuration mode
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the configuration mode was successfully ended, False otherwise
    '''
    ser.write(bytes.fromhex('FD FC FB FA 02 00 FE 00 04 03 02 01'))
    response = ser.read_until(bytes.fromhex('04 03 02 01'))
    if int.from_bytes(response[8:10], byteorder='little', signed=False)==0:
        return True
    else:
        return False

def read_current_configuration(ser:serial.Serial)->bool:
    '''
    Read the current configuration of the radar
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the configuration was successfully read, False otherwise
    '''
    ser.write(bytes.fromhex('FD FC FB FA 02 00 61 00 04 03 02 01'))  

def enable_engineering_mode(ser:serial.Serial)->bool:
    '''
    Enable engineering mode
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the engineering mode was successfully enabled, False otherwise
    '''
    ser.write(bytes.fromhex('FD FC FB FA 02 00 62 00 04 03 02 01'))
    response = ser.read_until(bytes.fromhex('04 03 02 01'))
    if int.from_bytes(response[8:10], byteorder='little', signed=False)==0:
        return True
    else:
        return False

def close_engineering_mode(ser:serial.Serial)->bool:
    '''
    Close engineering mode
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the engineering mode was successfully closed, False otherwise
    '''
    ser.write(bytes.fromhex('FD FC FB FA 02 00 63 00 04 03 02 01'))
    response = ser.read_until(bytes.fromhex('04 03 02 01'))
    if int.from_bytes(response[8:10], byteorder='little', signed=False)==0:
        return True
    else:
        return False
