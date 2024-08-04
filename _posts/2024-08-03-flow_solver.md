---
title: Flow Free Solver
date: 2024-08-03 -0400
categories: [Project Write-ups]
tags: [projects]
media_subpath: /assets/img/2024-08-03-flow_solver
---

## **Too long, didn't read**
For readers who are just interested in seeing the bot in action, here is a time trial demo:
{% include embed/youtube.html id='-yLt4shM00s' %}

---
## **Introduction**

![Flow Free app icon](https://images.squarespace-cdn.com/content/v1/586beec5e58c624be9f7b5a2/1483742317507-AJVS9HFEUN3Y3BNRDOGJ/image-asset.png?format=1000w){: .w-25 .left }

[Flow Free](https://www.bigduckgames.com/flowfree) is a simple puzzle game.
The player is presented a grid, which contains pairs of colored dots in some of the cells.  The game has been around for a long time, and the concept was originally called [Numberlink](https://en.wikipedia.org/wiki/Numberlink).  The objective is to connect each pair of dots with lines with a few rules, which we will elaborate on later.  There are several game modes, including variations on the puzzle concept and a time trial.

One day this summer, a friend of mine who also plays this game beat my time trial record in the 5x5 board with 30 seconds category, solving 14 puzzles in one run.  I remember it took me a while to score 13, because besides skill, you need a bit of luck with better puzzles: easier ones, or ones with less convoluted solution and thus faster finger swiping.  So, I thought I would just automate the whole thing instead of doing 14 legitimately.
<figure class="disp-flex center-all flex-column">
  <img src="rage.jpg" alt="Time trial record" class="w-75">
  <figcaption class="itx">"Ok"</figcaption>
</figure>

Author's note: I attempted to write this assuming little knowledge in computer science or theory of computation.  Thus, I gloss over some arguably important details but I do include the minimum necessary to (hopefully) understand the point.

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
<div class="disp-flex center-all">
  <img src="puzzle1-0.jpg" alt="puzzle 0" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-1.jpg" alt="puzzle 1" class="w-25">
</div>

Next, you might notice that the bottom orange terminal has a series of forced moves, where only one cardinal direction is not already occupied by a terminal (note that crossing a terminal violates one of the rules).
<div class="disp-flex center-all">
  <img src="puzzle1-1.jpg" alt="puzzle 1" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-2.jpg" alt="puzzle 2" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-3.jpg" alt="puzzle 3" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-4.jpg" alt="puzzle 4" class="w-25">
</div>

Coincidentally, these forced moves reach the other orange terminal.
<div class="disp-flex center-all">
  <img src="puzzle1-4.jpg" alt="puzzle 4" class="w-25">
  <span class="lr10">&#8594;</span>
  <img src="puzzle1-5.jpg" alt="puzzle 5" class="w-25">
</div>

Chances are, this was not your train of thought, but I hope this example helped illustrate some of the thought process behind solving flow puzzles at a smaller scale.

### **Computers**

The tricky part is programming a computer to do the solving.  Image parsing and automation aside, it is not trivial to lay out a strict set of rules which will solve any flow puzzle thrown at the machine (besides brute force, of course).  It may seem easy, but some puzzles are very complex and have solutions like this one, where the orange pipe goes around the entire board:
<figure class="disp-flex center-all flex-column">
  <div class="disp-flex center-all">
    <img src="puzzle2-0.jpg" alt="puzzle 0" class="w-25">
    <span class="lr10">&#8594;</span>
    <img src="puzzle2-1.jpg" alt="puzzle 1" class="w-25">
  </div>
  <figcaption class="itx">You're lying if this was intuitive for you.</figcaption>
</figure>
Heuristics can only get so far.  There are only two forced moves (red and pink terminals in the bottom right corner) and there are no outright obvious pipe connections.

Backtracking is unavoidable, of course.  As seen in the example above, you can't just "know" the solution without trying something first.  But a pure bashing solution like basic depth-first search (DFS), where you explore every option one by one, would take very long.  There are 38 possible starting moves in the example puzzle (enumerated below).  Accounting for forced moves actually increases that number (because it allows new, un-forced moves).  Of course, testing more new moves would increase that number further.
<figure class="disp-flex center-all flex-column">
  <img src="puzzle2-0-first_moves.jpg" alt="Starting moves" class="w-50">
  <figcaption class="itx">Move variety like chess.</figcaption>
</figure>

#### **A dead-end strategy**

Note that this not impossible to implement, I just thought it would not be worth the resources.  In fact, other people have implemented this!  Check the appendix for more.

I initially considered a different approach to this problem.

[**A-star (A\*) search**](https://en.wikipedia.org/wiki/A*_search_algorithm).  In short, A\* is a form of DFS which guides the search using heuristics to take more likely paths before unlikely ones.  If DFS takes too long, then an optimized version should do better.  However, I could not come up with a good heuristic to use.

Note that we wouldn't be using A\* to find pipe connections directly, rather, each "node" would be an entire state of the grid with its unique collection of pipe connections.  The source would then be an empty puzzle and the target would be a solved state.  It's also difficult to quantify certain characteristics, such as how "close" a game state is to the solution, which is necessary for A\* to function.  Pipe percent (the percentage of the grid covered by pipe) is one metric, but it is almost useless because of things like this:
<figure class="disp-flex center-all flex-column">
  <img src="large_pipe_pct.jpg" alt="Pipe percentage is useless" class="w-50">
  <figcaption class="itx">We're 91% of the way to solving the puzzle!  Wait...</figcaption>
</figure>

Additionally, to quantify closeness to a solution, it is necessary to consider terminals which are cut off from their counterpart (like every non-aqua terminal in the image above).  However, this requires checking the entire grid at each state which I thought would be inefficient.

#### **An open-end strategy?**

One day, this video was recommended to me:
{% include embed/youtube.html id='_2A3j9hSqnY' %}
Coincidentally, the creator of the video was a classmate of mine!  I only realized this very recently.  Anyway--

In short, it details the reduction of the flow problem into [boolean satisfiability](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem) or SAT (a summary of this comes in the next section).  This is genius for several reasons.  As it turns out, flow is part of a class of problems known as NP-complete.  In laymans terms, this basically means that humanity (currently) cannot solve this problem quickly, but if given a solution, you can quickly check if it is correct.  I say "quickly" here only for impossibly or "asymptotically" large puzzles; in practice you will see that the solver is actually very fast for practical purposes.

We need not get bogged down in the theory of this, but the key here is that solving a flow problem is as simple as rephrasing it as a different, widely-researched problem of which there are probably thousands of relatively efficient solvers already made.  Now the hard part is just the process of conversion.

---
## SAT reduction

The SAT problem 