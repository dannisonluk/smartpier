import _thread
from collections import deque

from monitor_intensity import monitor_intensity
from receive_usb_data import receive_usb_data

storage_queue = deque(maxlen=1000)


def main():
    # Create the receive_usb_data thread
    try:
        _thread.start_new_thread(receive_usb_data, (storage_queue,))
    except:
        print("Error: unable to start thread receive_usb_data")

    # Create the monitor_intensity thread
    try:
        _thread.start_new_thread(monitor_intensity, (storage_queue,))
    except:
        print("Error: unable to start thread monitor_intensity")

    # Wait for user input to stop the threads
    input("Press any key to stop the threads\n")


if __name__ == '__main__':
    print("starts")
    main()
    print("terminates")
