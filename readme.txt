Input Tutorial

TO START THE GAME:
    type "python main.py" into the terminal while accessing the folder where the project is located.

How to move a piece classically:
The idea behind this is that you need to swap the position of the vector 
entries for the probability and phase of your old position and new position.
  for example: to move your p4 pawn on d2 to d3 you would:
      1) specify the piece: "p4: "
      2) specify the starting location: "p4: d2: "
      3) specify the ending   location: "p4: d2: d3"
      4) then you specify the probability (in this case 1 for (100%)): "p4: d2: d3(1"
      5) then you have to specify the phase (in this case 0 for 0 phase): "p4: d2: d3(1~0)"
      6) That's it isn't it? No, sit down. We have to make sure our move is unitary
          currently, this input has doubled the probability of your piece by creating a copy on your new position.
          To counteract this, we must swap the probability of the empty position back into our old position.
      7) To move the 0 probability back into our starting position we perform a swap that looks similar to 
          steps 1-5: "p4: d3: d2(1~0)"
      8) Now we combine both movements into one input by listing their motions as follows:
          input = p4: d2: d3(1~0), d3: d2(1~0)
      9) Simple, right? just kidding of course it isn't it's Qhess.

How to move a piece into a split superposition:
  This part is a tad bit harder. But I believe in you. The main idea behind this is replicating a
  unitary matrix that splits the piece you want to move while swapping the necessary probabilities to add to 0
  here's an example:
      1) First we specify our piece like in the previous example: "n2: "
      2) Then we need to create a combination of moves that results in the negative and positive components
         canceling to add to 0.
          a) We can write this as a list of four moves each as sum of two moves for 8 swaps in total
          b) We write the first split as a combination of where we are moving the pieces:
              "n2: g1: f3(0.5~0) + h3(0.5~0)"
          c) The next step can be made either way but you need to pick one:
             You need to distribute your positive and negative phase swaps so that they cancel each other out.
             You can choose either one to be negative or positive but for this example we'll say that h3 is negative
             We split the state at f3 into g1 and g5 as follows:
              "f3: g1(0.5~0) + g5(0.5~0)"
             Then we split the state at h3 into g1 and g5 with a negative phase on g5:
              "h3: g1(0.5~0) + g5(0.5~1)"
          d) We also need to redistribute the auxillary position back into our two new positions with the following move:
              "g5: f3(0.5~0) + h3(0.5~1)"
             note that we apply a negative phase to the h3 component to remain consistent and unitary
          e) Finally we combine these four combinations into a comma seperated list as follows:
              "n2: g1: f3(0.5~0) + h3(0.5~0), f3: g1(0.5~0) + g5(0.5~0), h3: g1(0.5~0) + g5(0.5~1), g5: f3(0.5~0) + h3(0.5~1)"
      
How to move a piece conditionally:
  This part is a bit harder as well. I'll keep it simple as this is simply about specifying the move given an outcome.
  To make these moves you give conditions and two turns for an if then else block.
  For example:
      q: if wn2 at h3 { d7: h3(1~0), h3: d7(1~0) } else { d7: b5(1~0), b5: d7(1~0) }
      1) You specify for a piece on if condition. In this example the piece is white knight 2 (wn2) at h3. This attempts to measure the knight 
         if it's position is h3, then it goes into the turn (not move) of the first block which is the true block. Here you can specify another 
         move or another if then else or split. The options are endless sortof
      2) if the condition is not true it executes the second block (else)