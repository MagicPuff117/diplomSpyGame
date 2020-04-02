import json
from urllib.parse import urlencode
from pprint import pprint
import requests
import time

OAUTH_URL = 'https://oauth.vk.com/authorize'
OAUTH_PARAMS = {
    'client_id': 7279354,
    # 'redirect_uri':
    'display': 'popup',
    'scope': 'friends',
    'response_type': 'token'
}

# print('?'.join((OAUTH_URL, urlencode(OAUTH_PARAMS))))

TOKEN = '984e9baae14ba40cf49ac5494837330ff8a43f3b84ba1f305b4e13493fd641819cfc7072123d5db31'


###'https://api.vk.com/method/users.get?' обращение к апи вк


class VkUser:

    def __init__(self, id):
        self.id = id
        friends = []
        groups = []
        self.user = {
            'access_token': TOKEN,
            'user_ids': self.id,
            'v': 5.89

        }
        response_user = requests.get('https://api.vk.com/method/users.get?', urlencode(self.user))
        user_info = response_user.json()
        self.first_name = user_info['response'][0]['first_name']
        self.last_name = user_info['response'][0]['last_name']
        # pprint(user_info)
        print(self.first_name, self.last_name)

    def get_friends(self):
        response_friends = requests.get('https://api.vk.com/method/friends.get?', urlencode(self.user))
        self.friends = response_friends.json()['response']['items']
        # pprint(self.friends)

    def get_groups(self):
        response_groups = requests.get('https://api.vk.com/method/groups.get?', urlencode(self.user))
        self.groups = response_groups.json()['response']['items']
        # pprint(self.get_groups())


class GroupVk(object):
    gid = None
    name = ''
    count = 0
    members = []
    access_token = TOKEN
    version_api = '5.8'

    def __init__(self, gid):
        self.gid = gid
        self.get_members()

    def get_members(self):
        response = requests.get('https://api.vk.com/method/groups.getMembers', {
            'group_id': self.gid,
            'access_token': self.access_token,
            'v': self.version_api
        })
        self.members = response.json()['response']['users']
        self.count = response.json()['response']['count']

    def get_group_name(self):
        response = requests.get('https://api.vk.com/method/groups.getById', {
            'group_ids': self.gid,
            'access_token': self.access_token,
            'v': self.version_api
        })
        self.name = response.json()['response'][0]['name']


def get_user():
    while True:
        user_name = input('Введите короткое имя или id пользователя ВКонтакте: ')
        user_vk = VkUser(user_name)
        if user_vk.id:
            if user_vk.friends and user_vk.groups:
                break
            else:
                if not user_vk.friends:
                    print('У пользователя нет друзей')
                if not user_vk.groups:
                    print('Пользователь не состоит в группах')
        else:
            print('Произошла ошибка, скорее всего ВКонтакте не знает пользователя с таким именем')
    print('Данные пользователя ВК получены')
    return user_vk


def check_groups_for_friends(user_vk):
    group_count = len(user_vk.groups)
    print('Количество групп в которых состоит пользователь: {}'.format(group_count))
    print('Проверяем группы пользователя на друзей:')
    private_groups = []
    friends = set(user_vk.friends)
    for index, gid in enumerate(user_vk.groups):
        group_vk = GroupVk(gid)
        time.sleep(0.34)
        if friends.isdisjoint(group_vk.members):
            group_vk.get_group_name()
            time.sleep(0.34)
            private_groups.append(group_vk)
        percent_done = int((index + 1) / group_count * 100)
        print('\r{}%'.format(percent_done), end='')
    print('')
    return private_groups


def save_result(private_groups):
    result = []
    for group in private_groups:
        result.append({
            'name': group.name,
            'gid': group.gid,
            'members_count': group.count
        })
    with open('groups.json', 'w') as f:
        json.dump(result, f)
    print('Результаты поиска записаны в файл')


def main():
    user_vk = get_user()
    private_groups = check_groups_for_friends(user_vk)
    if private_groups:
        print('Найдено секретных групп: {}'.format(len(private_groups)))
        save_result(private_groups)
    else:
        print('У пользователя нет секретов от друзей')


if __name__ == '__main__':
    main()

