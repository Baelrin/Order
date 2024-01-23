# Discord Role Changer

This is a Discord bot implementation that changes roles for users who have joined the server for longer than a certain period. It reads the configuration from a `config.json` file and uses the values to perform its operations.

## Installation

Clone the repository:
`bash git clone https://github.com/YourUsername/discord-role-changer.git`

Navigate to the project directory:
`bash cd discord-role-changer`

Create a `config.json` file with the following structure:
```json
{
 "TOKEN": "<your-bot-token>",
 "ADMIN_ROLE_ID": "<admin-role-id>",
 "OLD_ROLE_ID": "<old-role-id>",
 "NEW_ROLE_ID": "<new-role-id>",
 "CHANNEL_ID": "<channel-id>",
 "JOIN_TIME_THRESHOLD": <threshold-in-seconds>,
 "TIMEZONE": "<timezone>",
 "PREFIX": "<command-prefix>",
 "LOG_FILE": "<log-file-path>"
}
```
Replace the placeholders with your actual values.

Run the bot:
`bash python main.py`

## Usage

The bot listens for a command `C` (or whatever prefix you set in the config followed by 'C'). When this command is issued by a user with the admin role, the bot will change the roles for users who have been in the server for longer than the threshold specified in the config.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
