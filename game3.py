import pgzrun
import random


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

bars_list = []

def draw():
    screen.blit("background.png", (0,0))
    paddle.draw()
    ball.draw()
    for bar in bars_list:
        bar.draw()


def place_bars(x,y,image):
    bar_x = x
    bar_y = y
    for i in range(8):
        bar = Actor(image)
        bar.x = bar_x
        bar.y = bar_y
        bar_x += 70
        bars_list.append(bar)

def update():
    global ball_x_speed, ball_y_speed

    val = fuzzyPaddleExpert.calculateMove(paddle.x - ball.x)

    paddle.x = paddle.x + val

    if paddle.x < 0:
        paddle.x = 0
    elif 700 < paddle.x:
        paddle.x = 700

    update_ball()
    for bar in bars_list:
        if ball.colliderect(bar):
            bars_list.remove(bar)
            ball_y_speed *= -1


    if paddle.colliderect(ball):
        ball_y_speed *= -1
        # randomly move ball left or right on hit
        rand = random.randint(0,1)
        if rand:
            ball_x_speed *= -1

def update_ball():
    global ball_x_speed, ball_y_speed
    ball.x -= ball_x_speed
    ball.y -= ball_y_speed
    if (ball.x >= WIDTH) or (ball.x <=0):
        ball_x_speed *= -1
    if (ball.y >= HEIGHT) or (ball.y <=0):
        ball_y_speed *= -1

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyPaddleExpert():
    def __init__(self):
        self.paddle_Xdiff = ctrl.Antecedent(np.arange(-600, 610, 10), 'paddle_Xdiff' )
        self.paddle_Xdiff[ 'leftSide'   ] = fuzz.trapmf(self.paddle_Xdiff.universe, [-600,-600, 0,0])
        self.paddle_Xdiff[ 'rightSide'  ] = fuzz.trapmf(self.paddle_Xdiff.universe, [0,0,600, 600])
        self.paddle_Xdiff.view()


        self.paddleMove = ctrl.Consequent(np.arange(-10, 11, 1), 'paddleMove' )
        self.paddleMove[ 'left'  ] = fuzz.trapmf(self.paddleMove.universe, [-10,-10, 0, 0]  )
        self.paddleMove[ 'right' ] = fuzz.trapmf(self.paddleMove.universe, [0,0, 10, 10]  )

        rules = [
            ctrl.Rule(self.paddle_Xdiff['leftSide'],     self.paddleMove['right']),
            ctrl.Rule(self.paddle_Xdiff['rightSide'],     self.paddleMove['left']),
        ]

        self.paddleControl = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))


    def calculateMove(self, paddle_Xdiff):
        self.paddleControl.input['paddle_Xdiff'] = paddle_Xdiff

        self.paddleControl.compute()
        return self.paddleControl.output['paddleMove']
        

coloured_box_list = ["element_blue_rectangle_glossy.png", "element_green_rectangle_glossy.png","element_red_rectangle_glossy.png"]
fuzzyPaddleExpert = FuzzyPaddleExpert()
x = 50
y = 50
for coloured_box in coloured_box_list:
    place_bars(x, y, coloured_box)
    y += 50


pgzrun.go()