from math import pi
import sys
import time
import json
import pygame
import os
import cv2
import numpy as np
from pygame import surface
from pygame.draw import circle
from pygame.locals import *

ConfigPath = os.getcwd() + "\Config.json"
PicPath = os.getcwd() + "\InPic.png"
BlueColor = pygame.Color(0,0,255)  
RedColor = pygame.Color(255,0,0)
GreenColor = pygame.Color(0,255,0)
YellowColor = pygame.Color(255,255,0)
BlackColor = pygame.Color(0,0,0)
PlayerColor = pygame.Color(114,51,4)
MonsterColor = pygame.Color(255,255,255)
LineColor = pygame.Color(128,0,128)
BaseColor = [BlueColor,RedColor,GreenColor,YellowColor]
UsedColorQueue = []
WalkedPath = []
CurrentIndex = 0
Quad = 50
Width = 9 * Quad
Height = 12 * Quad

def ReadInPic():
    img = cv2.imread(PicPath)
    try:
        img.shape
    except:
        return
    height,width = img.shape[:2]
    initpoint = (int(width*0.43),int(height*0.1))
    k = [30, 30.75, 31.5, 32.25, 33, 33.75, 34.5, 35.25, 36]
    k2 = np.math.tan(pi* 5 / 6)
    deltax = width * 0.05
    SquareColor = []
    for i in range(0,9):
        linestartpoint = (int(initpoint[0] - deltax * i), int(initpoint[1] - deltax * i *k2))
        k1 = np.math.tan(k[i] / 180 * pi)
        b = linestartpoint[1] - linestartpoint[0] * k1
        LineColor = []
        for j in range(0,9):
            pointx = int(linestartpoint[0] + j * deltax)
            pointy = int(linestartpoint[1] + j * deltax * k1)
            point = (pointx,pointy)
            color = img[pointy,pointx]

            isBlue = (color[0] > (color[1] * 1.3)) & (color[0] > (color[2] * 1.3))
            isGreen = (color[1] > (color[0] * 1.3)) & (color[1] > (color[2] * 1.3))
            isRed = (color[2] > (color[0] * 1.3)) & (color[2] > (color[1] * 1.3))
            isYellow = (color[2] > (color[0] * 1.3)) & (color[1] > (color[0] * 1.3))
            PointColor = (0,0,0)
            if isBlue:
                PointColor = (255,0,0)
                LineColor.append(0)
            elif isRed:
                PointColor = (0,0,255)
                LineColor.append(1)
            elif isGreen:
                PointColor = (0,255,0)
                LineColor.append(2)
            elif isYellow:
                PointColor = (0,255,255)
                LineColor.append(3)
            else:
                LineColor.append(-1)
            cv2.circle(img,point,2,PointColor,4)
        SquareColor.append(LineColor)
    Config = None
    with open(ConfigPath, 'r') as f:
        Config = json.load(f)
    Config["InitQuads"] = SquareColor

    NewConfigPathTmp = os.getcwd() + "\\NewConfigTmp.txt"
    NewConfigPath = os.getcwd() + "\Config.json"

    f = open(NewConfigPathTmp,'w+')
    json.dump(Config, f, indent = 0, separators = (",",":"))
    f.close()
    with open(NewConfigPathTmp,"r") as fin:
        with open(NewConfigPath, "w+") as fout:
            for line in fin:
                if not ("]," in line):
                    fout.write(line.replace("\n",""))
                else:
                    fout.write(line)
    os.remove(NewConfigPathTmp)
    img.resize()
    cv2.imshow("output", img)

def GoOneStep(screen, ColorList, Position, SquareColor):
    global CurrentIndex
    global UsedColorQueue
    global WalkedPath
    QuadColor = BaseColor[ColorList[CurrentIndex]]
    PathLength = len(WalkedPath)
    x = int(Position[0] / Quad)
    y = int(Position[1] / Quad)
    WalkedPath.append([x,y])
    pos = WalkedPath[PathLength-1]
    x = pos[0]
    y = pos[1]
    UsedColorQueue.append(SquareColor[y][x])
    SquareColor[y][x] = ColorList[CurrentIndex]
    CurrentIndex = CurrentIndex + 1
    print("Used Queue:")
    print(UsedColorQueue)
    print("WalkedPath:")
    print(WalkedPath)
    print("go one step")

def BackOneStep(screen, ColorList, SquareColor):
    global CurrentIndex
    global UsedColorQueue
    global WalkedPath
    QuadColor = UsedColorQueue.pop()
    WalkedPath.pop()
    LastPos = WalkedPath[len(WalkedPath) - 1]
    x = LastPos[0]
    y = LastPos[1]
    SquareColor[y][x] = QuadColor
    CurrentIndex = CurrentIndex - 1
    print("Used Queue:")
    print(UsedColorQueue)
    print("WalkedPath:")
    print(WalkedPath)
    print("back one step")

def OutputNewConfig(Config, ColorList, SquareColor):
    LastPos = WalkedPath[len(WalkedPath) - 1]
    x = LastPos[0]
    y = LastPos[1]
    SquareColor[y][x] = -1
    NewColorList = []
    for i in range(CurrentIndex,len(ColorList)):
        NewColorList.append(ColorList[i])
    NewConfigPathTmp = os.getcwd() + "\\NewConfigTmp.txt"
    NewConfigPath = os.getcwd() + "\\NewConfig.json"
    NewConfig = dict()
    NewConfig["InitQuads"] = SquareColor
    NewConfig["PlayerPosition"] = [x,y]
    NewConfig["MonsterPosition"] = Config["MonsterPosition"]
    NewConfig["QuadsColorList"] = NewColorList
    f = open(NewConfigPathTmp,'w+')
    json.dump(NewConfig, f, indent = 0, separators = (",",":"))
    f.close()
    with open(NewConfigPathTmp,"r") as fin:
        with open(NewConfigPath, "w+") as fout:
            for line in fin:
                if not ("]," in line):
                    fout.write(line.replace("\n",""))
                else:
                    fout.write(line)
    os.remove(NewConfigPathTmp)
        
def ChangeQuadColor(Position, SquareColor, NewColor):
    x = int(Position[0] / Quad)
    y = int(Position[1] / Quad)
    SquareColor[y][x] = NewColor

def main():
    print(cv2.__file__)
    ReadInPic()

    pygame.init()

    screen = pygame.display.set_mode((Width,Height))
    pygame.display.set_caption('Alchemy star sim')

    Config = None
    with open(ConfigPath, 'r') as f:
        Config = json.load(f)
    #print(Config)

    
    SquareColor = Config["InitQuads"]

    QuadsColorList = Config["QuadsColorList"]
    PlayerPosition = Config["PlayerPosition"]
    WalkedPath.append(PlayerPosition)
    OutputFont = pygame.font.SysFont("",32)
    OutputText = OutputFont.render("Output New Config", True, PlayerColor,BlackColor)
    OutputRect = OutputText.get_rect()
    OutputRect.center = (4*Quad, 10*Quad)
    bInEditMode = False
    LastPos = []
    while True:
        screen.fill((0))
        
        for i in range(0,9):
            for j in range(0,9):
                if (SquareColor[i][j] != -1):
                    QuadColor = BaseColor[SquareColor[i][j]]
                    pygame.draw.rect(screen, QuadColor, pygame.Rect(j*Quad, i*Quad, j*Quad+Quad, i*Quad+Quad))
                else:
                    pygame.draw.rect(screen, BlackColor, pygame.Rect(j*Quad, i*Quad, j*Quad+Quad, i*Quad+Quad))
                pygame.draw.rect(screen, BlackColor, pygame.Rect(j*Quad, i*Quad, j*Quad+Quad, i*Quad+Quad), 1)
        pygame.draw.rect(screen, BlackColor,Rect(0,Width,Width,Height))

        Center = [PlayerPosition[0] * Quad + 0.5*Quad, PlayerPosition[1] * Quad + 0.5*Quad]
        pygame.draw.circle(screen, PlayerColor, Center, 0.3*Quad)

        MonsterPosition = Config["MonsterPosition"]

        for Pos in MonsterPosition:
            Center = [Pos[0] * Quad + 0.5*Quad, Pos[1] * Quad + 0.5*Quad]
            pygame.draw.circle(screen,MonsterColor, Center, 0.3*Quad)
        
        screen.blit(OutputText,OutputRect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                LastPos = event.pos
                if event.button == 1:
                    print(event.pos)
                    if ((CurrentIndex < len(QuadsColorList)) & (event.pos[0] < Width) & (event.pos[1] < Width) & (not bInEditMode)):
                        GoOneStep(screen,QuadsColorList,event.pos,SquareColor)
                    elif ((event.pos[1] > 9*Quad) & (event.pos[1] < 11*Quad)):
                        OutputNewConfig(Config, QuadsColorList, SquareColor)
                elif event.button == 3:
                    if ((CurrentIndex > 0) & (not bInEditMode)):
                        BackOneStep(screen,QuadsColorList,SquareColor)
            elif event.type == pygame.KEYDOWN:
                if event.key == K_e:
                    bInEditMode = not bInEditMode
                if (bInEditMode == True):
                    if event.key == K_0:
                        ChangeQuadColor(LastPos,SquareColor,0)
                    if event.key == K_1:
                        ChangeQuadColor(LastPos,SquareColor,1)
                    if event.key == K_2:
                        ChangeQuadColor(LastPos,SquareColor,2)
                    if event.key == K_3:
                        ChangeQuadColor(LastPos,SquareColor,3)
                    if event.key == K_4:
                        ChangeQuadColor(LastPos,SquareColor,-1)


        for i in range(0,9):
            if (i + CurrentIndex >= len(QuadsColorList)):
                pygame.draw.rect(screen, BlackColor, pygame.Rect(i*Quad, Width + 2*Quad, i*Quad+Quad, Height))
            else:
                QuadColor = BaseColor[QuadsColorList[CurrentIndex + i]]
                pygame.draw.rect(screen, QuadColor, pygame.Rect(i*Quad, Width + 2*Quad, i*Quad+Quad, Height))

        if (len(WalkedPath) >= 2):
            for i in range(0,len(WalkedPath)-1):
                start = [WalkedPath[i][0] * Quad + 0.5 * Quad, WalkedPath[i][1] * Quad + 0.5 * Quad]
                end = [WalkedPath[i+1][0] * Quad + 0.5 * Quad, WalkedPath[i+1][1] * Quad + 0.5 * Quad]
                pygame.draw.line(screen, LineColor, start, end, 1)
            x = WalkedPath[len(WalkedPath) - 1][0]
            y = WalkedPath[len(WalkedPath) - 1][1]
            pygame.draw.rect(screen,BlackColor,pygame.Rect(x*Quad, y*Quad, Quad, Quad))
            Length = len(WalkedPath) - 1
            LengthFont = pygame.font.SysFont("",32)
            LengthText = LengthFont.render(str(Length),True,RedColor,BlackColor)
            screen.blit(LengthText,(x*Quad,y*Quad))
        

        pygame.display.update()


if __name__ == '__main__':
    main()