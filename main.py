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

TOKEN = 'efff9bed96234bacd266f20f057533d3fe293fc498f5f7e4f3d1217eb70bb51a693b464a0cf4f63f3a5bd'


###'https://api.vk.com/method/________' обращение к методам апи вк


class VkUser:
    friends = []
    groups = []
    id = None
    def __init__(self, id):
        self.id = id
        self.user = {
            'access_token': TOKEN,
            'user_ids': self.id,
            'v': 5.124

        }
        response_user = requests.get('https://api.vk.com/method/users.get?', urlencode(self.user))
        user_info = response_user.json()
        self.first_name = user_info['response'][0]['first_name']
        self.last_name = user_info['response'][0]['last_name']
        # pprint(user_info)
        # print(self.first_name, self.last_name)
        try:
            self.id = response_user.json()['response'][0]['id']
        except KeyError:
            self.id = None
        else:
            self.get_friends()
            self.get_groups()

    def get_friends(self):
        response_friends = requests.get('https://api.vk.com/method/friends.get?', urlencode(self.user))
        self.friends = response_friends.json()['response']['items']
        # pprint(self.friends)

    def get_groups(self):
        response_groups = requests.get('https://api.vk.com/method/groups.get?', urlencode(self.user))
        self.groups = response_groups.json()['response']['items']
        # pprint(self.groups)

# user1= VkUser(17460386)
# # user1.get_friends()
# user1.get_groups()

class VkGroup:
    gid = None
    name = ''
    count = 0
    members = []
    friends = []
    groups = []

    def __init__(self, gid):
        self.gid = gid

        self.group = {
            'access_token': TOKEN,
            'group_id': self.gid,
            'v': 5.103
        }
        # self.get_members()

    def get_members(self):
        response = requests.get('https://api.vk.com/method/groups.getMembers', urlencode(self.group))
        self.members = response.json()['response']['items']
        # pprint(self.members)
        self.count = response.json()['response']['count']
        # pprint(self.count)

    def get_group_name(self):
        response = requests.get('https://api.vk.com/method/groups.getById', urlencode(self.group))
        self.name = response.json()['response'][0]['name']
        # pprint(self.name)


# group = VkGroup(113682799)
# group.get_group_name()
# group.get_members()

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
        group_vk = VkGroup(gid)
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

