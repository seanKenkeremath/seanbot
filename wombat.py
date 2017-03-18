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
    return tileType(tile) == 'wood-barrier' or tileType(tile) =='steel-barrier'

global isFog    
def isFog(tile):
    return tileType(tile) == 'fog'

global isSmoke
def isSmoke(tile):
    return tileType(tile) == 'smoke'

global isEnemy
def isEnemy(tile):
    return tileType(tile) == 'wombat' or tileType(tile) == 'wood-barrier' or tileType(tile) == 'zakano'

global search
def search(x, y, maxTile):

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
    if tileType(searchTile) == 'food':
        return [x,y]
    elif tileType(searchTile) == 'zakano' or tileType(searchTile) == 'wombat':
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
    return search(nextTile[0], nextTile[1], maxTile)

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
    path = []
    currInPath = [x, y]
    currVector = [0,0]
    while currInPath != coords():

        currVector = fromTile[currInPath[0]][currInPath[1]]
        currInPath[0] = currInPath[0] + currVector[0]
        currInPath[1] = currInPath[1] + currVector[1]
        currVector[0] = currVector[0] * -1
        currVector[1] = currVector[1] * -1
        path.insert(0, currVector)
    return path

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
    global targetTile
    global targetType
    global width
    global height
    global currState
    global fromTile
    global searched
    global frontier

    currState = state
    for i in range(width):
        fromTile.append([])
        for j in range(height):
            fromTile[i].append([0,0])

    if 'saved-state' in state and state['saved-state']:
        savedState = state['saved-state']
        path = savedState['path']
        targetTile = savedState['target']
        targetType = savedState['targetType']
        bored = savedState['bored']
    else:
        path = []
        targetTile = []
        targetType = '';
        
    frontier = []
    searched = []
    
    #If we have no path, or our target is no longer valid. 
    #Fog and smoke still count as valid because target is probably still there
    currTargetTile = 0
    if len(targetTile) > 1:
        currTargetTile = tile(targetTile[0], targetTile[1])

    if len(path)==0 or len(targetTile) < 2 or (tileType(currTargetTile) != targetType and not isSmoke(currTargetTile) and not isFog(currTargetTile)):
        
        targetTile = search(coords()[0], coords()[1], [])
        targetType = tileType(tile(targetTile[0], targetTile[1]))
        global command
        if targetTile == coords() or len(targetTile) < 2:
            command = moveForward
        else:
            path = pathToTile(targetTile[0], targetTile[1])

    #If there is something right in front of us, shoot
    shooting = False
    
    for i in range (1,5):
        dx = coords()[0] + i * orientation()[0]
        dy = coords()[1] + i * orientation()[1]

        if dx > width -1 or dx < 0 or dy > height -1 or dy < 0:
            break
        sightTile = tile(coords()[0] + i * orientation()[0], coords()[1] + i * orientation()[1])
        if isEnemy(sightTile):
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
        'state': {'path': path, 'target': targetTile, 'targetType': targetType, 'bored': bored}
    }

bored = 0
width = 7
height = 7

path = []
targetTile = []
targetType = ''
currState = 0
frontier = []
searched = []
fromTile = []
