#!/usr/bin/env python3
"""
Main Act Generator Script
Simplified interface for generating service acts
"""

from datetime import date
from act_generator import ActGenerator
from config import FINANCIAL_SETTINGS


def create_act(
    services_list=None,
    currency='USD',
    customer_name=None,
    contract_date=None
):
    """
    Create a service act with given parameters
    
    Args:
        services_list (list): List of service dictionaries with description, start_date, end_date
                             OR list of strings (descriptions only - dates auto-generated)
        currency (str): Currency code (default: 'USD')
        customer_name (str): Customer name (REQUIRED)
        contract_date (date): Contract date (REQUIRED)
    
    Returns:
        str: Path to generated PDF or None if failed
        
    Raises:
        ValueError: If contract_date or customer_name is None
    """
    
    generator = ActGenerator()
    
    result_path = generator.generate_act(
        services_list=services_list,
        currency=currency,
        customer_name=customer_name,
        contract_date=contract_date,
        base_rate=FINANCIAL_SETTINGS['base_rate']
    )
    
    if result_path:
        print(f"✅ Act generated: {result_path}")
    else:
        print("❌ Act generation failed")
    
    return result_path


def main():
    """Main function with examples"""
    print("📋 Service Act Generator")
    print("=" * 50)
    
    print("\n📋 Generating act...")
    # Services as simple strings - dates will be auto-generated (26th to 26th)
    custom_services = [
        'Анализ и реализация инвестиционных проектов (Кракен, Citymall)',
        'Ведение проекта редомицилиации MLOne',
        'Актуализация соглашений по существующим инвестициям и анализ перспективных инвестиций в BeOnd',
        'Реализация проекта по аналитике портфельной аллокации'
    ]
    
    create_act(
        contract_date=date(2025, 5, 26),
        services_list=custom_services,
        customer_name="Гуринов Вадим Александрович"
    )
    
    print("\n✅ All acts generated successfully!")
    print("📂 Check the 'output' folder for your PDFs")


if __name__ == "__main__":
    main()
