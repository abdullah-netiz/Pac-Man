# search.py
# ---------


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
import csv
import os

# ---------------------------------------------------------------------------
# CSV Trace Logging Helpers
# ---------------------------------------------------------------------------

# Column header row shared by every trace file
_TRACE_COLUMNS = [
    "iteration", "expanded_state", "parent", "action",
    "generated_successors", "frontier_before", "frontier_after",
    "explored", "g", "h", "f",
]

# When a frontier or explored set exceeds this many entries we log only
# the size instead of dumping every element.  This keeps the CSV useful
# for small/medium problems while avoiding the huge serialisation cost
# that would otherwise make large searches (e.g. FoodSearchProblem on
# trickySearch) exceed the autograder timeout.
_SNAPSHOT_CAP = 200

# Maximum number of CSV rows (iterations) to write per search run.
# After this limit the algorithm keeps running but stops writing trace
# rows, so large problems (thousands of expansions with complex state
# objects) are not slowed down by logging overhead.
_MAX_TRACE_ROWS = 500


def _ensure_evidence_dir():
    """Create the evidence/ folder next to this module if it does not exist."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    evidence_folder = os.path.join(base_path, "evidence")
    if not os.path.isdir(evidence_folder):
        os.makedirs(evidence_folder, exist_ok=True)
    return evidence_folder


def _open_trace_file(algorithm_tag):
    """
    Open (or overwrite) a CSV trace file for *algorithm_tag* inside evidence/.
    Returns (csv_writer, file_handle) — caller must close the handle when done.
    """
    folder = _ensure_evidence_dir()
    filepath = os.path.join(folder, "{}_trace.csv".format(algorithm_tag))
    fh = open(filepath, "w", newline="", encoding="utf-8")
    writer = csv.writer(fh)
    writer.writerow(_TRACE_COLUMNS)
    return writer, fh


def _read_stack_states(stack_obj):
    """Return a list of states currently held in a util.Stack."""
    return [entry[0] for entry in stack_obj.list]


def _read_queue_states(queue_obj):
    """Return a list of states currently held in a util.Queue."""
    return [entry[0] for entry in queue_obj.list]


def _read_pq_states(pq_obj):
    """Return a list of states from a util.PriorityQueue.
    Each heap element is (priority, counter, item). The *item* varies by
    algorithm — we extract the state portion regardless of tuple length."""
    result = []
    for entry in pq_obj.heap:
        item = entry[2]  # (priority, count, item)
        if isinstance(item, tuple):
            result.append(item[0])  # state is always the first element
        else:
            result.append(item)
    return result


def _fmt(obj):
    """Compact string representation safe for CSV cells."""
    return str(obj)


def _snap_stack(stack_obj):
    """Return a CSV-safe snapshot of a Stack's states, capped for speed."""
    n = len(stack_obj.list)
    if n <= _SNAPSHOT_CAP:
        return _fmt([entry[0] for entry in stack_obj.list])
    return "<{} states>".format(n)


def _snap_queue(queue_obj):
    """Return a CSV-safe snapshot of a Queue's states, capped for speed."""
    n = len(queue_obj.list)
    if n <= _SNAPSHOT_CAP:
        return _fmt([entry[0] for entry in queue_obj.list])
    return "<{} states>".format(n)


def _snap_pq(pq_obj):
    """Return a CSV-safe snapshot of a PriorityQueue, capped for speed."""
    n = len(pq_obj.heap)
    if n <= _SNAPSHOT_CAP:
        return _fmt(_read_pq_states(pq_obj))
    return "<{} states>".format(n)


def _snap_pq_plain(pq_obj):
    """Snapshot for PQs whose items are plain states (not tuples wrapping
    state+actions), e.g. UCS."""
    n = len(pq_obj.heap)
    if n <= _SNAPSHOT_CAP:
        return _fmt([e[2] for e in pq_obj.heap])
    return "<{} states>".format(n)


def _snap_set(s):
    """Return a CSV-safe snapshot of an explored / visited set."""
    if len(s) <= _SNAPSHOT_CAP:
        return _fmt(s)
    return "<{} states>".format(len(s))

# ---------------------------------------------------------------------------


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
    trace_csv, trace_fh = _open_trace_file("dfs")
    step_counter = 0
    # Track which state is the parent for each pushed state
    parent_map = {}

    frontier = util.Stack()
    start = problem.getStartState()
    # Each entry on the stack: (state, actions_to_reach_state)
    frontier.push((start, []))
    parent_map[start] = (None, None)  # root has no parent or action
    explored = set()

    while not frontier.isEmpty():
        state, actions = frontier.pop()

        # Skip if already fully explored
        if state in explored:
            continue

        _do_trace = (step_counter <= _MAX_TRACE_ROWS)
        # ---------- trace: capture frontier BEFORE expansion ----------
        frontier_before_snap = _snap_stack(frontier) if _do_trace else ""

        # Mark as explored upon expansion
        explored.add(state)
        step_counter += 1

        par_state, par_action = parent_map.get(state, (None, None))

        if problem.isGoalState(state):
            if _do_trace:
                trace_csv.writerow([
                step_counter, _fmt(state), _fmt(par_state), _fmt(par_action),
                "[]", frontier_before_snap, _snap_stack(frontier),
                _snap_set(explored), len(actions), "N/A", "N/A",
            ])
            trace_fh.close()
            return actions

        # getSuccessors returns [North, South, East, West] by default.
        # Push in reversed order so North is on top and popped first.
        children_raw = problem.getSuccessors(state)
        generated_names = []
        for successor, action, stepCost in reversed(children_raw):
            if successor not in explored:
                frontier.push((successor, actions + [action]))
                # Only record parent if successor was not already tracked
                if successor not in parent_map:
                    parent_map[successor] = (state, action)
                generated_names.append(successor)

        # ---------- trace: capture frontier AFTER expansion ----------
        frontier_after_snap = _snap_stack(frontier) if _do_trace else ""

        if _do_trace:
            trace_csv.writerow([
            step_counter, _fmt(state), _fmt(par_state), _fmt(par_action),
            _fmt(generated_names), frontier_before_snap,
            frontier_after_snap, _snap_set(explored),
            len(actions), "N/A", "N/A",
        ])

    trace_fh.close()
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
    trace_csv, trace_fh = _open_trace_file("bfs")
    step_counter = 0
    parent_map = {}

    frontier = util.Queue()
    start = problem.getStartState()

    # enqueued tracks every state that has ever entered the queue,
    # preventing re-enqueuing states already in the frontier or expanded.
    enqueued = set()
    enqueued.add(start)
    frontier.push((start, []))
    parent_map[start] = (None, None)

    while not frontier.isEmpty():
        state, actions = frontier.pop()

        _do_trace = (step_counter <= _MAX_TRACE_ROWS)
        # ---------- trace: frontier snapshot before expansion ----------
        frontier_before_snap = _snap_queue(frontier) if _do_trace else ""
        step_counter += 1

        par_state, par_action = parent_map.get(state, (None, None))

        if problem.isGoalState(state):
            if _do_trace:
                trace_csv.writerow([
                step_counter, _fmt(state), _fmt(par_state), _fmt(par_action),
                "[]", frontier_before_snap,
                _snap_queue(frontier),
                _snap_set(enqueued), len(actions), "N/A", "N/A",
            ])
            trace_fh.close()
            return actions

        generated_names = []
        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in enqueued:
                enqueued.add(successor)
                frontier.push((successor, actions + [action]))
                parent_map[successor] = (state, action)
                generated_names.append(successor)

        # ---------- trace: frontier snapshot after expansion ----------
        frontier_after_snap = _snap_queue(frontier) if _do_trace else ""

        if _do_trace:
            trace_csv.writerow([
            step_counter, _fmt(state), _fmt(par_state), _fmt(par_action),
            _fmt(generated_names), frontier_before_snap,
            frontier_after_snap, _snap_set(enqueued),
            len(actions), "N/A", "N/A",
        ])

    trace_fh.close()
    return []

def uniformCostSearch(problem: SearchProblem):
    """
    Search the node of least total path cost first.

    Graph-search UCS using a PriorityQueue ordered by accumulated cost g(n).
    If a cheaper path to a state already on the frontier is found, that state's
    priority is updated so the queue always expands the lowest-g node next.
    """
    trace_csv, trace_fh = _open_trace_file("ucs")
    step_counter = 0
    parent_map = {}

    frontier = util.PriorityQueue()
    start = problem.getStartState()
    # Item on the queue is the state; path and g-cost are stored alongside.
    frontier.push(start, 0)
    best_g = {start: 0}
    best_actions = {start: []}
    parent_map[start] = (None, None)
    explored = set()

    while not frontier.isEmpty():
        state = frontier.pop()
        cost_so_far = best_g[state]

        if state in explored:
            continue

        _do_trace = (step_counter <= _MAX_TRACE_ROWS)
        # ---------- trace: frontier snapshot before expansion ----------
        # For UCS the heap items are plain states, so extract directly
        frontier_before_snap = _snap_pq_plain(frontier) if _do_trace else ""
        explored.add(state)
        step_counter += 1

        par_state, par_action = parent_map.get(state, (None, None))

        if problem.isGoalState(state):
            if _do_trace:
                trace_csv.writerow([
                step_counter, _fmt(state), _fmt(par_state), _fmt(par_action),
                "[]", frontier_before_snap,
                _snap_pq_plain(frontier),
                _snap_set(explored), cost_so_far, "N/A", cost_so_far,
            ])
            trace_fh.close()
            return best_actions[state]

        generated_names = []
        for successor, action, step_cost in problem.getSuccessors(state):
            if successor in explored:
                continue
            new_cost = cost_so_far + step_cost
            if successor not in best_g or new_cost < best_g[successor]:
                best_g[successor] = new_cost
                best_actions[successor] = best_actions[state] + [action]
                # update() decreases priority if successor is already on the fringe
                frontier.update(successor, new_cost)
                parent_map[successor] = (state, action)
                generated_names.append(successor)

        # ---------- trace: frontier snapshot after expansion ----------
        frontier_after_snap = _snap_pq_plain(frontier) if _do_trace else ""

        if _do_trace:
            trace_csv.writerow([
            step_counter, _fmt(state), _fmt(par_state), _fmt(par_action),
            _fmt(generated_names), frontier_before_snap,
            frontier_after_snap, _snap_set(explored),
            cost_so_far, "N/A", cost_so_far,
        ])

    trace_fh.close()
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
    trace_csv, trace_fh = _open_trace_file("gbfs")
    step_counter = 0
    parent_map = {}
    g_costs = {}  # track path cost for logging even though GBFS ignores it

    frontier = util.PriorityQueue()
    start = problem.getStartState()
    h_start = heuristic(start, problem)
    frontier.push((start, []), h_start)
    parent_map[start] = (None, None)
    g_costs[start] = 0
    explored = set()

    while not frontier.isEmpty():
        state, actions = frontier.pop()

        if state in explored:
            continue

        _do_trace = (step_counter <= _MAX_TRACE_ROWS)
        # ---------- trace: frontier snapshot before expansion ----------
        frontier_before_snap = _snap_pq(frontier) if _do_trace else ""
        explored.add(state)
        step_counter += 1

        par_state, par_action = parent_map.get(state, (None, None))
        cur_g = g_costs.get(state, len(actions))
        cur_h = heuristic(state, problem)
        cur_f = cur_g + cur_h

        if problem.isGoalState(state):
            if _do_trace:
                trace_csv.writerow([
                step_counter, _fmt(state), _fmt(par_state), _fmt(par_action),
                "[]", frontier_before_snap,
                _snap_pq(frontier),
                _snap_set(explored), cur_g, cur_h, cur_f,
            ])
            trace_fh.close()
            return actions

        generated_names = []
        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in explored:
                h_val = heuristic(successor, problem)
                frontier.push((successor, actions + [action]), h_val)
                child_g = cur_g + stepCost
                if successor not in parent_map:
                    parent_map[successor] = (state, action)
                    g_costs[successor] = child_g
                generated_names.append(successor)

        # ---------- trace: frontier snapshot after expansion ----------
        frontier_after_snap = _snap_pq(frontier) if _do_trace else ""

        if _do_trace:
            trace_csv.writerow([
            step_counter, _fmt(state), _fmt(par_state), _fmt(par_action),
            _fmt(generated_names), frontier_before_snap,
            frontier_after_snap, _snap_set(explored),
            cur_g, cur_h, cur_f,
        ])

    trace_fh.close()
    return []

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    trace_csv, trace_fh = _open_trace_file("astar")
    step_counter = 0
    parent_map = {}

    frontier = util.PriorityQueue()
    start_state = problem.getStartState()
    h_start = heuristic(start_state, problem)
    frontier.push((start_state, [], 0), h_start)
    parent_map[start_state] = (None, None)

    best_cost = {start_state: 0}

    while not frontier.isEmpty():
        current_state, actions, cost_so_far = frontier.pop()

        if cost_so_far > best_cost[current_state]:
            continue

        _do_trace = (step_counter <= _MAX_TRACE_ROWS)
        # ---------- trace: frontier snapshot before expansion ----------
        frontier_before_snap = _snap_pq(frontier) if _do_trace else ""
        step_counter += 1

        par_state, par_action = parent_map.get(current_state, (None, None))
        cur_h = heuristic(current_state, problem)
        cur_f = cost_so_far + cur_h

        if problem.isGoalState(current_state):
            if _do_trace:
                trace_csv.writerow([
                step_counter, _fmt(current_state),
                _fmt(par_state), _fmt(par_action),
                "[]", frontier_before_snap,
                _snap_pq(frontier),
                _snap_set(set(best_cost.keys())),
                cost_so_far, cur_h, cur_f,
            ])
            trace_fh.close()
            return actions

        generated_names = []
        for successor, action, step_cost in problem.getSuccessors(current_state):
            new_cost = cost_so_far + step_cost

            if successor not in best_cost or new_cost < best_cost[successor]:
                best_cost[successor] = new_cost
                new_actions = actions + [action]
                priority = new_cost + heuristic(successor, problem)
                frontier.push((successor, new_actions, new_cost), priority)
                parent_map[successor] = (current_state, action)
                generated_names.append(successor)

        # ---------- trace: frontier snapshot after expansion ----------
        frontier_after_snap = _snap_pq(frontier) if _do_trace else ""

        if _do_trace:
            trace_csv.writerow([
            step_counter, _fmt(current_state),
            _fmt(par_state), _fmt(par_action),
            _fmt(generated_names), frontier_before_snap,
            frontier_after_snap,
            _snap_set(set(best_cost.keys())),
            cost_so_far, cur_h, cur_f,
        ])

    trace_fh.close()
    return []


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
gbfs = greedyBestFirstSearch
