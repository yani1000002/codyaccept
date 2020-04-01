# подключаем модуль для работы с VK
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
import vk_api, sys
from bs4 import BeautifulSoup as bs
import requests
import config, user_acceptance
import colorama # цветной текст в консоли
colorama.init()

#--------------------- ANTI TIMEOUT -----------------------
class VkBotLongPoll(VkBotLongPoll):
	def listen(self):
		while True:
			try:
				for event in self.check():
					yield event
			except Exception as e:
				pass

#--------------- CONNECT ---------------------------
print(colorama.Fore.CYAN + '***************\n\n[*]Соеденение с сервером VK API..')

try: # пробуем подключиться
	vk_session = vk_api.VkApi(token = config.TOKEN_GROUP)
	print(colorama.Fore.CYAN + '[*]Отправка данных для подключения..')
	longpoll = VkBotLongPoll(vk_session, config.ID_GROUP)
	vk_group = vk_session.get_api()
	print(colorama.Fore.CYAN + '[*]Сессия создана')
	print(colorama.Fore.CYAN + '[*]Успешной подключение!\n\n***************')
except: # если получаем ошибку завершаем работу
	print(colorama.Fore.RED + '\n[*]Ошибка соединения с API VK')
	sys.exit()
#--------------------------------------------------

print(colorama.Fore.BLUE + '\nПрослушиваю сервер на заявки в группу\n')
for event in longpoll.listen(): # получаем события
    if event.type == VkBotEventType.GROUP_JOIN:
        first_name = vk_group.users.get(user_ids = event.obj.user_id, name_case = 'gen')[0]['first_name'] # сохраняем имя
        last_name = vk_group.users.get(user_ids = event.obj.user_id, name_case = 'gen')[0]['last_name'] # сохраняем фамилию
        user_acceptance.accept(vk_group, event, first_name, last_name, event.obj.user_id) # отправляем запрос на принятий в другой файл
