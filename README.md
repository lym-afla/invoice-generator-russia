# 🧾 Russian Invoice Generator

Профессиональная система автоматизированной генерации счетов-фактур с полной поддержкой российских стандартов и требований.

## ✨ Возможности

- 📄 **Генерация PDF счетов** из настраиваемых шаблонов
- 📱 **QR-коды для оплаты** (стандарт СПКР ГОСТ Р 56042-2014)
- 🔢 **Автоматическая нумерация** счетов (восьмеричная система yyyymm)
- 🔤 **Конвертация сумм в текст** на русском языке с правильными склонениями
- 🖊️ **Цифровые подписи** (изображения подписей руководителя и бухгалтера)
- 💰 **Автоматический расчет НДС** с настраиваемыми ставками
- 🖥️ **Кроссплатформенность** (Windows/Linux/macOS)
- ⚡ **Batch обработка** для массовой генерации счетов

## Установка

1. Клонировайте репозиторий:
```bash
git clone <repository-url>
cd invoice-generator
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте необходимые папки:
```bash
mkdir -p templates output signatures
```

## 💻 Использование

### Простейший пример

```python
# Windows
from invoice_generator_reportlab import InvoiceGeneratorReportLab as Generator

# Linux/macOS  
# from invoice_generator import InvoiceGenerator as Generator

generator = Generator()

invoice_data = {
    'client_name': 'ООО "Клиент"',
    'client_address': 'г. Москва, ул. Примерная, д. 123',
    'items': [
        {'description': 'Web-разработка', 'quantity': 1, 'price': 50000, 'total': 50000},
        {'description': 'Техподдержка', 'quantity': 3, 'price': 15000, 'total': 45000},
    ],
    'subtotal': 95000,
    'vat_rate': 20,
    'vat_amount': 19000,
    'total_amount': 114000,
    'payment_data': {
        'name': 'ООО "Ваша Компания"',
        'personal_acc': '40702810900000000001',
        'bank_name': 'ПАО "Сбербанк"',
        'bic': '044525225',
        'corresp_acc': '30101810400000000225',
        'payee_inn': '1234567890',
        'kpp': '123456789',
        'sum': '114000',
        'purpose': 'Оплата по счету №INV-613414'
    }
}

pdf_path = generator.generate_invoice(invoice_data)
print(f"✅ Счет создан: {pdf_path}")
```

### С подписями руководителя

```python
from signature_utils import SignatureManager, add_signature_to_invoice_data

# Настройка подписей
sig_manager = SignatureManager()
invoice_data = add_signature_to_invoice_data(
    invoice_data, 
    sig_manager,
    director_sig="director_signature.png",
    accountant_sig="accountant_signature.png"
)

pdf_path = generator.generate_invoice(invoice_data)
```

### Массовая генерация

```python
# Смотрите example_usage.py для полного примера batch-генерации
clients = ['ООО "Альфа"', 'ИП Иванов И.И.', 'ЗАО "Бета"']
for client in clients:
    # ... подготовка данных
    pdf_path = generator.generate_invoice(client_data)
    print(f"Создан счет для {client}: {pdf_path}")
```

## ⚙️ Настройка

### Конфигурация компании

Создайте файл `local_config.py` (автоматически создается при запуске `setup.py`):

```python
COMPANY_INFO = {
    'name': 'ООО "Ваша Компания"',
    'address': 'г. Москва, ул. Тверская, д. 10, офис 205',
    'inn': '1234567890',
    'kpp': '123456789',
    'phone': '+7 (495) 123-45-67',
    'email': 'info@yourcompany.ru'
}

BANK_INFO = {
    'name': 'ООО "Ваша Компания"',
    'personal_acc': '40702810900000000001',
    'bank_name': 'ПАО "Сбербанк"',
    'bic': '044525225',
    'corresp_acc': '30101810400000000225',
    'payee_inn': '1234567890',
    'kpp': '123456789'
}
```

### Добавление подписей

1. Сохраните изображения подписей в папку `signatures/`:
   - `director_signature.png` - подпись руководителя
   - `accountant_signature.png` - подпись главного бухгалтера

2. Поддерживаемые форматы: PNG, JPG, JPEG, GIF
3. Рекомендуемый размер: 200x50 пикселей
4. Прозрачный фон (PNG) для лучшего качества

## Структура проекта

```
invoice-generator/
├── invoice_generator.py    # Основной модуль
├── config.py              # Конфигурация
├── requirements.txt       # Зависимости
├── templates/            # HTML-шаблоны
│   └── invoice.html      # Шаблон счета
├── output/               # Сгенерированные PDF
├── signatures/           # Файлы подписей
└── README.md            # Документация
```

## Шаблоны

Шаблоны используют Jinja2 синтаксис. Доступные переменные:

- `invoice_number` - номер счета
- `invoice_date` - дата счета
- `client_name` - название клиента
- `items` - список товаров/услуг
- `total_amount` - общая сумма
- `amount_in_words` - сумма прописью
- `qr_code` - QR-код для оплаты

## QR-коды

QR-коды генерируются по стандарту СПКР (ГОСТ Р 56042-2014) и содержат:
- Название получателя
- Банковские реквизиты
- Сумму платежа
- Назначение платежа

## Нумерация счетов

Номера счетов генерируются по принципу:
```
YYYYMM → восьмеричное число → INV-XXXXXXX
```

Например: 202412 → 754734₈ → INV-754734

## Требования

- Python 3.7+
- WeasyPrint (для PDF)
- Jinja2 (для шаблонов)
- qrcode (для QR-кодов)
- num2words (для конвертации в слова)

## Лицензия

MIT License
