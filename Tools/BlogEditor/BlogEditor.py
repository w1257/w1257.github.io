from datetime import datetime, timezone
import subprocess
import questionary
import markdown
import tempfile
from pathlib import Path
import shutil
from jsonschema import validate, FormatChecker
from jsonschema.exceptions import ValidationError
import json
import re

BLOGS_FOLDER_PATH = Path('./../../pages/blogs/jsons')

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

regexEditFileFormat:re.Pattern[str] = re.compile(r"::Situation::\s*([\s\S]*?)\s*::Task::\s*([\s\S]*?)\s*::Action::\s*([\s\S]*?)\s*::Result::\s*([\s\S]*?)\s*::Extra::\s*([\s\S]*?)\s*$")
editFileTemplate:str = "::Situation::\n\n\n\n::Task::\n\n\n\n::Action::\n\n\n\n::Result::\n\n\n\n::Extra::\n\n"
tempEditFilePath:Path = Path("./temp")

time_format = '%m/%d/%Y %I:%M:%S %p %Z'

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

def tempFolderPrep():
    tempEditFilePath.mkdir(exist_ok=True)
    for i in tempEditFilePath.iterdir():
        if i.is_dir():
            shutil.rmtree(i)
        else:
            i.unlink()
    
def fileToPost(TargetFile:Path,title:str) -> dict[str,object]:
    file_content:str
    with open(TargetFile, 'r', encoding='utf-8') as f:
        file_content = f.read()
    regOut = regexEditFileFormat.findall(file_content)
    if (len(regOut) == 0): #if no match, return empty dict
        return {} 

    nowUTC = datetime.now(timezone.utc)

    json_obj:dict[str,object] = {
        "Title":title,
        "Situation":regOut[0][0],
        "Task":regOut[0][1],
        "Action":regOut[0][2],
        "Result":regOut[0][3],
        "Extra":regOut[0][4],
        "Time": nowUTC.strftime("%#m/%d/%Y %I:%M:%S %p UTC")
    }
    #if regOut[0][4] != "":
    #    json_obj["Extra"] = "<h2>Extra</h2>"+markdown.markdown(regOut[0][4])
    return json_obj

def addPost(jsonData:dict[str,object]):
    title:str = input("Enter Title for the post: ")
    complete:bool = False
    jsonPost:dict[str,object]
    with tempfile.NamedTemporaryFile(mode='w+',prefix=(title+"_"), suffix=".md",dir=tempEditFilePath, delete=False, encoding='utf-8') as tfile:
        ActiveEditTempFile:Path = tempEditFilePath.joinpath(tfile.name)
        tfile.write(editFileTemplate)
    try:
        while (True):
            print("\nOpening post file in nvim and waiting for exit...")
            subprocess.call(['nvim', ActiveEditTempFile])
            jsonPost = fileToPost(ActiveEditTempFile,title)
            if len(jsonPost) == 0:
                print("ERROR: post file incorrecly formatted. Please fix the formatting")
            else:
                break
        complete=True
    except FileNotFoundError:
        print("\nERROR: 'nvim' command not found.")
    finally:
        try:
            ActiveEditTempFile.unlink()
        except OSError as e:
            print(f"Error removing temporary file {ActiveEditTempFile}: {e}")
    if (complete):
        if editPostMenu(jsonPost, inMarkdown=True): # type: ignore
            jsonData["posts"].append(jsonPost) # type: ignore
            #And save

def displayPostData(jsonData:dict[str,object]):
    print("#############")
    print(f"Title: {jsonData["Title"]}\n\n\
Situation:\n    {jsonData["Situation"]}\n\n\
Task:\n    {jsonData["Task"]}\n\n\
Action:\n    {jsonData["Action"]}\n\n\
Result:\n    {jsonData["Result"]}\n\n\
Extra:\n    {jsonData["Extra"]}\n\n"
    )
    naive_utc_dt = datetime.strptime(jsonData["Time"], time_format) # type: ignore
    aware_utc_dt = naive_utc_dt.replace(tzinfo=timezone.utc)
    local_tz = datetime.now().astimezone().tzinfo
    local_dt = aware_utc_dt.astimezone(local_tz)
    print(f"Post Time: {local_dt.strftime('%m/%d/%Y %I:%M:%S %p %Z')}")

def markdownToHTML(jsonData:dict[str,object]):
    for i in ["Situation","Task","Action","Result"]:
        jsonData[i] = markdown.markdown(jsonData[i]) # type: ignore
    if jsonData["Extra"] != "":
        jsonData["Extra"] = "<h2>Extra</h2>"+markdown.markdown(jsonData["Extra"]) # type: ignore

def editInEditor(jsonData:dict[str,object],inMarkdown:bool=False):
    if inMarkdown:
        suffix_fileType = ".md"
    else:
        suffix_fileType = ".html"
    with tempfile.NamedTemporaryFile(mode='w+',prefix=(jsonData["Title"]+"_"), suffix=suffix_fileType,dir=tempEditFilePath, delete=False, encoding='utf-8') as tfile: # type: ignore
        ActiveEditTempFile:Path = tempEditFilePath.joinpath(tfile.name)
        for i in ["Situation","Task","Action","Result","Extra"]:
            tfile.write(f"::{i}::\n\n{jsonData[i]}\n\n")
    try:
        while (True):
            print("\nOpening post file in nvim and waiting for exit...")
            subprocess.call(['nvim', ActiveEditTempFile])
            jsonData = fileToPost(ActiveEditTempFile,jsonData["Title"]) # type: ignore
            if len(jsonData) == 0:
                print("ERROR: post file incorrecly formatted. Please fix the formatting")
            else:
                break
    except FileNotFoundError:
        print("\nERROR: 'nvim' command not found.")
    finally:
        try:
            ActiveEditTempFile.unlink()
        except OSError as e:
            print(f"Error removing temporary file {ActiveEditTempFile}: {e}")

def editPostMenu(jsonData:dict[str,object],inMarkdown:bool = False) -> bool:
    EditMenu:questionary.Question = questionary.select(
        "Select operation to do:",
        choices=["Edit","change Time","Change Title","Apply and Exit","Cancel"]
    )
    while True:
        displayPostData(jsonData) # type: ignore
        if inMarkdown:
            print("Post is still in Markdown.\n")
        else:
            print("Post is in HTML.\n")
        match (EditMenu.ask()):
            case "Edit":
                editInEditor(jsonData,inMarkdown)
            case "change Time":
                print(f"current time: {jsonData["Time"]}")
                jsonData["Time"] = input("Set new time: ")
            case "Change Title":
                jsonData["Title"] = input("Enter new title: ") # type: ignore
            case "Apply and Exit":
                if inMarkdown:
                    markdownToHTML(jsonData)
                return True
            case "Cancel":
                if input("type 'Cancel' to comfirm cancel: ") == 'Cancel':
                    return False
            case _:
                ValueError("This should not be possible. #2")

def editPost(jsonData:dict[str,object]):
    pass

def deletePost(jsonData:dict[str,object]):
    pass

def main():
    tempFolderPrep()
    retPath:list[Path] = [Path()]
    jsonData:list[dict[str,object]] = [{}]
    operationOptions:questionary.Question = questionary.select(
        "Select a Blog to edit:",
        choices=["Add Post","Edit Post","Delete Post","Return With Saving","Return Without Saving"]
    )
    while(blogSelect(retPath)):
        if getJson(retPath[0],jsonData):
            operationMenuLoop:bool = True
            SaveFile:bool = True
            while (operationMenuLoop):
                operationSelected:str = operationOptions.ask()
                match(operationSelected):
                    case "Add Post":
                        addPost(jsonData[0])
                    case "Edit Post":
                        editPost(jsonData[0])
                    case "Delete Post":
                        deletePost(jsonData[0])
                    case "Return With Saving":
                        operationMenuLoop = False
                    case "Return Without Saving":
                        if input("type 'Saveless' to comfirm return without saving: ") == 'Saveless':
                            SaveFile = False
                            operationMenuLoop = False
                    case _:
                        ValueError("This should not be possible. #1")
            if (SaveFile):
                with open(retPath[0], 'w') as f:
                    json.dump(jsonData[0], f, indent=4)
            

if __name__ == "__main__":
    main()