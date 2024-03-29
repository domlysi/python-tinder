from core.lib import TinderBot
import configparser
config = configparser.ConfigParser()
config.sections()

if __name__ == '__main__':
    config.read('config.ini')
    default_config = config['DEFAULT']

    bot = TinderBot(x_auth_token=default_config['Token'], messages_file='__messages.txt')
    # bot.message_starter()
    bot.random_like(is_message_starter=False, wait_after_match_in_s=3*60*60)
