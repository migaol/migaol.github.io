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
{% include embed/youtube.html id='GEJYJOYi5_c' %}

---
## **Introduction**

![Flow Free app icon](https://images.squarespace-cdn.com/content/v1/586beec5e58c624be9f7b5a2/1483742317507-AJVS9HFEUN3Y3BNRDOGJ/image-asset.png?format=1000w){: .w-25 .left }

[Flow Free](https://www.bigduckgames.com/flowfree) is a simple puzzle game.
The player is presented a grid, which contains pairs of colored dots in some of the cells.  The game has been around for a long time, and the concept was originally called [Numberlink](https://en.wikipedia.org/wiki/Numberlink).  The objective is to connect each pair of dots with lines with a few rules, which we will elaborate on later.  There are several game modes, including variations on the puzzle concept and a time trial.

One day this summer, a friend of mine who also plays this game beat my time trial record in the 5x5 board with 30 seconds category, solving 14 puzzles in one run.  So, I thought I would just automate the whole thing instead of doing 14 legitimately.
<figure class="disp-flex center-all flex-column">
  <img src="rage.jpg" alt="Time trial record" class="w-75">
  <figcaption class="caption">"Ok"</figcaption>
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

Chances are, this was not your train of thought and you solved the entire puzzle in a second, but I hope this example helped illustrate some of the thought process behind solving flow puzzles at a smaller scale.

### **Computers**

The tricky part is programming a computer to do the solving.  Image parsing and automation aside, it is not trivial to lay out a strict set of rules which will solve any flow puzzle thrown at the machine (besides brute force, of course).  It may seem easy, but some puzzles are very complex and have solutions like this one, where the orange pipe goes around the entire board:
<figure class="disp-flex center-all flex-column">
  <div class="disp-flex center-all">
    <img src="puzzle2-0.jpg" alt="puzzle 0" class="w-25">
    <span class="lr10">&#8594;</span>
    <img src="puzzle2-1.jpg" alt="puzzle 1" class="w-25">
  </div>
  <figcaption class="caption">You're lying if this was intuitive for you.</figcaption>
</figure>
Heuristics can only get so far.  There are only two forced moves (red and pink terminals in the bottom right corner) and there are no outright obvious pipe connections.

As seen in the example above, you can't just "know" the solution without trying something first.  But a pure bashing solution like basic depth-first search (DFS), where you explore every option of moving pipes one by one, would take very long.  There are 38 possible starting moves in the example puzzle (enumerated below).  Accounting for forced moves actually increases that number (because it allows new, un-forced moves).  Of course, testing more new moves would increase that number further.
<figure class="disp-flex center-all flex-column">
  <img src="puzzle2-0-first_moves.jpg" alt="Starting moves" class="w-50">
  <figcaption class="caption">Move variety like chess.</figcaption>
</figure>

#### **A dead-end strategy**

Note that this not impossible to implement, I just thought it would not be worth the resources.  In fact, other people have implemented this!  Check the appendix for more.

I initially considered a different approach to this problem, [**A-star (A\*) search**](https://en.wikipedia.org/wiki/A*_search_algorithm).  In short, A\* is a form of DFS which guides the search using heuristics which quantify the closeness of a path to the final solution to take more likely paths before unlikely ones, so it will probably never even consider most paths which don't go in the right direction.  The idea is that if DFS takes too long, then an optimized version should do better.

Note that we wouldn't be using A\* to find pipe connections directly; at each stage of the search, the search would consider an entire state of the grid with its unique collection of pipe connections holistically.  The search would begin at the empty puzzle, traverse through puzzle states, and eventually arrive at the target solved puzzle state.

However, I could not come up with a good heuristic to use.  It's difficult to quantify certain characteristics, such as how "close" a game state is to the solution, which is necessary for A\* to function.  Pipe percent (the percentage of the grid covered by pipe) is one metric, but it is almost useless because of things like this:
<figure class="disp-flex center-all flex-column">
  <img src="large_pipe_pct.jpg" alt="Pipe percentage is useless" class="w-50">
  <figcaption class="caption">We're 91% of the way to solving the puzzle!  Wait...</figcaption>
</figure>

Additionally, to quantify closeness to a solution, it is necessary to consider terminals which are cut off from their counterpart (for example, every non-aqua terminal in the image above).  Despite the fact that this consideration saves unnecessarily exploring an incorrect puzzle state, it also requires checking the entire grid at each step, which I thought would be inefficient.

#### **An open-end strategy?**

One day, this video popped up in my YouTube recommendations:
{% include embed/youtube.html id='_2A3j9hSqnY' %}
Coincidentally, the creator of the video was a classmate of mine!  I only realized this very recently.  Anyway--

In short, it details the reduction of the flow problem into [boolean satisfiability](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem) or SAT (a summary of this comes in the next section).  As it turns out, flow is part of a class of problems known as NP-complete.  In laymans terms, this basically means that humanity (currently) cannot solve this problem quickly, but if given a solution, you can quickly check if it is correct.  I say "quickly" here only for impossibly or "asymptotically" large puzzles; in practice you will see that the solver is actually very fast for practical purposes.

We need not get bogged down in the theory of this, but the key here is that solving a flow problem is as simple as rephrasing it as a different, widely-researched problem of which there are many efficient solvers already made.  Now the hard part is just the process of conversion.

---
## SAT reduction

The SAT problem takes a boolean formula called $$\phi$$ as input, which is essentially a set of variables $$x_1, x_2, ...$$ with boolean operators.  For example,
$$\phi = (x_1 \lor x_2) \land (x_3 \lor \neg x_1)$$
is a boolean formula (see the next paragraph for notation).  It then outputs a boolean value assignment $$\rho$$ for these variables such that $$\phi$$ evaluates to true.  In this case, the assignment
$$\rho = \{x_1=F, x_2=T, x_3=T\}$$
would result in
$$\rho(\phi) = (F \lor T) \land (T \lor \neg F)$$
, which evalues to $$T$$
and thus $$\rho$$ is called a _satisfying_ assignment of the variables in $$\phi$$.  If no such $$\rho$$ exists, then $$\phi$$ would be called _unsatisfiable_.

The vast majority of SAT solvers actually take a [_conjunctive normal form (CNF)_ boolean formula](https://en.wikipedia.org/wiki/Conjunctive_normal_form) as input, which is interchangeable with a regular boolean formula, for ease of representation.  A CNF formula is subject to several rules:
- A CNF formula only contains the operators AND ($$\land$$), OR ($$\lor$$), NOT ($$\neg$$), and parentheses.
- A CNF formula consists of a conjunction of clauses, which are in turn a disjunction of literals.
- A literal is either a variable, negated or not: $$x_1$$ and $$\neg x_2$$ are both valid literals.
- A clause, or disjunction of literals, is a set of literals which are all OR-ed together:
$$x_1 \lor x_2 \lor \neg x_3$$.
- A conjunction of clause is a set of clauses which are all AND-ed together:
$$\phi = (x_1 \lor x_2) \land (x_3 \lor \neg x_1)$$
from above is a conjunction of clauses, and thus a CNF formula.

In short, CNF is an "AND of OR's of literals".  To reduce the flow problem to SAT, we must create a way to convert a puzzle into a CNF boolean formula.

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
  <figcaption class="caption">Representing the grid as a graph.</figcaption>
</figure>
- All cells in the grid should be filled.
  - If all cells should be filled, then they should all be some color.  Also note should also be exactly one color.  This sounds obvious but we will have to explicitly enforce it for the reduction to work.
- All pipes are minimal paths; that is, a pipe will not "zigzag" needlessly when it could take a shorter route.
  - This one seems difficult to enforce, but it boils down to:
    1. A pipe cell requires exactly two neighbors of the same color: the previous and next cells in the pipe connection.  If there are fewer than two, then the pipe cell has a hanging end.  If there are more than two, then the pipe cell is part of some zigzagging part of the pipe.
    2. A terminal cell requires exactly one neighbor of the same color, so terminals are connected to a single pipe and serve as an endpoint.  If there is more than one neighbor, then the terminal would be adjacent to another pipe.
  - To allow this, we have to adjust the graph definition.  We will include an edge if and only if it connects two neighboring cells-- that is, if one of the cells is a pipe.  Likewise, two cells are neighboring but are not connected via a pipe, the graph representation should have no edge.
<figure class="disp-flex center-all flex-column">
  <div class="disp-flex center-all">
    <img src="puzzle3-blank.jpg" alt="grid representation" class="w-40">
    <span class="lr10">&#8594;</span>
    <img src="puzzle3-no_edges_graph.jpg" alt="graph representation without edges" class="w-40">
  </div>
  <figcaption class="caption">A grid without any pipes should be represented as a graph without any edges.</figcaption>
</figure>
<figure class="disp-flex center-all flex-column">
  <div class="disp-flex center-all">
    <img src="puzzle3-solved.jpg" alt="grid representation, solved" class="w-40">
    <span class="lr10">&#8594;</span>
    <img src="puzzle3-solved_graph.jpg" alt="graph representation, solved and only with necessary edges" class="w-40">
  </div>
  <figcaption class="caption">All grid cells which are connected with pipes have edges in the graph representation.</figcaption>
</figure>

### Encoding variables

Now, we need to actually convert the rules into a boolean formula.  The first task should be deciding how to choose variables to represent various parts of the puzzle.  There are probably many ways to do this, but here's what I used.  I discuss this at a high level; if you are interested in the details you can view the [code](https://github.com/migaol/flow-solver) on github.

Each cell in the grid or vertex $$v$$ in the graph will receive a variable $$x_{v,c}$$ for each color $$c$$ in the puzzle.  I will use "cell" and "vertex" interchangeably here, since they now essentially refer to the same entity, just in a different representation.

In other words, if we have a 10-by-10 puzzle with 9 unique colors as in the example before, we will create $$10*10*9 = 900$$ variables to represent the vertices, one for every combination of row, column, and color.  The reason we have so many duplicates is because these are boolean variables; they simply encode a true or false state and are thus incapable of encoding the complex information we need to represent every color.

Then, for vertices, we just need to create CNF clauses as follows:
- For each terminal cell:
  - The vertex is that color.  This is fairly obvious because the color is set.
  - The vertex should be at most one color.  This may seem like a given, but because of how edges will work, we do have to enforce this with additional clauses.
  - Exactly one incident edge exists.  For each of the variables corresponding to the 4 or less possible edges, only one should be true.  We encode the edges with variables; see below for more.
- For each empty cell (to-be pipe cell):
  - The vertex is exactly one color.  It can be any of the valid colors, but colors are exclusive.
  - Exactly two incident edges exist.  These are not terminal cells, so a path must exist in and out of the vertex.

Each potential edge $$e=(u,v)$$ in the graph will receive a single variable $$x_e$$ denoting whether it exists or not.  If the edge exists and $$x_e$$ is true, then a pipe connects the two cells corresponding to $$u$$ and $$v$$.  If the edge does not exist and $$x_e$$ is false, then no pipe conection exists between $$u$$ and $$v$$.

Then, we only need one additional rule for CNF clauses:
- An edge exists if and only if the cells it is incident on are the same color.  The condition of exactly two edges per vertex is covered above.

### Using a SAT Solver

The last step is to feed these clauses into a SAT solver.  I chose [Glucose 4.2.1](https://github.com/audemard/glucose) arbitrarily, and although I have not tested other solvers, I would assume they perform similarly for all relevant puzzles.  The largest puzzles (excluding expansion packs) in the game are 15 by 18 grid cells, use somewhere around 40,000 clauses, and take an insignificant amount of time to solve compared to the other aspects of the bot.

The puzzle below is Jumbo Rectangle - 150, the final level of the largest board size.  With 270 cells and 13 colors, it required 41,515 clauses and 0.0333 seconds to solve.  Not bad!  Pardon the messy output; this is just the SAT solver end of the bot and I did not see any necessity in making the text output fancy.  The blocks of text are unimportant, but solve statistics are displayed at the bottom of the third image.

<figure class="disp-flex center-all flex-column">
  <div class="disp-flex center-all">
    <img src="jumbo_rectangle_150-empty.jpg" alt="big puzzle, empty" class="w-40 r5">
    <img src="jumbo_rectangle_150-solved.jpg" alt="big puzzle, solved" class="w-40 l5">
  </div>
  <div class="disp-flex center-all">
    <img src="jumbo_rectangle_150-output.jpg" alt="big puzzle, code output" class="w-100">
  </div>
</figure>

This project was made with Python so it is not as fast as possible, but less than half the time is spent on creating the many clauses, which is good enough.  Many solvers are implemented in C++ with a Python interface, hence the speed of pure solving relative to creating the clauses.

---
## Automation

This part of the bot was easily the most annoying.  I will briefly list what the bot does in order and discuss more later in this section.

1. When initializing the bot, get the game window and monitor dimensions.
2. Take a screenshot of the game window.  We use this to locate the grid and the initial state.
3. Get the puzzle dimensions.  I use the [OpenCV](https://opencv.org/) Python package, [`cv2`](https://github.com/opencv/opencv-python) for this.
4. Read and parse the puzzle.
5. Solve the puzzle, using the SAT reducer and solver.
6. Find the pipe paths for each cell, then determine a coordinate path to drag the mouse through.  Then execute the mouse instructions and solve the puzzle.

I made the bot for macOS only.  The most important reason is that my primary machine is a macbook.  Also, the macOS app store supports some mobile applications designed for iOS (such as Flow Free) thanks to their shared parent company.  This allows me to run Flow Free without the use of a virtual machine or emulator such as BlueStacks.

### Initializing the bot

I implement the bot as an object, and upon creation it does several things:
1. Find the game window and move it to focus.  This just saves time, since during testing it gets pretty annoying switching from my code editor or terminal to the other window so mouse clicks work correctly.  It also helps to check that the game is actually open before doing anything and potentially clicking in unwanted places.
2. Get the location and dimensions of the window.  This allows the bot to function in any (normal) setting and removes the need to hard-code numbers or position the game window in a certain location.
3. Get the monitor dimensions.  This is useful later for image processing.  I have not tested every monitor dimension so this doesn't guarantee system compatibility, but it should work for all reasonable screens.

### Take a screenshot

This was surprisingly annoying.  *You'll notice this is a recurring theme! :)*

macOS has a built-in screenshot system.  By default, the keyboard shortcut is `cmd` + `shift` + `4`, which allows you to drag the cursor over a section of a screen.  There is also a terminal command:

```sh
screencapture -R100,200,300,400 ~/Desktop/screenshot.png
```

This would take a screenshot of the rectangular region 100 pixels from the left, 200 pixels from the top, 300 pixels wide, and 400 pixels high, then save it to the desktop as `screenshot.png`.  This is functional and native, but it is slow.

The next method I tried was [Pillow / PIL](https://pypi.org/project/pillow/), a Python image processing library.  This was even slower.

After turning to stack overflow, I ended up using [MSS](https://github.com/BoboTiG/python-MSS).

I tested each method by taking 10 fullscreen screenshots.  Here were the average times:

```text
Average screencapture time: 0.1508 seconds
       Average Pillow time: 0.7135 seconds
          Average MSS time: 0.1690 seconds
```

Hmm... `screencapture` seems to be the fastest still.  Let's rig this by taking a screenshot of just a third of the screen, or roughly the size of the Flow Free game window-- which cannot be resized, for whatever reason.  Thanks, Apple?  In practice, the bot will never take a screenshot of the entire screen so we shouldn't use that to evaluate efficiency.

Again, I took 10 screenshots, now of the left third of the screen, and averaged the times.

```text
Average screencapture time: 0.1088 seconds
       Average Pillow time: 0.1976 seconds
          Average MSS time: 0.0639 seconds
```

The native `screencapture` command used about 72% of the time compared to a fullscreen screenshot.  Pillow used 27%, and MSS used 37%.  I don't know what causes such a disparity, especially when 33% of the original time should be expected.  But whatever, MSS seems like the fastest method so that's what I ended up using.  Any small time save adds up for time trials, so I needed any worthwhile optimizations I could.  Spoiler: the final bot can solve well over 30 5-by-5 puzzles in 30 seconds, meaning even with MSS about 2 full seconds are used to just take screenshots!

Another way to get screen information is with `pyautogui.pixel()` or similar methods of getting a single pixel.  These implicitly take a screenshot so repeatedly calling it is actually far more inefficient than just taking a screenshot.

### Find the puzzle dimensions

This part was also surprisingly annoying.  I used OpenCV to process the images for generalization to avoid hard-coding specific puzzle dimensions.

In this section let's keep track of an example puzzle.  Here is the original screenshot:
<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-puzzle.jpg" alt="Puzzle processing: original screenshot" class="w-50">
</figure>

The first step is to convert the image to grayscale.  A standard image has 3 color channels (red, green, blue or RGB) while a grayscale only has 1, which is less stuff to process.  While this is impractical for discerning colors because converting an RGB image to grayscale effectively removes its hue (the type of color) and saturation (the intensity of the color) and thus makes colors of similar "brightness" near-indistiguishable, at this point only grid structure is relevant.  In fact, I ignore the color terminals at this step altogether.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-gray.jpg" alt="Puzzle processing: grayscale" class="w-50">
</figure>

Then, I apply an adaptive threshold to the grayscale image.  This converts the single gray color channel into a binary (black/white) color channel, which makes finding lines in the image much easier.  It works by comparing each pixel to its neighbors, checking if the difference between them exceeds a threshold, and using white to represent that pixel in resulting image if that is the case or black if not.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-threshold.jpg" alt="Puzzle processing: thresholding" class="w-50">
</figure>

Now we can start finding the grid lines.  I initially tried using [Hough Line Transform](https://docs.opencv.org/4.x/d9/db0/tutorial_hough_lines.html), which detects straight line segments.  However, after extensive tuning and playing around, I determined it wasn't good enough.  If you look closely in threshold image above (click an image to enlarge it), you may see that the borders between grid lines are double-struck.  This is a relic of thresholding.  I could use a larger threshold kernel (scale) but that misses some lines.  Overall, this made using Hough Lines unsatisfactory.  After testing other non-rectangular puzzle shapes, it turns out Hough Lines is also not very generalizable if you can't confidently specify a line size it should search for.

Instead, I found [contours](https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html), or more simply, shapes.  However, the contours found would often be numerous (several hundreds) paired with a modest grid size.  This is thanks to the double-struck lines as described above as well as clutter outside the grid, including words, buttons, and advertisements.  It would also occasionally miss grid squares becuse the lines were thin.

To solve this issue I employed [dilation](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html).  This is a morphological function which makes things larger, but in our case, it has the added benefit of merging the duplicate lines and closing gaps.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-dilate_all.jpg" alt="Puzzle processing: dilation" class="w-50">
</figure>

Now we can find contours correctly.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-contours_screen_all.jpg" alt="Puzzle processing: all contours on screen" class="w-50">
  <figcaption class="caption">Contours outlined in red.</figcaption>
</figure>

I used an external contour finding method so none of the inner squares or circles of the grid are found.  This first round of contours is to locate the grid.  The largest contour by area is always the grid after testing, which saves some time.  Contrary to the visuals, the largest contour is not always square, so we additionally need to find and use its bounding box.

<div class="disp-flex center-all">
  <figure class="disp-flex center-all flex-column">
    <img src="puzzle4-contours_largest.jpg" alt="Puzzle processing: largest contour" class="w-75">
    <figcaption class="caption">Vertices of the contour indicated in yellow.</figcaption>
  </figure>
  <figure class="disp-flex center-all flex-column">
    <img src="puzzle4-board_bbox.jpg" alt="Puzzle processing: largest contour bbox" class="w-75">
    <figcaption class="caption">Bounding box of the contour in green.</figcaption>
  </figure>
</div>

We can now discard everything outside the bounding box to focus on the grid area only.  We want to find the grid cells now.

The circles of the grid now pose a problem, since not only will they be found as extraneous contours, they take away from the cell they occupy.  We can dilate the image again and erode it, a process known as a [*morphological closing*](https://en.wikipedia.org/wiki/Closing_(morphology)).  Normally this is used to fill holes in an image, but because the grid lines were originally slightly larger than the circle lines, dilating then eroding with a larger kernel (scale) can erase most of the circles while only thinning the grid lines.

<div class="disp-flex center-all">
  <figure class="disp-flex center-all flex-column">
    <img src="puzzle4-dilate_grid.jpg" alt="Puzzle processing: dilate on grid" class="w-75">
    <figcaption class="caption">Dilate...</figcaption>
  </figure>
  <figure class="disp-flex center-all flex-column">
    <img src="puzzle4-erode_grid.jpg" alt="Puzzle processing: erode on grid" class="w-75">
    <figcaption class="caption">...then erode.</figcaption>
  </figure>
</div>

It is now easy to find contours again and locate grid cells.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-contours_grid_all.jpg" alt="Puzzle processing: grid contour bounding boxes" class="w-50">
  <figcaption class="caption">Contours outlined in green.</figcaption>
</figure>

There are also some imperfections mixed in from the remnants of the morphological closing.  I first construct a bounding box for each contour, then filter out ones which are too small.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-contours_groups.jpg" alt="Puzzle processing: grid contours" class="w-50">
  <figcaption class="caption">Contours' bounding boxes outlined in pink.</figcaption>
</figure>

Using individual grid cell contour boxes, we can calculate the rough size of a cell in pixels, which can in turn be used to find the number of rows and columns in the grid.

### Read the puzzle

We now have the necessary information to parse the puzzle by finding the terminal cells.  The terminal cell circles are large so they can be located just by looking at the center of each cell.  We're using a color image again to differentiate terminals.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-pixel_samples.jpg" alt="Puzzle processing: finding terminal cells" class="w-50">
  <figcaption class="caption">Sample a pixel from the center of each cell, indicated by the white circle.</figcaption>
</figure>

### Solve the puzzle

We can reconstruct the puzzle in the code and pass it to the solver.  Assuming everything went as planned, the solver outputs a solution.  To decipher it, first locate one terminal of each color and follow a path to the other terminal to find the cells a pipe must go through.  Normally dragging a mouse through these is enough, but in certain cases this is extremely slow...

### Find paths and drag the mouse

I grouped the last two procedures together because they are closely related.  For mouse control, I use [`pyautogui`](https://pypi.org/project/PyAutoGUI/), which is probably the only good option.  [`pynput`](https://pypi.org/project/pynput/) is also a choice but I did not have success with it.

The first version of the bot used the primitive method of simply dragging a mouse through each cell necessary, following paths parallel to the grid lines:

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-path_v1.jpg" alt="Pathfinding: dragging through every cell" class="w-50">
  <figcaption class="caption">The mouse follows the path in white and stops at each gray dot.</figcaption>
</figure>

This simple solution is very slow.  You can see the *real-time* demonstration of this method in action below.  I logged the time to solve the puzzle as well, and the distribution is disappointing.  Almost all of the time spent on the puzzle is from dragging the mouse.  A human is even likely to do it faster manually.

```text
Pathfinding version 1
-----------------------------------------
           Screenshot: 0.1144 s (0.82%)
Get puzzle dimensions: 0.0151 s (0.11%)
Read and parse puzzle: 0.0069 s (0.05%)
         Solve puzzle: 0.0068 s (0.05%)
   Compute mouse path: 0.0001 s (0.00%)
           Drag mouse: 13.7326 s (98.97%)
                total: 13.8759 s
```

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-v1.gif" alt="Pathfinding: dragging through every cell" class="w-75">
  <figcaption class="caption">Pathfinding version 1: Dragging through every cell.</figcaption>
</figure>

Fortunately, there is ample room for improvement.  For example, it is unnecessary to drag the cursor fully through the flow.  The game has a nice little feature which allows pipes which end in any cell adjacent to the other terminal will automatically connect to the terminal.  This reduces dragging by one cell per color, which is a small but welcome improvement.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-path_v2.jpg" alt="Pathfinding: skipping the final terminal" class="w-50">
  <figcaption class="caption">The path now skips the final terminal.</figcaption>
</figure>

In this example, it shaves about 1 second off the solve time.

```text
Pathfinding version 2
-----------------------------------------
           Screenshot: 0.0941 s (0.75%)
Get puzzle dimensions: 0.0131 s (0.10%)
Read and parse puzzle: 0.0058 s (0.05%)
         Solve puzzle: 0.0068 s (0.05%)
   Compute mouse path: 0.0001 s (0.00%)
           Drag mouse: 12.3669 s (99.04%)
                total: 12.4868 s
```

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-v2.gif" alt="Pathfinding: skipping the final terminal" class="w-75">
  <figcaption class="caption">Pathfinding version 2: Dragging through every cell except the final terminal.</figcaption>
</figure>

At this point you might have noticed that the mouse is spending unnecessary time at cells which are not turns in the path.  A straight part of a path done in one mouse motion is functionally identical to the same straight part done in 5 separate segments.  Thus we can optimize more by "merging" consecutive mouse motions in the same direction in each path.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-path_v3.jpg" alt="Pathfinding: dragging to turns only." class="w-50">
  <figcaption class="caption">The path now goes as far as possible before making a 90-degree turn.</figcaption>
</figure>

This improvement cuts the time requirement of mouse dragging by about half.

```text
Pathfinding version 3:
----------------------------------------
           Screenshot: 0.1260 s (2.11%)
Get puzzle dimensions: 0.0188 s (0.31%)
Read and parse puzzle: 0.0059 s (0.10%)
         Solve puzzle: 0.0084 s (0.14%)
   Compute mouse path: 0.0001 s (0.00%)
           Drag mouse: 5.8160 s (97.34%)
                total: 5.9751 s
```

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-v3.gif" alt="Pathfinding: dragging to turns only." class="w-75">
  <figcaption class="caption">Pathfinding version 3: Skipping the final terminal and dragging to turns only.</figcaption>
</figure>

You may also notice that the mouse seems to take longer than necessary to execute each movement itself.  I wish that mouse control could be instant, but there are unfortunate limitations.  In `pyautogui`, each mouse button action requires about 0.01 seconds, and each mouse drag/movement requires about 0.03 seconds.  Most of `pyautogui`'s mouse control methods have a keyword argument which allows you to set the duration of mouse movement to 0:

```python
pyautogui.moveTo(x, y, duration=0)
```

This should be instantaneous, but after doing some research, it seems that the OS must fully register mouse actions in order for it to count, so a small length of time is required to execute mouse commands.  This argument is 0 by default for all relevant methods so it was already implemented in previous pathfinding verions.

I spent a while trying to figure out why it was still so slow.  It turns out there's a hidden argument behind all the functions.  This is the function signature of `pyautogui.moveTo()`:

```python
def moveTo(
    x: Any | None = None,
    y: Any | None = None,
    duration: float = 0,
    tween: Any = linear,
    logScreenshot: bool = False,
    _pause: bool = True
) -> None
```

There is an argument `_pause` which is `True` by default.  I initially did not think much of it, because an argument preceded by an underscore (`_`) is the pythonic way of marking it as private (something you shouldn't mess with) because there are no visibility modifiers in the language.  I looked into the [source code](https://github.com/asweigart/pyautogui) and it's [not even used](https://github.com/asweigart/pyautogui/blob/b4255d0be42c377154c7d92337d7f8515fc63234/pyautogui/__init__.py#L1261) in the `pyautogui.moveTo()` method.

However, it has an unsettling name, and after trying to specify `_pause = False`, it turns out this is some sort of failsafe.  Disabling this parameter magically made the bot so much faster-- almost a 5x speed-up.

```text
Pathfinding version 4:
----------------------------------------
           Screenshot: 0.1095 s (7.58%)
Get puzzle dimensions: 0.0144 s (0.99%)
Read and parse puzzle: 0.0065 s (0.45%)
         Solve puzzle: 0.0075 s (0.52%)
   Compute mouse path: 0.0001 s (0.01%)
           Drag mouse: 1.3076 s (90.46%)
                total: 1.4456 s
```

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-v4.gif" alt="Pathfinding: dragging to turns only." class="w-75">
  <figcaption class="caption">Pathfinding version 4: Removing pausing.</figcaption>
</figure>

It's obviously not a good idea to go around disabling failsafes but I have had no problems after making the change.  The bot is very fast now, and for a while I thought it was at peak performance.

There's a small source of inefficiency, though.  On some puzzles there are zigzag patterns where taking 90-degree turns is sub-optimal.  Here is one where there are a few paths with frequent turns.

<figure class="disp-flex center-all">
  <img src="puzzle5-empty.jpg" alt="empty puzzle with many turns" class="w-40">
  <span class="lr10">&#8594;</span>
  <img src="puzzle5-solved.jpg" alt="solved puzzle with many turns" class="w-40">
</figure>

And here is the path and time it takes to solve the puzzle with the best method thus far (version 4).

<figure class="disp-flex center-all flex-column">
  <img src="puzzle5-straight_lines.jpg" alt="Pathfinding: puzzle with turns" class="w-50">
</figure>

```text
           Screenshot: 0.0964 s (6.13%)
Get puzzle dimensions: 0.0094 s (0.60%)
Read and parse puzzle: 0.0062 s (0.40%)
         Solve puzzle: 0.0075 s (0.48%)
   Compute mouse path: 0.0001 s (0.01%)
           Drag mouse: 1.4530 s (92.39%)
                total: 1.5726 s
```

It looks fast, but it can be improved upon.  I implemented a new path finder which views the cells in the grid as squares, not a single point in the center.  That way, it can see more complex paths that take diagonals smoothly instead of at 90-degree angles.  This is the path the new version finds:

<figure class="disp-flex center-all flex-column">
  <img src="puzzle5-corner_cuts.jpg" alt="Pathfinding: puzzle with turns" class="w-50">
</figure>

It looks messy and a little confusing, because it no longer takes paths through the center of each cell-- recall that mouse moves can be "instantaneous" in `pyautogui`, and this is true regardless of distance, so the goal with this path finder is to minimize the number of segments in each path, not the distance the mouse travels.  Note how the maroon and purple paths merge the diagonal portions into diagonal lines instead of zigzags.

This method improves the time significantly for puzzles with drastic zigzags.  At the cost of a little more time to compute a mouse path, it eliminates almost a third of time spent on unnecessary mouse movement.

```text
           Screenshot: 0.1165 s (9.50%)
Get puzzle dimensions: 0.0222 s (1.81%)
Read and parse puzzle: 0.0059 s (0.48%)
         Solve puzzle: 0.0083 s (0.68%)
   Compute mouse path: 0.0077 s (0.63%)
           Drag mouse: 1.0655 s (86.90%)
                total: 1.2261 s
```

Here is a side-by-side comparison for the two pathfinding methods.

<div class="disp-flex center-all">
  <figure class="disp-flex center-all flex-column">
    <img src="puzzle5-straight_lines.gif" alt="Puzzle solving: straight lines" class="w-75">
    <figcaption class="caption">With 90-degree turns.</figcaption>
  </figure>
  <figure class="disp-flex center-all flex-column">
    <img src="puzzle5-corner_cuts.gif" alt="Puzzle solving: cutting corners" class="w-75">
    <figcaption class="caption">Optimizing diagonals.</figcaption>
  </figure>
</div>

How does this compare for the original puzzle we were examining?

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-path.jpg" alt="Pathfinding: cutting corners." class="w-50">
  <figcaption class="caption">Pathfinding version 5: optimizing diagonals.</figcaption>
</figure>

This improvement does not make a difference.  There are only a few zigzag areas where the new pathfinding algorithm can detect a path in fewer segments, namely, the red and white pipes.  Mouse dragging is very slightly faster but the gain is offset by the time to compute a mouse path.  There's some small variation, probably due to background processes (though throughout all the timing, I only had the terminal and Flow Free apps open and closed what I could to minimize variation), but the total time is unchanged.

<figure class="disp-flex center-all flex-column">
  <img src="puzzle4-v5.gif" alt="Puzzle solving: cutting corners" class="w-75">
</figure>

```text
Pathfinding version 5
----------------------------------------
           Screenshot: 0.1228 s (8.43%)
Get puzzle dimensions: 0.0180 s (1.23%)
Read and parse puzzle: 0.0050 s (0.34%)
         Solve puzzle: 0.0074 s (0.51%)
   Compute mouse path: 0.0075 s (0.51%)
           Drag mouse: 1.2966 s (88.98%)
                total: 1.4571 s
```

The diagonal path improvement is a sidegrade for some puzzles and a noticeable upgrade for others.

---
## Time trials

To finalize the bot for time trials, I made a separate solving mode.  It would only get the puzzle dimensions once, then use that information for the remainder of the time trial since it will remain the same.  Besides this small time save, the bot just loops over and over taking a screenshot, reading the puzzle, solving the puzzle, and finding a path to drag the mouse.

There is one last obstacle to solving Flow Free time trials quickly.  After each puzzle is completed in a time trial, there is a *long* animation where the grid flips over to show the new puzzle.

<figure class="disp-flex center-all flex-column">
  <img src="slow_transition.gif" alt="Slow puzzle transition" class="w-50">
  <figcaption class="caption">*Insert concrete sliding sound effect.*</figcaption>
</figure>

It seems to be just over exactly 0.5 seconds long, which is enough to effectively cut a time trial's duration by over half.  A 30-second time trial is less 15 seconds of solve time when the bot solves more than 30 puzzles (and it does solve that many), which makes it even more difficult for further optimization.

I tried to make the bot take a screenshot before the animation even finishes, when the board is still viewed at an angle.  This was inconsistent and wouldn't always work.  Part of the grid is always either off-screen or obscured by button and text elements, which makes discerning the board extremely difficult.

Ultimately, the bot is not most constrained by its code, but by the game itself.  I believe this qualifies as bad game design.

---
## Notes for improvement

You can skip this section to see the bot in action.  Here, I discuss some other optimization options available which did not make the cut for the final bot.

### Mouse dragging in one movement

One such optimization is dragging the mouse as one continuous motion, without dragging paths as line segments.  To help explain, consider pseudocode for my line dragging algorithm:

```python
for color in terminal colors:
    pyautogui.moveTo(a terminal of the color)
    mouse_path = pathfinder(color.path)
    for point in mouse_path:
        pyautogui.dragTo(point)
```

The `pyautogui.dragTo()` function actually presses the left mouse button down, moves, then releases it.  As discussed before, this takes a small amount of time.  It is possible to toggle this off, and instead only press and release the mouse button once:

```python
for color in terminal colors:
    pyautogui.moveTo(a terminal of the color)
    pyautogui.mouseDown(left mouse button)
    mouse_path = pathfinder(color.path)
    for point in mouse_path:
        pyautogui.dragTo(point, mouseUpDown = False)
    pyautogui.mouseUp(left mouse button)
```

Notice the parameter `mouseUpDown = False`, which suppresses any mouse button press/release when dragging.  This seems like it would improve the time, but unfortunately the cursor moves too fast for the operating system to register it correctly.  I also tried to manually add `time.sleep()` pauses between mouse drags, but it was ultimately not able to improve the speed without sacrificing accuracy.

With `mouseUpDown = False` and minimal pausing between mouse drags, however, I noticed the bot was still able to solve many puzzles without any issues, but it was almost impossible to successfully do so for the entire duration of a time trial.  With the right combination of puzzles though, this just might work...

### Python and system

To reiterate from the automation section above, this project was made in Python because 1) it is my language of choice, 2) it is simple to use, and 3) it has many libraries available.  However, none of the libraries or features I use would necessitate Python.  The big libraries I use, `cv2` and `pysat`, are implemented in C++.  Everything else has viable alternatives or can be worked around, so this bot could also be made a faster language like C++.  Looking at the time requirements for each step though, it does not seem like rewriting in C++ would make a big difference; almost 99% of the solve time goes to mouse movement and screenshots, both of which are limited by the OS.

I would be interested in seeing if Linux behaves differently with mouse movements, or if Windows and [AutoHotKey](https://www.autohotkey.com/) would offer more efficiency.

### Pathfinding

As discussed in the path finding part, I treat each grid cell as a square.  This is just a simplified verion; I actually treat it as a square roughly 2/3 the size which shares the same center.  This smaller square is necessary because at high speeds of mouse movement, dragging the mouse too close to the border of cells will cause the game to not register pipes correctly.

Finding the optimal mouse path in this context boils down to "solving a maze in continuous space in the minimum number of line segments".  "Continuous space" means we are not constrained to discrete coordinates.  Technically, the bot is constrained by pixels, but these are relatively high in number: grid cells can be as large as about 120x120 or 14,400 pixels.  Thus, continuous space is a good starting point, because the optimal path could be quite literally any combination of lines within the grid cells.

After doing some research, I was not able to find any good algorithms which might help solve the problem of "sovling a maze in a minimum number of line segments".  Some topics of interest include:

- [**Ramer-Douglas-Peucker (RDP)**](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm): This algorithm aims to approximate a curve composed of line segments with fewer line segments.  Without modifications, this doesn't work because the optimal mouse path can be very different and erratic in shape from the path through the centers of pipe cells.
- [**A-star**](https://en.wikipedia.org/wiki/A*_search_algorithm): A graph search algorithm which offers the benefit of heuristics.  My idea was to represent the search space with pixels as vertices, then bias the search in favor of outgoing edges which continue in the same direction as the incoming edge.  However, it is still very computationally expensive to search every pixel.

Instead, I made my own very simple pathfinding method-- which may be sub-optimal in many departments, but works well enough and is fast.  To understand how it works, consider the example path below.

<figure class="disp-flex center-all flex-column">
  <img src="pathfinder-ex0.jpg" alt="Pathfinding example" class="w-75">
</figure>

The mouse drag path to optimize resides within the light gray boundaries shaped like a segment-display "2".  The darker gray grid lines which run the lengths of the image represent grid cells.  The light gray boundaries are noticeably smaller than a full grid cell; recall that this size difference ensures mouse drags are fully registered by the game.

The source is highlighted in green, and the target is highlighted in red.  Each dot on the image, either red, green, or aqua, is a point considered by the path finder in [breadth-first search (BFS)](https://en.wikipedia.org/wiki/Breadth-first_search).  Valid neighbors in the search are checked via intersection with the outline polygon.  You may notice that there are relatively few points for such a vast space to search, but path finding is limited by time so fewer points is preferred.  Since optimal mouse paths will tend to "hug" the boundary more often than not, most points are close to the path border.  The center of each square is also considered in the event that paths don't hug the boundary.

The sources of BFS are green and located in the source cell, which will have a terminal.  There are five, at the corners of the grid cell and in the center.

The targets of BFS are red and located in the *penultimate* cell, just before the other terminal.  They don't extend into the terminal itself because dragging pipes into the penultimate cell is sufficient to connect the pipe fully.  However, the red points are also concentrated closer to the terminal, because dragging pipes into the penultimate cell too far from the terminal will not work.

The intermediate points are colored aqua.  One is located in the center of each cell between the source and target.  Only cells which are a corner in the path have any points other than the center.  Here, the corners are labeled 1,3,4,6.  The additional points are located at the corners of the boundary, with the idea that these points offer the most "vision", or accessibility to other points and are thus more valuable to include.

Executing BFS tries to find a path better than just using the center of each cell.  Here is the attempt for this example:

<figure class="disp-flex center-all flex-column">
  <img src="pathfinder-ex0_path.jpg" alt="Pathfinding example paths" class="w-75">
  <figcaption class="caption">The path finder identified the orange path as the optimal one.</figcaption>
</figure>

The pathfinder found the orange path as an optimal one.  In this case, it does not perform better or worse than the naive path, colored white.  Each path consists of 4 segments.  This is the worst-case scenario.  There is a better solution though, which was not found by the path finder.

<figure class="disp-flex center-all flex-column">
  <img src="pathfinder-ex0_path_2.jpg" alt="Pathfinding example paths" class="w-75">
  <figcaption class="caption">The yellow path consists of 3 segments but was not found by the path finder.</figcaption>
</figure>

However, the path finder is still useful.  Consider other example paths, where the path finder does identify an actual optimal path:

<figure class="disp-flex center-all flex-column">
  <img src="pathfinder-ex1_path.jpg" alt="Pathfinding example paths" class="w-75">
  <figcaption class="caption">The orange optimal path has 4 segments, while the white naive path has 5.</figcaption>
</figure>

<figure class="disp-flex center-all flex-column">
  <img src="pathfinder-ex2_path.jpg" alt="Pathfinding example paths" class="w-75">
  <figcaption class="caption">The orange optimal path has 2 segments, while the white naive path has 5.</figcaption>
</figure>

Obviously, the more points searched, the more likely the true optimal path is found.  However, this has sacrifices in the time department.  I have experimented with brute-forcing a solution and pausing the time trial while solving puzzles, but the pausing/unpausing resulting in more time loss than the optimal solution saved.  Until I can figure out a better path finding algorithm, this is the best the bot can do.

## Bot demonstration

### Time trials

A demonstration of speed in solving many puzzles in quick succession.

Q: Why is the bot only solving 34 puzzles when your best is 35?  A: The bot got lucky when it solved 35.  It had some easier puzzles which took less time to solve, and the small time saves added up.

#### 5x5 - 30 seconds
{% include embed/youtube.html id='GEJYJOYi5_c' %}

#### 9x9 - 30 seconds
{% include embed/youtube.html id='acRdvVHRM0E' %}

#### 5x5 - 4 minutes
{% include embed/youtube.html id='tZ9pJd76trc' %}

### Large puzzles

A demonstration of efficiency in solving gigantic puzzles.

{% include embed/youtube.html id='uXpEVKPRwmY' %}

## Appendix & Acknowledgements

The development of this Flow Free solver and bot would not be possible without the help of other people.  Many thanks to the contributors and maintainers of all the libraries I used, especially [OpenCV](https://opencv.org/), as well as Stack Overflow and Super User users from a decade ago for several obscure problems and questions I had.

In an initial iteration of the bot, I coded the automation end and used someone else's Flow Free solver as a proof of concept.  This [solver](https://github.com/mzucker/flow_solver), made by Matt Zucker, is a nice little program which also solves puzzles using SAT via a graph representaiton.  I used it to abstract the solving part away, just feeding it input and decoding its output to use for my bot.  After seeing the bot did work well (a record of 32 5-by-5 puzzles in a 30 second time trial before optimizations), I decided to make my own bot.  Though the idea is similar I coded from scratch and made some improvements.  Aside from using a less lightweight SAT solver than Matt Zucker's [`pycosat`](https://github.com/conda/pycosat), my version also uses less clauses and a different way of enforcing puzzle rules to solve puzzles quicker.

Also, thanks to [probabilis](https://www.youtube.com/@probabilis2992/videos) for the Flow Free computability [video](https://www.youtube.com/watch?v=_2A3j9hSqnY) which made creating the solver a lot easier.

There are a couple other Flow Free bots out there:
- A hard-coded Windows version which uses SAT reduction: [https://github.com/MusadiqPasha/FlowFree-Solver](https://github.com/MusadiqPasha/FlowFree-Solver)
- A bot with a video tutorial series which incorporates OpenCV: [https://github.com/lukegarbutt/Flow-Free-Solver](https://github.com/lukegarbutt/Flow-Free-Solver)

There are many solvers without automation as well, but I believe my bot is unique in many aspects.

If there are any mistakes or typos in this don't hesitate to email me so I can correct it.  Thanks for reading! :)