# search.py
# ---------


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Graph-search DFS using a LIFO Stack as the frontier.
    An explicit explored set prevents re-expanding already-visited states,
    guaranteeing termination even in cyclic graphs.

    Successors are pushed in reverse order (West→South→East→North) so that
    when popped they follow the mandatory expansion order: North→East→South→West.
    """
    frontier = util.Stack()
    start = problem.getStartState()
    # Each entry on the stack: (state, actions_to_reach_state)
    frontier.push((start, []))
    explored = set()

    while not frontier.isEmpty():
        state, actions = frontier.pop()

        # Skip if already fully explored
        if state in explored:
            continue

        # Mark as explored upon expansion
        explored.add(state)

        if problem.isGoalState(state):
            return actions

        # getSuccessors returns [North, South, East, West] by default.
        # Push in reversed order so North is on top and popped first.
        for successor, action, stepCost in reversed(problem.getSuccessors(state)):
            if successor not in explored:
                frontier.push((successor, actions + [action]))

    return []

def breadthFirstSearch(problem: SearchProblem):
    """
    Search the shallowest nodes in the search tree first.

    Graph-search BFS using a FIFO Queue as the frontier.
    States are added to 'enqueued' as soon as they enter the queue, so they
    are never re-enqueued regardless of whether they are in the frontier or
    the explored set.  This guarantees the shallowest (optimal) path is found
    for any unweighted (uniform step-cost) graph.
    """
    frontier = util.Queue()
    start = problem.getStartState()

    # enqueued tracks every state that has ever entered the queue,
    # preventing re-enqueuing states already in the frontier or expanded.
    enqueued = set()
    enqueued.add(start)
    frontier.push((start, []))

    while not frontier.isEmpty():
        state, actions = frontier.pop()

        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in enqueued:
                enqueued.add(successor)
                frontier.push((successor, actions + [action]))

    return []

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    frontier = util.PriorityQueue()
    start_state = problem.getStartState()
    frontier.push((start_state, [], 0), heuristic(start_state, problem))

    best_cost = {start_state: 0}

    while not frontier.isEmpty():
        current_state, actions, cost_so_far = frontier.pop()

        if cost_so_far > best_cost[current_state]:
            continue

        if problem.isGoalState(current_state):
            return actions

        for successor, action, step_cost in problem.getSuccessors(current_state):
            new_cost = cost_so_far + step_cost

            if successor not in best_cost or new_cost < best_cost[successor]:
                best_cost[successor] = new_cost
                new_actions = actions + [action]
                priority = new_cost + heuristic(successor, problem)
                frontier.push((successor, new_actions, new_cost), priority)

    return []


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
