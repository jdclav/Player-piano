import math

def timeDistanceAcceleration(distance, acceleration):
    return math.sqrt((2 * distance) / acceleration)

def timeDistanceVelocity(distance, velocity, distanceOffset, timeOffset):
    return ((distance - distanceOffset) / velocity) + timeOffset

def timeDistanceDeceleration(distance, velocity, acceleration, distanceOffset, timeOffset):
    squareRoot = math.sqrt((velocity ** 2) - (2 * acceleration * (distance - distanceOffset)))
    return ((velocity - squareRoot) / acceleration) + timeOffset

def timeDistanceFunction(distance, acceleration, maxVelocity, totalDistance):
    timeToVelocity = (maxVelocity / acceleration)
    distanceToVelocity = (0.5 * acceleration * (timeToVelocity ** 2))

    timePoint = 0

    # totalDistance is the total distance traveled for this calculation so any distance greater than
    # that would be out of scope.
    if((distance > totalDistance) or (distance < 0)):
        return timePoint

    if((2 * distanceToVelocity) > totalDistance):
        halfDistance = totalDistance / 2
        timeOffset = math.sqrt((2 * halfDistance) / acceleration) 
        if(distance < halfDistance):
            timePoint = timeDistanceAcceleration(distance, acceleration)
        else:
            timePoint = timeDistanceDeceleration(distance, maxVelocity, acceleration, halfDistance, 
                                            timeOffset)
    else:
        distanceToDeceleration = totalDistance - distanceToVelocity
        
        if(distance < distanceToVelocity):
            timePoint = timeDistanceAcceleration(distance, acceleration)
        elif(distance < distanceToDeceleration):
            timePoint = timeDistanceVelocity(distance, maxVelocity, distanceToVelocity, 
                                               timeToVelocity)
        else:
            timeToDeceleration = timeDistanceVelocity(distanceToDeceleration, maxVelocity, 
                                                  distanceToVelocity, timeToVelocity)
            
            timePoint = timeDistanceDeceleration(distance, maxVelocity, acceleration, 
                                            distanceToDeceleration, timeToDeceleration)

    return 1000 * (timePoint)    
    
def timeDistanceList(distanceInterval, acceleration, maxVelocity, totalDistance): 
    adjustedAcceleration = (acceleration / distanceInterval)
    adjustedVelocity = (maxVelocity / distanceInterval)
    adjustedTotalDistance = (totalDistance / distanceInterval)

    positions = []
    
    for i in range(int(adjustedTotalDistance) + 1):
        positions.append([(distanceInterval * i), 
                          timeDistanceFunction(i, adjustedAcceleration, adjustedVelocity, 
                                               adjustedTotalDistance)])
    
    return positions
        

totalDistance = 232
acceleration = (2000)
maxVelocity = (1000)

frameUpdates = timeDistanceList(23.2, acceleration, maxVelocity, totalDistance) 
print(frameUpdates)