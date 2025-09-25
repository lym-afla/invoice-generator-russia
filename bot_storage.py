"""
Simple storage for Telegram bot data
Stores previous services and user preferences
"""

import json
import os
from datetime import datetime
from typing import List, Dict


class BotStorage:
    """Simple JSON-based storage for bot data"""
    
    def __init__(self, storage_file: str = 'bot_data.json'):
        self.storage_file = storage_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading storage file: {e}")
                return self._get_default_data()
        else:
            return self._get_default_data()
    
    def _get_default_data(self) -> Dict:
        """Get default storage structure"""
        return {
            'last_services': [
                'Анализ и реализация инвестиционных проектов (Кракен, Citymall)',
                'Ведение проекта редомицилиации MLOne',
                'Актуализация соглашений по существующим инвестициям и анализ перспективных инвестиций в BeOnd',
                'Реализация проекта по аналитике портфельной аллокации'
            ],
            'last_generation_date': None,
            'generation_count': 0,
            'user_preferences': {
                'default_services_count': 4
            }
        }
    
    def save_data(self) -> bool:
        """Save data to storage file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"❌ Error saving storage file: {e}")
            return False
    
    def get_last_services(self) -> List[str]:
        """Get the last used services"""
        return self.data.get('last_services', [])
    
    def set_last_services(self, services: List[str]) -> bool:
        """Set the last used services"""
        self.data['last_services'] = services
        self.data['last_generation_date'] = datetime.now().isoformat()
        self.data['generation_count'] = self.data.get('generation_count', 0) + 1
        return self.save_data()
    
    def get_generation_stats(self) -> Dict:
        """Get generation statistics"""
        return {
            'count': self.data.get('generation_count', 0),
            'last_date': self.data.get('last_generation_date'),
            'last_services_count': len(self.get_last_services())
        }
    
    def format_services_list(self, services: List[str]) -> str:
        """Format services list for display"""
        if not services:
            return "Нет сохраненных услуг"
        
        formatted = []
        for i, service in enumerate(services, 1):
            formatted.append(f"{i}. {service}")
        
        return "\n".join(formatted)


# Global storage instance
storage = BotStorage()
