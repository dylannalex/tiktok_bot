import os
import ctypes
from colorama import init as _init
from colorama import Fore as _Fore
from colorama import Style as _Style

from . import bot
from . import ascii


class Menu:
    WINDOW_TITLE = """Tiktok Bot | Github: @dylannalex"""

    def __init__(self, operating_system: str):
        # Operating System config
        self.operating_system = operating_system
        if operating_system == "Windows":
            self.clear_command = "cls"
            self._set_window_title()
        else:
            self.clear_command = "clear"

        # Other
        _init(autoreset=True)
        self._load_bot()

    def _load_bot(self):
        self._print_title()
        self._print_text("Waiting for Zefoy to load.")
        self.zefoy_bot = bot.ZefoyBot()
        self._print_text("Site loaded. Complete CAPTCHA to continue...")
        self.zefoy_bot.complete_captcha()

    def select_task(self, error: str = None):
        self._print_title()
        # Print tasks
        if error:
            self._print_text(f"{_Fore.RED}ERROR: {_Fore.WHITE}{error}.\n")
        else:
            self._print_text(f"Select your option below.\n")

        for task in self.zefoy_bot.tasks:
            if task.status == bot.TaskStatus.OFFLINE:
                status = f"{_Fore.RED}[OFFLINE]"
            else:
                status = f"{_Fore.GREEN}[WORKS]"
            self._print_text(f"{task.name} {status}", bullet=task.id_)

        option = self._input("Enter an option: ", new_lines=1)
        self._validate_option(option)
        task = bot.find_task(int(option), self.zefoy_bot.tasks)
        url = self._input("Enter TikTok Video link: ")
        total_executions = int(self._input("Enter total executions: "))
        self.zefoy_bot.set_task_request(selected_task=task, tiktok_video_url=url)

        task_log = bot.TaskLog(
            task.name, url, 0, total_executions, self._print_text, self._print_title
        )
        for execution in range(total_executions):
            task_log.current_execution = execution
            self.zefoy_bot.complete_task(task_log)

    def _print_title(self):
        os.system(self.clear_command)
        print(f"{_Style.BRIGHT}{_Fore.BLUE}{ascii.TITLE}\n\n")

    def _print_text(
        self, text: str, bullet: str = "-", end: str = "\n", new_lines: int = 0
    ):
        start = "\n" * new_lines
        bullet_ = f"{_Style.BRIGHT}{_Fore.BLUE}{bullet}"
        print(
            f"{start} {_Fore.WHITE}[{bullet_}{_Fore.WHITE}] {text}",
            end=end,
        )

    def _input(self, text: str, new_lines: int = 0):
        self._print_text(text, end="", new_lines=new_lines)
        return input(_Fore.WHITE)

    def _set_window_title(self, message: str = None):
        if self.operating_system != "Windows":
            return
        title = __class__.WINDOW_TITLE
        if message:
            title += f" | {message}"
        ctypes.windll.kernel32.SetConsoleTitleW(title)

    def _validate_option(self, option: str):
        try:
            option = int(option)
        except ValueError:
            raise ValueError("Option must be a number")

        task = bot.find_task(option, self.zefoy_bot.tasks)

        if not task:
            raise ValueError(f"'{option}' is not a valid option")

        if task.status == bot.TaskStatus.OFFLINE:
            raise ValueError(f"{task.name.capitalize()} is offline")
