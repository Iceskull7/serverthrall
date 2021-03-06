from .exceptions import UnloadPluginException
import logging
import time


class Thrall(object):

    def __init__(self, steamcmd, config, conan_config, plugins, server):
        self.steamcmd = steamcmd
        self.config = config
        self.conan_config = conan_config
        self.plugins = plugins
        self.server = server
        self.logger = logging.getLogger('serverthrall')

    def get_plugin(self, type):
        for plugin in self.plugins:
            if isinstance(plugin, type):
                return plugin
        return None

    def stop(self):
        self.logger.info('Stopping ServerThrall')

    def start(self):
        if not self.server.is_running():
            self.server.start()
            self.conan_config.refresh()

        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin.ready(self.server, self.steamcmd, self)
                except UnloadPluginException:
                    self.plugins.remove(plugin)
                    plugin.unload()
                except Exception:
                    self.logger.exception('Unloading %s plugin after error ' % plugin.name)
                    self.plugins.remove(plugin)
                    plugin.unload()

        while True:
            for plugin in self.plugins:
                if not plugin.enabled:
                    continue

                try:
                    plugin.tick()
                except UnloadPluginException:
                    self.plugins.remove(plugin)
                    plugin.unload()
                except Exception:
                    self.logger.exception('Unloading %s plugin after error ' % plugin.name)
                    self.plugins.remove(plugin)
                    plugin.unload()

            self.config.save_if_queued()
            time.sleep(0.16)
