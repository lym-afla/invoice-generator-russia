"""
Discord Bot for Document Generation
Handles user interactions and document generation requests via Discord
"""

import asyncio
import os
from datetime import date, datetime
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from bot_storage import storage
from config import DISCORD_CONFIG, COMPANY_INFO, BANK_INFO, CLIENT_INFO, FINANCIAL_SETTINGS
from generate_documents import UnifiedDocumentGenerator


class ServicesInputModal(discord.ui.Modal, title='Введите список услуг'):
    """Modal popup for entering services list"""

    services_input = discord.ui.TextInput(
        label='Услуги (одна на строку)',
        style=discord.TextStyle.paragraph,
        placeholder='Консультационные услуги\nАнализ проектов\nРазработка стратегии',
        required=True,
        max_length=4000
    )

    def __init__(self, bot_ref: 'DiscordDocumentBot'):
        super().__init__()
        self.bot_ref = bot_ref

    async def on_submit(self, interaction: discord.Interaction):
        services = [line.strip() for line in self.services_input.value.split('\n') if line.strip()]

        if not services:
            await interaction.response.send_message(
                '❌ Список услуг не может быть пустым.',
                ephemeral=True
            )
            return

        await self.bot_ref.confirm_date(interaction, services)


class ServiceChoiceView(discord.ui.View):
    """View with buttons to choose: use last services or update list"""

    def __init__(self, bot_ref: 'DiscordDocumentBot'):
        super().__init__(timeout=180)
        self.bot_ref = bot_ref

    @discord.ui.button(label='Использовать эти', style=discord.ButtonStyle.success, emoji='✅')
    async def use_last_services(self, interaction: discord.Interaction, button: discord.ui.Button):
        services = storage.get_last_services()
        await self.bot_ref.confirm_date(interaction, services)

    @discord.ui.button(label='Обновить список', style=discord.ButtonStyle.secondary, emoji='📝')
    async def update_services(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ServicesInputModal(self.bot_ref)
        await interaction.response.send_modal(modal)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class DateConfirmView(discord.ui.View):
    """View with date confirmation button"""

    def __init__(self, bot_ref: 'DiscordDocumentBot', services: List[str]):
        super().__init__(timeout=180)
        self.bot_ref = bot_ref
        self.services = services

    @discord.ui.button(
        label=f'Сегодня ({date.today().strftime("%d.%m.%Y")})',
        style=discord.ButtonStyle.primary,
        emoji='📅'
    )
    async def confirm_today(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot_ref.generate_and_send(interaction, self.services, date.today())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class DiscordDocumentBot:
    """Discord bot for document generation"""

    def __init__(self):
        self.bot_token = DISCORD_CONFIG['bot_token']
        self.authorized_user_id = DISCORD_CONFIG['authorized_user_id']
        self.generator = UnifiedDocumentGenerator()

        if not self.bot_token:
            raise ValueError("DISCORD_BOT_TOKEN not found in environment variables")

    def is_authorized(self, user_id) -> bool:
        if not self.authorized_user_id:
            return True
        return str(user_id) == str(self.authorized_user_id)

    async def start_command(self, interaction: discord.Interaction):
        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message('❌ Unauthorized access', ephemeral=True)
            return

        welcome_text = (
            "**Document Generator Bot**\n\n"
            "Я помогу вам создать документы (Счет и Акт) с минимальными усилиями!\n\n"
            "**Команды:**\n"
            "• `/generate` - Создать документы\n"
            "• `/status` - Статистика генерации\n"
            "• `/help` - Помощь\n\n"
            "Готов к работе!"
        )

        await interaction.response.send_message(welcome_text, ephemeral=True)

    async def help_command(self, interaction: discord.Interaction):
        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message('❌ Unauthorized access', ephemeral=True)
            return

        help_text = (
            "**Как использовать бота:**\n\n"
            "1️⃣ Используйте `/generate` для создания документов\n"
            "2️⃣ Я покажу последние услуги и спрошу об обновлениях\n"
            "3️⃣ Введите услуги построчно (одна услуга = одна строка)\n"
            "4️⃣ Подтвердите дату генерации\n"
            "5️⃣ Получите готовые PDF файлы\n\n"
            "**Другие команды:**\n"
            "• `/status` - Посмотреть статистику\n"
            "• `/help` - Эта справка"
        )

        await interaction.response.send_message(help_text, ephemeral=True)

    async def status_command(self, interaction: discord.Interaction):
        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message('❌ Unauthorized access', ephemeral=True)
            return

        stats = storage.get_generation_stats()
        last_services = storage.get_last_services()

        status_text = (
            f"**Статистика генерации:**\n\n"
            f"Всего сгенерировано: {stats['count']}\n"
            f"Последняя генерация: {stats['last_date'] or 'Никогда'}\n"
            f"Услуг в последнем отчете: {stats['last_services_count']}\n\n"
            f"**Последние услуги:**\n"
            f"```\n{storage.format_services_list(last_services)}\n```"
        )

        await interaction.response.send_message(status_text, ephemeral=True)

    async def generate_command(self, interaction: discord.Interaction):
        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message('❌ Unauthorized access', ephemeral=True)
            return

        last_services = storage.get_last_services()

        if last_services:
            services_text = storage.format_services_list(last_services)
            message_text = (
                f"**Последние услуги:**\n\n```\n{services_text}\n```\n\n"
                f"Хотите использовать эти услуги или обновить список?"
            )
            view = ServiceChoiceView(self)
            await interaction.response.send_message(message_text, view=view, ephemeral=True)
        else:
            modal = ServicesInputModal(self)
            await interaction.response.send_modal(modal)

    async def confirm_date(self, interaction: discord.Interaction, services: List[str]):
        services_text = storage.format_services_list(services)
        message_text = (
            f"**Подтвердите дату генерации документов:**\n\n"
            f"**Услуги ({len(services)}):**\n```\n{services_text}\n```\n\n"
            f"Выберите дату:"
        )

        view = DateConfirmView(self, services)

        if interaction.response.is_done():
            await interaction.followup.send(message_text, view=view, ephemeral=True)
        else:
            await interaction.response.send_message(message_text, view=view, ephemeral=True)

    async def generate_and_send(self, interaction: discord.Interaction,
                                 services: List[str], generation_date: date):
        progress_text = (
            f"⏳ Генерирую документы...\n\n"
            f"📋 Услуг: {len(services)}\n"
            f"📅 Дата: {generation_date.strftime('%d.%m.%Y')}"
        )

        if interaction.response.is_done():
            await interaction.followup.send(progress_text, ephemeral=True)
        else:
            await interaction.response.send_message(progress_text, ephemeral=True)

        try:
            client_info = CLIENT_INFO.copy()
            results = self.generator.generate_both_documents(
                services,
                COMPANY_INFO,
                BANK_INFO,
                client_info,
                FINANCIAL_SETTINGS,
                'signatures/YL_Signature.png',
                generation_date
            )

            storage.set_last_services(services)

            if results['act_path'] and results['invoice_path']:
                success_text = (
                    f"**Документы успешно созданы!**\n\n"
                    f"📋 Услуг: {len(services)}\n"
                    f"💰 Сумма: {results['act_amount']:,.0f} RUB\n"
                    f"📅 Дата: {generation_date.strftime('%d.%m.%Y')}\n\n"
                    f"📄 Отправляю файлы..."
                )

                channel = interaction.channel or interaction.user.dm_channel
                if channel is None:
                    await interaction.user.create_dm()
                    channel = interaction.user.dm_channel

                await channel.send(success_text)

                with open(results['act_path'], 'rb') as act_file:
                    await channel.send(
                        file=discord.File(act_file, filename=os.path.basename(results['act_path'])),
                        content='📋 Акт оказанных услуг'
                    )

                with open(results['invoice_path'], 'rb') as invoice_file:
                    await channel.send(
                        file=discord.File(invoice_file, filename=os.path.basename(results['invoice_path'])),
                        content='🧾 Счет на оплату'
                    )
            else:
                error_text = (
                    f"❌ **Ошибка при генерации документов**\n\n"
                    f"Акт: {'✅' if results['act_path'] else '❌'}\n"
                    f"Счет: {'✅' if results['invoice_path'] else '❌'}"
                )
                await interaction.followup.send(error_text, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(
                f"❌ **Ошибка при генерации:**\n\n```\n{str(e)}\n```",
                ephemeral=True
            )

    async def run(self):
        print("🤖 Starting Discord Bot...")
        print(f"👤 Authorized user ID: {self.authorized_user_id or 'All users'}")

        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        tree = app_commands.CommandTree(client)
        bot_ref = self

        @tree.command(name='start', description='Начать работу с ботом')
        async def start_cmd(interaction: discord.Interaction):
            await bot_ref.start_command(interaction)

        @tree.command(name='help', description='Помощь по использованию')
        async def help_cmd(interaction: discord.Interaction):
            await bot_ref.help_command(interaction)

        @tree.command(name='status', description='Статистика генерации')
        async def status_cmd(interaction: discord.Interaction):
            await bot_ref.status_command(interaction)

        @tree.command(name='generate', description='Создать документы (Счет и Акт)')
        async def generate_cmd(interaction: discord.Interaction):
            await bot_ref.generate_command(interaction)

        @client.event
        async def on_ready():
            await tree.sync()
            print(f'✅ Discord Bot is running as {client.user}!')
            print('📋 Slash commands synced.')

        async with client:
            await client.start(self.bot_token)
