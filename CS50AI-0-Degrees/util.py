class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

    def __repr__(self):
        return "\nstate: " + repr(self.state) + "\n" + "parent: " + repr(self.parent) + "\n" + "action: " +  repr(self.action)

    def __str__(self):
        return "\nstate: " + str(self.state) + "\n" + "parent: " + str(self.parent) + "\n" + "action: " +  str(self.action)

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

    def __repr__(self):
        resultStr = ""
        for i in self.frontier:
            resultStr += str(i)
        return resultStr


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
