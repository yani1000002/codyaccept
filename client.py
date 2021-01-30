from httpx import AsyncClient
from typing import Optional, Union

from json.decoder import JSONDecodeError
import asyncio


class Api:
    def __init__(self, token: Union[str] = None,
                 group_id: Union[str, int] = None, v: Union[int, str] = '5.126',
                 wait: Union[int] = 25) -> None:

        if not token or not group_id:
            return False

        self.token, self.group_id = token, group_id
        self.wait = wait
        self.client = AsyncClient(
            base_url="https://api.vk.com/method/", params={'access_token': token, 'v': v})

        self.key, self.server, self.ts = None, None, None
        self.last_event_hash = None

    async def _update_longpoll_server(self, update_ts: Union[bool] = True) -> Optional[dict]:
        async with self.client as client:
            data = {
                'group_id': self.group_id
            }

            response = (await self._get_json_or_panic(await client.post('groups.getLongPollServer', params=data)))['response']
            self.key, self.server = response['key'], response['server']

            if update_ts:
                self.ts = response['ts']

    async def _set_longpoll_settings(self, params: Union[dict]) -> None:
        async with self.client as client:
            data = {**params, 'group_id': self.group_id}

            response = await self._get_json_or_panic(await client.post('groups.setLongPollSettings', params=data))
            return response

    async def _check(self) -> Optional[list]:
        values = {'act': 'a_check', 'key': self.key,
                  'ts': self.ts, 'wait': self.wait}

        async with self.client as client:
            response = (await self._get_json_or_panic(await client.post(url=self.server,
                                                                        params=values,
                                                                        timeout=self.wait + 10)))
            if 'failed' not in response:
                self.ts = response['ts']
                return [response]

            elif response['failed'] == 1:
                self.ts = response['ts']

            elif response['failed'] == 2:
                await self._update_longpoll_server(update_ts=False)

            elif response['failed'] == 3:
                await self._update_longpoll_server()

            else:
                return []

    async def listen(self) -> Optional[list]:
        while True:
            for event in await self._check():
                yield event['updates'][0]['object']

    async def _get_json_or_panic(self, response: Union[dict]) -> Union[dict]:
        try:
            return response.json()
        except JSONDecodeError:
            return print(
                f"{response.status_code}: {response.url.path}: {response.content}",
            )

    async def __aenter__(self) -> 'api':
        await self._set_longpoll_settings({'group_join': 1})
        await self._update_longpoll_server()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass


class User(Api):
    def __init__(self, token: Union[str] = None, group_id: Union[str, int] = None) -> None:
        if not token or not group_id:
            return False

        self.group_id = group_id

        self.client = AsyncClient(
            base_url="https://api.vk.com/method/", params={'access_token': token, 'v': '5.126'})

    async def approve_request(self, user_id: Union[str, int]) -> None:

        async with self.client as client:
            params = {
                'group_id': self.group_id,
                'user_id': user_id
            }

            return await self._get_json_or_panic(await client.post('groups.approveRequest', params=params))
