# подключаем модуль для работы с VK
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, sys
import config
import colorama # цветной текст в консоли
colorama.init()


##################### AUTH #######################
try: # пробуем подключиться
	vk_session = vk_api.VkApi(token = config.USER_TOKEN)
	longpoll = VkLongPoll(vk_session)
	vk_user = vk_session.get_api()
except: # если получаем ошибку завершаем работу
	print(colorama.Fore.RED + '\n[*]Ошибка при соединении администратора группы с VK AI')
	sys.exit()

##################################################

def accept(vk_group, event, first_name, last_name, ID):
	global vk_user
	try:
		vk_user.groups.approveRequest(group_id = config.ID_GROUP, user_id = event.obj.user_id) # принимаем заявку от имени администратора
	except Exception as error:
		pass
		
	try:
		vk_group.messages.send(peer_id = config.PEER_ID_CHAT, random_id = 0, message = f'Принял заявку в группу от [id{ID}|{first_name} {last_name}] <&#2;3')
	except:
		pass