"""
Unified Bot Runner
Starts whichever bots have tokens configured in .env
"""

import asyncio

from config import TELEGRAM_CONFIG, DISCORD_CONFIG


async def main():
    tasks = []

    if TELEGRAM_CONFIG['bot_token']:
        from telegram_bot import DocumentBot
        tasks.append(asyncio.create_task(DocumentBot().run()))

    if DISCORD_CONFIG['bot_token']:
        from discord_bot import DiscordDocumentBot
        tasks.append(asyncio.create_task(DiscordDocumentBot().run()))

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
    except ValueError as e:
        print(f'❌ Configuration error: {e}')
    except Exception as e:
        print(f'❌ Bot error: {e}')
