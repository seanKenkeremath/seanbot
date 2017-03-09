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
    
global isEnemy
def isEnemy(tile):
    return tileType(tile) == 'wombat' or tileType(tile) == 'wood-barrier' or tileType(tile) == 'zakano'

global search
def search(x, y, ring, maxTile):

    def valid(coord):
        theTile = tile(coord[0], coord[1])
        return coord not in searched and coord not in frontier and not isWall(theTile) and not isPoison(theTile) and not isFog(theTile)

    def tryAdd(dx, dy, backVector):
        if valid([dx, dy]):
            frontier.insert(0, [dx, dy])
            fromTile[dx][dy] = backVector
    
    
    if ring >12:
        return maxTile
        
    global foods
    searchTile = tile(x, y)
    if tileType(searchTile) == 'food':
        print("Food: " + str([x,y]))
        foods.append(maxTile)
        return [x,y]
        if maxTile == [0,0] or maxTile == coords() or ring < maxTileRing:
            global maxTileRing
            maxTileRing = ring
            maxTile[0] = x
            maxTile[1] = y
            foods.append(maxTile)
    
    searched.append([x, y])
    
    if x > 0:
        tryAdd(x-1, y, [1, 0])
    if x < width - 1:
        tryAdd(x+1, y, [-1, 0])
    if y > 0:
        tryAdd(x, y-1, [0, 1])
    if y < height - 1:
        tryAdd(x, y+1, [0, -1])
    
    print("Searched: ")
    print(searched)

    print("Frontier: ")
    print(frontier)

    if len(frontier) == 0:
        print("Returning")
        print(maxTile)
        return maxTile
    
    nextTile = frontier.pop(0)
    return search(nextTile[0], nextTile[1], ring + 1, maxTile)

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

        print("PATH: " + str([currInPath[0], currInPath[1]]))
        currVector = fromTile[currInPath[0]][currInPath[1]]
        currInPath[0] = currInPath[0] + currVector[0]
        currInPath[1] = currInPath[1] + currVector[1]
        print("Movement: ")
        print(currVector)
        currVector[0] = currVector[0] * -1
        currVector[1] = currVector[1] * -1
        path.append(currVector)
    return path
    
def wombat(state, time_left):
    global path
    global foods
    global width
    global height
    global currState
    global fromTile
    global searched
    global frontier
    global maxTileRing
    currState = state
    for i in range(width):
        fromTile.append([])
        for j in range(height):
            fromTile[i].append([0,0])
    
    if 'saved-state' in state and state['saved-state']:
        log = "saved"
        savedState = state['saved-state']
        path = savedState['path']
    else:
        log = "not saved"
        path = []
        
    log = state
    foods = []
    frontier = []
    searched = []
    maxTileRing = 0
    
    move = [0,0]

    ev = 0
    points = 20
    
    if len(path)==0:
        
        targetTile = search(coords()[0], coords()[1], 0, [0,0])
    
        print("Result: ")
        print(targetTile)
        log = targetTile
        global command
        if targetTile == coords() or targetTile == [0,0] or len(targetTile) < 2:
            command = {'action': 'move', 'metadata': {}}
        else:
            path = pathToTile(targetTile[0], targetTile[1])

    shooting = False
    
    for i in range (1,5):
        dx = coords()[0] + i * orientation()[0]
        dy = coords()[1] + i * orientation()[1]

        if dx > width -1 or dx < 0 or dy > height -1 or dy < 0:
            break
        sightTile = tile(coords()[0] + i * orientation()[0], coords()[1] + i * orientation()[1])
        if isEnemy(sightTile):
            command = {'action': 'shoot'}
            shooting = True
            break
    
    if not shooting:
        if len(path) == 0:
            command = {'action': 'move', 'metadata': {}}
            move = orientation()
        else:
            ev = points/len(path)
            move = path[0]
            if orientation() == move:
                command = {'action': 'move', 'metadata': {}}
                path.pop(0)
            else:
                command ={'action': 'turn', 'metadata': {'direction': turnToVector(move)}}

    frontTile = 0
    if command['action'] == 'move':
        frontTile = tile(coords()[0] + move[0], coords()[1] + move[1])
        if isPoison(frontTile) or isWall(frontTile):
            command ={'action': 'turn', 'metadata': {'direction': 'right'}}
    return {
        'command': command,
        'state': {'path': path, 'ev': ev}
    }

width = 7
height = 7

foods = []

path = []

currState = 0
frontier = []
searched = []
fromTile = []
maxTileRing = 0