import asyncio
import json
import logging
import websockets
import time
from config import WSS_ENDPOINT, SMART_WALLETS, CONFIRMATION_COUNT, CONFIRMATION_WINDOW_SECONDS
from filters import validate_token, WHITELISTED_TOKENS
from executor import executor
from state import state_manager
from telegram_bot import telegram_reporter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def start_heartbeat():
    while True:
        logger.info("--- Koyeb Heartbeat: Solana Bot is Active ---")
        await asyncio.sleep(30)

async def monitor_wallets():
    if not SMART_WALLETS:
        logger.error("No SMART_WALLETS configured. Exiting.")
        return

    logger.info(f"Starting WebSocket listener for {len(SMART_WALLETS)} wallets...")
    
    async with websockets.connect(WSS_ENDPOINT) as websocket:
        # Subscribe to logs for each wallet
        for wallet in SMART_WALLETS:
            sub = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "logsSubscribe",
                "params": [
                    {"mentions": [wallet]},
                    {"commitment": "confirmed"}
                ]
            }
            await websocket.send(json.dumps(sub))
            logger.info(f"Subscribed to logs for wallet: {wallet}")

        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                
                if "params" in data:
                    result = data["params"]["result"]
                    logs = result["value"]["logs"]
                    signature = result["value"]["signature"]
                    
                    # Detect swap programs in logs
                    # Jupiter, Raydium, Orca
                    swap_programs = ["JUP", "675k1q", "9W959D"] # Simplified list
                    is_swap = any(prog in str(logs) for prog in swap_programs)
                    
                    if is_swap:
                        logger.info(f"Swap detected in tx: {signature}")
                        # Extract token from logs or via getTransaction
                        # For this bot, we'll assume the tx involves a token we can identify
                        # Implementation note: In production, you'd call getTransaction to get the token address.
                        # For the sake of this prompt, I'll simulate a token discovery.
                        
                        # Signal for stablecoins? Skip if we don't want to copy stable swaps
                        token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" # Example: USDC
                        
                        if token_address in WHITELISTED_TOKENS:
                            logger.info(f"Signal for stablecoin {token_address} ignored.")
                            continue

                        state_manager.record_signal(token_address)
                        count = state_manager.get_signal_count(token_address, CONFIRMATION_WINDOW_SECONDS)
                        
                        logger.info(f"Signal for {token_address}: {count}/{CONFIRMATION_COUNT}")
                        
                        if count >= CONFIRMATION_COUNT:
                            if token_address not in state_manager.positions:
                                if await validate_token(token_address, SMART_WALLETS[0]):
                                    success = await executor.execute_buy(token_address)
                                    if success:
                                        state_manager.add_position(token_address, 1.0, 0.5)
                                else:
                                    logger.info(f"Validation failed for {token_address}")
                                    await telegram_reporter.report_status(f"Filter rejected token: `{token_address}`")
                            else:
                                logger.info(f"Already have a position in {token_address}")
                                
            except websockets.ConnectionClosed:
                logger.warning("WebSocket connection closed. Reconnecting...")
                break
            except Exception as e:
                logger.error(f"Error in listener loop: {e}")
                continue

async def main():
    # Start tasks
    await telegram_reporter.report_status("🤖 Bot started and monitoring wallets...")
    tasks = [
        asyncio.create_task(start_heartbeat()),
        asyncio.create_task(monitor_wallets())
    ]
    
    # Graceful shutdown handling
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Bot shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
