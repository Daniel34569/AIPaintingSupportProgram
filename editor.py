import os
from PIL import Image
from pathlib import Path
import argparse
import curses
import tkinter as tk
from tkinter import ttk
import multiprocessing
import ctypes
import threading
import queue
import time

from editor_basic_operator import * 

DEFAULT_CELL_WIDTH = 120
DEFAULT_CELL_HEIGHT = 120

CURRENT_SORT_METHOD = 'descend'
CURRENT_SELECTED_IN_MAIN = 0
IS_TAGS_WINDOWS_OPEN = multiprocessing.Value('i', 0)
SHARED_TAG = multiprocessing.Queue()
BUTTON_PRESSED = multiprocessing.Value('i', 0)
tag_queue = queue.Queue()
    
def monitor_selected_tag():
    global SHARED_TAG, BUTTON_PRESSED, tag_queue
    print(f"Monitoring...")
    while True:
        if BUTTON_PRESSED.value == 1:
            print(f"In thread, BUTTON_PRESSED.value == 1")
            print(f"In thread, put value:{SHARED_TAG}")
            received_value = SHARED_TAG.get()
            print(f"In thread, get Success?")
            print(f"In thread, get value:{received_value}")
            tag_queue.put(received_value)
            BUTTON_PRESSED.value = 0
        time.sleep(0.1)

def create_readonly_text(parent, text, width, height):
    readonly_text = tk.Text(parent, wrap=tk.NONE, width=width, height=height)
    readonly_text.insert(tk.END, text)
    readonly_text.configure(state=tk.DISABLED)
    return readonly_text

def start_tkinter_window(sorted_tags, global_tags, global_selected_tag, global_button_click):
    def close_window():
        global_tags.value -= 1
        window.destroy()

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * event.delta / 120), "units")
    def button_callback(tag):
        #with global_selected_tag.get_lock():
        global_selected_tag.put(tag)
        print(f"Set Select tag value the encode of : {tag}")
        #print(f"Set Select tag value the encode  : {global_selected_tag.value}")
        with global_button_click.get_lock():
            global_button_click.value = 1
        print(f"global_button_click.value = True Success")

    window = tk.Tk()
    window.title("Possible Tags")

    canvas = tk.Canvas(window)
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
    tags_frame = tk.Frame(canvas)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.create_window((0, 0), window=tags_frame, anchor=tk.NW)

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    tags_frame.bind("<Configure>", on_frame_configure)
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    max_tag_with_frequency_length = max(len(f"{tag}: {frequency}") for tag, frequency in sorted_tags)
    max_tag_length = max(len(tag) for tag, _ in sorted_tags)

    for index, (tag, frequency) in enumerate(sorted_tags):
        #tag_with_frequency_text = create_readonly_text(tags_frame, f"{tag}: {frequency}", width=max_tag_with_frequency_length, height=1)
        button = tk.Button(tags_frame, text=f"{tag}: {frequency}", command=lambda t=tag: button_callback(t), width=max_tag_with_frequency_length, height=1)
        tag_text = create_readonly_text(tags_frame, tag, width=max_tag_length, height=1)

        #tag_with_frequency_text.grid(row=index, column=0)
        button.grid(row=index, column=0)
        tag_text.grid(row=index, column=1)

    close_button = tk.Button(window, text="Close", command=close_window)
    close_button.pack(side=tk.BOTTOM)

    window.protocol("WM_DELETE_WINDOW", close_window)
    window.mainloop()

def show_possible_tags(sorted_tags):
    global IS_TAGS_WINDOWS_OPEN
    tkinter_process = multiprocessing.Process(target=start_tkinter_window, args=(sorted_tags, IS_TAGS_WINDOWS_OPEN, SHARED_TAG, BUTTON_PRESSED))
    IS_TAGS_WINDOWS_OPEN.value += 1
    tkinter_process.start()

def process_image_folder(target_folder):
    tags_dict = {}
    for entry in os.scandir(target_folder):
        if entry.is_file() and entry.name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_name = entry.name
            txt_filename = Path(entry.path).stem + '.txt'
            txt_filepath = os.path.join(target_folder, txt_filename)
            
            if os.path.exists(txt_filepath):
                tags = read_tags_from_file(txt_filepath)
                tags_dict[image_name] = {
                    'tags': tags,
                    'image_path': entry.path,
                    'tagging_file_path': txt_filepath
                }
    return tags_dict

def print_image_names(tags_dict):
    print("Image names:")
    for image_name in tags_dict:
        print(Path(image_name).stem)

def sort_tags_frequency(tags_dict, method='descend'):
    tag_frequency = {}
    for image_data in tags_dict.values():
        for tag in image_data['tags']:
            if tag not in tag_frequency:
                tag_frequency[tag] = 1
            else:
                tag_frequency[tag] += 1

    if method == 'none':
        sorted_tags = tag_frequency
    else:
        sorted_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=method == 'descend')
    return sorted_tags

def print_tags_frequency(tags_dict, sorted_tags):
    print("Tags frequency:")
    for tag, frequency in sorted_tags:
        print(f"{tag}: {frequency}")

def menu_print_tags_frequency_and_select_sort(stdscr, tags_dict):
    options = [
        ("Sort by ascending frequency", "ascend"),
        ("Sort by descending frequency", "descend")
    ]
    current_option = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a sorting method:")

        for index, (option_text, _) in enumerate(options):
            if index == current_option:
                stdscr.addstr(index + 1, 0, f"> {option_text}")
            else:
                stdscr.addstr(index + 1, 0, f"  {option_text}")

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_option = (current_option - 1) % len(options)
        elif key == curses.KEY_DOWN:
            current_option = (current_option + 1) % len(options)
        elif key == curses.KEY_ENTER or key == ord('\n'):
            stdscr.clear()
            _, method = options[current_option]
            curses.endwin()
            sorted_tags = sort_tags_frequency(tags_dict, method=method)
            show_possible_tags(sorted_tags)
            CURRENT_SORT_METHOD = method
            print("\nPress any key to return to the main menu")
            input()
            break

def remove_tag_if_other_exists(tags_dict, tags_input, tag_remove):
    if not tags_input or not tag_remove:
        print("Input not exist")
        return
    found = False
    for image_name, image_data in tags_dict.items():
        if all(tag in image_data['tags'] for tag in tags_input) and tag_remove in image_data['tags']:
            image_data['tags'].remove(tag_remove)
            found = True

    if found:
        print(f"Remove {tag_remove} complete.")
    else:
        print("Tags not found.")

def remove_tag(tags_dict, tag_remove):
    if not tag_remove:
        print("Input not exist")
        return
    found = False
    for image_name, image_data in tags_dict.items():
        if tag_remove in image_data['tags']:
            image_data['tags'].remove(tag_remove)
            found = True

    if found:
        print(f"Remove {tag_remove} complete.")
    else:
        print("Tags not found.")

def add_tag_if_others_not_exist(tags_dict, tags_input, tag_append):
    if not tags_input or not tag_append:
        print("Input not exist")
        return
    found = False
    for image_name, image_data in tags_dict.items():
        if not any(tag in image_data['tags'] for tag in tags_input):
            image_data['tags'].append(tag_append)
            found = True

    if found:
        print(f"Adding {tag_append} complete.")
    else:
        print("Tags not found.")

def remove_repeated_tags(tags_dict):
    for image_data in tags_dict.values():
        unique_tags = []
        for tag in image_data['tags']:
            if tag not in unique_tags:
                unique_tags.append(tag)
        image_data['tags'] = unique_tags

    return tags_dict

def replace_tags(tags_dict, inputlist, target):
    for image_data in tags_dict.values():
        new_tags = []
        replaced = False
        for tag in image_data['tags']:
            if tag in inputlist:
                if not replaced:
                    new_tags.append(target)
                    replaced = True
            else:
                new_tags.append(tag)
        image_data['tags'] = new_tags

    return tags_dict

def remove_tags_with_substring(tags_dict, inputtags):
    for image_data in tags_dict.values():
        new_tags = [tag for tag in image_data['tags'] if inputtags not in tag]
        image_data['tags'] = new_tags

    return tags_dict

def replace_tags_with_substring(tags_dict, inputlist, target):
    for image_data in tags_dict.values():
        new_tags = []
        for tag in image_data['tags']:
            if any(substring in tag for substring in inputlist):
                if target not in new_tags:
                    new_tags.append(target)
            else:
                new_tags.append(tag)
        image_data['tags'] = new_tags

    return tags_dict

def menu_modify_tags(stdscr, tags_dict):
    options = [
        ("Remove tag", remove_tag),
        ("Remove tag(Multiple)", remove_tag),
        ("Remove tag if another tag exist", remove_tag_if_other_exists),
        ("Remove tag (Search Substring)", remove_tags_with_substring),
        ("Add tag if others not exist", add_tag_if_others_not_exist),
        ("Remove all repeated tags", remove_repeated_tags),
        ("Replace tags ", replace_tags),
        ("Replace tags (Search Substring)", replace_tags_with_substring),
    ]
    current_option = 0
    global IS_TAGS_WINDOWS_OPEN
    if IS_TAGS_WINDOWS_OPEN.value == 0:
        sorted_tags = sort_tags_frequency(tags_dict, method=CURRENT_SORT_METHOD)
        show_possible_tags(sorted_tags)

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select an option:")

        for index, (option_text, _) in enumerate(options):
            if index == current_option:
                stdscr.addstr(index + 1, 0, f"> {option_text}")
            else:
                stdscr.addstr(index + 1, 0, f"  {option_text}")

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_option = (current_option - 1) % len(options)
        elif key == curses.KEY_DOWN:
            current_option = (current_option + 1) % len(options)
        elif key == curses.KEY_ENTER or key == ord('\n'):
            stdscr.clear()
            opt_name, func = options[current_option]

            if IS_TAGS_WINDOWS_OPEN.value == 0:
                sorted_tags = sort_tags_frequency(tags_dict, method=CURRENT_SORT_METHOD)
                show_possible_tags(sorted_tags)

            if opt_name == "Remove tag" or func == remove_tags_with_substring:
                curses.echo()
                stdscr.addstr(0, 0, "Enter the tag to remove: ")
                tag = stdscr.getstr().decode('utf-8')
                curses.noecho()
                curses.endwin()
                func(tags_dict, tag)
            elif opt_name == "Remove tag(Multiple)":
                curses.echo()
                stdscr.addstr(0, 0, "Enter tags to removed, press ENTER directly when done: ")
                global tag_queue
                while True:
                    tag = stdscr.getstr().decode('utf-8')
                    if tag:
                        func(tags_dict, tag)
                    else:
                        break
            elif func == remove_tag_if_other_exists or func == replace_tags or func == replace_tags_with_substring:
                tags_a = []
                tag_c = ""
                curses.echo()

                stdscr.addstr(0, 0, "Enter tags for the List that you want to check if it exist, press ENTER directly when done: ")
                while True:
                    tag = stdscr.getstr().decode('utf-8')
                    if tag:
                        tags_a.append(tag)
                    else:
                        break

                stdscr.addstr(len(tags_a) + 2, 0, "Enter the tag to add: ")
                tag_c = stdscr.getstr().decode('utf-8')
                curses.noecho()
                curses.endwin()
                func(tags_dict, tags_a, tag_c)
            elif func == add_tag_if_others_not_exist:
                tags_a = []
                tag_c = ""
                curses.echo()

                stdscr.addstr(0, 0, "Enter tags for the List that you want to check if it not exist, press ENTER directly when done: ")
                while True:
                    tag = stdscr.getstr().decode('utf-8')
                    if tag:
                        tags_a.append(tag)
                    else:
                        break

                stdscr.addstr(len(tags_a) + 2, 0, "Enter the tag to add: ")
                tag_c = stdscr.getstr().decode('utf-8')
                curses.noecho()
                curses.endwin()
                func(tags_dict, tags_a, tag_c)
            else:
                curses.endwin()
                func(tags_dict)


            print("\nPress any key to return to the main menu")
            input()
            break

#Main menu of UI
def main_menu(stdscr, tags_dict):
    options = [
        ("Print all image names", print_image_names),
        ("Print tags frequency (Select sort)", menu_print_tags_frequency_and_select_sort),
        ("Menu Modify Tags", menu_modify_tags),
        ("Save Tags", save_tags)
    ]
    global CURRENT_SELECTED_IN_MAIN
    current_option = CURRENT_SELECTED_IN_MAIN
    stdscr.timeout(0)

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"What to do?(Their are {len(tags_dict)} images in total) (press Q/q to leave)")

        for index, (text, _) in enumerate(options):
            if index == current_option:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(index + 2, 0, text)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(index + 2, 0, text)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            current_option = (current_option - 1) % len(options)
        elif key == curses.KEY_DOWN:
            current_option = (current_option + 1) % len(options)
        elif key == curses.KEY_ENTER or key == ord('\n'):
            stdscr.clear()
            CURRENT_SELECTED_IN_MAIN = current_option
            opt_name, func = options[current_option]
            if (opt_name == "Print tags frequency (Select sort)"):
                func(stdscr, tags_dict)
                curses.doupdate()  # Refresh the curses window after opening the tkinter window
            elif (opt_name == "Menu Modify Tags"):
                func(stdscr, tags_dict)
            else:
                curses.endwin()
                func(tags_dict)
                print("\nPress any key to return to the main menu")
                input()
            curses.wrapper(main_menu, tags_dict)
            break
        elif key == ord('q') or key == ord('Q'):
            break

# Add command line arguments
def init_args():
    parser = argparse.ArgumentParser(description="Process PNG files")
    parser.add_argument('--input_dir', type=str, default='./input_image/part no halo', help='Input directory (default: ./)')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # Set the directory path containing the PNG files
    args = init_args()
    target_folder = args.input_dir
    tags_dict = process_image_folder(target_folder)
    
    monitoring_thread = threading.Thread(target=monitor_selected_tag)
    monitoring_thread.daemon = True
    monitoring_thread.start()


    curses.wrapper(main_menu, tags_dict)
    # Accessing the tags using the image name
    """
    image_name = 'example.jpg'
    if image_name in tags_dict:
        tags = tags_dict[image_name]['tags']
        print(f"Tags for {image_name}: {tags}")
    else:
        print(f"No tags found for {image_name}")
    """