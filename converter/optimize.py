from playable import PlayableNote

def new_point(locations: list[int], group: list[PlayableNote], remaining: int) -> bool:
    another_location = len(locations) > 1
    another_group = len(group)
    another_remaining = remaining > 0

    result = another_location and another_group and another_remaining

    return result