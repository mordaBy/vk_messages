# coding: utf-8

# TODO: Store user_id in list
# TODO: Hold timeout vk api exception ???

import configparser as cp
import vk
from time import sleep
import datetime

config = cp.ConfigParser()
config.read("config.txt")
user_login = config.get('credentials', 'login')
user_password = config.get('credentials', 'password')
session = vk.AuthSession(app_id='4409067', user_login=user_login, user_password=user_password, scope="messages")
api = vk.API(session, v='5.62', lang='ru', timeout=10)


def do_fwd(forwarded, iter_count=1):
    sleep(1 / 3)
    iter_count += 1
    # TODO: move to function
    fwd_ids = set()
    for fwd in forwarded:
        fwd_ids.add(fwd['user_id'])
    fwd_users = api.users.get(user_ids=fwd_ids)

    # It creates dictionary, that stores values in id: (first_name + last_name) pair
    users = {}
    for user in fwd_users:
        users[user['id']] = " ".join([user['first_name'], user['last_name']])

    for fwd in forwarded:
        if fwd['body']:
            print('%s %s: %s' % ('-' * iter_count, users[fwd['user_id']], fwd['body']))
        if 'fwd_messages' in fwd:
            do_fwd(fwd['fwd_messages'], iter_count)


my_user = api.users.get()
my_user_id = my_user[0]['id']
my_user_name = my_user[0]['first_name'] + ' ' + my_user[0]['last_name']

dialogs = api.execute.getNamedDialogs()
for idx, dialog in enumerate(dialogs):
    print("[%2d] %s %s Message: %s " % (idx + 1,
                                        dialog['first_name'],
                                        dialog['last_name'],
                                        dialog['body']))

user_n = int(input("Enter the dialog number: ")) - 1
user_id = dialogs[user_n]['user_id']
user_name = " ".join([dialogs[user_n]['first_name'] + ' ' + dialogs[user_n]['last_name']])

mes_offset = 0
mes_count = api.messages.getHistory(user_id=user_id, count=0)['count']
while mes_offset <= mes_count:
    history = api.messages.getHistory(user_id=user_id, count=200, offset=mes_offset)['items']
    for message in history:
        print("[%s] " % (datetime.datetime.fromtimestamp(message['date'])).strftime('%Y-%m-%d %H:%M:%S'), end='')
        if message['from_id'] == my_user_id:
            print('%s: %s' % (my_user_name, message['body']))
        else:
            print('%s: %s' % (user_name, message['body']))
        if 'attachments' in message:
            for att in message['attachments']:
                if att['type'] == 'sticker':
                    print('Attachment sticker: %d' % att['sticker']['product_id'])
                if att['type'] == 'photo':
                    print('Attachment photo: ')
                    for key in att['photo']:
                        if 'photo' in key:
                            print(key, att['photo'][key])

        if 'fwd_messages' in message:
            print("Forwarded messages:")
            do_fwd(message['fwd_messages'])

    sleep(0.25)
    mes_offset += 200
