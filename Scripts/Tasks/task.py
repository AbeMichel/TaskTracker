from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QDateTime

TIMER_UPDATE_INTERVAL_MS = 100

class Task(QObject):
    focused = pyqtSignal(object)
    unfocused = pyqtSignal(object)
    finished = pyqtSignal(object)
    updated = pyqtSignal(object)

    def __init__(self, name, categoryId = 1, durationMs = 0, elapsedMs = 0, dailyWork = None, show = True):
        super().__init__()
        self.name = name
        self.show = show
        self.categoryId = categoryId
        self.durationMs = durationMs
        self.active = False
        self.elapsedTimeMs = elapsedMs

        self.startTime = None
        # Stores cumulative work per day, key = "yyyy-MM-dd", value = milliseconds
        self.dailyWork = dailyWork if dailyWork is not None else {}
        self.sentFinishedSignal = False

        self.timer = QTimer()
        self.timer.timeout.connect(self._updateTime)

    def _updateTime(self):
        self.elapsedTimeMs += TIMER_UPDATE_INTERVAL_MS
        self.updated.emit(self)
        if not self.sentFinishedSignal and self.isFinished():
            self.finished.emit(self)
            self.sentFinishedSignal = True

    def setFocused(self, focused):
        now = QDateTime.currentDateTime()
        if focused and not self.active:
            if not self.timer.isActive():
                self.timer.start(TIMER_UPDATE_INTERVAL_MS)
            self.active = True
            self.startTime = now
            self.focused.emit(self)
        elif self.active:
            self.active = False
            self.addDailyWork(self.startTime, now)
            self.timer.stop()
            self.unfocused.emit(self)

    def addDailyWork(self, start: QDateTime, end: QDateTime):
        current = start
        while current.date() < end.date():
            # end of current day
            dayEnd = QDateTime(current.date()).addDays(1)
            elapsed = current.msecsTo(dayEnd)
            dayStr = current.toString("yyyy-MM-dd")
            self.dailyWork[dayStr] = self.dailyWork.get(dayStr, 0) + elapsed
            current = dayEnd
        # Add remaining time on last day
        dayStr = current.toString("yyyy-MM-dd")
        elapsed = current.msecsTo(end)
        self.dailyWork[dayStr] = self.dailyWork.get(dayStr, 0) + elapsed

    def isFinished(self):
        return self.elapsedTimeMs >= self.durationMs
    
    def progress(self):
        if self.durationMs == 0:
            return 0
        return int((self.elapsedTimeMs / self.durationMs) * 100)
    
    def getSaveData(self):
        if self.active:
            self.setFocused(False)
        dailyHours = {day: ms / 1000 / 3600 for day, ms in self.dailyWork.items()}
        return {
            "Name" : self.name,
            "Show" : self.show,
            "Category" : self.categoryId,
            "Duration" : self.durationMs,
            "Elapsed" : self.elapsedTimeMs,
            "DailyWork" : dailyHours,
        }


def GetTaskFromData(data):
    dailyWork = {day: int(hours * 3600 * 1000) for day, hours in data.get("DailyWork", {}).items()}

    return Task(
        name=data["Name"],
        show=data["Show"],
        categoryId=data["Category"],
        durationMs=data["Duration"],
        elapsedMs=data["Elapsed"],
        dailyWork=dailyWork,
    )