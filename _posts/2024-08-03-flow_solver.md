---
title: Flow Free Solver
description: A bot which automatically reads, deciphers, and solves Flow Free puzzles.
date: 2024-08-03 -0400
categories: [Project Write-ups]
tags: [projects]
media_subpath: /assets/img/2024-08-03-flow_solver
math: true
image:
  path: https://images.squarespace-cdn.com/content/v1/586beec5e58c624be9f7b5a2/1483733488663-JYE1NGU7MZCBOTGO9JQI/image-asset.jpeg?format=2500w
  lqip: https://images.squarespace-cdn.com/content/v1/586beec5e58c624be9f7b5a2/1483733488663-JYE1NGU7MZCBOTGO9JQI/image-asset.jpeg?format=250w
  alt: Flow Free
---

## **Too long, didn't read**
For readers who are just interested in seeing the bot in action, here is a time trial demo:
{% include embed/youtube.html id='-yLt4shM00s' %}

---
## **Introduction**

![Flow Free app icon](https://images.squarespace-cdn.com/content/v1/586beec5e58c624be9f7b5a2/1483742317507-AJVS9HFEUN3Y3BNRDOGJ/image-asset.png?format=1000w){: .w-25 .left }

[Flow Free](https://www.bigduckgames.com/flowfree) is a simple puzzle game.
The player is presented a grid, which contains pairs of colored dots in some of the cells.  The game has been around for a long time, and the concept was originally called [Numberlink](https://en.wikipedia.org/wiki/Numberlink).  The objective is to connect each pair of dots with lines with a few rules, which we will elaborate on later.  There are several game modes, including variations on the puzzle concept and a time trial.

One day this summer, a friend of mine who also plays this game beat my time trial record in the 5x5 board with 30 seconds category, solving 14 puzzles in one run.  So, I thought I would just automate the whole thing instead of doing 14 legitimately.
<figure class="disp-flex center-all flex-column">
  <img src="rage.jpg" alt="Time trial record" class="w-75">
  <figcaption class="itx caption">"Ok"</figcaption>
</figure>

Author's note: I attempted to write this assuming little knowledge in computer science or theory of computation.  Thus, I gloss over some arguably important details but I do include the minimum necessary to (hopefully) understand the point.  If you have a computer science background, you will notice that I refer to the idea of solving a flow free puzzle as the "flow problem" on occasion; this is not to be confused with any sort of flow network problem.

---
## **The rules of the game**

As discussed prior, the objective is to connect each pair of dots with lines.  I will refer to the dots as "terminals" and the lines as "pipes" when referring to the full connection or "pipe cells" when referring to a single segment of the line.  There are several constraints to how the puzzle should be solved:

<div style="display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 20px;">
  <div class="b10">
    <img src="pipe_cutting.jpg" alt="Pipe cutting" class="w-30 right">
    <p>Pipes cannot cross each other, regardless of color. They also cannot cross a terminal.</p>
    <p>Here, the blue pipe cannot connect the blue terminals because the green pipe blocks them.</p>
  </div>

  <div class="b10">
    <img src="full_pipe.jpg" alt="Full pipe" class="w-30 right">
    <p>All cells in the grid should be filled.</p>
    <p>All cells in the grid to the right are filled with either a terminal or pipe. You can see this with the "pipe: 100%" indicator above the grid.</p>
  </div>

  <div>
    <img src="pipe_snaking.jpg" alt="Pipe snaking" class="w-30 right">
    <p>All pipes are minimal paths; that is, a pipe will not "zigzag" needlessly when it could take a shorter route.</p>
    <p>In the grid to the right, the green pipe does not need to turn as much as it does to accomplish the same goal.</p>
  </div>
</div>

These rules are subject to change in certain game modes, but for the standard flow game, these are sufficient guidelines.  As it happens, every puzzle in the app is designed such that there exists exactly one solution which satisfies all conditions.

Currently, my bot only supports rectangular grids with these three standard rules, so we will only consider these for now.  I do plan to implement more complex features later.

---
## **Finding a solution**

### **Humans**

For a human player, finding a solution is not too difficult, especially for the simpler puzzles.  Us monkeys can use heuristics, logic, and intuition to find a solution.

In this example, you might guess that the red terminals shold connect along the left border, just because it "feels right".
<figure class="disp-flex center-all">
  <img src="puzzle1-0.jpg" alt="puzzle 0" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-1.jpg" alt="puzzle 1" class="w-25">
</figure>

Next, you might notice that the bottom orange terminal has a series of forced moves, where only one cardinal direction is not already occupied by a terminal (note that crossing a terminal violates one of the rules).
<figure class="disp-flex center-all">
  <img src="puzzle1-1.jpg" alt="puzzle 1" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-2.jpg" alt="puzzle 2" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-3.jpg" alt="puzzle 3" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-4.jpg" alt="puzzle 4" class="w-25">
</figure>

Coincidentally, these forced moves reach the other orange terminal.
<figure class="disp-flex center-all">
  <img src="puzzle1-4.jpg" alt="puzzle 4" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-5.jpg" alt="puzzle 5" class="w-25">
</figure>

Chances are, this was not your train of thought, but I hope this example helped illustrate some of the thought process behind solving flow puzzles at a smaller scale.

### **Computers**

The tricky part is programming a computer to do the solving.  Image parsing and automation aside, it is not trivial to lay out a strict set of rules which will solve any flow puzzle thrown at the machine (besides brute force, of course).  It may seem easy, but some puzzles are very complex and have solutions like this one, where the orange pipe goes around the entire board:
<figure class="disp-flex center-all flex-column">
  <div class="disp-flex center-all">
    <img src="puzzle2-0.jpg" alt="puzzle 0" class="w-25">
    <span class="lr10">&#8594;</span>
    <img src="puzzle2-1.jpg" alt="puzzle 1" class="w-25">
  </div>
  <figcaption class="itx caption">You're lying if this was intuitive for you.</figcaption>
</figure>
Heuristics can only get so far.  There are only two forced moves (red and pink terminals in the bottom right corner) and there are no outright obvious pipe connections.

Backtracking is unavoidable, of course.  As seen in the example above, you can't just "know" the solution without trying something first.  But a pure bashing solution like basic depth-first search (DFS), where you explore every option of moving pipes one by one, would take very long.  There are 38 possible starting moves in the example puzzle (enumerated below).  Accounting for forced moves actually increases that number (because it allows new, un-forced moves).  Of course, testing more new moves would increase that number further.
<figure class="disp-flex center-all flex-column">
  <img src="puzzle2-0-first_moves.jpg" alt="Starting moves" class="w-50">
  <figcaption class="itx caption">Move variety like chess.</figcaption>
</figure>

#### **A dead-end strategy**

Note that this not impossible to implement, I just thought it would not be worth the resources.  In fact, other people have implemented this!  Check the appendix for more.

I initially considered a different approach to this problem.

[**A-star (A\*) search**](https://en.wikipedia.org/wiki/A*_search_algorithm).  In short, A\* is a form of DFS which guides the search using heuristics which quantify the closeness of a path to the final solution to take more likely paths before unlikely ones.  If DFS takes too long, then an optimized version should do better.  However, I could not come up with a good heuristic to use.

Note that we wouldn't be using A\* to find pipe connections directly; at each stage, the search would consider an entire state of the grid with its unique collection of pipe connections.  The source would then be an empty puzzle and the target would be a solved state.  It's difficult to quantify certain characteristics, such as how "close" a game state is to the solution, which is necessary for A\* to function.  Pipe percent (the percentage of the grid covered by pipe) is one metric, but it is almost useless because of things like this:
<figure class="disp-flex center-all flex-column">
  <img src="large_pipe_pct.jpg" alt="Pipe percentage is useless" class="w-50">
  <figcaption class="itx caption">We're 91% of the way to solving the puzzle!  Wait...</figcaption>
</figure>

Additionally, to quantify closeness to a solution, it is necessary to consider terminals which are cut off from their counterpart (like every non-aqua terminal in the image above).  However, this requires checking the entire grid at each state which I thought would be inefficient.

#### **An open-end strategy?**

One day, this video was recommended to me:
{% include embed/youtube.html id='_2A3j9hSqnY' %}
Coincidentally, the creator of the video was a classmate of mine!  I only realized this very recently.  Anyway--

In short, it details the reduction of the flow problem into [boolean satisfiability](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem) or SAT (a summary of this comes in the next section).  As it turns out, flow is part of a class of problems known as NP-complete.  In laymans terms, this basically means that humanity (currently) cannot solve this problem quickly, but if given a solution, you can quickly check if it is correct.  I say "quickly" here only for impossibly or "asymptotically" large puzzles; in practice you will see that the solver is actually very fast for practical purposes.

We need not get bogged down in the theory of this, but the key here is that solving a flow problem is as simple as rephrasing it as a different, widely-researched problem of which there are many efficient solvers already made.  Now the hard part is just the process of conversion.

---
## SAT reduction

The SAT problem takes as input a boolean formula called $$\phi$$, which is essentially a set of variables $$x_1, x_2, ...$$ with boolean operators.  For example,
$$\phi = (x_1 \lor x_2) \land (x_3 \lor \neg x_1)$$
is a boolean formula.  It then outputs a boolean value assignment $$\rho$$ for these variables such that $$\phi$$ evaluates to true.  In this case, the assignment
$$\rho = \{x_1=F, x_2=T, x_3=T\}$$
would result in
$$\rho(\phi) = (F \lor T) \land (T \lor \neg F)$$
, which evalues to $$T$$
and thus $$\rho$$ is called a _satisfying_ assignment of the variables in $$\phi$$.  If no such $$\rho$$ exists, then $$\phi$$ would be called _unsatisfiable_.

The vast majority of SAT solvers actually take as input a [_conjunctive normal form (CNF)_ boolean formula](https://en.wikipedia.org/wiki/Conjunctive_normal_form) which is interchangeable with a regular boolean formula, for ease of representation.  A CNF formula is subject to several rules:
- A CNF formula only contains the operators AND ($$\land$$), OR ($$\lor$$), NOT ($$\neg$$), and parentheses.
- A CNF formula consists of a conjunction of clauses, which are in turn a disjunction of literals.
- A literal is either a variable, negated or not: $$x_1$$ and $$\neg x_2$$ are both valid literals.
- A clause, or disjunction of literals, is a set of literals which are all OR-ed together:
$$x_1 \lor x_2 \lor \neg x_3$$.
- A conjunction of clause is a set of clauses which are all AND-ed together:
$$\phi = (x_1 \lor x_2) \land (x_3 \lor \neg x_1)$$
from above is a conjunction of clauses, and thus a CNF formula.

To reduce the flow problem to SAT, we must create a way to convert a puzzle into a CNF boolean formula.

### Enforcing the rules

To do this, let's look at the rules again.  They will function as guidelines to convert the puzzle into variables and operators.
- Pipes cannot cross each other, regardless of color. They also cannot cross a terminal.
  - This one alludes nicely to a way of representing the puzzle more concretely: using a [graph](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)).  Rather than checking if a pipe illegally crosses some cell, we can just enforce pipes only connecting to neighboring cells.  What better way than to use a graph!  We can use vertices to represent cells in the grid, and connect vertices with edges only if they are neighboring along one of the four cardinal directions.  That way, a pipe cannot "jump" a cell to make an illegal connection because the absence of an edge disallows it.
<figure class="disp-flex center-all flex-column">
  <div class="disp-flex center-all">
    <img src="puzzle3-blank.jpg" alt="grid representation" class="w-40">
    <span class="lr10">&#8594;</span>
    <img src="puzzle3-graph.jpg" alt="graph representation" class="w-40">
  </div>
  <figcaption class="itx caption">Representing the grid as a graph.</figcaption>
</figure>
- All cells in the grid should be filled.
  - If all cells should be filled, then they should all be some color.  Also note should also be exactly one color.  This sounds obvious but we will have to explicitly enforce it for the reduction to work.
- All pipes are minimal paths; that is, a pipe will not "zigzag" needlessly when it could take a shorter route.
  - This one seems difficult to enforce, but it boils down to 1) a pipe cell requires exactly two neighbors of the same color (the previous and next cells in the pipe connection) and 2) a terminal cell requires exactly one neighbor of the same color, so terminals are connected to a pipe and serve as an endpoint.

### Encoding variables

Now, we need to actually convert the rules into a boolean formula.  The first task should be deciding how to choose variables to represent various parts of the puzzle.  There are probably many ways to do this, but here's what I used.  I discuss this at a high level; if you are interested in the details you can view the code on github.

Each cell in the grid or vertex in the graph $$v$$ will receive a variable $$x_{v,c}$$ for each color $$c$$ in the puzzle.  I will use "cell" and "vertex" interchangeably here, since they now essentially refer to the same entity, just in a different representation.

In other words, if we have a 10-by-10 puzzle with 9 unique colors as in the example before, we will create $$10*10*9 = 900$$ variables to represent the vertices, one for every combination of row, column, and color.  The reason we have so many duplicates is because these are boolean variables; they simply encode a true or false state and are thus incapable of encoding the complex information we need to represent every color.

Then, for vertices, we just need to create CNF clauses as follows:
- For each terminal cell:
  - The vertex is that color.  This is fairly obvious because the color is set.
  - The vertex should be at most one color.  This may seem like a given, but because of how edges will work, we do have to enforce this with additional clauses.
  - Exactly one incident edge exists.  For each of the variables corresponding to the 4 or less possible edges, only one should be true.  We encode the edges with variables; see below for more.
- For each empty cell (to-be pipe cell):
  - The vertex exactly one color.  It can be any of the valid colors, but colors are exclusive.
  - Exactly two incident edges exist.  These are not terminal cells, so a path must exist in and out of the vertex.

Each potential edge $$e=(u,v)$$ in the graph will receive a single variable $$x_e$$ denoting whether it exists or not.  If the edge exists and $$x_e$$ is true, then a pipe connects the two cells corresponding to $$u$$ and $$v$$.  If the edge does not exist and $$x_e$$ is false, then no pipe conection exists between $$u$$ and $$v$$.

Then, we only need one additional rule for CNF clauses:
- An edge exists if and only if the cells it is incident on are the same color.  The issue of only two edges per vertex is covered above.

### Using a SAT Solver

The last step is to feed these clauses into a SAT solver.  I chose [Glucose 4.2.1](https://github.com/audemard/glucose) arbitrarily, and although I have not tested other solvers, I would assume they perform similarly for all relevant puzzles.  The largest puzzles (excluding expansion packs) in the game are 15 by 18 grid cells, use somewhere around 40,000 clauses, and take an insignificant amount of time to solve compared to the other aspects of the bot...

This is Jumbo Rectangle - 150, the final level of the largest board size.  With 270 cells and 13 colors, it required 41,515 clauses and 0.0333 seconds to solve.  Not bad!  Pardon the messy output; this is just the SAT solver end of the bot and I did not see any necessity in making the text output fancy.

<figure class="disp-flex center-all flex-column">
  <div class="disp-flex center-all">
    <img src="jumbo_rectangle_150-empty.jpg" alt="big puzzle, empty" class="w-40 r5">
    <img src="jumbo_rectangle_150-solved.jpg" alt="big puzzle, solved" class="w-40 l5">
  </div>
  <div class="disp-flex center-all">
    <img src="jumbo_rectangle_150-output.jpg" alt="big puzzle, code output" class="w-100">
  </div>
</figure>

This project was made with Python so it is not as fast as possible, but less than half the time is spent on creating the many clauses, which is good enough.  Many solvers are implemented in C++ with a Python interface, hence the speed.

---
## Automation

This part of the bot was easily the most annoying.  I will briefly list what the bot does in order and discuss more later in this section.

1. When initializing the bot, get the game window and monitor dimensions.
2. Take a screenshot of the game window.  We use this to locate the grid and the initial state.
3. Get the puzzle dimensions.  I use the [OpenCV](https://opencv.org/) Python package, [`cv2`](https://github.com/opencv/opencv-python) for this.
4. Read and parse the puzzle.
5. Solve the puzzle, using the SAT reducer and solver.
6. Find the pipe paths for each cell, then determine a coordinate path to drag the mouse through.
7. Execute the mouse instructions and solve the puzzle.

### Initializing the bot

I implement the bot as an object, and upon creation it does several things:
1. Find the game window and move it to focus.  This just saves time, since during testing it gets pretty annoying switching from my code editor or terminal to the other window so mouse clicks work correctly.  It also helps to check that the game is actually open before doing anything.
2. Get the location and dimensions of the window.  This allows the bot to function in any (normal) setting and removes the need to hard-code numbers or position the game window in a certain location.
3. Get the monitor dimensions.  This is useful later for image processing.  I have not tested every monitor dimension so this doesn't guarantee system compatibility, but it should work for all reasonable screens.

### Take a screenshot

This was surprisingly annoying.  *You'll notice this is a recurring theme! :)*

MacOS has a built-in screenshot system.  By default, the keyboard shortcut is `cmd` + `shift` + `4`, which allows you to drag the cursor over a section of a screen.  There is also a terminal command:

```sh
screencapture -R100,200,300,400 ~/Desktop/screenshot.png
```

This would take a screenshot of the rectangular region 100 pixels from the left, 200 pixels from the top, 300 pixels wide, and 400 pixels high, then save it to the desktop as `screenshot.png`.  This is functional and native, but it is slow.

The next method I tried was [Pillow / PIL](https://pypi.org/project/pillow/), a Python image processing library.  This was even slower.

Turning to stack overflow, I ended up using [MSS](https://github.com/BoboTiG/python-MSS).

I tested each method by taking 10 fullscreen screenshots.  Here were the average times:

```text
Average screencapture time: 0.1508 seconds
       Average Pillow time: 0.7135 seconds
          Average MSS time: 0.1690 seconds
```

Hmm... `screencapture` seems to be the fastest still.  Let's rig the game by taking a screenshot of just a third of the screen, which (for me) is roughly the size of the Flow Free game window-- which cannot be resized, for whatever reason.  Thanks, Apple?  In practice, the bot will never take a screenshot of the entire screen.

Again, I took 10 screenshots, now of the left third of the screen, and averaged the times.

```text
Average screencapture time: 0.1088 seconds
       Average Pillow time: 0.1976 seconds
          Average MSS time: 0.0639 seconds
```

The native `screencapture` command used about 72% of the time compared to a fullscreen screenshot.  Pillow used 27%, and MSS used 37%.  I don't know what causes such a disparity, especially when 33% of the time should be expected.  But whatever, MSS seems like the fastest method so that's what I ended up using.

### Find the puzzle dimensions

This part was also surprisingly annoying.  I used OpenCV to process the images for generalization to avoid hard-coding specific puzzle dimensions.

The first step is to convert the image to grayscale.  A standard image has 3 color channels (red, green, blue) while a grayscale only has 1, which is less stuff to process.

### Read the puzzle

### Solve the puzzle

### Find paths

### Drag the mouse