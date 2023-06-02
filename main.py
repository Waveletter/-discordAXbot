import platform
from bot_config import settings
import discord
from discord.ext import commands
import logging
import asyncio
from general_cog import GeneralCog
from reports_cog import ReportsCog
from fun_cog import DebugCog
from colorama import Back, Fore, Style
import time
import reports

import sqlite3


class BotHelp (commands.MinimalHelpCommand):
    """
    Minimal class for printing help in embed
    """
    async def send_pages(self):
        destination = self.get_destination()
        embed = discord.Embed(color=discord.Color.dark_gold(), description='')
        for page in self.paginator.pages:
            embed.description += page
        await destination.send(embed=embed)


class BotClient(commands.Bot):

    def __init__(self, command_prefix, intent, help, db: str, repo_manager: reports.ReportManager = None):
        super().__init__(command_prefix=command_prefix, intents=intent)
        self.help_command = help
        self.db_conn = sqlite3.connect(db)
        if repo_manager is not None:
            self.report_manager = repo_manager
        else:
            self.report_manager = reports.ReportManager(database=self.db_conn)

    def add_cogs(self, cogs: list, guilds: discord.Object):
        for cog in cogs:
            asyncio.run(self.add_cog(cog, guilds=guilds))

    def add_a_cog(self, cog: commands.Cog, guilds: discord.Object):
        asyncio.run(self.add_cog(cog, guilds=guilds))

    def assign_report_manager(self, report_manager: reports.ReportManager):
        """

        :type report_manager: ReportManager
        """
        self.report_manager = report_manager

    async def on_ready(self):
        prefix = (Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(f'{prefix} Logged in as {Fore.YELLOW + str(self.user) + Fore.RESET}')
        print(f'{prefix} Bot ID {Fore.YELLOW + str(self.user.id) + Fore.RESET}')
        print(f'{prefix} Discord Version {Fore.YELLOW + discord.__version__ + Fore.RESET}')
        print(f'{prefix} Python Version {Fore.YELLOW + str(platform.python_version()) + Fore.RESET}')


if __name__ == "__main__":
    # initialize the bot

    intent = discord.Intents.default()
    intent.message_content = True
    bot = BotClient(command_prefix=settings['prefix'], intent=intent, help=BotHelp(), db=settings['db'])
    bot.add_cogs(cogs=[GeneralCog(bot), ReportsCog(bot)], guilds=settings['guilds'])
    bot.add_a_cog(cog=DebugCog(bot), guilds=[settings['guilds'][0]])

    log_handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')

    for i in bot.tree.get_commands():
        print(f'{Fore.YELLOW + i.name} {Fore.WHITE + i.description + Fore.RESET}')

    bot.run(settings['token'], log_handler=log_handler)
