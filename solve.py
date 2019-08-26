#!/usr/bin/python3

# Mastermind is a two player game.
# There are n colors. Let k < n be a positive number.
#
# 1. Player one chooses a hidden sequence of k colors (colors may repeat)
# 2. The game proceeds iteratively as follows until player two has guessed
#    the sequence correctly.
#   2.1 Player two makes a guess of sequence of k colors
#   2.2 Player one gives feedback to player two by giving
#     * the number of correct in both position and color, and
#     * the number of correct colors in the wrong positions.
#
# Play online
# http://www.webgamesonline.com/mastermind/index.php

# Objective of this exercise - Implement player two
#
#  Bonus point
#     - Support for imperfect player one. Imagine player one is a childs.
#       Sometimes (s)he may give wrong feedback.
#     - Optimizations for faster codebreaking
#

# Submission by: Rishi Sharma

from z3 import *
import argparse
import itertools
import time
from random import randint

def sum_to_one( ls ):
    # At least one
    atLeastOne = Or(ls)
    atMostOne = True
    for i,j in itertools.combinations(ls,2):
        atMostOne = And(Or(Not(i), Not(j)), atMostOne)
    exactlyOne = And(atLeastOne, atMostOne)
    return exactlyOne

n=8
k=4

vs = [  [Bool ("e_{}_{}".format(i,j))  for j in range(n)] for i in range(k)]

base_cons = []

# add basic constraints
for i in vs:
    base_cons.append(sum_to_one(i))

s = Solver()
# To remember how much we can backtrack
stack_size = 0

s.add( And(base_cons) )

def add_a_guess_solution( guess, reds, whites ):
    global stack_size
    guess_cons = True

    # Considering only Red
    redCombs = False
    for rc in itertools.combinations(range(k), reds):
        notRC = []
        for i in range(k):
            if i not in rc:
                notRC.append(i)

        C1 = True
        for x in rc:
            C1 = And(C1, vs[x][guess[x]])

        C2 = False

        for x in notRC:
            C2 = Or(C2, vs[x][guess[x]])

        redCombs = Or(redCombs, And(C1, Not(C2)))

    # Considering only White
    whiteConstraint = False
    for wc in itertools.combinations(range(k), whites):
        temp1 = True
        for x in wc:
            temp = False
            for i in range(k):
                if i!=x:
                    temp = Or(temp, vs[i][guess[x]])
            temp = And(Not(vs[x][guess[x]]), temp)
            temp1 = And(temp1, temp)
        whiteConstraint = Or(whiteConstraint, temp1)

    # If no Red no white
    others = k - reds - whites

    noColor = False
    if reds==0 and whites==0:
        for i in range(k):
            for j in range(k):
                noColor = Or(noColor, vs[j][guess[i]])
    noColor = Not(noColor)

    # Add the above Conditions
    guess_cons = And(whiteConstraint, And(redCombs, noColor))
    s.push() # Add backtracking point
    s.add( guess_cons )
    stack_size += 1


color_name =  { 0:'R', 1:'G', 2:'B', 3:'Y', 4:'Br', 5:'O', 6:'Bl', 7:'W', }
if n > 8:
    for i in range(8,n):
        color_name[i] = 'C'+str(i)

def print_move( move ):
    for i in range(k):
        c = color_name[move[i]]
        print(c, end=' '),
    print("\n")


def get_a_solution():
    global stack_size
    sol = [0]*k
    if s.check() == sat:
        m = s.model()
        for i in range(k):
            for j in range(n):
                val = m[vs[i][j]]
                if is_true( val ):
                    sol[i] = j
        return sol
    else:
        if stack_size == 0: # Something REALLY BAD Happened
            print("some thing bad happened! no more moves!\n")
            raise Exception('Failed!')
        else:
            # If made unsatisfiable, backtrack random number of steps
            to_pop = randint(1,stack_size)
            stack_size -= to_pop
            for i in range(to_pop):
                s.pop()
            r = s.check()
            m = s.model() # Return last model
            for i in range(k):
                for j in range(n):
                    val = m[vs[i][j]]
                    if is_true( val ):
                        sol[i] = j
            return sol

def get_response():
    red = int(input("Enter red count: "))
    white = int(input("Enter white count: "))
    if white+red > k:
        raise Exception("bad input!")
    return red,white


def play_game():
    guess_list = []
    response_list = []
    red = 0
    while red < k:
        if len(guess_list) == 0:
            # start with random guess
            move = [randint(0,k-1) for i in range(k)]  # The bug was here. replaced 4 => k
        else:
            move = get_a_solution()
        guess_list.append(move)
        print("found a move:")
        print_move( move )
        red, white = get_response()
        add_a_guess_solution( move, red, white )
    print("Game solved!")


play_game()
