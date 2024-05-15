

---

# Discord Vanity URL Sniper

This script snipes available vanity URLs for Discord servers and sends a notification to a specified webhook upon successful snipe, including the time taken for sniping.

## Prerequisites

- Python 3.7 or higher
- Required Python packages can be installed using `pip install -r requirements.txt`

## Configuration

1. Create a `config.json` file with the following structure:
    ```json
    {
        "token": "token",
        "webhook_url": "webhook",
        "guild_id": "guild id"
    }
    ```
    - Replace `"guild id"` with your Discord server's ID.
    - Replace `"token"` with your Discord bot's token.
    - Replace `"webhook"` with the URL of the Discord webhook where notifications will be sent.

2. Create a `vanities.txt` file containing a list of vanity URLs to snipe, with each URL on a new line.

## Usage

Run the script using the following command:
```
python3 main.py
```

## Logging

The script uses logging for output. You can adjust the logging level and configuration as needed by modifying the `logging.basicConfig()` call in the script.

## Notes

- This script utilizes asynchronous HTTP requests for improved performance and efficiency.
- It uses the `aiohttp` library for making asynchronous HTTP requests and `BeautifulSoup` for parsing HTML.
- Upon successful snipe, the script sends a notification to the specified Discord webhook, including the duration taken for sniping the vanity URL.

---

