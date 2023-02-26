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

    # totalDistance is the total distance traveled for this calculation so any distance greater than
    # that would be out of scope.
    if((distance > totalDistance) or (distance < 0)):
        return 0

    if((2 * distanceToVelocity) > totalDistance):
        halfDistance = totalDistance / 2
        timeOffset = math.sqrt((2 * halfDistance) / acceleration) 
        if(distance < halfDistance):
            return 1000 * timeDistanceAcceleration(distance, acceleration)
        else:
            return 1000 * timeDistanceDeceleration(distance, maxVelocity, acceleration, halfDistance, 
                                            timeOffset)
    else:
        distanceToDeceleration = totalDistance - distanceToVelocity
        
        if(distance < distanceToVelocity):
            return 1000 * timeDistanceAcceleration(distance, acceleration)
        elif(distance < distanceToDeceleration):
            return 1000 * timeDistanceVelocity(distance, maxVelocity, distanceToVelocity, 
                                               timeToVelocity)
        else:
            timeToDeceleration = timeDistanceVelocity(distanceToDeceleration, maxVelocity, 
                                                  distanceToVelocity, timeToVelocity)
            
            return 1000 * timeDistanceDeceleration(distance, maxVelocity, acceleration, 
                                            distanceToDeceleration, timeToDeceleration)
        

totalDistance = 200
acceleration = 200
maxVelocity = 100

positions = []

for i in range(totalDistance + 1):
    positions.append([i, timeDistanceFunction(i, acceleration, maxVelocity, totalDistance)])
print(positions)