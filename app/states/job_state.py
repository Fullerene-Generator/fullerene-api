from enum import Enum

class JobState(Enum):
    RUNNING = 1,
    IDLE = 2

class ProcessWrapper:
    def __init__(self):
        self.state = JobState.IDLE
        self.process = None
    def setRunning(self):
        self.state = JobState.RUNNING
    def setIdle(self):
        self.state = JobState.IDLE
    def isRunning(self):
        return self.state == JobState.RUNNING
    def kill(self):
        if self.process != None:
            self.process.kill()
            self.state = JobState.IDLE