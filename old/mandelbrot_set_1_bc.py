# The Mandelbrot Set
# Copyright (C) Felipe Durar 2021

import pygame
import numpy as np
import math
import threading
import time
from colour import Color

complexSpaceTransformation = np.array(
    [[200.0, 0.0, 400.0],
     [0.0, 200.0, 300.0],
     [0.0, 0.0, 1.0]])

displayComplexPlane = True
maxIterations = 1000
ok = False

threadLock = threading.Lock()
offscreenThreadLock = threading.Lock()
threadList = []
threads = 10
 
# define a main function
def main():
    global screen
    global renderingSurface
    global offscreenSurface
    global defaultFont
    global rendering

    rendering = False
     
    # initialize the pygame module
    pygame.init()
    
    # load and set the logo
    #logo = pygame.image.load("./Pics/Screenshot_2.png")
    #pygame.display.set_icon(logo)
    pygame.display.set_caption("Mandelbrot Set - By Felipe Durar")
     
    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((800,600), pygame.RESIZABLE)
    renderingSurface = pygame.Surface((800,600))
    offscreenSurface = pygame.Surface((800,600))
    
    defaultFont = pygame.font.SysFont('Consolas', 18)

    renderingSurface.fill((100, 0, 0))
    offscreenSurface.fill((0, 0, 0))
     
    # define a variable to control the main loop
    running = True
    
    # Calculate Transformations
    calculateTransformationMatrix()

    # Initialize Interpolated Pallete
    initInterpolationVals()
     
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
        
        draw()
        

def draw():
    global screenBoundaries
    global unitSize
    global ok

    screen.fill((0, 0, 0))

    #screen.set_at((10, 10), (255, 255, 255))
    screenBoundaries = getScreenBoundariesInComplexSpace()
    unitSize = getUnitInComplexSpace()

    threadLock.acquire()
    screen.blit(renderingSurface, (0, 0))
    threadLock.release()

    infoTxt = defaultFont.render('Press i for more informations', False, (255, 255, 255))
    screen.blit(infoTxt, (10,10))
    
    if (displayComplexPlane):
        drawComplexPlane()
    
    pygame.display.flip()
    return

def request_render():
    threadLock.acquire()
    if (rendering):
        return
    threadLock.release()

    renderThred = threading.Thread(target = render, args=())
    renderThred.start()

def render():
    threadLock.acquire()
    rendering = True
    threadLock.release()

    # threadList = []
    # deltaIm = screenBoundaries[3] - screenBoundaries[1]
    # segmentSizes = deltaIm / float(threads)

    # for im in np.arange(0, threads, 1):
    #     segName = "SEG" + str(im)
    #     cImaginary = (im * segmentSizes) + screenBoundaries[1]
    #     renderSegmentThred = threading.Thread(target = render_segment, args=(segName, cImaginary, cImaginary + segmentSizes))
    #     threadList.append(renderSegmentThred)
    #     renderSegmentThred.start()

    # for index, cThread in enumerate(threadList):
    #     cThread.join()



    # threadList = []
    # deltaIm = screenBoundaries[3] - screenBoundaries[1]
    # segmentsCount = deltaIm / unitSize[1]
    # segmentSize = unitSize[1] * 50

    # for im in np.arange(0, 12, 1):
    #     segName = "SEG" + str(im)
    #     cImaginary = (im * segmentSize) + screenBoundaries[1]

    #     renderSegmentThred = threading.Thread(target = render_segment, args=(segName, cImaginary, cImaginary + segmentSize ))
    #     threadList.append(renderSegmentThred)
    #     renderSegmentThred.start()

    # for index, cThread in enumerate(threadList):
    #     cThread.join()






    #---------------------------------------------------------------------------------------
    for im in np.arange(screenBoundaries[1], screenBoundaries[3], unitSize[1]):
        print("Im: " + str(im))
        for real in np.arange(screenBoundaries[0], screenBoundaries[2], unitSize[0]):
            iterRes = iterateComplex(complex(real, im))
            outColor = (0, 0, 0)
            if (iterRes is not None):
                iterRes = iterNormalize(iterRes)
                scalledIndex = int(iterRes * 100)
                if (scalledIndex >= 100): scalledIndex = 99
                normalizedColor = interpolatedPallete[scalledIndex]
                outColor = (normalizedColor.rgb[0] * 255.0, normalizedColor.rgb[1] * 255.0, normalizedColor.rgb[2] * 255.0)
            
            screenSpacePoint = projectFromComplex(real, im)
            naturalPoint = (int(screenSpacePoint[0]), int(screenSpacePoint[1]))
            #print(naturalPoint)
            if (naturalPoint[0] > 0 and naturalPoint[0] < 800 and naturalPoint[1] > 0 and naturalPoint[1] < 600):
                offscreenSurface.set_at(naturalPoint, outColor)
    #---------------------------------------------------------------------------------------
    
    threadLock.acquire()
    renderingSurface.blit(offscreenSurface, (0, 0))
    rendering = False
    threadLock.release()
    return

# def render_segment(segName, imInit, imEnd):
#     print(segName + ": " + str(imInit) + " - " + str(imEnd))

#     deltaIm = imEnd - imInit
#     nHeight = 50 # projectFromComplex(0, deltaIm)[1]
#     nY = projectFromComplex(0, imInit)[1]

#     segmentSurface = pygame.Surface((800,nHeight))
#     print("HEIGHT: " + str(nHeight))
#     segmentSurface.fill((0, 0, 0))

#     for im in np.arange(imInit, imEnd, unitSize[1]):
#         print(segName + " - Im: " + str(im))
#         for real in np.arange(screenBoundaries[0], screenBoundaries[2], unitSize[0]):
#             iterRes = iterateComplex(complex(real, im))
#             outColor = (0, 0, 0)
#             if (iterRes is not None):
#                 iterRes = iterNormalize(iterRes)
#                 scalledIndex = int(iterRes * 100)
#                 if (scalledIndex >= 100): scalledIndex = 99
#                 normalizedColor = interpolatedPallete[scalledIndex]
#                 outColor = (normalizedColor.rgb[0] * 255.0, normalizedColor.rgb[1] * 255.0, normalizedColor.rgb[2] * 255.0)
            
#             screenSpacePoint = projectFromComplex(real, im - imInit)
#             screenPoint = (int(screenSpacePoint[0]), int(screenSpacePoint[1]))
#             #print(naturalPoint)
#             if (screenPoint[0] > 0 and screenPoint[0] < 800 and screenPoint[1] > 0 and screenPoint[1] < 600):
#                 segmentSurface.set_at(screenPoint, outColor)
    
#     offscreenThreadLock.acquire()
#     offscreenSurface.blit(segmentSurface, (0, nY))
#     offscreenThreadLock.release()

#     print("Finished: " + segName + " - NY: " + str(nY))

#     return

def initInterpolationVals():
    global interpolatedPallete
    blue = Color("blue")
    interpolatedPallete = list(blue.range_to(Color("magenta"), 100))
    return

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
def iterateComplex(complexNum):
    results = []
    iterations = 0.0
    z = complex(0, 0)
    while iterations < maxIterations:
        try:
            z = (z ** 2) + complexNum
        except:
            return iterations # idk how i gonna deal with it
        
        if z in results:
            # Recursive case
            return None
        else:
            results.append(z)
            iterations += 1.0

    return iterations

def iterNormalize(iterations):
    res = iterations / 1000.0
    if (res > 1000.0): return 1.0
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
    bottomRightCorner = [[800, 600, 1]]
    topLeftRes = np.dot(topLeftCorner, complexSpaceTransformationTransposedInverse)
    bottomRightRes = np.dot(bottomRightCorner, complexSpaceTransformationTransposedInverse)
    return (topLeftRes[0][0], topLeftRes[0][1], bottomRightRes[0][0], bottomRightRes[0][1])

def projectFromComplex(real, imaginary):
    outMatrix = np.dot([[real, imaginary, 1]], complexSpaceTransformationTransposed)
    return (outMatrix[0][0], outMatrix[0][1])

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()

