#!/usr/bin/env python3
"""
Setup script for Telegram Bot
Creates necessary files and explains configuration
"""

import os
import shutil


def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = '.env'
    template_file = 'env.template'
    
    if os.path.exists(env_file):
        print(f"✅ {env_file} already exists")
        return False
    
    if not os.path.exists(template_file):
        print(f"❌ {template_file} not found")
        return False
    
    # Copy template to .env
    shutil.copy2(template_file, env_file)
    print(f"✅ Created {env_file} from {template_file}")
    return True


def check_signature_file():
    """Check if signature file exists"""
    signature_path = 'signatures/YL_Signature.png'
    
    if os.path.exists(signature_path):
        print(f"✅ Signature file exists: {signature_path}")
        return True
    else:
        print(f"⚠️  Signature file not found: {signature_path}")
        print("   Place your signature image in the signatures/ folder")
        return False


def print_configuration_guide():
    """Print configuration instructions"""
    print("\n" + "="*60)
    print("🤖 TELEGRAM BOT CONFIGURATION GUIDE")
    print("="*60)
    
    print("\n1. 🔑 CREATE TELEGRAM BOT:")
    print("   • Message @BotFather on Telegram")
    print("   • Send: /newbot")
    print("   • Follow instructions to get your bot token")
    
    print("\n2. 📝 GET CHAT ID:")
    print("   • Start your bot and send it a message")
    print("   • Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("   • Find your chat ID in the response")
    
    print("\n3. ⚙️ CONFIGURE ENVIRONMENT:")
    print("   • Edit the .env file with your bot token and chat ID")
    print("   • Update other settings as needed")
    
    print("\n4. 🚀 START THE BOT:")
    print("   • Install dependencies: pip install -r requirements.txt")
    print("   • Run: python telegram_bot.py")
    
    print("\n5. 📋 USAGE:")
    print("   • Send /start to your bot")
    print("   • Use /generate to create documents")
    print("   • Follow the interactive prompts")
    
    print(f"\n{'='*60}")


def main():
    """Main setup function"""
    print("🔧 Setting up Telegram Bot...")
    
    # Create .env file
    env_created = create_env_file()
    
    # Check signature
    check_signature_file()
    
    # Check bot storage
    if not os.path.exists('bot_data.json'):
        print("ℹ️  bot_data.json will be created automatically on first run")
    else:
        print("✅ bot_data.json exists")
    
    # Print configuration guide
    print_configuration_guide()
    
    if env_created:
        print("\n⚠️  IMPORTANT: Edit the .env file with your bot credentials before running!")
    
    print("\n✅ Setup complete!")


if __name__ == "__main__":
    main()
