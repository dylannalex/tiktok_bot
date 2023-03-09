import os
import ctypes
from colorama import Fore as _Fore

from . import bot


class Menu:
    TITLE = """\
▄▄▄▄▄▪  ▄ •▄ ▄▄▄▄▄      ▄ •▄     ▄▄▄▄·       ▄▄▄▄▄
•██  ██ █▌▄▌▪•██  ▪     █▌▄▌▪    ▐█ ▀█▪▪     •██  
 ▐█.▪▐█·▐▀▀▄· ▐█.▪ ▄█▀▄ ▐▀▀▄·    ▐█▀▀█▄ ▄█▀▄  ▐█.▪
 ▐█▌·▐█▌▐█.█▌ ▐█▌·▐█▌.▐▌▐█.█▌    ██▄▪▐█▐█▌.▐▌ ▐█▌·
 ▀▀▀ ▀▀▀·▀  ▀ ▀▀▀  ▀█▄▀▪·▀  ▀    ·▀▀▀▀  ▀█▄▀▪ ▀▀▀ 
\n\n"""

    WINDOW_TITLE = """Tiktok Bot | Github: @dylannalex"""

    def __init__(self, operating_system: str):
        # Operating System config
        self.operating_system = operating_system
        if operating_system == "Windows":
            self.clear_command = "cls"
        else:
            self.clear_command = "clear"

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
        task_id = int(option)
        url = self._input("Enter TikTok Video link: ")
        total_executions = int(self._input("Enter total executions: "))
        self.zefoy_bot.set_task_request(task_id=task_id, tiktok_video_url=url)

        for execution in range(total_executions):
            log_function = lambda *msg: self._task_log(execution, url, *msg)
            self.zefoy_bot.complete_task(log_function)

    def _task_log(self, execution: int, tiktok_video: str, *messages: str):
        self._print_title()
        task_name = self.zefoy_bot.task_request.task.name.capitalize()
        self._print_text(f"Task selected: {task_name}")
        self._print_text(f"TikTok video: {tiktok_video}")
        self._print_text(f"Times sent: {execution}")

        for message in messages:
            self._print_text(message)

    def _print_title(self):
        os.system(self.clear_command)
        print(f"{_Fore.BLUE}{__class__.TITLE}")

    def _print_text(
        self, text: str, bullet: str = "-", end: str = "\n", new_lines: int = 0
    ):
        start = "\n" * new_lines
        print(
            f"{start} {_Fore.WHITE}[{_Fore.BLUE}{bullet}{_Fore.WHITE}] {text}", end=end
        )

    def _input(self, text: str, new_lines: int = 0):
        self._print_text(text, end="", new_lines=new_lines)
        return input()

    def set_window_title(self, message: str = None):
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
