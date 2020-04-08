from core.lib import TinderBot
import configparser
config = configparser.ConfigParser()
config.sections()

if __name__ == '__main__':
    config.read('config.ini')
    default_config = config['DEFAULT']

    bot = TinderBot(x_auth_token=default_config['Token'])
    bot.random_like()
