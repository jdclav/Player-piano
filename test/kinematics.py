import math
from decimal import Decimal


def accel_time(dist: Decimal, accel: Decimal) -> Decimal:
    """
    Calculates the time in seconds to travel a given distance with a given acceleration.

    param dist: A Decimal value representing the distance to travel in mm.
    param accel: A Decimal value representing the acceleration of the move in mm/s^2.

    return: A Decimal value representing the time in seconds it take to travel
    dist with the given accel.
    """

    under_root = (2 * dist) / accel
    result_time = under_root.sqrt()

    return result_time


def velocity_time(dist: Decimal, vel: Decimal) -> Decimal:
    """
    Returns time to travel a given distance at a constant velocity.

    param dist: A Decimal value representing the final distance to travel in mm.
    param vel: A Decimal value representing the velocity of the move in mm/s.

    return: A Decimal value for the total time in seconds to travel dist with
    the given vel.
    """

    result_time = dist / vel

    return result_time


def deceleration_time(dist: Decimal, vel: Decimal, accel: Decimal) -> Decimal:
    """
    Calculates the time in seconds it takes to travel a given distance
    while decelerating at a given rate from a given starting velocity.

    param dist: A Decimal value representing the final distance to travel in mm.
    param vel: A Decimal value representing the velocity of the move in mm/s.
    param accel: A Decimal value representing the deceleration of the move in mm/s^2.

    return: A Decimal value representing the time to decelerate from a given velocity
    over a certain distance.
    """

    under_abs = (vel**2) - (2 * accel * (dist))
    under_root = abs(under_abs)
    squareRoot = under_root.sqrt(under_root)
    result_time = (vel - squareRoot) / accel

    return result_time


def time_distance_function(
    dist: Decimal,
    accel: Decimal,
    vel: Decimal,
    total_dist: Decimal,
) -> Decimal:
    """
    Calculate the time to travel a given distance out of the total distance
    with a given acceleration. The acceleration is limited by the a max velocity.

    param dist: A Decimal value that represents the distance
    into the move time should be calculated for. Should always be less that total_dist
    param accel: A Decimal value that represents the acceleration of the move.
    param vel: A Decimal value that represents the maximum velocity of the move.
    This will limit the acceleration.
    param total_dist: A Decimal value that represents the total distance of the move
    which defines how much of the move is in acceleration, constant velocity, and
    deceleration.

    return: A Decimal value that represents the time it takes to reach the dist
    based on the entire move.
    """
    vel_time = vel / accel

    vel_distance = 0.5 * accel * (vel_time**2)

    timePoint = 0

    assert (dist <= total_dist) or (
        dist >= 0
    ), "Distance must be positve and less than or equal to the total distance."

    """If the total distance is less that twice the distance it takes to get to a 
    constant velocity then constant velocity never occurs for the travel path."""
    if (2 * vel_distance) > total_dist:
        halfDistance = total_dist / 2
        timeOffset = math.sqrt((2 * halfDistance) / accel)

        if dist < halfDistance:
            timePoint = accel_time(dist, accel)
        else:
            decel_dist = dist - halfDistance
            timePoint = deceleration_time(decel_dist, vel, accel) + timeOffset

    else:
        distanceToDeceleration = total_dist - vel_distance

        if dist < vel_distance:
            timePoint = accel_time(dist, accel)

        elif dist < distanceToDeceleration:
            vel_distance_2 = dist - vel_distance
            timePoint = velocity_time(vel_distance_2, vel) + vel_time

        else:
            vel_distance_2 = distanceToDeceleration - vel_distance
            timeToDeceleration = velocity_time(vel_distance_2, vel) + vel_time

            decel_dist = dist - distanceToDeceleration

            timePoint = deceleration_time(decel_dist, vel, accel) + timeToDeceleration

    return 1000 * (timePoint)


def time_distance_list(
    dist_interval: Decimal, accel: Decimal, vel: Decimal, num_intervals: int
) -> list[Decimal]:
    """
    Generates a list of Decimal values that represent the time to travel
    a number of distance intervals equal to the index of the list

    param dist_interval: A Decimal value that represents the distance interval
    that will be used to divide the result list.
    param accel: A Decimal value that represents the acceleration for the total move.
    param vel: A Decimal value that represents the maximum velocity of the move.
    param num_intervals: A integer value that represents the total number of intervals.
    This mulitplied by the dist_interval will equal the total distance.

    return: A list of Decimals where the index represents the intervals travelled and
    the Decimal represents the time to travel that number of intervals.
    """
    adjusted_accel = accel / dist_interval
    adjusted_vel = vel / dist_interval

    positions: list[Decimal] = []

    for i in range(int(num_intervals) + 1):
        positions.append(
            time_distance_function(i, adjusted_accel, adjusted_vel, num_intervals)
        )

    return positions
