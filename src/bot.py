import time
import selenium
import undetected_chromedriver as uc

from typing import Callable
from enum import Enum


def find_task(task_id: int, tasks: list["Task"]):
    tasks_found = list(filter(lambda task: task.id_ == task_id, tasks))
    if not tasks_found:
        return None
    return tasks_found[0]


def _convert_time(min, sec):
    seconds = 0
    if min != 0:
        answer = int(min) * 60
        seconds += answer
    seconds += int(sec) + 5
    return seconds


class TaskStatus(Enum):
    WORKING = 0
    OFFLINE = 1


class Task:
    def __init__(self, id_: int, name: str, status: TaskStatus = None):
        self.id_ = id_
        self.name = name
        self.status = status
        self.div = str(id_ + 1)


class TaskRequest:
    def __init__(
        self, task: Task, tiktok_video_url: str, video_url_box: str, search_box: str
    ):
        self.task = task
        self.tiktok_video_url = tiktok_video_url
        self.video_url_box = video_url_box
        self.search_box = search_box
        self.initial_value: int = None
        self.final_value: int = None


class ZefoyBot:
    URL = "https://zefoy.com"
    CAPTCHA_BOX = "/html/body/div[4]/div[2]/form/div/div"
    TASKS_XPATH = {
        "followers": "/html/body/div[5]/div[1]/div[3]/div[2]/div[1]/div/button",
        "hearts": "/html/body/div[5]/div[1]/div[3]/div[2]/div[2]/div/button",
        "comment_hearts": "/html/body/div[5]/div[1]/div[3]/div[2]/div[3]/div/button",
        "views": "/html/body/div[5]/div[1]/div[3]/div[2]/div[4]/div/button",
        "shares": "/html/body/div[5]/div[1]/div[3]/div[2]/div[5]/div/button",
        "favorites": "/html/body/div[5]/div[1]/div[3]/div[2]/div[6]/div/button",
    }
    SLEEP_TIME = 3

    def __init__(self):
        self.driver = uc.Chrome()

        # Create tasks
        self.tasks: list[Task] = []
        tasks_name = __class__.TASKS_XPATH.keys()
        for i, task_name in enumerate(tasks_name):
            id_ = i + 1
            self.tasks.append(Task(id_, task_name))

        # Go to zefoy.com and wait for captcha
        self.driver.get(__class__.URL)
        self.wait_for_xpath(__class__.CAPTCHA_BOX)

    def complete_captcha(self):
        self.wait_for_xpath(__class__.TASKS_XPATH["followers"])
        self.update_task_status()

    def update_task_status(self):
        for task in self.tasks:
            xpath = __class__.TASKS_XPATH[task.name]
            element = self.driver.find_element("xpath", xpath)
            status = TaskStatus.WORKING if element.is_enabled() else TaskStatus.OFFLINE
            task.status = status

    def set_task_request(self, task_id: int, tiktok_video_url: str):
        # Find task
        selected_task = None
        for task in self.tasks:
            if task_id == task.id_:
                selected_task = task

        # Click element
        element_xpath = __class__.TASKS_XPATH[selected_task.name]
        self.driver.find_element("xpath", element_xpath).click()
        video_url_box = f"/html/body/div[5]/div[{selected_task.div}]/div/form/div/input"
        search_box = (
            f"/html/body/div[5]/div[{selected_task.div}]/div/form/div/div/button"
        )

        # Create task request
        self.task_request = TaskRequest(
            selected_task, tiktok_video_url, video_url_box, search_box
        )

    def complete_task(self, log_function: Callable[[str], None]):
        element = self.driver.find_element("xpath", self.task_request.video_url_box)
        element.clear()
        element.send_keys(self.task_request.tiktok_video_url)
        self.driver.find_element("xpath", self.task_request.search_box).click()
        time.sleep(__class__.SLEEP_TIME)

        # Get wait time
        wait_time, full = self.get_wait_time(self.task_request.task.div)
        if "(s)" in str(full):
            self._wait_for_task(wait_time, log_function)
            self.driver.find_element("xpath", self.task_request.search_box).click()
            time.sleep(__class__.SLEEP_TIME)
        time.sleep(__class__.SLEEP_TIME)
        send_button_xpath = f"/html/body/div[5]/div[{self.task_request.task.div}]/div/div/div[1]/div/form/button"
        send_button = self.driver.find_element("xpath", send_button_xpath)

        if not self.task_request.initial_value:
            self.task_request.initial_value = send_button.text

        self.task_request.final_value = send_button.text
        send_button.text
        send_button.click()
        time.sleep(__class__.SLEEP_TIME)

    def _wait_for_task(self, wait_time: int, log_function: Callable[[str], None]):
        while wait_time != 0:
            time.sleep(1)
            wait_time -= 1
            message = f"Cooldown: {wait_time} sec"
            log_function(message)

    def get_wait_time(self, div):
        remaining = f"/html/body/div[5]/div[{div}]/div/div/h4"
        try:
            element = self.driver.find_element("xpath", remaining)
        except:
            return None, None
        if "READY" in element.text:
            return True, True
        if "seconds for your next submit" in element.text:
            output = element.text.split("Please wait ")[1].split(" for")[0]
            minutes = element.text.split("Please wait ")[1].split(" ")[0]
            seconds = element.text.split("(s) ")[1].split(" ")[0]
            sleep_duration = _convert_time(minutes, seconds)
            return sleep_duration, output
        return element.text, None

    def wait_for_xpath(self, xpath):
        while True:
            try:
                self.driver.find_element("xpath", xpath)
                return True
            except selenium.common.exceptions.NoSuchElementException:
                pass
