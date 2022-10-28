from pprint import pprint

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard

import requests
from random import randint

TOKEN = '4fb3cca045f1205be1886f039ab833b1062b789832cdda5baf8a341780aefcbc5714153fc922d3ae4597f'
GROUP_ID = '206835749'


def main():
    ID_ASKED = False
    vk_session = vk_api.VkApi(
        token=TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    start_keyboard = VkKeyboard(inline=True)
    start_keyboard.add_callback_button('О игроке', payload={'type': 'about_player'})
    start_keyboard.add_callback_button('О матче(soon)', payload={'type': 'about_match'})
    start_keyboard.add_line()
    start_keyboard.add_callback_button('О персонаже(soon)', payload={'type': 'about_hero'})
    start_keyboard.add_callback_button('О предмете(soon)', payload={'type': 'about_item'})

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if not ID_ASKED:
                vk.messages.send(
                    user_id=event.obj.message['from_id'],
                    message='О чём вы хотите получить информацию?',
                    random_id=randint(0, (2 ** 64)),
                    keyboard=start_keyboard.get_keyboard()
                )
            else:
                account_id = event.obj.message['text']
                if len(account_id) == 10 and account_id.isdigit():
                    response = requests.get(f'https://api.opendota.com/api/players/{account_id}')
                    ID_ASKED = False

                    about_account_keyboard = VkKeyboard(inline=True)
                    about_account_keyboard.add_callback_button('Статистика за последнюю игру',
                                                               payload={'type': 'last_game_stat'})
                    about_account_keyboard.add_line()
                    about_account_keyboard.add_callback_button('Статистика за последние 20 игр(soon)',
                                                               payload={'type': 'last_20_game_stat'})

                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        message='Что из этого вам интересно?',
                        random_id=randint(0, (2 ** 64)),
                        keyboard=about_account_keyboard.get_keyboard()
                    )

                else:
                    vk.messages.send(
                        user_id=event.obj.message.text,
                        message='Account ID неверный\nПопробуйте ещё раз:',
                        random_id=randint(0, (2 ** 64))
                    )

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            if event.obj.payload['type'] == 'about_player':
                ID_ASKED = True
                vk.messages.send(
                    user_id=event.obj.user_id,
                    message='Введите Account ID:',
                    random_id=randint(0, (2 ** 64))
                )
            elif event.obj.payload['type'] == 'last_game_stat':

                last_game_stat_keyboard = VkKeyboard(inline=True)
                last_game_stat_keyboard.add_callback_button('K/D/A в последней игре(soon)',
                                                            payload={'type': 'kda_last_game'})
                last_game_stat_keyboard.add_callback_button('Нетворс', payload={'type': 'net_worth_last_game'})
                last_game_stat_keyboard.add_line()
                last_game_stat_keyboard.add_callback_button('Урон героям(soon)',
                                                            payload={'type': 'hero_damage_last_game'})
                last_game_stat_keyboard.add_callback_button('Крипов добито(soon)', payload={'type': 'creeps_kill'})

                vk.messages.send(
                    user_id=event.obj.user_id,
                    message='Выбирайте:',
                    random_id=randint(0, (2 ** 64)),
                    keyboard=last_game_stat_keyboard.get_keyboard()
                )
            elif event.obj.payload['type'] == 'net_worth_last_game':
                id_match = requests.get(f'https://api.opendota.com/api/players/'
                                        f'{account_id}/matches').json()[0]['match_id']
                info_about_match = requests.get(f'https://api.opendota.com/api/matches/{id_match}')
                for i in info_about_match.json()['players']:
                    print(i)
                    if i['account_id'] == account_id:
                        print(i['net_worth'])


if __name__ == '__main__':
    main()
