# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Mocked classes and functions from dynamixel_sdk to allow for continuous integration
and testing code logic that requires hardware and devices (e.g. robot arms, cameras)

Warning: These mocked versions are minimalist. They do not exactly mock every behaviors
from the original classes and functions (e.g. return types might be None instead of boolean).
"""

# from dynamixel_sdk import COMM_SUCCESS

# Mock pour le SDK Feetech
# Ce fichier simule les fonctionnalités du SDK Feetech pour les tests

# Constantes
COMM_SUCCESS = 0
COMM_TX_FAIL = -1001
COMM_RX_FAIL = -1002
COMM_TX_ERROR = -2001
COMM_RX_WAITING = -2002
COMM_RX_TIMEOUT = -2003
COMM_RX_CORRUPT = -2004
COMM_NOT_AVAILABLE = -2005

# Valeurs par défaut
DEFAULT_BAUDRATE = 1000000
DEFAULT_DEVICE_NAME = "/dev/ttyUSB0"
DEFAULT_PROTOCOL_VERSION = 2.0


def convert_to_bytes(value, bytes):
    # TODO(rcadene): remove need to mock `convert_to_bytes` by implemented the inverse transform
    # `convert_bytes_to_value`
    del bytes  # unused
    return value


def get_default_motor_values(motor_index):
    return {
        # Key (int) are from SCS_SERIES_CONTROL_TABLE
        5: motor_index,  # ID
        6: DEFAULT_BAUDRATE,  # Baud_rate
        10: 0,  # Drive_Mode
        21: 32,  # P_Coefficient
        22: 32,  # D_Coefficient
        23: 0,  # I_Coefficient
        40: 0,  # Torque_Enable
        41: 254,  # Acceleration
        31: -2047,  # Offset
        33: 0,  # Mode
        55: 1,  # Lock
        # Set 2560 since calibration values for Aloha gripper is between start_pos=2499 and end_pos=3144
        # For other joints, 2560 will be autocorrected to be in calibration range
        56: 2560,  # Present_Position
        58: 0,  # Present_Speed
        69: 0,  # Present_Current
        85: 150,  # Maximum_Acceleration
    }


class PortHandler:
    def __init__(self, port_name):
        self.port_name = port_name
        self.baudrate = DEFAULT_BAUDRATE
        self.is_open = False
        self.ser = None  # Simuler un port série

    def openPort(self):
        self.is_open = True
        return True

    def closePort(self):
        self.is_open = False
        return True

    def setBaudRate(self, baudrate):
        self.baudrate = baudrate
        return True

    def getBaudRate(self):
        return self.baudrate

    def setPacketTimeoutMillis(self, timeout_ms):
        return True


class PacketHandler:
    def __init__(self, protocol_version):
        self.protocol_version = protocol_version
        self.data = {}  # Stocker les données simulées

    def getTxRxResult(self, result):
        if result == COMM_SUCCESS:
            return "COMM_SUCCESS"
        elif result == COMM_TX_FAIL:
            return "COMM_TX_FAIL"
        elif result == COMM_RX_FAIL:
            return "COMM_RX_FAIL"
        elif result == COMM_TX_ERROR:
            return "COMM_TX_ERROR"
        elif result == COMM_RX_WAITING:
            return "COMM_RX_WAITING"
        elif result == COMM_RX_TIMEOUT:
            return "COMM_RX_TIMEOUT"
        elif result == COMM_RX_CORRUPT:
            return "COMM_RX_CORRUPT"
        elif result == COMM_NOT_AVAILABLE:
            return "COMM_NOT_AVAILABLE"
        else:
            return "UNKNOWN_ERROR"

    def getRxPacketError(self, error):
        return "NO_ERROR"  # Simuler qu'il n'y a pas d'erreur


class GroupSyncRead:
    def __init__(self, port_handler, packet_handler, start_address, data_length):
        self.port_handler = port_handler
        self.packet_handler = packet_handler
        self.start_address = start_address
        self.data_length = data_length
        self.data = {}  # Stocker les données simulées par ID de moteur

    def addParam(self, id):
        # Initialiser les données pour ce moteur si nécessaire
        if id not in self.data:
            self.data[id] = {}
            for addr in range(self.start_address, self.start_address + self.data_length):
                self.data[id][addr] = 0  # Valeur par défaut

    def removeParam(self, id):
        if id in self.data:
            del self.data[id]

    def clearParam(self):
        self.data = {}

    def txRxPacket(self):
        return COMM_SUCCESS

    def isAvailable(self, id, address, data_length):
        return id in self.data and address in self.data[id]

    def getData(self, id, address, data_length):
        if id in self.data and address in self.data[id]:
            return self.data[id][address]
        return 0


class GroupSyncWrite:
    def __init__(self, port_handler, packet_handler, start_address, data_length):
        self.port_handler = port_handler
        self.packet_handler = packet_handler
        self.start_address = start_address
        self.data_length = data_length
        self.data = {}  # Stocker les données simulées par ID de moteur

    def addParam(self, id, data):
        if id not in self.data:
            self.data[id] = {}
        self.data[id][self.start_address] = data

    def removeParam(self, id):
        if id in self.data:
            del self.data[id]

    def changeParam(self, id, data):
        if id in self.data:
            self.data[id][self.start_address] = data

    def clearParam(self):
        self.data = {}

    def txPacket(self):
        return COMM_SUCCESS


# Fonctions utilitaires
def SCS_LOBYTE(w):
    return w & 0xFF

def SCS_HIBYTE(w):
    return (w >> 8) & 0xFF

def SCS_LOWORD(dw):
    return dw & 0xFFFF

def SCS_HIWORD(dw):
    return (dw >> 16) & 0xFFFF

def SCS_MAKEWORD(low, high):
    return (high << 8) | low

def SCS_MAKEDWORD(low, high):
    return (high << 16) | low
