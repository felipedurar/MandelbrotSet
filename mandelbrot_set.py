# The Mandelbrot Set
# Copyright (C) Felipe Durar 2021

import pygame
import numpy as np
import math
import threading
import time
from PIL import Image

complexSpaceTransformation = np.array(
    [[200.0, 0.0, 500.0],
     [0.0, 200.0, 300.0],
     [0.0, 0.0, 1.0]])

displayComplexPlane = True
maxIterations = 1000

renderingThreadLock = threading.Lock()
txtThreadLock = threading.Lock()

# define a main function
def main():
    global screen
    global renderingSurface
    global offscreenSurface
    global defaultFont
    global rendering
    global status
    global WINDOW_W
    global WINDOW_H
    global moveSpeed
    global zoomSpeed

    rendering = False
    status = 'Ready'
    WINDOW_W = 800
    WINDOW_H = 600
    moveSpeed = 5.0
    zoomSpeed = 5.0
     
    # initialize the pygame module
    pygame.init()
    
    # Set Caption
    pygame.display.set_caption("Mandelbrot Set - By Felipe Durar")
     
    # Create Surfaces
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
    renderingSurface = pygame.Surface((WINDOW_W, WINDOW_H))
    offscreenSurface = pygame.Surface((WINDOW_W, WINDOW_H))
    
    defaultFont = pygame.font.SysFont('Consolas', 16)

    renderingSurface.fill((100, 0, 0))
    offscreenSurface.fill((0, 0, 0))
     
    # define a variable to control the main loop
    running = True
    
    # Calculate Transformations
    calculateTransformationMatrix()

    # Load Color Pallete
    loadPallete('./palletes/pallete3.bmp')
     
    # main loop
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    request_render()
                if event.key == pygame.K_w:
                    zoomDir(1)
                if event.key == pygame.K_s:
                    zoomDir(-1)
                if event.key == pygame.K_o:
                    iterDir(1)
                if event.key == pygame.K_l:
                    iterDir(-1)
                if event.key == pygame.K_LEFT:
                    moveDir(-1, 0)
                if event.key == pygame.K_RIGHT:
                    moveDir(1, 0)
                if event.key == pygame.K_UP:
                    moveDir(0, -1)
                if event.key == pygame.K_DOWN:
                    moveDir(0, 1)
            if event.type == pygame.VIDEORESIZE:
                resizeWin(event.w, event.h)
        
        draw()
        
def draw():
    global screenBoundaries
    global unitSize
    global ok
    global moveSpeed
    global zoomSpeed

    screen.fill((0, 0, 0))

    #screen.set_at((10, 10), (255, 255, 255))
    screenBoundaries = getScreenBoundariesInComplexSpace()
    unitSize = getUnitInComplexSpace()

    renderingThreadLock.acquire()
    screen.blit(renderingSurface, (0, 0))
    renderingThreadLock.release()

    txtThreadLock.acquire()
    infoTxt = defaultFont.render('Press r to start rendering', False, (255, 255, 255))
    speedZoom = defaultFont.render('Move Speed: ' + "{:.2f}".format(moveSpeed) + 
        ' - Zoom Speed: ' + "{:.2f}".format(zoomSpeed) + 
        ' - Zoom: ' + "{:.2f}".format(complexSpaceTransformation[0][0] / 100.0) + 'x' + 
        ' - Max Iterations: ' + "{:.2f}".format(maxIterations), False, (255, 255, 255))
        
    statusTxt = defaultFont.render(status, False, (255, 255, 255))
    txtThreadLock.release()

    screen.blit(infoTxt, (10, 10))
    screen.blit(speedZoom, (10, 25))
    screen.blit(statusTxt, (10, 40))
    
    if (displayComplexPlane):
        drawComplexPlane()
    
    pygame.display.flip()
    return

def resizeWin(w, h):
    global WINDOW_W
    global WINDOW_H
    global screen
    global renderingSurface
    global offscreenSurface
    WINDOW_W = w
    WINDOW_H = h

    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H),
                                pygame.RESIZABLE)
    renderingSurface = pygame.Surface((WINDOW_W, WINDOW_H))
    offscreenSurface = pygame.Surface((WINDOW_W, WINDOW_H))
    renderingSurface.fill((100, 0, 0))
    offscreenSurface.fill((0, 0, 0))

    return

def request_render():
    renderingThreadLock.acquire()
    if (rendering):
        return
    renderingThreadLock.release()

    renderThred = threading.Thread(target = render, args=())
    renderThred.start()

def setStatus(statusText):
    global status

    txtThreadLock.acquire()
    status = statusText
    txtThreadLock.release()
    return

def render():
    renderingThreadLock.acquire()
    rendering = True
    renderingThreadLock.release()

    iterationMap = [[0 for x in range(WINDOW_H)] for y in range(WINDOW_W)]
    numIterationsPerPixel = [0 for v in range(maxIterations + 1)]
    for i in range(0, maxIterations): numIterationsPerPixel[i] = 0

    # Create the iteration map
    for x in range(0, WINDOW_W):
        progress = (x / (WINDOW_W * 1.0)) * 100.0
        setStatus("Generating Iteration Map: " + "{:.2f}".format(progress) + "%")
        for y in range(0, WINDOW_H):
            complexCoord = projectToComplex(x, y)
            iterationMap[x][y] = iterateComplex(complexCoord[0], complexCoord[1])
            iterations = iterationMap[x][y]
            numIterationsPerPixel[iterations] += 1

    # Calculate total amount of iterations
    setStatus("Calculating Total Interations")
    total = 0
    for i in range(0, maxIterations):
        total += numIterationsPerPixel[i]
    #if (total == 0): total = 1; # avoid division by zero
    
    # Create hue based on total amount iterations
    hue = [[0 for x in range(WINDOW_H)] for y in range(WINDOW_W)]
    for x in range(0, WINDOW_W):
        progress = (x / (WINDOW_W * 1.0)) * 100.0
        setStatus("Calculating Hue Based on Histogram: " + "{:.2f}".format(progress) + "%")

        for y in range(0, WINDOW_H):
            iteration = iterationMap[x][y]
            if (iteration == maxIterations):
                hue[x][y] = None
            else:
                for i in range(0, iteration):
                    hue[x][y] += numIterationsPerPixel[i] / total
    
    # Transform to complex plane space and get the collor from the pallete
    for x in range(0, WINDOW_W):
        progress = (x / (WINDOW_W * 1.0)) * 100.0
        setStatus("Rasterizing: " + "{:.2f}".format(progress) + "%")
        for y in range(0, WINDOW_H):
            hueVal = hue[x][y]
            outColor = (0, 0, 0)
            if (hueVal is not None):
                if (hueVal > 1.0): hueVal = 1.0
                if (hueVal < 0.0): hueVal = 0.0
                pColor = getPalleteColor(hueVal)
                outColor = (pColor[0], pColor[1], pColor[2])

            offscreenSurface.set_at((x, y), outColor)
    
    renderingThreadLock.acquire()
    renderingSurface.blit(offscreenSurface, (0, 0))
    rendering = False
    renderingThreadLock.release()

    setStatus("Ready")
    return

def moveDir(x, y):
    global complexSpaceTransformation
    global moveSpeed

    scaledValue = projectFromComplex(x / 100.0, y / 100.0, 0)
    transformation = np.array(
        [[0.0, 0.0, scaledValue[0] * moveSpeed],
        [0.0, 0.0, scaledValue[1] * moveSpeed],
        [0.0, 0.0, 0.0]])

    complexSpaceTransformation = np.add(complexSpaceTransformation, transformation)

    calculateTransformationMatrix()
    return

def zoomDir(scalar):
    global complexSpaceTransformation
    global zoomSpeed

    scaledValue = projectFromComplex(scalar / 100.0, scalar / 100.0, 0)
    transformation = np.array(
        [[scaledValue[0] * zoomSpeed, 0.0, 0.0],
        [0.0, scaledValue[1] * zoomSpeed, 0.0],
        [0.0, 0.0, 0.0]])

    complexSpaceTransformation = np.add(complexSpaceTransformation, transformation)

    calculateTransformationMatrix()
    return

def iterDir(scalar):
    global maxIterations
    if (scalar == 1):
        if (maxIterations > 10.0):
            maxIterations = int(maxIterations / 10)
    if (scalar == -1):
        if (maxIterations < 10000000000.0):
            maxIterations = int(maxIterations * 10)
    return

def loadPallete(palleteFilePath):
    global collorPallete
    global palleteImage
    palleteImage = Image.open(palleteFilePath)
    collorPallete = palleteImage.load()
    return

def getPalleteColor(scalar):
    width, height = palleteImage.size
    x = scalar * (width * 1.0)
    if (x >= width): x = width - 1
    return collorPallete[x, 0]

def drawComplexPlane():
    pygame.draw.line(screen, (255, 255, 255), projectFromComplex(screenBoundaries[0], 0), projectFromComplex(screenBoundaries[2], 0))
    pygame.draw.line(screen, (255, 255, 255), projectFromComplex(0, screenBoundaries[1]), projectFromComplex(0, screenBoundaries[3]))

    i = 0
    while i < screenBoundaries[2]:
        p = projectFromComplex(i, 0)
        pygame.draw.line(screen, (255, 255, 255), (p[0], p[1] - 5), (p[0], p[1] + 5))
        i += 1

    i = 0
    while i > screenBoundaries[0]:
        p = projectFromComplex(i, 0)
        pygame.draw.line(screen, (255, 255, 255), (p[0], p[1] - 5), (p[0], p[1] + 5))
        i -= 1

    i = 0
    while i < screenBoundaries[3]:
        p = projectFromComplex(0, i)
        pygame.draw.line(screen, (255, 255, 255), (p[0] - 5, p[1]), (p[0] + 5, p[1]))
        i += 1

    i = 0
    while i > screenBoundaries[1]:
        p = projectFromComplex(0, i)
        pygame.draw.line(screen, (255, 255, 255), (p[0] - 5, p[1]), (p[0] + 5, p[1]))
        i -= 1
    
    return

# Maldelbrot formula
# Z[n] = Z[n-1] ^ 2 + C
# Optimized escape time algorithm
def iterateComplex(x0, y0):
    x2 = 0
    y2 = 0
    x = 0
    y = 0
    iterations = 0
    while (x2 + y2 <= 4 and iterations < maxIterations):
        y = 2 * x * y + y0
        x = x2 - y2 + x0
        x2 = x * x
        y2 = y * y
        iterations += 1
    return iterations

def iterNormalize(iterations):
    res = iterations / 100.0
    if (res > 100.0): return 1.0
    return res

def getUnitInComplexSpace():
    unit = [[1, 1, 0]] # IT IS NOT AN UNITARY VECTOR!
    unitComplx = np.dot(unit, complexSpaceTransformationTransposedInverse)
    return (unitComplx[0][0], unitComplx[0][1])

def calculateTransformationMatrix():
    global complexSpaceTransformationTransposed
    global complexSpaceTransformationTransposedInverse

    complexSpaceTransformationTransposed = np.transpose(complexSpaceTransformation)
    complexSpaceTransformationTransposedInverse = np.linalg.inv(complexSpaceTransformationTransposed)
    print(complexSpaceTransformationTransposedInverse)
    return

# It returns the x, y, w, h
def getScreenBoundariesInComplexSpace():
    topLeftCorner = [[0, 0, 1]]
    bottomRightCorner = [[WINDOW_W, WINDOW_H, 1]]
    topLeftRes = np.dot(topLeftCorner, complexSpaceTransformationTransposedInverse)
    bottomRightRes = np.dot(bottomRightCorner, complexSpaceTransformationTransposedInverse)
    return (topLeftRes[0][0], topLeftRes[0][1], bottomRightRes[0][0], bottomRightRes[0][1])

def projectFromComplex(real, imaginary, w = 1):
    outMatrix = np.dot([[real, imaginary, w]], complexSpaceTransformationTransposed)
    return (outMatrix[0][0], outMatrix[0][1])

def projectToComplex(x, y, w = 1):
    screenPoint = [[x, y, w]]
    complexSpacePoint = np.dot(screenPoint, complexSpaceTransformationTransposedInverse)
    return (complexSpacePoint[0][0], complexSpacePoint[0][1])

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()

