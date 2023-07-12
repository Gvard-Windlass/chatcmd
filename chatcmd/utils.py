import sys
import shutil


def save_cursor_position() -> None:
    sys.stdout.write("\0337")


def restore_cursor_position() -> None:
    sys.stdout.write("\0338")


def move_to_top_of_screen() -> None:
    sys.stdout.write("\033[H")


def delete_line() -> None:
    sys.stdout.write("\033[2K")


def clear_line() -> None:
    sys.stdout.write("\033[2K\033[0G")


def clear_screen() -> None:
    sys.stdout.write("\033[2J\033[0G")


def move_back_one_char() -> None:
    sys.stdout.write("\033[1D")


def move_to_bottom_of_screen() -> int:
    _, total_rows = shutil.get_terminal_size()
    input_row = total_rows - 1
    sys.stdout.write(f"\033[{input_row}E")
    return total_rows
