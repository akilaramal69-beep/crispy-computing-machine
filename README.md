# Solana Smart Money Copy-Trading Bot (2026)

A production-ready, Dockerized Solana copy-trading bot optimized for low latency and anti-MEV protection. Built with Python and designed to run as a **Koyeb Worker**.

## 🚀 Features

- **Jito Bundle Submission**: All trades are sent as Jito bundles to prevent sandwich attacks and front-running.
- **Jupiter V6 Aggregator**: Uses Jupiter Swap API for best price execution and liquidity.
- **WebSocket Monitoring**: Low-latency Helius/QuickNode WebSocket listener monitors up to 5 smart wallets.
- **Safety Filters**:
  - **Market Cap**: Filter out tokens with low liquidity.
  - **Freeze Authority**: Prevents buying rugs with active freeze authority.
  - **Honeypot Detection**: Simulates a sell via Jupiter to ensure exit liquidity.
- **Multi-Wallet Confirmation**: Only executes a trade if 2+ monitored wallets buy the same token in a 60s window.
- **State Persistence**: Positions are saved to `positions.json` to survive restarts.

## 🛠️ Installation

### 1. Prerequisites
- [Docker](https://www.docker.com/)
- [Helius](https://helius.dev/) or QuickNode API Key
- Solana Wallet Private Key (Base58)

### 2. Setup
Clone the repository and install dependencies (if running locally):
```bash
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

## 🚢 Deployment on Koyeb

This bot is designed to run as a **Worker** service (no public ports needed).

1.  **Create App**: Go to Koyeb and create a new Web Service or Worker.
2.  **Environment Variables**: 
    - Set `PRIVATE_KEY` as a Secret.
    - Set `RPC_ENDPOINT`, `WSS_ENDPOINT`, `SMART_WALLETS`, etc.
3.  **Deploy**: Connect your GitHub repository or use the provided `Dockerfile`.

## ⚙️ Configuration Parameters

| Variable | Description | Default |
| :--- | :--- | :--- |
| `MAX_POSITION_SOL` | Amount of SOL to spend per trade | `0.5` |
| `JITO_TIP_AMOUNT_SOL`| Tip for Jito validators (needed for bundles) | `0.0001` |
| `STOP_LOSS_PERCENT` | Auto-sell at -X% from entry | `15` |
| `CONFIRMATION_COUNT`| Number of wallets required for a trade | `2` |
| `TELEGRAM_BOT_TOKEN`| Token from BotFather | `None` |
| `TELEGRAM_CHAT_ID` | Your Telegram User/Chat ID | `None` |

## ⚠️ Disclaimer

Trading cryptocurrencies, especially meme coins on Solana, carries significant risk. This software is provided "as is" and the developers are not responsible for any financial losses. **Test with small amounts first!**
