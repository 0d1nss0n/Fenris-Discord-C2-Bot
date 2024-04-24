# Fenris Discord C2 Bot

Fenris is a Discord bot designed for Command and Control (C2) purposes. It provides various functionalities to interact with a Discord server, including executing commands, uploading and downloading files, taking screenshots, and more.

## Features

- **Command Execution**: Execute PowerShell commands on the host system.
- **File Management**: Upload and download files to and from the Discord server.
- **Keylogging**: Start and stop a keylogger to capture keystrokes.
- **Screenshot**: Take a screenshot of the host system and upload it.
- **Heartbeat**: Periodically sends a heartbeat message to indicate the bot's online status.
- **Bot Termination**: Stop the bot and delete its channel from the Discord server.

## Prerequisites

Before running Fenris, ensure you have the following prerequisites installed:

- Python 3.x

## Installation

1. Clone or download the Fenris repository.
2. Navigate to the project directory.
3. Install the required dependencies using pip:


pip install -r requirements.txt

## Configuration

1.Replace the TOKEN variable in fenris.py with your Discord bot token.
2.Set the GUILD_ID variable to your Discord server ID.
3.Customize other settings as per your requirements.

## Usage

To start Fenris, run the following command:

python3 fenris.py

Once the bot is running, you can interact with it using Discord commands.

## Commands

/cmd <command>: Execute a PowerShell command.
/url: Show the URL of the last uploaded file.
/kstart: Start the keylogger.
/kstop: Stop the keylogger and save the log.
/ping: Check if the bot is up and measure latency.
/upload <file_path>: Upload a file to the Discord channel.
/download <file_path>: Download the last uploaded file to a specified path.
/screenshot: Take a screenshot and upload it.
/kill: Stop the bot and delete its channel.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, feel free to open an issue or submit a pull request.