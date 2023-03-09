import platform
from . import menu

_MAX_ERROR_LENGTH = 200


def main(handle_exception=True):
    menu_ = menu.Menu(operating_system=platform.system())
    error: str = None
    while True:
        try:
            menu_.select_task(error)
        except Exception as exception:
            if handle_exception:
                error = str(exception)[:_MAX_ERROR_LENGTH]
                error = ". ".join(error.split("\n"))
            else:
                raise exception


if __name__ == "__main__":
    main()
