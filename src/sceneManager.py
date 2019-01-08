# *-* coding: utf8 *-*

import os, re

import pygame

import logger
import audio
import inputHandler
import eventManager
import speech

from scene import *

# scene types map from string to real objects.
_sceneTypesMap = {
    "menu": MenuScene,
    "storytext": StoryTextScene
}

# Global scene manager instance
_instance = None

class SceneManager(object):
    scenes = {}
    intervalScenes = []
    activeScene = None

    def __init__(self, gameConfig):
        eventManager.addListener(self)

    def getLogName(self):
        return 'SceneManager'

    def createScene(self, config):
        global _sceneTypesMap
        
        type = config.get("type", None)
        name = config.get("name", None)
        cls = _sceneTypesMap.get(type, None)
        if cls is None:
            raise RuntimeError("Scene type {type} is not known.".format(type=type))
        if issubclass(cls, Scene) is False:
            raise RuntimeError("Scene type {type} is not a valid scene type ({realType})".format(type=type, realType=cls.__name__))
        try:
            obj = cls(name, config)
        except Exception as e:
            logger.error(self, "Error instanciating scene {name}: {exception}.".format(name=name, exception=e))
            return None
        return obj
    
    def addScene(self, name, obj):
        if name is None or name == "" or obj is None or isinstance(obj, Scene) is False:
            raise RuntimeError("Invalid argument")
        self.scenes[name] = obj

    def load(self, sceneName, silentEntering=False, silentLeaving=False):
        s = self.scenes.get(sceneName, None)
        if s is None:
            logger.error(self, "Scene {name} not found".format(name=sceneName))
            return False
        if self.activeScene is not None:
            self.activeScene.deactivate(silentLeaving)
            eventManager.post(eventManager.LEAVE_SCENE, {"scene": self.activeScene})
        self.activeScene = s
        s.activate(silentEntering)

    def leave(self, silentLeaving=False):
        if self.activeScene is not None:
            nextScene = self.activeScene.getNextScene()
            if nextScene is None:
                return
            if nextScene == '__quit':
                eventManager.post(eventManager.QUIT_GAME)
            else:
                if self.load(nextScene) is False:
                    speech.speak("scene {name} not created yet.".format(name=nextScene))
            
    def getActiveScene(self):
        return self.activeScene


    # events

    def event_leave_scene(self, event):
        if self.activeScene is None:
            eventManager.post(eventManager.QUIT_GAME)


    def event_quit_game(self, event):
        for key in self.scenes:
            self.execute('event_quit_game')
        self.scenes = {}
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def event_pause_game(self, event):
        self.execute('event_pause_game', event.data)

    def event_leave_current_scene(self, event):
        self.leave()

    def event_scene_interval_activate(self, event):
        scene = event.get('scene', None)
        if scene is None:
            raise RuntimeError("Invalid call to event_scene_interval_activate without a target scene.")
        scene._nextTick = pygame.time.get_ticks() + scene._interval
        self.intervalScenes.append(scene)

    def event_scene_interval_deactivate(self, event):
        scene = event.get('scene', None)
        if scene is None:
            raise RuntimeError("Invalid call to event_scene_interval_activate without a target scene.")
        idx = 0
        for x in self.intervalScenes:
            if x.name == scene.name:
                self.intervalScenes.pop(idx)
                return
            idx += 1
        logger.error(self, "Failed to remove scene from interval scenes: {name}: {exception}".format(name=scene.name, exception=e))

    def event_scene_interval_tick(self, evt):
        now = evt.get('time', 0)
        for x in self.intervalScenes:
            if x._nextTick <= now:
                try:
                    x.event_interval()
                except Exception as e:
                    logger.error(self, "Failed to execute {cls}.event_interval: {exception}".format(cls=x.__class__.__name__, exception=e))
                x._nextTick = now + x._interval
                
    def execute(self, script, data=None):
        if self.activeScene:
            method = getattr(self.activeScene, script, None)
            if method:
                try:
                    method(data)
                except Exception as e:
                    logger.error(self, "Failed to execute {name}.{script}: {exception}".format(name=self.activeScene.__class__.__name__, script=script, exception=e))


def initialize(gameConfig):
    global _instance

    if _instance is None:
        try:
            _instance = SceneManager(gameConfig)
        except Exception as e:
            logger.error("sceneManager", "Failed to initialize scene manager: {exception}".format(exception=e))
            return False

    # Load all scenes fresent within the scene directory
    totalScenes = 0
    loadedScenes = 0
    # load Python-created scenes
    
    try:
        dir = os.scandir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes"))
    except Exception as e:
        logger.error(_instance, "Failed to load secenes: {exception}".format(exception=e))
        return False
    for entry in dir:
        m = re.match("(^[^#]*.*)\.py$", entry.name)
        if m is not None and entry.name != 'scene.py':
            logger.info(_instance, "Loading scene {name}".format(name=m.group(1)))
            totalScenes += 1
            try:
                obj = __import__("scenes.%s" % m.group(1), globals(), locals(), ("scenes")).Scene(m.group(1), gameConfig.getSceneConfiguration(m.group(1)))
                if obj is not None:
                    _instance.addScene(m.group(1), obj)
                    loadedScenes += 1
            except Exception as e:
                logger.error(_instance, "Failed to instanciate scene {name}: {exception}".format(name=m.group(1), exception=ee))

    # Load JSON-created scenes
    try:
        dir = os.scandir(os.path.join(os.path.abspath("."), "data", "scenes"))
    except Exception as e:
        logger.warning(self, "No user-defined scenes found.")
    if dir is not None:
        for entry in dir:
            m = re.match("(^[^#]*.*)\.json$", entry.name)
            if m is not None:
                jsonConfig = gameConfig.loadSceneConfiguration(entry.name)
                totalScenes += 1
                if jsonConfig is not None:
                    try:
                        obj = _instance.createScene(jsonConfig)
                    except Exception as e:
                        logger.error(_instance, "Failed to create scene {file}: {exception}".format(file=entry.name, exception=e))
                        continue
                    if obj is not None:
                        _instance.addScene(obj.name, obj)
                        loadedScenes += 1
                    
        
    if totalScenes > loadedScenes:
        logger.error(_instance, "{count} scenes failed to load".format(count=totalScenes - loadedScenes))
        print("{count} scenes failed to load".format(count=totalScenes - loadedScenes))
        return False
    logger.info(_instance, "Loaded {count} scenes".format(count=loadedScenes))
    return True

def onKeyDown(key, mods):
    global _instance
    
    activeScene = _instance.getActiveScene()
    if activeScene is None:
        return
    activeScene.onKeyDown(key, mods)

def onKeyUp(key, mods):
    global _instance

    activeScene = _instance.getActiveScene()
    if activeScene is None:
        return
    activeScene.onKeyUp(key, mods)

def loadScene(name):
    global _instance

    return _instance.load(name)

def leaveCurrentScene():
    global _instance

    _instance.leave()
