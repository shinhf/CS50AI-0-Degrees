import csv
import sys
import pprint
import logging

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    logger = logging.getLogger("BFS")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"
    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target, logger)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target, logger):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    #state - table [movie, actorId]
    #action - list of states
    frontier = QueueFrontier()
    exploredSet = []
    
    #create initial nodes
    action = neighbors_for_person(source)
    #logger.debug("List of actions for node %s : %s", str(source), str(action))
    sourceNode = Node((None, source), None, action)
    createNodesFromAction(action, sourceNode, exploredSet, frontier, logger)
    

    while True:
        currentNode = frontier.remove()
        #logger.info("===Node removed from frontier %s", len(frontier.frontier))
        #logger.debug("%s ", repr(frontier) )

        if checkIfNodeContainsTarget(currentNode, target ,logger ):
            break
        exploredSet.append(currentNode)
        #logger.info("===Status of explored set changed %s", len(exploredSet) )
        #logger.debug("%s ", repr(exploredSet) )
        createNodesFromAction(currentNode.action, currentNode, exploredSet, frontier, logger)
        #logger.info("===Status of the frontier after expanding node  %s", len(frontier.frontier))
        #logger.debug("%s ", repr(frontier) )
        if not frontier:
            return None

    path = list(reversed(createPath(currentNode, source)))
    return path


def createPath(node, source):
    path = []
    tempNode = node
    while tempNode.state[1] != source :
        path.append(tempNode.state)
        tempNode= tempNode.parent
    return path

def checkIfFrontierIsEmpty(frontier):
    if not frontier:
        return True
    else:
        return False

def checkIfNodeContainsTarget(node, target,logger ):
    if node.state[1] == target:
        #logger.debug("===status True contains target compare %s %s", node.state[1], target)
        return True
    else:
        #logger.debug("===status False contains target compare %s %s", node.state[1], target)
        return False

    
#checking the neighbour movies is based on the personId, no need to worry about multiple films

def checkIfNodeIsInExploredSet(node, exploredSet):
    #no need to remove node from action, it will be just ignored using check
    actorId = node.state[1]
    for tempNode in exploredSet:
        if tempNode.state[1] == actorId:
            return True
    return False

def checkIfStateIsInExploredSet(state, exploredSet, logger):
    #role is table [movie, actorId]
    #no need to remove node from action, it will be just ignored using check
    for tempNode in exploredSet:
        if tempNode.state[1] == state[1]:
            #logger.debug("===status of true compare %s %s", tempNode.state[1], state[1])
            return True
    return False


def createNodesFromAction(action, parent, exploredSet, frontier, logger):
    #create node from action and add it to frontier
    for state in action:
        if not checkIfStateIsInExploredSet(state, exploredSet, logger):
            tempNode = Node(state, parent, neighbors_for_person(state[1]))
            frontier.add(tempNode)



def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
