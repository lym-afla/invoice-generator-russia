"""
Unified Bot Runner
Starts whichever bots have tokens configured in .env
"""

import asyncio

from config import TELEGRAM_CONFIG, DISCORD_CONFIG


async def run_telegram():
    try:
        from telegram_bot import DocumentBot
        await DocumentBot().run()
    except Exception as e:
        print(f'❌ Telegram bot error: {e}')


async def run_discord():
    try:
        from discord_bot import DiscordDocumentBot
        await DiscordDocumentBot().run()
    except Exception as e:
        print(f'❌ Discord bot error: {e}')


async def main():
    tasks = []

    if TELEGRAM_CONFIG['bot_token']:
        tasks.append(asyncio.create_task(run_telegram()))

    if DISCORD_CONFIG['bot_token']:
        tasks.append(asyncio.create_task(run_discord()))

    if not tasks:
        print('❌ No bot tokens configured. Set TELEGRAM_BOT_TOKEN or DISCORD_BOT_TOKEN in .env')
        return

    print(f'🚀 Starting {len(tasks)} bot(s)...')
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n🛑 Stopping bots...')
