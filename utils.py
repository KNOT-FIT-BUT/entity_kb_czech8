import colorama

colorama.init()


def readlines(filename, mode="r", **kwargs):
    with open(filename, mode=mode, **kwargs) as file:
        while True:
            line = file.readline()
            if not line:
                break
            yield line


def blue(text):
    return colorama.Fore.BLUE + text + colorama.Style.RESET_ALL


def yellow(text):
    return colorama.Fore.YELLOW + text + colorama.Style.RESET_ALL
