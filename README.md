<div align="center">

# 🟡 Pac-Man AI Search Agent 🎮

### *Teaching Pac-Man to think before he eats*

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![UC Berkeley](https://img.shields.io/badge/UC_Berkeley-CS188-003262?style=for-the-badge)](https://inst.eecs.berkeley.edu/~cs188/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge&logo=checkmarx&logoColor=white)]()

<br>

```
%%%%%%%
%    P%          P = Pac-Man (Start)
% %%% %          . = Food (Goal)
%  %  %          % = Wall
%%   %%
%. %%%%
%%%%%%%
```

**5 Search Algorithms** · **Automated CSV Trace Logging** · **Full Autograder Compliance**

</div>

---

## 📑 Table of Contents

- [🎯 About The Project](#-about-the-project)
- [🧠 Algorithms Implemented](#-algorithms-implemented)
- [📊 Automated CSV Trace Logging](#-automated-csv-trace-logging)
- [🚀 Getting Started](#-getting-started)
- [🕹️ Usage & Examples](#%EF%B8%8F-usage--examples)
- [✅ Autograder Results](#-autograder-results)
- [📁 Project Structure](#-project-structure)
- [👥 Contributors](#-contributors)

---

## 🎯 About The Project

This project is based on the **UC Berkeley CS 188 Pac-Man framework**. The goal is to implement classical AI search algorithms that guide Pac-Man through various maze layouts to find food pellets efficiently.

Beyond solving mazes, every algorithm execution **automatically generates a state-by-state CSV trace log** inside the `evidence/` folder — providing full transparency into how each algorithm explores the search space, proving correctness at every single expansion step.

> 💡 **Key Insight:** Pac-Man doesn't just find food — he *documents every step of his journey*.

---

## 🧠 Algorithms Implemented

<div align="center">

| # | Algorithm | Data Structure | Optimal? | Complete? | Uses Heuristic? |
|:-:|-----------|:--------------:|:--------:|:---------:|:---------------:|
| 1 | **Depth-First Search (DFS)** | `Stack` (LIFO) | ❌ | ✅ | ❌ |
| 2 | **Breadth-First Search (BFS)** | `Queue` (FIFO) | ✅* | ✅ | ❌ |
| 3 | **Uniform-Cost Search (UCS)** | `PriorityQueue` | ✅ | ✅ | ❌ |
| 4 | **Greedy Best-First Search** | `PriorityQueue` | ❌ | ✅ | ✅ `h(n)` |
| 5 | **A\* Search** | `PriorityQueue` | ✅ | ✅ | ✅ `g(n)+h(n)` |

</div>

> *\*BFS is optimal when all step costs are equal*

### How They Compare on `mediumMaze`

```
Algorithm        Path Cost    Nodes Expanded
─────────────    ─────────    ──────────────
DFS                  246             269
BFS                   68             269
UCS                   68             269
A* (manhattan)        68             221   ⬅ fewest expansions!
```

---

## 📊 Automated CSV Trace Logging

Every time a search algorithm runs, it writes a **detailed execution trace** to a CSV file in the `evidence/` folder. This is implemented entirely within `search.py` — no external files modified.

### 📋 CSV Column Specification

```
iteration │ expanded_state │ parent │ action │ generated_successors │ frontier_before │ frontier_after │ explored │ g │ h │ f
```

| Column | What It Records |
|:------:|:----------------|
| `iteration` | 🔢 Expansion step number (1-based) |
| `expanded_state` | 📍 The state being expanded |
| `parent` | ⬆️ State that generated this node |
| `action` | 🎮 Action taken from parent → current |
| `generated_successors` | 👶 New children pushed to frontier |
| `frontier_before` | 📥 Frontier snapshot *before* expansion |
| `frontier_after` | 📤 Frontier snapshot *after* expansion |
| `explored` | ✅ Full visited set at this point |
| `g` | 💰 Path cost from start |
| `h` | 🔮 Heuristic estimate to goal |
| `f` | 📊 Total cost `g + h` |

### 📂 Generated Trace Files

```
evidence/
├── dfs_trace.csv       ← Depth-First Search trace
├── bfs_trace.csv       ← Breadth-First Search trace
├── ucs_trace.csv       ← Uniform-Cost Search trace
├── gbfs_trace.csv      ← Greedy Best-First Search trace
└── astar_trace.csv     ← A* Search trace
```

### 🔍 Sample Trace — A* on tinyMaze

```csv
iteration,expanded_state,parent,action,generated_successors,frontier_before,frontier_after,explored,g,h,f
1,"(5,5)",None,None,"[(5,4),(4,5)]",[],"[(5,4),(4,5)]","{(5,5)}",0,8,8
2,"(5,4)","(5,5)",South,"[(5,3)]","[(4,5)]","[(4,5),(5,3)]","{...}",1,7,8
...
15,"(1,1)","(2,1)",West,[],"[(2,3)]","[(2,3)]","{...}",8,0,8  ← 🏁 GOAL!
```

> Notice how `f = g + h = 8` stays constant for A* on this uniform-cost maze — a hallmark of a consistent heuristic!

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (developed with 3.12)
- No external packages required — uses only Python standard library

### Installation

```bash
git clone https://github.com/i243137-oss/Pac-Man.git
cd Pac-Man
```

---

## 🕹️ Usage & Examples

### Run Pac-Man with Different Algorithms

```bash
# 🔵 Depth-First Search
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs

# 🟢 Breadth-First Search
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs

# 🟡 Uniform-Cost Search
python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs

# 🟠 Greedy Best-First Search
python pacman.py -l mediumMaze -p SearchAgent -a "fn=gbfs,heuristic=manhattanHeuristic"

# 🔴 A* Search
python pacman.py -l bigMaze -p SearchAgent -a "fn=astar,heuristic=manhattanHeuristic"
```

### Quick Mode (no GUI)

```bash
python pacman.py -l tinyMaze -p SearchAgent -a fn=bfs -q
```

### Run the Autograder

```bash
python autograder.py            # Grade all questions
python autograder.py -q q1      # DFS
python autograder.py -q q2      # BFS
python autograder.py -q q3      # UCS
python autograder.py -q q4      # A*
```

### Available Maze Layouts

```
tinyMaze · smallMaze · mediumMaze · bigMaze · openMaze · contoursMaze
mediumCorners · bigCorners · tinyCorners · mediumSearch · bigSearch
oddSearch · trickySearch · tinySearch · smallSearch
```

---

## ✅ Autograder Results

<div align="center">

| Question | Algorithm | Score | Status |
|:--------:|-----------|:-----:|:------:|
| **Q1** | Depth-First Search | `3/3` | ✅ Pass |
| **Q2** | Breadth-First Search | `3/3` | ✅ Pass |
| **Q3** | Uniform-Cost Search | `3/3` | ✅ Pass |
| **Q4** | A* Search | `3/3` | ✅ Pass |
| | | **12/12** | **🏆 Full Score** |

</div>

---

## 📁 Project Structure

```
Pac-Man/
│
├── search.py              ← OUR IMPLEMENTATION (all 5 algorithms + CSV logging)
├── searchAgents.py         ← Search agents & heuristics
├── pacman.py               ← Main game engine
├── game.py                 ← Core game logic & data types
│
├── evidence/               ← Auto-generated CSV trace logs
│   ├── dfs_trace.csv
│   ├── bfs_trace.csv
│   ├── ucs_trace.csv
│   ├── gbfs_trace.csv
│   └── astar_trace.csv
│
├── layouts/                ← Maze layout files (.lay)
├── test_cases/             ← Autograder test cases (q1–q8)
├── util.py                 ← Data structures (Stack, Queue, PriorityQueue)
├── graphicsDisplay.py      ← Graphics rendering
├── autograder.py           ← Automated grading script
└── Assignment 01.pdf       ← Original assignment specification
```

---

## 🔧 Technical Highlights

<table>
<tr>
<td width="50%">

### 🏗️ Architecture Decisions
- **Graph-search** with explored sets prevents infinite loops
- **Parent tracking** via dictionaries for trace logging
- **Frontier introspection** reads internal data structures directly

</td>
<td width="50%">

### 📏 Design Constraints
- ✅ Only `search.py` was modified
- ✅ Zero external dependencies (only `csv`, `os`)
- ✅ CSV files auto-overwrite on each run
- ✅ All original algorithm logic preserved

</td>
</tr>
</table>

---

## 👥 Contributors

<div align="center">

<table>
<tr>
<td align="center">
<a href="https://github.com/abdullah-netiz">
<img src="https://github.com/abdullah-netiz.png" width="100px;" alt="Abdullah"/><br />
<sub><b>Abdullah</b></sub>
</a>
</td>
<td align="center">
<a href="https://github.com/i243137-oss">
<img src="https://github.com/i243137-oss.png" width="100px;" alt="Umair Hassan"/><br />
<sub><b>Umair Hassan</b></sub>
</a>
</td>
<td align="center">
<a href="https://github.com/muhammmadanas10">
<img src="https://github.com/muhammmadanas10.png" width="100px;" alt="Muhammad Anas"/><br />
<sub><b>Muhammad Anas</b></sub>
</a>
</td>
</tr>
</table>

</div>

---

<div align="center">

### ⭐ If this project helped you, give it a star!

*Built with 🧠 intelligence and 🟡 Pac-Man spirit*

**[⬆ Back to Top](#-pac-man-ai-search-agent-)**

</div>
