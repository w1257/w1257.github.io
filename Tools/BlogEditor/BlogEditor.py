#import os
#import time
#import subprocess
import questionary
#import markdown
#from datetime import datetime
#from zoneinfo import ZoneInfo
#import tempfile
from pathlib import Path

BLOGS_FOLDER_PATH = Path('./../../pages/blogs/jsons')


def blogSelect(selectedValue:list[Path]) -> bool:
    if not len(selectedValue):
        raise ValueError("selectedValue needs at least 1 item")
    if not BLOGS_FOLDER_PATH.is_dir():
        raise FileNotFoundError(f"Path in BLOGS_FOLDER_PATH to blogs doesn't exsist.\nBLOGS_FOLDER_PATH: {BLOGS_FOLDER_PATH}")
    all_contents:list[Path] = [i for i in list(BLOGS_FOLDER_PATH.glob('*.json')) if i.is_file()]
    blog_options:list[str] = [i.name[:-5] for i in all_contents]
    forbiddenNames:set[str] = set(["Exit"]);
    if bool(forbiddenNames.intersection(blog_options)):
        raise ValueError(f"BLOGS_FOLDER_PATH contains a forbbiden name(s). \nBLOGS_FOLDER_PATH: {BLOGS_FOLDER_PATH}\nforbidden Names:{forbiddenNames}")
    blog_options.append("Exit")
    selected_name:str = questionary.select(
        "Select a Blog to edit:",
        choices=blog_options
    ).ask()
    if (selected_name == "Exit"):
        return False
    selectedValue[0] = all_contents[blog_options.index(selected_name)]
    return True


def main():
    retPath:list[Path] = [Path()]
    while(blogSelect(retPath)):
        print(retPath,end="\n\n")

if __name__ == "__main__":
    main()