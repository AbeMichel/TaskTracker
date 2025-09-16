# Task Tracker

A general use time tracker for time blocking different tasks. Helps the user keep a log of how much time they are spending on various things.

**Table of Contents**
- [AI Disclosure](#ai-disclosure)
- [Functionality](#functionality)
    - [Categories](#categories)
    - [Tasks](#tasks)
    - [Visuals](#visuals)
        - [Graph](#graph)
        - [Mini View](#mini-view)
    - [Future Work](#future-work)
- [Installation](#installation)
    - [Development Environment](#development-environment)
    - [Setting up the Virtual Environment](#setting-up-the-virtual-environment)
    - [Creating the Executable](#creating-the-executable-optional)
    - [Running the Application](#running-the-application)
- [License](#license)

### AI Disclosure
To help support the quick development/prototyping of this project I've used AI tools to enhance my workflow.

## Functionality

### Categories
Categories are used to organize your tasks and are whats used in the visualization of your time allotment.

### Tasks
These are intended to be time blocks with a specific purpose, but ultimately you can use them however you want. When creating a task you will be able to give it a title, category it belongs to, and the duration you want to work on it for.

### Visuals
#### Graph
There is a graph in the main window which shows you a breakdown of the time spent on each category over the given time period as a bargraph. I would like to expand the functionality of this in the future.

#### Mini View
The mini view is a snapshot of the tasks you have active and what you are currently working on. By clicking on a task you can *activate* it and the bar will become colored as the time counts down. You can quickly switch tasks by clicking on another one or pause them by clicking them again.

Hovering over the mini view window will show options for creating new tasks, reopening the large view, or quiting the application.

Hovering over a task will show the remaining time you have allotted to it.

### Future Work
These are features/QOL/improvements I would like to make when I get time. Listed in no particular order.

- More analytical data tracking
    - What tasks are taking the most time
    - Tracking which applications are focused during certain tasks
    - Detecting when a user is off/on task
- Allowing the user to 'block' applications during certain tasks
- More UI 'juice'
- Allowing for different graph visuals
- Custom UI themes
- Transparency when the mini view isn't focused
- Enabling/Disabling tasks from the mini view
- Integration for Google Tasks
- Integration for Google Calendar


## Installation
### Development Environment
**Python:** 3.13.7

**OS:** Windows 11

**Virtual Environemnt:** Yes, Python's venv

**Libraries Used:** [requirements.txt](./requirements.txt)

### Setting up the Virtual Environment
Create the virtual environment
```bat
py -3.13 -m venv ".venv"
```
Activate the virtual environment
```bat
".venv/Scripts/activate.bat"
```
Install the requirements
```bat
pip install -r "requirements.txt"
```

### Creating the Executable (Optional)

```bat
pip install pyinstaller
```

Build the executable using [`build.bat`](./build.bat)
```bat
build.bat
```

The resulting standalone application will be at `dist/Task Tracker.exe`

### Running the Application
If you didn't [build the application using pyinstaller](#creating-the-executable-optional), you can run the application from the command line using Python.
```bat
py main.py
```

Otherwise, simply double clicking on the executable at `dist/Task Tracker.exe` is sufficient.

## License

[MIT License](./LICENSE)