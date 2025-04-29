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
"""
This script configures a single Feetech motor at a time to a given ID and baudrate.

Example of usage:
```bash
python max_v1/motors/configure_motor.py \
  --port /dev/tty.usbmodem585A0080521 \
  --model sts3215 \
  --baudrate 1000000 \
  --ID 1
```
"""

import argparse
import time
from max_v1.motors.configs import FeetechMotorsBusConfig
from max_v1.motors.feetech import (
    MODEL_BAUDRATE_TABLE,
    SCS_SERIES_BAUDRATE_TABLE,
    FeetechMotorsBus,
)


def configure_motor(port, model, motor_idx_des, baudrate_des):
    # Check if the provided model exists in the model_baud_rate_table
    if model not in MODEL_BAUDRATE_TABLE:
        raise ValueError(
            f"Invalid model '{model}'. Supported models: {list(MODEL_BAUDRATE_TABLE.keys())}"
        )

    # Setup motor names, indices, and models
    motor_name = "motor"
    motor_index_arbitrary = motor_idx_des  # Use the motor ID passed via argument
    motor_model = model  # Use the motor model passed via argument

    config = FeetechMotorsBusConfig(port=port, motors={motor_name: (motor_index_arbitrary, motor_model)})

    # Initialize the MotorBus with the correct port and motor configurations
    motor_bus = FeetechMotorsBus(config=config)

    # Try to connect to the motor bus and handle any connection-specific errors
    try:
        motor_bus.connect()
        print(f"Connected on port {motor_bus.port}")
    except OSError as e:
        print(f"Error occurred when connecting to the motor bus: {e}")
        return

    # Motor bus is connected, proceed with the rest of the operations
    try:
        print("Scanning all baudrates and motor indices")
        all_baudrates = set(SCS_SERIES_BAUDRATE_TABLE.values())
        motor_index = -1  # Set the motor index to an out-of-range value.

        for baudrate in all_baudrates:
            motor_bus.set_bus_baudrate(baudrate)
            present_ids = motor_bus.find_motor_indices(list(range(1, 10)))
            if len(present_ids) > 1:
                raise ValueError(
                    "Error: More than one motor ID detected. This script is designed to only handle one motor at a time. Please disconnect all but one motor."
                )

            if len(present_ids) == 1:
                if motor_index != -1:
                    raise ValueError(
                        "Error: More than one motor ID detected. This script is designed to only handle one motor at a time. Please disconnect all but one motor."
                    )
                motor_index = present_ids[0]
                break

        if motor_index == -1:
            raise ValueError("No motors detected. Please ensure you have one motor connected.")

        print(f"Motor index found at: {motor_index}")

        # Allows ID and BAUDRATE to be written in memory
        motor_bus.write_with_motor_ids(motor_bus.motor_models, motor_index, "Lock", 0)

        if baudrate != baudrate_des:
            print(f"Setting its baudrate to {baudrate_des}")
            baudrate_idx = list(SCS_SERIES_BAUDRATE_TABLE.values()).index(baudrate_des)

            # The write can fail, so we allow retries
            motor_bus.write_with_motor_ids(motor_bus.motor_models, motor_index, "Baud_Rate", baudrate_idx)
            time.sleep(0.5)
            motor_bus.set_bus_baudrate(baudrate_des)
            present_baudrate_idx = motor_bus.read_with_motor_ids(
                motor_bus.motor_models, motor_index, "Baud_Rate", num_retry=2
            )

            if present_baudrate_idx != baudrate_idx:
                raise OSError("Failed to write baudrate.")

        print(f"Setting its index to desired index {motor_idx_des}")
        motor_bus.write_with_motor_ids(motor_bus.motor_models, motor_index, "Lock", 0)
        motor_bus.write_with_motor_ids(motor_bus.motor_models, motor_index, "ID", motor_idx_des)

        present_idx = motor_bus.read_with_motor_ids(motor_bus.motor_models, motor_idx_des, "ID", num_retry=2)
        if present_idx != motor_idx_des:
            raise OSError("Failed to write index.")

        # Set Maximum_Acceleration to 254 to speedup acceleration and deceleration of
        # the motors. Note: this configuration is not in the official STS3215 Memory Table
        motor_bus.write("Lock", 0)
        motor_bus.write("Maximum_Acceleration", 254)

        motor_bus.write("Goal_Position", 2048)
        time.sleep(4)
        print("Present Position", motor_bus.read("Present_Position"))

        motor_bus.write("Offset", 0)
        time.sleep(4)
        print("Offset", motor_bus.read("Offset"))

    except Exception as e:
        print(f"Error occurred during motor configuration: {e}")

    finally:
        motor_bus.disconnect()
        print("Disconnected from motor bus.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=str, required=True, help="Motors bus port")
    parser.add_argument("--model", type=str, required=True, help="Motor model (e.g. sts3215)")
    parser.add_argument("--ID", type=int, required=True, help="Desired ID of the current motor (e.g. 1,2,3)")
    parser.add_argument(
        "--baudrate", type=int, default=1000000, help="Desired baudrate for the motor (default: 1000000)"
    )
    args = parser.parse_args()

    configure_motor(args.port, args.model, args.ID, args.baudrate)
