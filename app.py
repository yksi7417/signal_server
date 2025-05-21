import random
import eel

# 1. point Eel at your web/ folder
eel.init('static/game')


# 2. simple game‐state stored in Python
TILES = ["🀇", "🀈", "🀉", "🀊", "🀋", "🀌"]
history = []


@eel.expose
def draw_tile():
    """Called from JS: pick a random tile, record history, and return it."""
    tile = random.choice(TILES)
    history.append(tile)
    # after drawing, notify JS of updated history
    eel.update_history(history)
    return tile


@eel.expose
def reset_game():
    """Called from JS: clear history."""
    history.clear()
    eel.update_history(history)
    return True


if __name__ == '__main__':
    # 3. start a Chromium window at web/index.html
    eel.start('index.html', size=(400, 500))
