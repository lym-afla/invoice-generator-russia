#!/usr/bin/env python3
"""
Example usage of bot storage and document generation
Shows how to interact with the bot components programmatically
"""

from bot_storage import storage
from config import COMPANY_INFO, BANK_INFO, CLIENT_INFO, FINANCIAL_SETTINGS
from generate_documents import UnifiedDocumentGenerator


def example_storage_usage():
    """Example of using bot storage"""
    print("📋 Bot Storage Example")
    print("=" * 40)
    
    # Get current services
    services = storage.get_last_services()
    print(f"Current services ({len(services)}):")
    print(storage.format_services_list(services))
    
    # Get statistics
    stats = storage.get_generation_stats()
    print(f"\nGeneration stats:")
    print(f"  Count: {stats['count']}")
    print(f"  Last date: {stats['last_date']}")
    print(f"  Last services count: {stats['last_services_count']}")


def example_document_generation():
    """Example of generating documents programmatically"""
    print("\n🚀 Document Generation Example")
    print("=" * 40)
    
    # Custom services
    services = [
        'Разработка стратегии развития',
        'Анализ рыночных возможностей',
        'Консультации по инвестициям'
    ]
    
    print(f"Generating documents for {len(services)} services...")
    
    # Generate documents
    generator = UnifiedDocumentGenerator()
    results = generator.generate_both_documents(
        services,
        COMPANY_INFO,
        BANK_INFO,
        CLIENT_INFO,
        FINANCIAL_SETTINGS,
        'signatures/YL_Signature.png'
    )
    
    # Save services to storage
    storage.set_last_services(services)
    
    # Show results
    print(f"Results:")
    print(f"  Act: {'✅' if results['act_path'] else '❌'}")
    print(f"  Invoice: {'✅' if results['invoice_path'] else '❌'}")
    if results['act_amount']:
        print(f"  Amount: {results['act_amount']:,.0f} RUB")


def example_configuration():
    """Example of configuration usage"""
    print("\n⚙️ Configuration Example")
    print("=" * 40)
    
    print(f"Company: {COMPANY_INFO['name']}")
    print(f"Bank: {BANK_INFO['bank_name']}")
    print(f"Client: {CLIENT_INFO['name']}")
    print(f"Base rate: {FINANCIAL_SETTINGS['base_rate']:,} {FINANCIAL_SETTINGS['currency']}")


def main():
    """Main example function"""
    print("🤖 Bot Components Example")
    print("=" * 50)
    
    # Show current configuration
    example_configuration()
    
    # Show storage usage
    example_storage_usage()
    
    # Generate documents (uncomment to test)
    # example_document_generation()
    
    print(f"\n{'=' * 50}")
    print("💡 To start the Telegram bot, run: python telegram_bot.py")


if __name__ == "__main__":
    main()
