from datetime import datetime


class Profiler:
    def __init__(self):
        self.times = []

    def start(self, message):
        self.times = [(datetime.now(), message)]
        print("[" + str(self.times[0][0]) + "] " + message)

    def done(self, message):
        timestamp = (datetime.now(), message)
        time_diff = timestamp[0] - self.times[-1][0]
        self.times.append(timestamp)
        print(message + " done: " + str(time_diff))

    def stop(self):
        self.times.append((datetime.now(), "[Done]"))
        print("Total time: " + str(self.times[-1][0] - self.times[0][0]))

