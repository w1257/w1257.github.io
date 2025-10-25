#import os
#import time
#import subprocess
import questionary
#import markdown
#from datetime import datetime
#from zoneinfo import ZoneInfo
#import tempfile
from pathlib import Path
from jsonschema import validate, FormatChecker
from jsonschema.exceptions import ValidationError
import json

BLOGS_FOLDER_PATH = Path('./../../pages/blogs/jsons')

# The corrected and robust schema
json_schema:dict[str,object] = {
  "type": "object",
  "properties": {
    "posts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "Title": {"type": "string"},
          "Situation": {"type": "string"},
          "Task": {"type": "string"},
          "Action": {"type": "string"},
          "Result": {"type": "string"},
          "Extra": {"type": "string"},
          "Time": {"type": "string", "format": "date-time"} 
        },
        "required": ["Title", "Situation", "Task", "Action", "Result", "Extra", "Time"],
        "additionalProperties": False
      }
    }
  },
  "required": ["posts"],
  "additionalProperties": False
}

def blogSelect(selectedValue_out:list[Path]) -> bool:
    if not len(selectedValue_out):
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
    selectedValue_out[0] = all_contents[blog_options.index(selected_name)]
    return True

def getJson(blogPath:Path,jsonData_out:list[dict[str,object]]):
    
    try:
        data:dict[str,object]
        with open(blogPath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        validate(instance=data, schema=json_schema, format_checker=FormatChecker())
        jsonData_out[0] = data
        return True
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON. \nJSON File: {blogPath}")
        return False
    except ValidationError as e:
        print(f"Json Validation Failed: {e.message}")
        print(f"Error occurred at path: {list(e.path)}")
        return False

def main():
    retPath:list[Path] = [Path()]
    jsonData:list[dict[str,object]] = [{}]
    while(blogSelect(retPath)):
        if getJson(retPath[0],jsonData):
            print(jsonData[0],end="\n\n")

if __name__ == "__main__":
    main()