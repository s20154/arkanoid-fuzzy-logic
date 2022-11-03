"""
Gra:
    Arkanoid[https://pl.wikipedia.org/wiki/Arkanoid]

Zasady gry:
    Celem gry jest przesuwanie paletką po linii poziomej w taki sposób, aby odbijająca piłka
    uderzyła w kolorowe prostokąty. Gdy wszystkie prostokąty znikną z planszy, gracz wygrywa grę.
    Przegrać można jedynie, gdy piłka znajdzie się na wysokości uniemożliwiającej
    odbicie się od paletki.

Autorzy:
    Damian Kijańczuk s20154
    Szymon Ciemny    s21355

Przygotowanie środowiska:
    Oprócz języka Python, potrzebne takze będa biblioteki:
    - Pygame Zero[https://pygame-zero.readthedocs.io/en/stable/ide-mode.html]
    - Numpy[https://numpy.org]
    - Scikit-fuzzy[https://github.com/scikit-fuzzy/scikit-fuzzy]

    By zainstalowac te biblioteki wykonaj:
     pip3 install pgzero
     pip3 install numpy
     pip3 install scikit-fuzzy

Uruchomienie oraz instrukcja:
    By uruchomic wpisujemy w glownym katalogu
     python3 game3.py


"""


import pgzrun
import random
import sys
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Initialization of game parameters like window size, paddle info etc.
TITLE = "Arkanoid clone"
WIDTH = 600
HEIGHT = 500

paddle = Actor("paddleblue.png")
paddle.x = 300
paddle.y = 480

ball = Actor("ballblue.png")
ball.x = 300
ball.y = 400
ball_x_speed = -4
ball_y_speed = 5

# List to which bars will be created and stored
bars_list = []

def draw():
    """
    Function required by pgzrun.
    Sets what and in which order has to be drawn each frame.

    """
    screen.blit("background.png", (0,0))
    paddle.draw()
    ball.draw()

    # Draw destroyable bars
    for bar in bars_list:
        bar.draw()


def place_bars(x,y,image):
    """
    Function responsible for placing bars at the begging of the game.

    Parameters:
    x (int):
        specifies x dimension of a block
    
    y (int):
        specifies y dimension of a block

    image [string,string,...]
        list of .png files that represent blocks.
        More images more x levels of block there will be
    
    """
    
    bar_x = x
    bar_y = y
    for i in range(8):
        bar = Actor(image)
        bar.x = bar_x
        bar.y = bar_y
        bar_x += 70
        bars_list.append(bar)

def update():
    """
    Logic of a game that is calculate each frame.
    Responsible for calculating move of paddle and ball and taking care
    of colision between elements of play area.

    """
    global ball_x_speed, ball_y_speed

    # Calculate move of paddle using fuzzy logic
    val = fuzzyPaddleExpert.calculateMove(paddle.x - ball.x, ball.x, ball.y)
    # Move paddle in specified direction
    paddle.x = paddle.x + val

    # Dont let paddle go of the screen
    if paddle.x < 0:
        paddle.x = 0
    elif WIDTH < paddle.x:
        paddle.x = WIDTH

    update_ball()

    # Check if ball touched any of the bars
    for bar in bars_list:
        # If ball collided with bar
        if ball.colliderect(bar):
            # Remove bar
            bars_list.remove(bar)
            ball_y_speed *= -1

    # Check if paddle collided with ball and act on it  
    if paddle.colliderect(ball):
        ball_y_speed *= -1
        # Randomly move ball left or right on hit
        rand = random.randint(0,1)
        if rand:
            ball_x_speed *= -1

    # Check for ending conditions
    if bars_list == []:
        print("Wygranko!!! 🤪🤪🤪🤪🤪🤪🤪🤪🤪")
        sys.exit()
    if ball.y > 490:
        print("Przegranko :( Nie zlapales pilki 😔😔😔😔")
        sys.exit()

def update_ball():
    """
    Function for updating ball each frame
    Moves ball and takes care of collision with walls
    
    """
    global ball_x_speed, ball_y_speed
    ball.x -= ball_x_speed
    ball.y -= ball_y_speed
    if (ball.x >= WIDTH) or (ball.x <=0):
        ball_x_speed *= -1
    if (ball.y >= HEIGHT) or (ball.y <=0):
        ball_y_speed *= -1

class FuzzyPaddleExpert():
    """
    Class holds all the logic required for calculating next move of the paddle.
    
    """
    def __init__(self):
        """
        Initialization of Antecedents, Consequent and rules.
        
        """
        
        self.ball_X = ctrl.Antecedent(np.arange(-1, 601, 1), 'ball_X' )
        self.ball_X['leftSide' ] = fuzz.trapmf(self.ball_X.universe, [-1, -1, 100, 100]  )
        self.ball_X['middle'   ] = fuzz.trimf( self.ball_X.universe, [-1, 300, 601]      )
        self.ball_X['rightSide'] = fuzz.trapmf(self.ball_X.universe, [550, 550, 601, 601])
        self.ball_X.view()

        self.ball_Y = ctrl.Antecedent(np.arange(-1, 501, 1), 'ball_Y' )
        self.ball_Y['high'] = fuzz.trimf(self.ball_Y.universe, [-1, -1, 401] )
        self.ball_Y['low' ] = fuzz.trimf(self.ball_Y.universe, [-1, 501, 501])
        self.ball_Y.view()


        self.paddle_Xdiff = ctrl.Antecedent(np.arange(-600, 610, 10), 'paddle_Xdiff' )
        self.paddle_Xdiff['leftSide' ] = fuzz.trapmf(self.paddle_Xdiff.universe, [-600,-600, 0,0])
        self.paddle_Xdiff['rightSide'] = fuzz.trapmf(self.paddle_Xdiff.universe, [0,0,600, 600]  )
        self.paddle_Xdiff.view()


        self.paddleMove = ctrl.Consequent(np.arange(-10, 11, 1), 'paddleMove' )
        self.paddleMove['left' ] = fuzz.trapmf(self.paddleMove.universe, [-10,-10, 0, 0])
        self.paddleMove['right'] = fuzz.trapmf(self.paddleMove.universe, [0,0, 10, 10]  )

        rules = [
            ctrl.Rule(self.paddle_Xdiff['leftSide' ] & self.ball_X["middle"], self.paddleMove['right']),
            ctrl.Rule(self.paddle_Xdiff['rightSide'] & self.ball_X["middle"], self.paddleMove['left'] ),
            ctrl.Rule(self.ball_X[      "leftSide" ] & self.ball_Y["high"  ], self.paddleMove['right']),
            ctrl.Rule(self.ball_X[      "rightSide"] & self.ball_Y["high"  ], self.paddleMove['left'] ),
        ]

        self.paddleControl = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))


    def calculateMove(self, paddle_Xdiff, ball_X, ball_Y):
        """
        Function used to calculate move of the paddle.

        Parmeters:
        paddle_Xdiff (int):
            position on ball in relation to middle of the paddle on x axis.
            For example; if value is '-40', then ball is to the left of paddle
        ball_X (int):
            x cordinates of ball
        ball_Y (int):
            y cordinates of ball

        Returns:
        (int):
            move that paddle should take
        """
        self.paddleControl.input['paddle_Xdiff'] = paddle_Xdiff
        self.paddleControl.input['ball_X'] = ball_X
        self.paddleControl.input['ball_Y'] = ball_Y

        self.paddleControl.compute()
        return self.paddleControl.output['paddleMove']
        

# List of bars
coloured_box_list = ["element_blue_rectangle_glossy.png",
                     "element_green_rectangle_glossy.png",
                     "element_red_rectangle_glossy.png"]
# Initialization of fuzzy logic helper
fuzzyPaddleExpert = FuzzyPaddleExpert()

x = 50
y = 50
for coloured_box in coloured_box_list:
    place_bars(x, y, coloured_box)
    y += 50

# Start the game
pgzrun.go()
