"""
Telegram Bot for Document Generation
Handles user interactions and document generation requests
"""

import asyncio
import os
from datetime import date, datetime
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from bot_storage import storage
from config import TELEGRAM_CONFIG, COMPANY_INFO, BANK_INFO, CLIENT_INFO, FINANCIAL_SETTINGS
from generate_documents import UnifiedDocumentGenerator


class DocumentBot:
    """Telegram bot for document generation"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_CONFIG['bot_token']
        self.authorized_chat_id = TELEGRAM_CONFIG['chat_id']
        self.generator = UnifiedDocumentGenerator()
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    def is_authorized(self, chat_id: str) -> bool:
        """Check if chat_id is authorized"""
        if not self.authorized_chat_id:
            return True  # Allow all if no specific chat_id configured
        return str(chat_id) == str(self.authorized_chat_id)
    
    def get_main_keyboard(self):
        """Get the main keyboard with buttons"""
        keyboard = [
            [KeyboardButton("📋 Создать документы"), KeyboardButton("📊 Статистика")],
            [KeyboardButton("❓ Помощь")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        
        if not self.is_authorized(chat_id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        welcome_text = (
            "🚀 **Document Generator Bot**\n\n"
            "Я помогу вам создать документы (Счет и Акт) с минимальными усилиями!\n\n"
            "**Команды:**\n"
            "• `/generate` - Создать документы\n"
            "• `/status` - Статистика генерации\n"
            "• `/help` - Помощь\n\n"
            "Готов к работе! 📋"
        )
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=self.get_main_keyboard()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self.is_authorized(update.effective_chat.id):
            return
        
        help_text = (
            "📋 **Как использовать бота:**\n\n"
            "1️⃣ Используйте `/generate` для создания документов\n"
            "2️⃣ Я покажу последние услуги и спрошу об обновлениях\n"
            "3️⃣ Введите услуги построчно (одна услуга = одна строка)\n"
            "4️⃣ Подтвердите дату генерации\n"
            "5️⃣ Получите готовые PDF файлы\n\n"
            "**Формат услуг:**\n"
            "```\n"
            "Консультационные услуги\n"
            "Анализ проектов\n"
            "Разработка стратегии\n"
            "```\n\n"
            "**Другие команды:**\n"
            "• `/status` - Посмотреть статистику\n"
            "• `/help` - Эта справка"
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=self.get_main_keyboard()
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self.is_authorized(update.effective_chat.id):
            return
        
        stats = storage.get_generation_stats()
        last_services = storage.get_last_services()
        
        status_text = (
            f"📊 **Статистика генерации:**\n\n"
            f"📋 Всего сгенерировано: {stats['count']}\n"
            f"📅 Последняя генерация: {stats['last_date'] or 'Никогда'}\n"
            f"🔢 Услуг в последнем отчете: {stats['last_services_count']}\n\n"
            f"**Последние услуги:**\n"
            f"```\n{storage.format_services_list(last_services)}\n```"
        )
        
        await update.message.reply_text(
            status_text,
            parse_mode='Markdown',
            reply_markup=self.get_main_keyboard()
        )
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate command"""
        chat_id = update.effective_chat.id
        
        if not self.is_authorized(chat_id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        # Show last services and ask for updates
        last_services = storage.get_last_services()
        
        if last_services:
            services_text = storage.format_services_list(last_services)
            message_text = (
                f"📋 **Последние услуги:**\n\n```\n{services_text}\n```\n\n"
                f"Хотите использовать эти услуги или обновить список?"
            )
            
            keyboard = [
                [InlineKeyboardButton("✅ Использовать эти", callback_data="use_last_services")],
                [InlineKeyboardButton("📝 Обновить список", callback_data="update_services")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
        else:
            message_text = (
                "📋 Нет сохраненных услуг.\n\n"
                "Пожалуйста, введите список услуг (одна услуга на строку):"
            )
            reply_markup = None
            context.user_data['expecting_services'] = True
        
        await update.message.reply_text(
            message_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_authorized(query.message.chat_id):
            return
        
        if query.data == "use_last_services":
            # Use last services, proceed to date confirmation
            services = storage.get_last_services()
            await self.confirm_date(query, context, services)
            
        elif query.data == "update_services":
            # Show previous services without numbers for easy copying
            last_services = storage.get_last_services()
            if last_services:
                plain_list = storage.format_services_list_plain(last_services)
                await query.edit_message_text(
                    f"📝 Введите новый список услуг (одна услуга на строку):\n\n"
                    f"Предыдущий список для копирования:\n```\n{plain_list}\n```",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    "📝 Введите новый список услуг (одна услуга на строку):",
                    parse_mode='Markdown'
                )
            context.user_data['expecting_services'] = True
            
        elif query.data.startswith("date_"):
            # Handle date confirmation
            date_choice = query.data.split("_")[1]
            services = context.user_data.get('pending_services', [])
            
            if date_choice == "today":
                generation_date = date.today()
            else:
                # Parse custom date (format: YYYYMMDD)
                try:
                    date_str = date_choice
                    generation_date = datetime.strptime(date_str, "%Y%m%d").date()
                except ValueError:
                    await query.edit_message_text("❌ Ошибка в формате даты")
                    return
            
            await self.generate_documents(query, context, services, generation_date)
    
    async def confirm_date(self, query_or_update, context: ContextTypes.DEFAULT_TYPE, services: List[str]):
        """Confirm generation date"""
        context.user_data['pending_services'] = services
        
        today = date.today()
        services_text = storage.format_services_list(services)
        
        message_text = (
            f"📅 **Подтвердите дату генерации документов:**\n\n"
            f"**Услуги ({len(services)}):**\n```\n{services_text}\n```\n\n"
            f"Выберите дату:"
        )
        
        keyboard = [
            [InlineKeyboardButton(f"📅 Сегодня ({today.strftime('%d.%m.%Y')})", 
                                callback_data="date_today")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(query_or_update, 'edit_message_text'):
            await query_or_update.edit_message_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await query_or_update.message.reply_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def handle_button_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button text messages"""
        if not self.is_authorized(update.effective_chat.id):
            return
        
        text = update.message.text
        
        if text == "📋 Создать документы":
            await self.generate_command(update, context)
        elif text == "📊 Статистика":
            await self.status_command(update, context)
        elif text == "❓ Помощь":
            await self.help_command(update, context)
        else:
            # Handle services input if we're expecting it
            await self.handle_services_input(update, context)
    
    async def handle_services_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle services input from user"""
        if not context.user_data.get('expecting_services'):
            return
        
        if not self.is_authorized(update.effective_chat.id):
            return
        
        # Parse services from message
        services_text = update.message.text.strip()
        services = [line.strip() for line in services_text.split('\n') if line.strip()]
        
        if not services:
            await update.message.reply_text(
                "❌ Список услуг не может быть пустым. Попробуйте еще раз:"
            )
            return
        
        context.user_data['expecting_services'] = False
        
        # Confirm services and ask for date
        await self.confirm_date(update, context, services)
    
    async def generate_documents(self, query, context: ContextTypes.DEFAULT_TYPE, 
                               services: List[str], generation_date: date):
        """Generate documents and send them to user"""
        
        # Update the message to show generation in progress
        await query.edit_message_text(
            "⏳ Генерирую документы...\n\n"
            f"📋 Услуг: {len(services)}\n"
            f"📅 Дата: {generation_date.strftime('%d.%m.%Y')}"
        )
        
        try:
            # Update CLIENT_INFO with generation date if needed
            client_info = CLIENT_INFO.copy()
            # Keep original contract date, generation_date is just for document dates
            
            # Generate documents
            results = self.generator.generate_both_documents(
                services,
                COMPANY_INFO,
                BANK_INFO,
                client_info,
                FINANCIAL_SETTINGS,
                'signatures/YL_Signature.png',
                generation_date
            )
            
            # Save services for next time
            storage.set_last_services(services)
            
            # Send results
            if results['act_path'] and results['invoice_path']:
                # Send both files
                success_text = (
                    f"✅ **Документы успешно созданы!**\n\n"
                    f"📋 Услуг: {len(services)}\n"
                    f"💰 Сумма: {results['act_amount']:,.0f} RUB\n"
                    f"📅 Дата: {generation_date.strftime('%d.%m.%Y')}\n\n"
                    f"📄 Отправляю файлы..."
                )
                
                await query.edit_message_text(success_text, parse_mode='Markdown')
                
                # Send files
                chat_id = query.message.chat_id
                
                # Send Act
                with open(results['act_path'], 'rb') as act_file:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=act_file,
                        filename=os.path.basename(results['act_path']),
                        caption="📋 Акт оказанных услуг"
                    )
                
                # Send Invoice
                with open(results['invoice_path'], 'rb') as invoice_file:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=invoice_file,
                        filename=os.path.basename(results['invoice_path']),
                        caption="🧾 Счет на оплату"
                    )
                
            else:
                # Error in generation
                error_text = (
                    f"❌ **Ошибка при генерации документов**\n\n"
                    f"Акт: {'✅' if results['act_path'] else '❌'}\n"
                    f"Счет: {'✅' if results['invoice_path'] else '❌'}"
                )
                await query.edit_message_text(error_text, parse_mode='Markdown')
                
        except Exception as e:
            await query.edit_message_text(
                f"❌ **Ошибка при генерации:**\n\n```\n{str(e)}\n```",
                parse_mode='Markdown'
            )
    
    def create_application(self) -> Application:
        """Create and configure the bot application"""
        application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("generate", self.generate_command))
        
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_button_text
        ))
        
        return application
    
    async def run(self):
        """Run the bot"""
        print("🤖 Starting Telegram Bot...")
        print(f"👤 Authorized chat ID: {self.authorized_chat_id or 'All chats'}")
        
        application = self.create_application()
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        print("✅ Bot is running! Press Ctrl+C to stop.")
        
        try:
            # Keep the bot running
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("\n🛑 Stopping bot...")
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()


async def main():
    """Main function to run the bot"""
    try:
        bot = DocumentBot()
        await bot.run()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please check your .env file and ensure TELEGRAM_BOT_TOKEN is set")
    except Exception as e:
        print(f"❌ Bot error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
