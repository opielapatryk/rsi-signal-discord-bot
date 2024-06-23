# Discord RSI Bot

This project implements a Discord bot that fetches spot K-line data for the SOL/USDT trading pair from Bybit, calculates the Relative Strength Index (RSI) based on the closing prices, and sends a notification to a Discord channel if the RSI value is over 70 (overbought) or below 30 (oversold). The bot operates on a 1-hour time frame.

## Features

- Fetches 1-hour K-line data for SOL/USDT from Bybit.
- Calculates RSI using the closing prices.
- Sends alerts to a Discord channel when RSI is overbought or oversold.
- Runs inside a Docker container.

## Prerequisites

- Docker
- Discord bot token
- Channel ID for Discord notifications

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/opielapatryk/rsi-signal-discord-bot.git
   cd rsi-signal-discord-bot
   ```

2. **Configuration**

   Create a `.env` file in the root directory and add your Discord bot token and channel ID:

   ```dotenv
   DISCORD_TOKEN=your-discord-bot-token
   CHANNEL_ID=your-channel-id
   ```

3. **Build and Run the Docker Container**

   Use Docker Compose to build and run the container:

   ```bash
   docker-compose up -d
   ```

## Running the Bot

- The bot will start automatically and fetch K-line data for the SOL/USDT trading pair every hour.
- It calculates the RSI and sends a notification to the specified Discord channel if the RSI is over 70 or below 30.

## File Structure

```
rsi-signal-discord-bot/
├── bot.py             # Main bot code
├── Dockerfile         # Dockerfile for containerizing the application
├── docker-compose.yml # Docker Compose file
├── .env               # Holds DISCORD_TOKEN and CHANNEL_ID
├── requirements.txt   # Python dependencies
├── .gitignore         # Ignore ceratin files on commits
└── README.md          # Project documentation
└── LICENSE            # MIT License
```

## Technical Details

- **API**: Uses Bybit API to fetch K-line data.
- **RSI Calculation**: Utilizes `pandas_ta` library for calculating the RSI.
- **Discord**: Uses `discord.py` library for interacting with Discord.

## Questions

For any questions or clarifications, please contact [patryk.opiela02@gmail.com].

## License

This project is licensed under the MIT License.