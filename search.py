# search.py
# ---------


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
import csv
import os
from datetime import datetime


class SearchLogger:
    FIELDNAMES = [
        "iteration", "expanded_state", "parent", "action",
        "generated_successors", "frontier_before", "frontier_after",
        "explored", "g", "h", "f",
    ]

    def __init__(self, algorithm_name):
        os.makedirs("evidence", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.path = os.path.join("evidence", f"{algorithm_name}_{timestamp}.csv")
        self._file = open(self.path, "w", newline="")
        self._writer = csv.DictWriter(self._file, fieldnames=self.FIELDNAMES)
        self._writer.writeheader()
        self.iteration = 0

    def log(self, expanded_state, parent, action, generated_successors,
            frontier_before, frontier_after, explored, g, h):
        self.iteration += 1
        self._writer.writerow({
            "iteration": self.iteration,
            "expanded_state": expanded_state,
            "parent": parent,
            "action": action,
            "generated_successors": generated_successors,
            "frontier_before": frontier_before,
            "frontier_after": frontier_after,
            "explored": explored,
            "g": g,
            "h": h,
            "f": g + h,
        })

    def close(self):
        self._file.close()


def _frontier_states(frontier):
    if hasattr(frontier, "heap"):
        return [entry[2][0] for entry in frontier.heap]
    if hasattr(frontier, "list"):
        return [entry[0] for entry in frontier.list]
    return []



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
    frontier.push((start, []))
    explored = set()
    logger = SearchLogger("dfs")
    parent_of = {start: None}

    while not frontier.isEmpty():
        state, actions = frontier.pop()

        if state in explored:
            continue

        frontier_before = _frontier_states(frontier)
        explored.add(state)
        successors = problem.getSuccessors(state)

        if problem.isGoalState(state):
            logger.log(state, parent_of.get(state), actions[-1] if actions else None,
                       [s for s, a, c in successors], frontier_before,
                       _frontier_states(frontier), len(explored), len(actions), 0)
            logger.close()
            return actions

        for successor, action, stepCost in reversed(successors):
            if successor not in explored:
                parent_of.setdefault(successor, state)
                frontier.push((successor, actions + [action]))

        logger.log(state, parent_of.get(state), actions[-1] if actions else None,
                   [s for s, a, c in successors], frontier_before,
                   _frontier_states(frontier), len(explored), len(actions), 0)

    logger.close()
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
    enqueued = set()
    enqueued.add(start)
    frontier.push((start, []))
    logger = SearchLogger("bfs")
    parent_of = {start: None}

    while not frontier.isEmpty():
        state, actions = frontier.pop()
        frontier_before = _frontier_states(frontier)
        successors = problem.getSuccessors(state)

        if problem.isGoalState(state):
            logger.log(state, parent_of.get(state), actions[-1] if actions else None,
                       [s for s, a, c in successors], frontier_before,
                       _frontier_states(frontier), len(enqueued), len(actions), 0)
            logger.close()
            return actions

        for successor, action, stepCost in successors:
            if successor not in enqueued:
                enqueued.add(successor)
                parent_of.setdefault(successor, state)
                frontier.push((successor, actions + [action]))

        logger.log(state, parent_of.get(state), actions[-1] if actions else None,
                   [s for s, a, c in successors], frontier_before,
                   _frontier_states(frontier), len(enqueued), len(actions), 0)

    logger.close()
    return []

def uniformCostSearch(problem: SearchProblem):
    """
    Search the node of least total path cost first.

    Graph-search UCS using a PriorityQueue ordered by accumulated cost g(n).
    If a cheaper path to a state already on the frontier is found, that state's
    priority is updated so the queue always expands the lowest-g node next.
    """
    frontier = util.PriorityQueue()
    start = problem.getStartState()
    frontier.push(start, 0)
    best_g = {start: 0}
    best_actions = {start: []}
    explored = set()
    logger = SearchLogger("ucs")
    parent_of = {start: None}

    while not frontier.isEmpty():
        state = frontier.pop()
        cost_so_far = best_g[state]

        if state in explored:
            continue

        frontier_before = _frontier_states(frontier)
        explored.add(state)
        successors = problem.getSuccessors(state)

        if problem.isGoalState(state):
            logger.log(state, parent_of.get(state), best_actions[state][-1] if best_actions[state] else None,
                       [s for s, a, c in successors], frontier_before,
                       _frontier_states(frontier), len(explored), cost_so_far, 0)
            logger.close()
            return best_actions[state]

        for successor, action, step_cost in successors:
            if successor in explored:
                continue
            new_cost = cost_so_far + step_cost
            if successor not in best_g or new_cost < best_g[successor]:
                best_g[successor] = new_cost
                best_actions[successor] = best_actions[state] + [action]
                parent_of[successor] = state
                frontier.update(successor, new_cost)

        logger.log(state, parent_of.get(state), best_actions[state][-1] if best_actions[state] else None,
                   [s for s, a, c in successors], frontier_before,
                   _frontier_states(frontier), len(explored), cost_so_far, 0)

    logger.close()
    return []

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def greedyBestFirstSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """
    Search the node that looks closest to the goal first.

    Graph-search GBFS using a PriorityQueue ordered strictly by h(n).
    Path cost g(n) is ignored when choosing what to expand next.
    The heuristic is passed in from the command line (e.g. manhattanHeuristic).
    """
    frontier = util.PriorityQueue()
    start = problem.getStartState()
    frontier.push((start, []), heuristic(start, problem))
    explored = set()

    while not frontier.isEmpty():
        state, actions = frontier.pop()

        if state in explored:
            continue
        explored.add(state)

        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in explored:
                h = heuristic(successor, problem)
                frontier.push((successor, actions + [action]), h)

    return []

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    frontier = util.PriorityQueue()
    start_state = problem.getStartState()
    frontier.push((start_state, [], 0), heuristic(start_state, problem))
    best_cost = {start_state: 0}
    logger = SearchLogger("astar")
    parent_of = {start_state: None}
    explored = set()

    while not frontier.isEmpty():
        current_state, actions, cost_so_far = frontier.pop()

        if cost_so_far > best_cost[current_state]:
            continue

        frontier_before = _frontier_states(frontier)
        explored.add(current_state)
        successors = problem.getSuccessors(current_state)
        h_value = heuristic(current_state, problem)

        if problem.isGoalState(current_state):
            logger.log(current_state, parent_of.get(current_state),
                       actions[-1] if actions else None,
                       [s for s, a, c in successors], frontier_before,
                       _frontier_states(frontier), len(explored),
                       cost_so_far, h_value)
            logger.close()
            return actions

        for successor, action, step_cost in successors:
            new_cost = cost_so_far + step_cost
            if successor not in best_cost or new_cost < best_cost[successor]:
                best_cost[successor] = new_cost
                new_actions = actions + [action]
                priority = new_cost + heuristic(successor, problem)
                parent_of[successor] = current_state
                frontier.push((successor, new_actions, new_cost), priority)

        logger.log(current_state, parent_of.get(current_state),
                   actions[-1] if actions else None,
                   [s for s, a, c in successors], frontier_before,
                   _frontier_states(frontier), len(explored),
                   cost_so_far, h_value)

    logger.close()
    return []



# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
gbfs = greedyBestFirstSearch
