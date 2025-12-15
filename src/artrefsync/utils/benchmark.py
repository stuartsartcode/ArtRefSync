import shutil
import sys
import time
import humanize
from pympler import asizeof


def main():

    with Bm("Test"):
        test = "Hello World"
        test2 = "I don't know?"

    with Bm("Test 2"):
        test3 = "Hello World"
        test4 = "I don't know?"
    


def obj_size(obj) -> str:
    return humanize.naturalsize(asizeof.asizeof(obj))


def wrap_line(lines, line_size, border_char='│'):
    for line in lines.split("\n"):
        inner_line = line_size - 4
        c_line = ""
        for s in line.split(" "):
            if len(c_line) == 0:
                pass
            elif (
                len(c_line) > inner_line or len(c_line) + len(s) + 1 > inner_line
            ):
                print(f"│ {c_line.ljust(inner_line)} │")
                c_line = ""
            c_line += " " if len(c_line) > 0 else ""
            c_line += s
        if c_line != "":
            print(f"│ {c_line.ljust(inner_line)} │")


class Bm(object):
    def __init__(self, name, pretty = True):
        self.name = name
        self.pretty = pretty

    def __enter__(self):
        self.time_start = time.perf_counter()
        self.old_locals = sys._getframe(1).f_locals.copy()
        return self

    def __exit__(self, exc_time, exc_value, traceback):
        lines = f"{self.name} took {time.perf_counter()-self.time_start:.4f} seconds."
        new_locals = sys._getframe(1).f_locals
        for local in new_locals.keys() - self.old_locals.keys():
            lines += f"\n- {local}: {obj_size(new_locals[local])}"

        if self.pretty:
            line_size = int(min(120, shutil.get_terminal_size((120, 50)).columns))
            print(f"╭{"─" * (line_size - 2)}╮")
            wrap_line(lines, line_size)
            print(f"╰{"─" * (line_size - 2)}╯")
        else:
            print(lines)
        return False
if __name__ == "__main__":
    main()
