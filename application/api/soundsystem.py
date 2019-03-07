""" This api provides shortcuts function to play sound with the enibar
soudsystem daemon """

import api.redis


def play(action, **kwargs):
    """ Send a soundsystem play request to the daemon

    :param action: Action used to select the sound to play
    """
    message = {
        'action': action,
        'params': kwargs,
    }
    api.redis.send_message('enibar-soundsystem', message)
