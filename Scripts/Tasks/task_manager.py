from Scripts.Util.colors import COLORS, ColorHex
from Scripts.Tasks.task import Task, GetTaskFromData



CATEGORIES = {
    1: {
        "Name": "None",
        "Description": "",
        "Color": COLORS.Blue,
        "Tasks": [],
    },
}

def AddCategory(name, color=COLORS.Blue, description=""):
    id = 0
    while id in CATEGORIES.keys():
        id += 1
    
    CATEGORIES[id] = {
        "Name": name,
        "Description": description,
        "Color": color,
        "Tasks": [],
    }

    return id


def GetCategory(id):
    return CATEGORIES[id]

def GetTasks():
    return [
        task for category in CATEGORIES.values() for task in category["Tasks"]
    ]


def CreateTask(name, categoryId, durationMs):
    newTask = Task(name=name, categoryId=categoryId, durationMs=durationMs)
    category = CATEGORIES[categoryId]
    category["Tasks"].append(newTask)
    return newTask
    

def ChangeTaskCategory(task: Task, newCategoryId):
    newCategory = CATEGORIES[newCategoryId]
    oldCategory = CATEGORIES[task.categoryId]

    oldCategory["Tasks"].remove(task)
    newCategory["Tasks"].append(task)
    task.categoryId = newCategoryId


def GetSaveData(categoryId):
    category = CATEGORIES[categoryId]
    return {
        "Id": categoryId,
        "Name": category["Name"],
        "Description": category["Description"],
        "Color": str(category["Color"]),  # convert Color object to hex
        "Tasks": [task.getSaveData() for task in category["Tasks"]]
    }

def LoadFromData(categoryData):
    CATEGORIES[categoryData["Id"]] = {
        "Name": categoryData["Name"],
        "Description": categoryData["Description"],
        "Color": ColorHex(categoryData["Color"]),
        "Tasks": [GetTaskFromData(taskData) for taskData in categoryData["Tasks"]],
    }

def SaveAll():
    categories = []
    for id in CATEGORIES.keys():
        categories.append(GetSaveData(id))
    return categories

def LoadAll(data):
    CATEGORIES.clear()
    for categoryData in data:
        LoadFromData(categoryData)