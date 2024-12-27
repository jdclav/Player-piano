import math


def accel_time(dist: float, accel: float) -> float:
    """
    Calculates the time in seconds to travel a given distance with a given acceleration.

    param dist: A float value representing the distance to travel in mm.
    param accel: A float value representing the acceleration of the move in mm/s^2.

    return: A float value representing the time in seconds it take to travel
    dist with the given accel.
    """

    result_time = math.sqrt((2 * dist) / accel)

    return result_time


def velocity_time(dist: float, vel: float) -> float:
    """
    Returns time to travel a given distance at a constant velocity.

    param dist: A float value representing the final distance to travel in mm.
    param vel: A float value representing the velocity of the move in mm/s.

    return: A float value for the total time in seconds to travel dist with
    the given vel.
    """

    result_time = dist / vel

    return result_time


def deceleration_time(
    dist: float,
    vel: float,
    accel: float,
) -> float:
    """
    Calculates the time in seconds it takes to travel a given distance
    while decelerating at a given rate from a given starting velocity.

    param dist: A float value representing the final distance to travel in mm.
    param vel: A float value representing the velocity of the move in mm/s.
    param accel: A float value representing the deceleration of the move in mm/s^2.
    """

    squareRoot = math.sqrt(abs((vel**2) - (2 * accel * (dist))))
    result_time = (vel - squareRoot) / accel

    return result_time


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
            timePoint = accel_time(distance, acceleration)
        else:
            decel_dist = distance - halfDistance
            timePoint = (
                deceleration_time(decel_dist, maxVelocity, acceleration) + timeOffset
            )

    else:
        distanceToDeceleration = totalDistance - distanceToVelocity

        if distance < distanceToVelocity:
            timePoint = accel_time(distance, acceleration)

        elif distance < distanceToDeceleration:
            vel_distance = distance - distanceToVelocity
            timePoint = velocity_time(vel_distance, maxVelocity) + timeToVelocity

        else:
            vel_distance = distanceToDeceleration - distanceToVelocity
            timeToDeceleration = (
                velocity_time(vel_distance, maxVelocity) + timeToVelocity
            )

            decel_dist = distance - distanceToDeceleration

            timePoint = (
                deceleration_time(decel_dist, maxVelocity, acceleration)
                + timeToDeceleration
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
