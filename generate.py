#!/usr/bin/env python3
"""
Simple Document Generator
Generate both Invoice and Act PDFs with minimal input

Usage:
    python generate.py
"""

from config import BANK_INFO, CLIENT_INFO, COMPANY_INFO, FINANCIAL_SETTINGS
from generate_documents import UnifiedDocumentGenerator

def main():
    """
    Simple interface - just provide your services!
    All other data comes from config.py
    """
    
    # 🎯 ONLY INPUT REQUIRED: List of services
    services = [
        'Анализ и реализация инвестиционных проектов (Кракен, Citymall)',
        'Ведение проекта редомицилиации MLOne',
        'Актуализация соглашений по существующим инвестициям и анализ перспективных инвестиций в BeOnd',
        'Реализация проекта по аналитике портфельной аллокации'
    ]
    
    # 🚀 Generate both documents
    generator = UnifiedDocumentGenerator()
    results = generator.generate_both_documents(
        services,
        COMPANY_INFO,
        BANK_INFO,
        CLIENT_INFO,
        FINANCIAL_SETTINGS,
        'signatures/YL_Signature.png'
        )  # Using default date (today)
    
    # 📊 Summary
    print(f"\n{'='*60}")
    print("📋 DOCUMENT GENERATION COMPLETE")
    print(f"{'='*60}")
    
    if results['act_path']:
        print(f"✅ Act:     {results['act_path']}")
    else:
        print("❌ Act:     FAILED")
        
    if results['invoice_path']:
        print(f"✅ Invoice: {results['invoice_path']}")
    else:
        print("❌ Invoice: FAILED")
    
    if results['act_amount']:
        print(f"💰 Amount:  {results['act_amount']:,.0f} RUB")
    
    print(f"📂 Location: output/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
