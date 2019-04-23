# *-* coding utf8 *-*

import queue
import pygame

import logger

# general game events

INITÆGAME = 1
QUIT_GAME = 2
PAUSE_GAME = 3

# scene events
LOAD_SCENE = 10
LEAVE_SCENE = 11
LEAVE_CURRENT_SCENE = 12
SCENE_INTERVAL_ACTIVATE = 13
SCENE_INTERVAL_DEACTIVATE = 14
SCENE_INTERVAL_TICK = 15
SCENE_STACK = 16
SCENE_UNSTACK = 17

# hero specific events
HERO_SPAWN = 50
HERO_WALK_START = 51
HERO_WALK_STOP = 52
HERO_RUN_START = 53
HERO_RUN_STOP = 54



# List objects receiving custom game events.
eventListeners = []
eventQueue = queue.Queue()

def pump():
    global eventQueue
    
    try:
        e = eventQueue.get(block=False)
    except queue.Empty:
        return
    dispatch(e)

        # Maps event constants to strings to ease event handler executions.
eventNames = {
    LOAD_SCENE: "load_scene",
    LEAVE_SCENE: "leave_scene",
    LEAVE_CURRENT_SCENE: "leave_current_scene",
    SCENE_INTERVAL_ACTIVATE: "scene_interval_activate",
    SCENE_INTERVAL_DEACTIVATE: "scene_interval_deactivate",
    SCENE_INTERVAL_TICK: "scene_interval_tick",
    SCENE_STACK: "scene_stack",
    SCENE_UNSTACK: "scene_unstack",
    QUIT_GAME: "quit_game",
    PAUSE_GAME: "pause_game",

    HERO_SPAWN: "hero_spawn",
    HERO_WALK_START: "hero_walk_start",
    HERO_WALK_STOP: "hero_walk_stop",
    HERO_RUN_START: "hero_run_start",
    HERO_RUN_STOP: "hero_run_stop"
}

def addListener(obj):
    """Adds obj as a listener who will be notified when events occur, if the corresponding method
is found within obj's implementation."""
    global eventListeners

    if obj is not None:
        eventListeners.append(obj)

def post(type, data=None, target=None):
    """Posts an event to all listeners. the type argument must be one of the defined eventManager
constants above. The data argument is a dict which may contain any useful data for listeners.
"""
    if isinstance(type, int) is False:
        raise RuntimeError("Event type parameter has to be integer.")
    global eventQueue
    
    eventQueue.put({"type": type, "data": data, "target": target})


def dispatch(event):
    """Dispatches incoming event to listeners that implement the appropriate method."""
    global eventNames
    global eventListeners

    script = "event_%s" % eventNames.get(event.get("type", 'unknown'), None)
    willScript = "event_will_%s" % eventNames.get(event.get("type", 'unknown'), None)
    didScript = "event_did_%s" % eventNames.get(event.get("type", 'unknown'), None)
    target = event.get("target", None)
    targets = []
    if target is not None:
        target.append(target)
    else:
        targets.extend(eventListeners)
    for listener in targets:
        method = getattr(listener, script, None)
        willMethod = getattr(listener, willScript, None)
        didMethod = getattr(listener, didScript, None)
        if willMethod:
            try:
                willMethod(event.get('data', None))
            except:
                logger.exception("eventManager", "Failed to execute {name}.{script}({event}): {exception}".format(name=listener.__class__.__name__, script=willScript, event=event, exception=e), e)
                pass
        
        if method:
            try:
                method(event.get('data', None))
            except Exception as e:
                logger.exception("eventManager", "Failed to execute {name}.{script}({event}): {exception}".format(name=listener.__class__.__name__, script=script, event=event, exception=e), e)
                continue
        if didMethod:
            try:
                didMethod(event.get('data', None))
            except:
                logger.exception("eventManager", "Failed to execute {name}.{script}({event}): {exception}".format(name=listener.__class__.__name__, script=script, event=event, exception=e), e)
