import math


def timeDistanceAcceleration(distance: float, acceleration: int):
    """Returns the time it takes to travel a given distance with a constant
    acceleration."""
    return math.sqrt((2 * distance) / acceleration)


def timeDistanceVelocity(
    distance: float, velocity: int, distanceOffset: float, timeOffset: float
):
    """Returns time to travel a given distance at a constant velocity. Includes both
    distance and time offsets. timeOffest should be the time from start the constant
    velocity starts. distanceOffset should be the distance from start the constant
    velocity starts.
    """
    return ((distance - distanceOffset) / velocity) + timeOffset


def timeDistanceDeceleration(
    distance: float,
    velocity: int,
    acceleration: int,
    distanceOffset: float,
    timeOffset: float,
):
    """Returns time to a given distance when decelerating at a constant rate from a
    given velocity."""
    squareRoot = math.sqrt(
        abs((velocity**2) - (2 * acceleration * (distance - distanceOffset)))
    )
    return ((velocity - squareRoot) / acceleration) + timeOffset


def timeDistanceFunction(
    distance: float, acceleration: int, maxVelocity: int, totalDistance: float
):
    """Returns the time to a given distance along a travel path that includes
    acceleration, constant velocity, and  deceleration. totalDistance is the total
    distance of the move. distance is the distance measuring for returned time."""
    timeToVelocity = maxVelocity / acceleration

    distanceToVelocity = 0.5 * acceleration * (timeToVelocity**2)

    timePoint = 0

    """totalDistance is the total distance traveled for this calculation so any 
    distance greater than that would be out of scope."""
    if (distance > totalDistance) or (distance < 0):
        raise ValueError("Distance is greater than total distance.")

    """If the total distance is less that twice the distance it takes to get to a 
    constant velocity then constant velocity never occurs for the travel path."""
    if (2 * distanceToVelocity) > totalDistance:
        halfDistance = totalDistance / 2
        timeOffset = math.sqrt((2 * halfDistance) / acceleration)

        if distance < halfDistance:
            timePoint = timeDistanceAcceleration(distance, acceleration)
        else:
            timePoint = timeDistanceDeceleration(
                distance, maxVelocity, acceleration, halfDistance, timeOffset
            )
    else:
        distanceToDeceleration = totalDistance - distanceToVelocity

        if distance < distanceToVelocity:
            timePoint = timeDistanceAcceleration(distance, acceleration)

        elif distance < distanceToDeceleration:
            timePoint = timeDistanceVelocity(
                distance, maxVelocity, distanceToVelocity, timeToVelocity
            )

        else:
            timeToDeceleration = timeDistanceVelocity(
                distanceToDeceleration, maxVelocity, distanceToVelocity, timeToVelocity
            )

            timePoint = timeDistanceDeceleration(
                distance,
                maxVelocity,
                acceleration,
                distanceToDeceleration,
                timeToDeceleration,
            )

    return 1000 * (timePoint)


def timeDistanceList(
    distanceInterval: float, acceleration: int, maxVelocity: int, numberOfKeys: int
):
    """Returns a list of location-time pairs representing how long it took to get to
    the paired position."""
    adjustedAcceleration = acceleration / distanceInterval
    adjustedVelocity = maxVelocity / distanceInterval
    adjustedTotalDistance = numberOfKeys

    positions = []

    for i in range(int(adjustedTotalDistance) + 1):
        positions.append(
            timeDistanceFunction(
                i, adjustedAcceleration, adjustedVelocity, adjustedTotalDistance
            )
        )

    return positions
