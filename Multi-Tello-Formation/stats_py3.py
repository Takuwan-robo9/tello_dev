from datetime import datetime

class Stats:
    def __init__(self, command, id):
        self.command = command
        self.response = None
        self.id = id

        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.drone_ip = None
    def add_response(self, response, ip):
        if self.response == None:
            self.response = response
            self.end_time = datetime.now()
            self.duration = self.get_duration()
            self.drone_ip = ip                  
        # self.print_stats()

    def get_duration(self):
        diff = self.end_time - self.start_time
        return diff.total_seconds()

    def print_stats(self):
        print('\nid: %s' % self.id)
        print('command: %s' % self.command)
        print('response: %s' % self.response)
        print('start time: %s' % self.start_time)
        print('end_time: %s' % self.end_time)
        print('duration: %s\n' % self.duration)

    def got_response(self):
        if self.response is None:
            return False
        else:
            return True

    def return_stats(self):
        str_val = ''
        str_val += '\nid: %s\n' % self.id
        str_val += 'command: %s\n' % self.command
        str_val += 'response: %s\n' % self.response
        str_val += 'start time: %s\n' % self.start_time
        str_val += 'end_time: %s\n' % self.end_time
        str_val += 'duration: %s\n' % self.duration
        return str_val
