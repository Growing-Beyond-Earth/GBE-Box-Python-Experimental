# Growing Beyond Earth 3.0

## ⚠️ Highly Experimental Code ⚠️

All of the code here is experimental and mostly untested. Expect instability and errors.

## Todo 📜
- Finish the backend
- Add support for more devices
- Fix Red led pulsing on startup (due to "disconnected" devices that were never connected in the first place)
- Finish cryptography, the pico should not be sending it's raw board ID, rather, sending an encrypted version using the public key in key.json, and decrypted on the server using the private key. The encrypt function is already there.

# Growing Beyond Earth Control Box 🌱📦

This Micropython project is designed to control the LED lights, fans, and other accessories in a Growing Beyond Earth (GBE) growth chamber. The device is based on a Raspberry Pi Pico W microcontroller. It provides control for a variety of sensors and devices, such as environmental sensors.

## Features 🚀

- Control of LED lights and fan in the GBE growth chamber.
- Ability to connect and control a variety of sensors such as soil moisture sensors, temperature sensors, and electrical current sensors.
- Ability to sync with network time or use an internal RTC (Real-Time Clock) for accurate timestamps.
- Data logging capability to monitor the status of the system and sensors online. <----------------TODO
- MQTT protocol for data transfer to a server.
- Resilience against hardware disconnection or failure.
- The control box also includes a status LED that provides visual feedback about the system's status.

## Setup 🛠️

Before running the main program, make sure to run `SETUP.py` to initialize and setup necessary files and settings. The program checks for the required libraries and files in the `/lib/` directory, and configuration files in the `/config/` directories. Make sure all the necessary files are present.

## Network and Hardware Setup 📡

This program leverages Wi-Fi for network connectivity, specifically for wireless logging. However, the presence of Wi-Fi configuration is mandatory for the program to run. Before starting the program, make sure that the Wi-Fi configuration file (wifi_settings.json) exists in the /config/ directory. If the file does not exist, the program will throw an error and halt. You can setup wifi by running SETUP.PY

## LED and Fan Control 💡🌬️

LED lights are controlled using PWM (Pulse Width Modulation) on GPIO Pins 0-3. The fan is also controlled using PWM on GPIO Pin 4. All channels operate at a frequency of 20kHz.

## Data Logging 📈

Data is logged to a GBE server for real-time analysis. In case of a network interruption, the program temporarily stores the data locally in the /logs/ directory as a json file. Once the network connectivity is restored, the locally stored data is sent to the GBE server, ensuring no data loss.

## Error Handling and Resilience 🚧

The program is designed to be resilient against hardware disconnections or failures. It periodically checks for the connection status of various sensors and devices. If any disconnection or failure is detected, it will attempt to reconnect.

## How to Contribute 🤝

Contributions are always welcome! If you want to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## Join Our Community 🌍
Our community plays a pivotal role in the development and refinement of this program. We encourage everyone to join us, share their experiences, ask questions, and provide feedback.

The best place to connect with us is on our Discord server. Here, you can interact with both the developers and other users. It's a great place to learn more about the program, stay updated with the latest changes, and help us create a better tool for everyone.

Here's the link to our Discord server: https://discord.gg/k8xd4xTD87

We look forward to seeing you there!

## Links 🔗

- Project repository: https://github.com/Growing-Beyond-Earth/GBE-Box-Python-Experimental

## Licensing ⚖️

The code in this project is licensed under MIT license.
