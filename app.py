from client import Api, User
import asyncio


group_id = 123
group_token = 'token' 
user_token = 'token' # kate mobile token


async def main():
	longpoll = Api(token=group_token, group_id=group_id,)
	user = User(token=user_token, group_id=group_id,)

	async with longpoll as api:
		async for event in api.listen():
			await user.approve_request(event['user_id'])

asyncio.run(main())