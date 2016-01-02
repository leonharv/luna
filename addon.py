import xbmc
import xbmcgui

from xbmcswift2 import Plugin, xbmcaddon

from resources.lib.core.corefunctions import Core, Logger
from resources.lib.controller.configcontroller import ConfigController
from resources.lib.controller.gamecontroller import GameController
from resources.lib.core.coremonitor import CoreMonitor
from resources.lib.di.featurebroker import features
from resources.lib.di.requiredfeature import RequiredFeature
from resources.lib.scraper.scraperchain import ScraperChain
from resources.lib.util.confighelper import ConfigHelper
from resources.lib.util.moonlighthelper import MoonlightHelper

from resources.lib.views.gameinfo import GameInfo

plugin = Plugin()

addon_path = plugin.storage_path
addon_internal_path = xbmcaddon.Addon().getAddonInfo('path')


@plugin.route('/')
def index():
    items = [
        {
            'label': 'Games',
            'thumbnail': addon_internal_path + '/resources/icons/controller.png',
            'path': plugin.url_for(
                    endpoint='show_games'
            )
        }, {
            'label': 'Settings',
            'thumbnail': addon_internal_path + '/resources/icons/cog.png',
            'path': plugin.url_for(
                    endpoint='open_settings'
            )
        }
    ]

    return plugin.finish(items)


@plugin.route('/settings')
def open_settings():
    plugin.open_settings()
    core_monitor.onSettingsChanged()


@plugin.route('/actions/create-mapping')
def create_mapping():
    config_controller.create_controller_mapping()


@plugin.route('/actions/pair-host')
def pair_host():
    config_controller.pair_host()


@plugin.route('/actions/reset-cache')
def reset_cache():
    confirmed = xbmcgui.Dialog().yesno(
            core.string('name'),
            core.string('reset_cache_warning')
    )

    if confirmed:
        scraper_chain.reset_cache()
    else:
        return


@plugin.route('/games')
def show_games():
    plugin.set_content('movies')
    return plugin.finish(game_controller.get_games_as_list(), sort_methods=['label'])


@plugin.route('/games/refresh')
def do_full_refresh():
    game_controller.get_games()


@plugin.route('/games/info/<game_id>')
def show_game_info(game_id):
    game = core.get_storage().get(game_id)
    cache_fanart = game.get_selected_fanart()
    cache_poster = game.get_selected_poster()
    window = GameInfo(game, game.name)
    window.doModal()
    del window
    if cache_fanart != game.get_selected_fanart() or cache_poster != game.get_selected_poster():
        xbmc.executebuiltin('Container.Refresh')


@plugin.route('/games/launch/<game_id>')
def launch_game(game_id):
    core.logger.info('Launching game %s' % game_id)
    game_controller.launch_game(game_id)


if __name__ == '__main__':
    features.provide('plugin', Plugin('script.luna'))
    features.provide('logger', Logger)
    features.provide('core', Core)
    features.provide('moonlight-helper', MoonlightHelper)
    features.provide('scraper-chain', ScraperChain)
    features.provide('config-helper', ConfigHelper)
    features.provide('config-controller', ConfigController)
    features.provide('game-controller', GameController)
    features.provide('core-monitor', CoreMonitor)

    core = RequiredFeature('core')
    config_helper = RequiredFeature('config_helper')
    scraper_chain = RequiredFeature('scraper-chain')
    core_monitor = RequiredFeature('core-monitor')
    game_controller = RequiredFeature('game-controller')
    config_controller = RequiredFeature('config-controller')

    if plugin.get_setting('host', unicode):
        config_helper.configure()
        plugin.run()
    else:
        xbmcgui.Dialog().ok(
                core.string('name'),
                core.string('configure_first')
        )
