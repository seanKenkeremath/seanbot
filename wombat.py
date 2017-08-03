log = {}
bored = 0
width = 7
height = 7
path = []
targetCoords = []
targetTile = 0
currState = 0
frontier = []
searched = []
fromTile = []
shotDamage = 10

global arena
def arena():
    return currState['arena']

global tile 
def tile(x, y):
    return arena()[y][x]

global playerTile   
def playerTile():
    return tile(coords()[0], coords()[1])

global coords   
def coords():
    return currState['local-coords']

global tileType 
def tileType(tile):
    return tile['contents']['type']

global isPoison 
def isPoison(tile):
    return tileType(tile) == 'poison'

global isWall   
def isWall(tile):
    return isWoodWall(tile) or tileType(tile) =='steel-barrier'

global isWoodWall
def isWoodWall(tile):
    return tileType(tile) == 'wood-barrier'

global isOtherWombat
def isOtherWombat(x, y, tile):
    return tileType(tile) == 'wombat' and [x,y] != coords()

global hp
def hp(tile):
    if 'contents' in tile.keys():
        if 'hp' in tile['contents'].keys():
            return tile['contents']['hp']
    return 0

global isFog    
def isFog(tile):
    return tileType(tile) == 'fog'

global isSmoke
def isSmoke(tile):
    return tileType(tile) == 'smoke'

global isEnemy
def isEnemy(x, y, tile):
    return isOtherWombat(x, y, tile) or isWoodWall(tile) or tileType(tile) == 'zakano'

global tileValue
def tileValue(x, y, tile):

    global shotDamage

    if tileType(tile) == 'food':
        if hp(playerTile()) < shotDamage * 2:
            return 26
        return 10
    elif tileType(tile) == 'zakano':
        if hp(tile) <= shotDamage:
            return 15
        elif hp(tile) <= shotDamage*2:
            return 8
        return 2
    elif isOtherWombat(x, y, tile):
        if hp(playerTile()) < hp(tile):
            return 7
        elif hp(tile) <= shotDamage:
            return 25
        elif hp(tile) <= shotDamage*2:
            return 13
        return 3
    elif isWoodWall(tile):
        return 1.5
    return 0

global tileEv
def tileEv(x, y, tile):
    evPathToTile = pathToTile(x, y)
    evTileValue = tileValue(x, y, tile)
    evPathTime = pathTime(evPathToTile, [x,y], orientation())
    if evPathTime == 0:
        return 0
    return evTileValue/float(evPathTime)

global search
def search(x, y, maxTile, maxEv):

    def valid(coord):
        global frontier
        global searched
        theTile = tile(coord[0], coord[1])
        return coord not in searched and coord not in frontier and not isFog(theTile) and not isWall(theTile) and not isPoison(theTile)
    
    def tryAdd(dx, dy, backVector):
        if valid([dx, dy]):
            global frontier
            global fromTile
            frontier.append([dx, dy])
            fromTile[dx][dy] = backVector
        
    searchTile = tile(x, y)
    searchTileEv = tileEv(x, y, searchTile)

    if searchTileEv > maxEv or maxTile == []:
        maxEv = searchTileEv
        maxTile = [x,y]
        
    global frontier
    global searched
    global width
    global height
    searched.append([x, y])
    
    if x > 0:
        tryAdd(x-1, y, [1, 0])
    if x < width - 1:
        tryAdd(x+1, y, [-1, 0])
    if y > 0:
        tryAdd(x, y-1, [0, 1])
    if y < height - 1:
        tryAdd(x, y+1, [0, -1])

    if len(frontier) == 0:
        return maxTile
    
    nextTile = frontier.pop(0)
    return search(nextTile[0], nextTile[1], maxTile, maxEv)

global orientation
def orientation():
    orientation = tile(coords()[0], coords()[1])['contents']['orientation']
    if orientation == 'n':
        return [0, -1]
    if orientation == 'w':
        return [-1, 0]
    if orientation == 's':
        return [0, 1]
    if orientation == 'e':
        return [1, 0]   

global turnToVector
def turnToVector(vector):
    orientationVector = orientation()
    sumVector = [vector[0] + orientationVector[0], vector[1] + orientationVector[1]]
    if sumVector == [0,0]:
        return "about-face"
    prod = sumVector[0] * sumVector[1]
    if orientationVector[0] == 0:
        #north/south facing
        if prod == -1:
            return "right"
        return "left"

    #east/west facing
    if prod == -1:
        return "left"
    return "right"

global pathToTile
def pathToTile(x, y):
    buildPath = []
    currInPath = [x, y]
    currVector = [0,0]
    while currInPath != coords():

        currVector = fromTile[currInPath[0]][currInPath[1]]
        currVector = [currVector[0], currVector[1]]
        currInPath[0] = currInPath[0] + currVector[0]
        currInPath[1] = currInPath[1] + currVector[1]
        currVector[0] = currVector[0] * -1
        currVector[1] = currVector[1] * -1
        buildPath.insert(0, currVector)
    return buildPath

global pathTime
def pathTime(path, tileCoords, currDirection):
    totalTime = 0
    for i in range(0, len(path)):
        totalTime += 1
        if currDirection != path[i]:
            totalTime += 1
            currDirection = path[i]
    if isEnemy(tileCoords[0], tileCoords[1], tile(tileCoords[0], tileCoords[1])):
        # Add a turn to account for shooting
        totalTime += 1
    return totalTime

global turn
def turn(direction):
    return {'action': 'turn', 'metadata': {'direction': direction}}
global moveForward
def moveForward():
    return {'action': 'move', 'metadata': {}}
global shoot
def shoot():
    return {'action': 'shoot'}
    
def wombat(state, time_left):
    global bored
    global path
    global targetCoords
    global targetTile
    global width
    global height
    global currState
    global fromTile
    global searched
    global frontier
    global command
    global log
    global shotDamage

    currState = state
    for i in range(width):
        fromTile.append([])
        for j in range(height):
            fromTile[i].append([0,0])

    if 'saved-state' in state and state['saved-state']:
        savedState = state['saved-state']
        path = savedState['path']
        targetCoords = savedState['targetCoords']
        targetTile = savedState['targetTile']
        bored = savedState['bored']
    else:
        path = []
        targetCoords = []
        targetTile = 0;
        
    frontier = []
    searched = []
    

    #Calculate ev of our stored target using the remainder of our saved path
    currTargetTile = 0
    targetEv = 0
    if len(targetCoords) > 1 and len(path) > 0:
        currTargetTile = tile(targetCoords[0], targetCoords[1])
        targetEv = tileValue(targetCoords[0], targetCoords[1], targetTile)/float(pathTime(path, targetCoords, orientation()))

    #Perform search and calculate ev of max value target
    newTargetCoords = search(coords()[0], coords()[1], [], 0)
    newTargetTile = tile(newTargetCoords[0], newTargetCoords[1])
    newTargetEv = tileEv(newTargetCoords[0], newTargetCoords[1], newTargetTile)

    log['targetEv'] = targetEv
    log['newSearchEv'] = newTargetEv

    #If we have no path, we see something more valuable, or our target is no longer valid. 
    #Fog and smoke still count as valid because target is probably still there
    if len(path) == 0 or len(targetCoords) < 2 or newTargetEv > targetEv or (tileType(currTargetTile) != tileType(targetTile) and not isSmoke(currTargetTile) and not isFog(currTargetTile)):
        targetCoords = newTargetCoords
        targetTile = newTargetTile
        if targetCoords != coords() and len(targetCoords) > 1:
            path = pathToTile(targetCoords[0], targetCoords[1])

    if len(targetCoords) > 1:
        log['targetHp'] = hp(targetTile) 
        log['targetValue'] = tileValue(targetCoords[0], targetCoords[1], targetTile)

    #If there is something right in front of us, shoot
    shooting = False
    for i in range (1,5):
        dx = coords()[0] + i * orientation()[0]
        dy = coords()[1] + i * orientation()[1]

        if dx > width -1 or dx < 0 or dy > height -1 or dy < 0:
            break
        sightTile = tile(coords()[0] + i * orientation()[0], coords()[1] + i * orientation()[1])

        #Shoot if there's something in front, but only shoot at wall if you ahve nothing else to do
        if isEnemy(dx, dy, sightTile) and not (len(path) > 0 and isWall(sightTile)):
            command = shoot()
            shooting = True
            break
    
    if not shooting:
        move = [0,0]
        #If we have no path, just start moving forward for a while
        if len(path) == 0:
            bored +=1
            if bored > 8:
                bored = 0
                command = turn('right')
            else:
                command = moveForward()
                move = orientation()
        #Move along the path, turn if necessary
        else:
            bored = 0
            move = path[0]
            if orientation() == move:
                command = moveForward()
                path.pop(0)
            else:
                command = turn(turnToVector(move))

    #If we're about to move into a wall or poison, turn right. this should only happen when no path
    frontTile = tile(coords()[0] + orientation()[0], coords()[1] + orientation()[1])
    if command['action'] == 'move':
        if isPoison(frontTile) or isWall(frontTile):
            command = turn('right')
    return {
        'command': command,
        'state': {'path': path, 'targetCoords': targetCoords, 'targetTile': targetTile, 'bored': bored, 'log': log}
    }
