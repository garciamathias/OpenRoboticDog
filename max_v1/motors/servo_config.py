#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import time
import json
import os

class ServoConfig:
    def __init__(self):
        # Define servo IDs
        self.front_servo_ids = list(range(1, 7))  # IDs 1-6 for front servos
        self.rear_servo_ids = list(range(7, 13))  # IDs 7-12 for rear servos
        self.all_servo_ids = self.front_servo_ids + self.rear_servo_ids
        
        # Servo configuration
        self.baudrate = 1000000  # Default baudrate for STS3215 is 1,000,000
        self.front_servo_port = None
        self.rear_servo_port = None
        
        # Config file path
        self.config_file = "servo_config.json"
        
        # Load config if exists
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.front_servo_port = config.get('front_servo_port')
                    self.rear_servo_port = config.get('rear_servo_port')
                    print(f"Loaded configuration from {self.config_file}")
                    print(f"Front servo port: {self.front_servo_port}")
                    print(f"Rear servo port: {self.rear_servo_port}")
                    return True
            except Exception as e:
                print(f"Error loading configuration: {e}")
        return False
    
    def save_config(self):
        """Save configuration to JSON file"""
        config = {
            'front_servo_ids': self.front_servo_ids,
            'rear_servo_ids': self.rear_servo_ids,
            'baudrate': self.baudrate,
            'front_servo_port': self.front_servo_port,
            'rear_servo_port': self.rear_servo_port
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
        
    def find_port_by_disconnect_reconnect(self, port_type="front"):
        """
        Find the servo port by having the user disconnect and reconnect it
        port_type: "front" or "rear" to specify which servo bus to configure
        """
        display_type = "FRONT" if port_type == "front" else "REAR"
        print(f"\n=== PORT DETECTION FOR {display_type} SERVO BUS ===")
        print("1. We'll scan for currently connected devices")
        print(f"2. Then you'll disconnect the {display_type.lower()} servo controller")
        print("3. Then reconnect it")
        print("4. We'll identify which port appeared\n")
        
        input(f"Press Enter when ready to scan for CONNECTED devices (with {display_type.lower()} controller connected)...")
        
        # Get the list of ports before disconnecting
        before_ports = set([p.device for p in serial.tools.list_ports.comports()])
        if not before_ports:
            print("No ports detected initially!")
            return None
            
        print(f"Detected {len(before_ports)} ports: {', '.join(before_ports)}")
        
        # Ask user to disconnect the device
        print(f"\nNow, please DISCONNECT the {display_type.lower()} servo controller")
        input("Press Enter after disconnecting...")
        
        # Get the list after disconnecting
        disconnected_ports = set([p.device for p in serial.tools.list_ports.comports()])
        disappeared_ports = before_ports - disconnected_ports
        
        if disappeared_ports:
            print(f"Ports that disappeared: {', '.join(disappeared_ports)}")
        else:
            print("No ports disappeared after disconnecting. Something went wrong.")
            return None
        
        # Ask user to reconnect
        print(f"\nNow, please RECONNECT the {display_type.lower()} servo controller")
        input("Press Enter after reconnecting...")
        time.sleep(2)  # Give the system time to recognize the device
        
        # Get the list after reconnecting
        after_ports = set([p.device for p in serial.tools.list_ports.comports()])
        appeared_ports = after_ports - disconnected_ports
        
        if not appeared_ports:
            print("No new ports detected after reconnecting!")
            return None
            
        if len(appeared_ports) == 1:
            port = list(appeared_ports)[0]
            if port_type == "front":
                self.front_servo_port = port
            else:
                self.rear_servo_port = port
            print(f"\nDetected {display_type.lower()} servo port: {port}")
            return port
        else:
            print(f"\nMultiple ports appeared: {', '.join(appeared_ports)}")
            print(f"Please select the correct port for {display_type.lower()} servo bus:")
            ports_list = list(appeared_ports)
            for i, port in enumerate(ports_list):
                print(f"{i+1}. {port}")
            
            try:
                choice = int(input("Enter your choice (number): "))
                if 1 <= choice <= len(ports_list):
                    selected_port = ports_list[choice-1]
                    if port_type == "front":
                        self.front_servo_port = selected_port
                    else:
                        self.rear_servo_port = selected_port
                    print(f"Selected: {selected_port}")
                    return selected_port
                else:
                    print("Invalid choice!")
                    return None
            except ValueError:
                print("Invalid input!")
                return None
    
    def scan_for_servo_port(self, port_type="front"):
        """
        Scan available serial ports to find the servo bus.
        port_type: "front" or "rear" to specify which servo bus to configure
        """
        display_type = "FRONT" if port_type == "front" else "REAR"
        print(f"\n=== MANUAL PORT SELECTION FOR {display_type} SERVO BUS ===")
        print("Scanning for servo ports...")
        available_ports = list(serial.tools.list_ports.comports())
        
        if not available_ports:
            print("No serial ports found!")
            return None
        
        print("Available ports:")
        for i, port in enumerate(available_ports):
            print(f"{i+1}. {port.device} - {port.description}")
        
        # If there's only one port, use it automatically
        if len(available_ports) == 1:
            selected_port = available_ports[0].device
            if port_type == "front":
                self.front_servo_port = selected_port
            else:
                self.rear_servo_port = selected_port
            print(f"Automatically selected the only available port for {display_type.lower()} servo bus: {selected_port}")
            return selected_port
        
        # Otherwise, let the user choose
        try:
            choice = int(input(f"Enter the number of the port to use for {display_type.lower()} servo bus: "))
            if 1 <= choice <= len(available_ports):
                selected_port = available_ports[choice-1].device
                if port_type == "front":
                    self.front_servo_port = selected_port
                else:
                    self.rear_servo_port = selected_port
                print(f"Selected {display_type.lower()} port: {selected_port}")
                return selected_port
            else:
                print("Invalid choice!")
                return None
        except ValueError:
            print("Invalid input!")
            return None
    
    def test_connection(self, port_type="front"):
        """
        Test if we can connect to the selected port
        port_type: "front" or "rear" to specify which servo bus to test
        """
        port = self.front_servo_port if port_type == "front" else self.rear_servo_port
        display_type = "front" if port_type == "front" else "rear"
        
        if not port:
            print(f"No {display_type} servo port selected!")
            return False
        
        try:
            with serial.Serial(port, self.baudrate, timeout=1) as ser:
                print(f"Successfully opened connection to {display_type} servo port: {port}")
                return True
        except serial.SerialException as e:
            print(f"Failed to connect to {display_type} servo port {port}: {e}")
            return False
    
    def print_servo_config(self):
        """
        Print the servo configuration
        """
        print("\nServo Configuration:")
        print(f"Front Servo IDs: {self.front_servo_ids}")
        print(f"Rear Servo IDs: {self.rear_servo_ids}")
        print(f"Baudrate: {self.baudrate}")
        print(f"Front Servo Port: {self.front_servo_port if self.front_servo_port else 'Not selected'}")
        print(f"Rear Servo Port: {self.rear_servo_port if self.rear_servo_port else 'Not selected'}")

    def configure_port(self, port_type="front"):
        """
        Configure a specific servo port (front or rear)
        """
        display_type = "FRONT" if port_type == "front" else "REAR"
        print(f"\nConfiguring {display_type} servo bus:")
        
        # Choose port detection method
        print("\nPort detection methods:")
        print("1. Disconnect/Reconnect method (recommended)")
        print("2. Manual selection")
        
        try:
            choice = int(input("Choose a method (1 or 2): "))
            if choice == 1:
                port = self.find_port_by_disconnect_reconnect(port_type)
            else:
                port = self.scan_for_servo_port(port_type)
        except ValueError:
            print("Invalid input! Defaulting to disconnect/reconnect method")
            port = self.find_port_by_disconnect_reconnect(port_type)
        
        if port:
            if self.test_connection(port_type):
                return True
            else:
                print(f"\nFailed to connect to {display_type.lower()} port.")
                return False
        return False

if __name__ == "__main__":
    config = ServoConfig()
    config.print_servo_config()
    
    # Configure front servo bus
    print("\n" + "="*50)
    print("STEP 1: CONFIGURE FRONT SERVO BUS")
    print("="*50)
    front_configured = config.configure_port("front")
    
    # Configure rear servo bus
    print("\n" + "="*50)
    print("STEP 2: CONFIGURE REAR SERVO BUS")
    print("="*50)
    rear_configured = config.configure_port("rear")
    
    # Save configuration if at least one bus was configured
    if front_configured or rear_configured:
        config.save_config()
        print("\nConfiguration complete and saved!")
        config.print_servo_config()
    else:
        print("\nFailed to configure any servo buses. Configuration not saved.") 