import asyncio
import os
import json
import traceback
import aiohttp
import aiofiles
import random
import time as tm

from datetime import datetime, timezone
from datetime import datetime, timedelta
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from typing import Tuple, Dict, Any
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView
from pyrogram.raw.types import InputBotAppShortName
from urllib.parse import unquote, parse_qs

from bot.config import settings
from bot.core.agents import generate_random_user_agent
from bot.utils.logger import logger
from bot.exceptions import InvalidSession
from bot.utils.connection_manager import connection_manager
from .headers import headers


class Tapper:
    def __init__(self, tg_client: Client, proxy: str):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.proxy = proxy

        self.user_agents_dir = "user_agents"
        self.session_ug_dict = {}
        self.headers = headers.copy()

    async def init(self):
        os.makedirs(self.user_agents_dir, exist_ok=True)
        await self.load_user_agents()
        user_agent, sec_ch_ua = await self.check_user_agent()
        self.headers['User-Agent'] = user_agent
        self.headers['Sec-Ch-Ua'] = sec_ch_ua

    async def generate_random_user_agent(self):
        user_agent, sec_ch_ua = generate_random_user_agent(device_type='android', browser_type='webview')
        return user_agent, sec_ch_ua

    async def load_user_agents(self) -> None:
        try:
            os.makedirs(self.user_agents_dir, exist_ok=True)
            filename = f"{self.session_name}.json"
            file_path = os.path.join(self.user_agents_dir, filename)

            if not os.path.exists(file_path):
                logger.info(f"{self.session_name} | User agent file not found. A new one will be created when needed.")
                return

            try:
                async with aiofiles.open(file_path, 'r') as user_agent_file:
                    content = await user_agent_file.read()
                    if not content.strip():
                        logger.warning(f"{self.session_name} | User agent file '{filename}' is empty.")
                        return

                    data = json.loads(content)
                    if data['session_name'] != self.session_name:
                        logger.warning(f"{self.session_name} | Session name mismatch in file '{filename}'.")
                        return

                    self.session_ug_dict = {self.session_name: data}
            except json.JSONDecodeError:
                logger.warning(f"{self.session_name} | Invalid JSON in user agent file: {filename}")
            except Exception as e:
                logger.error(f"{self.session_name} | Error reading user agent file {filename}: {e}")
        except Exception as e:
            logger.error(f"{self.session_name} | Error loading user agents: {e}")

    async def save_user_agent(self) -> Tuple[str, str]:
        user_agent_str, sec_ch_ua = await self.generate_random_user_agent()

        new_session_data = {
            'session_name': self.session_name,
            'user_agent': user_agent_str,
            'sec_ch_ua': sec_ch_ua
        }

        file_path = os.path.join(self.user_agents_dir, f"{self.session_name}.json")
        try:
            async with aiofiles.open(file_path, 'w') as user_agent_file:
                await user_agent_file.write(json.dumps(new_session_data, indent=4, ensure_ascii=False))
        except Exception as e:
            logger.error(f"{self.session_name} | Error saving user agent data: {e}")

        self.session_ug_dict = {self.session_name: new_session_data}

        logger.info(f"{self.session_name} | User agent saved successfully: {user_agent_str}")

        return user_agent_str, sec_ch_ua

    async def check_user_agent(self) -> Tuple[str, str]:
        if self.session_name not in self.session_ug_dict:
            return await self.save_user_agent()

        session_data = self.session_ug_dict[self.session_name]
        if 'user_agent' not in session_data or 'sec_ch_ua' not in session_data:
            return await self.save_user_agent()

        return session_data['user_agent'], session_data['sec_ch_ua']

    async def check_proxy(self, http_client: aiohttp.ClientSession) -> bool:
        try:
            response = await http_client.get(url='https://ipinfo.io/json', timeout=aiohttp.ClientTimeout(total=5))
            data = await response.json()

            ip = data.get('ip')
            city = data.get('city')
            country = data.get('country')

            logger.info(
                f"{self.session_name} | Check proxy! Country: <cyan>{country}</cyan> | City: <light-yellow>{city}</light-yellow> | Proxy IP: {ip}")

            return True

        except Exception as error:
            logger.error(f"{self.session_name} | Proxy error: {error}")
            return False

    async def get_tg_web_data(self) -> str:
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('TimeFarmCryptoBot'),
                bot=await self.tg_client.resolve_peer('TimeFarmCryptoBot'),
                platform='android',
                from_bot_menu=False,
                url='https://tg-tap-miniapp.laborx.io/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def login(self, http_client: aiohttp.ClientSession, tg_web_data: dict[str]) -> dict[str]:
        try:
            response = await http_client.post(url='https://tg-bot-tap.laborx.io/api/v1/auth/validate-init/v2', data={"initData":tg_web_data,"platform":"android"})
            response.raise_for_status()

            response_json = await response.json()

            json_data = {
                'token': response_json['token'],
                'level': response_json['info']['level'],
                'levelDescriptions': response_json['levelDescriptions']
            }

            return json_data

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting Access Token: {error}")
            await asyncio.sleep(delay=3)

    async def get_mining_data(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            response = await http_client.get('https://tg-bot-tap.laborx.io/api/v1/farming/info')
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Profile Data: {error}")
            await asyncio.sleep(delay=3)

    async def get_tasks_list(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            response = await http_client.get('https://tg-bot-tap.laborx.io/api/v1/tasks')
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Tasks Data: {error}")
            await asyncio.sleep(delay=3)

    async def get_task_data(self, http_client: aiohttp.ClientSession, task_id: str) -> dict[str]:
        try:
            response = await http_client.get(f'https://tg-bot-tap.laborx.io/api/v1/tasks/{task_id}')
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Task Data: {error}")
            await asyncio.sleep(delay=3)

    async def upgrade_level(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            response = await http_client.post(url=f'https://tg-bot-tap.laborx.io/api/v1/me/level/upgrade', json={})
            response.raise_for_status()

            response_json = await response.json()

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while Upgrade Level: {error}")
            await asyncio.sleep(delay=3)

    async def task_claim(self, http_client: aiohttp.ClientSession, task_id: str) -> str:
        try:
            response = await http_client.post(url=f'https://tg-bot-tap.laborx.io/api/v1/tasks/{task_id}/claims', json={})
            response.raise_for_status()

            return response.text

        except Exception as error:
            #logger.error(f"{self.session_name} | Unknown error while claim task: {error}")
            await asyncio.sleep(delay=3)

    async def task_submiss(self, http_client: aiohttp.ClientSession, task_id: str) -> str:
        try:
            response = await http_client.post(url=f'https://tg-bot-tap.laborx.io/api/v1/tasks/{task_id}/submissions', json={})
            response.raise_for_status()

            return response.text

        except Exception as error:
            #logger.error(f"{self.session_name} | Unknown error while submissions task: {error}")
            await asyncio.sleep(delay=3)

    async def start_mine(self, http_client: aiohttp.ClientSession) -> dict[str, bool | int] | dict[str, bool | Any]:
        try:
            response = await http_client.post('https://tg-bot-tap.laborx.io/api/v1/farming/start', json={})
            response.raise_for_status()

            if response.status == 200:
                return {
                    'ok': True,
                    'code': 200
                }

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when start miner: {error}")
            await asyncio.sleep(delay=3)

            return {
                    'ok': True,
                    'code': response.status
                }

    async def finish_mine(self, http_client: aiohttp.ClientSession) -> dict[str, bool | int] | dict[str, bool | Any]:
        try:
            response = await http_client.post('https://tg-bot-tap.laborx.io/api/v1/farming/finish', json={})
            response.raise_for_status()

            response_json = await response.json()

            if response.status == 200:
                return {
                    'ok': True,
                    'code': 200,
                    'balance': int(response_json['balance'])
                }

        except Exception as error:
            #logger.error(f"{self.session_name} | Unknown error when Claiming: {error}")
            await asyncio.sleep(delay=3)

            return {
                    'ok': True,
                    'code': response.status
                }

    async def claim_staking(self, http_client: aiohttp.ClientSession, stake_id: str) -> None:
        try:
            response = await http_client.post(
                'https://tg-bot-tap.laborx.io/api/v1/staking/claim',
                json={'id': stake_id}
            )
            response.raise_for_status()

            if response.status == 200:
                balance_data = await response.json()
                # logger.debug(f"{self.session_name} | Response: {json.dumps(response, indent=4)}")
                new_balance = balance_data.get('balance')

                if new_balance is not None:
                    logger.success(
                        f"{self.session_name} | Successfully claimed staking reward for stake ID: <y>{stake_id}</y>")
                    logger.info(f"{self.session_name} | New balance: <c>{int(float(new_balance)):,}</c>")
                    await asyncio.sleep(random.randint(10, 30))
                    if random.random() < 0.5:
                        await self.perform_staking(http_client)
                else:
                    logger.warning(f"{self.session_name} | Staking reward claimed, but balance information is missing")
            else:
                logger.error(
                    f"{self.session_name} | Failed to claim staking reward for stake ID: {stake_id}. Status: {response.status}")

        except aiohttp.ClientResponseError as e:
            logger.error(f"{self.session_name} | HTTP error while claiming staking reward: {e.status}: {str(e)}")
        except json.JSONDecodeError:
            logger.error(f"{self.session_name} | Failed to parse JSON response from staking claim")
        except Exception as error:
            logger.exception(f"{self.session_name} | Unexpected error claiming staking reward: {error}")

    async def get_current_staking(self, http_client: aiohttp.ClientSession) -> None:
        try:
            response = await http_client.get('https://tg-bot-tap.laborx.io/api/v1/staking/active')
            response.raise_for_status()
            staking_data = await response.json()

            if 'stakes' in staking_data and staking_data['stakes']:
                for stake in staking_data['stakes']:
                    stake_id = stake.get('id')
                    amount = stake.get('amount', 0)
                    duration = stake.get('duration', 0)
                    percent = stake.get('percent', 0)
                    finish_at = datetime.fromisoformat(stake.get('finishAt', '').replace('Z', '+00:00'))
                    formatted_finish_at = finish_at.strftime('%d/%m/%Y %H:%M %Z')

                    logger.info(
                        f"{self.session_name} | Current staking | "
                        f"Amount: <c>{amount:,}</c> | "
                        f"Duration: <g>{duration} days</g> | "
                        f"Percent: <y>{percent}%</y> | "
                        f"Finish at <lr>{formatted_finish_at}</lr>"
                    )

                    # Проверяем, наступило ли время для клейма
                    current_time = datetime.now(timezone.utc)
                    formatted_current_time = current_time.strftime('%d/%m/%Y %H:%M')
                    # logger.info(
                    #     f"{self.session_name} | Current time (UTC): <cyan>{formatted_current_time}</cyan>")

                    if current_time >= finish_at:
                        logger.info(
                            f"{self.session_name} | <ly>Time to claim staking reward!</ly> Current time: {formatted_current_time} | Finish time: {formatted_finish_at}")
                        await asyncio.sleep(random.randint(5, 15))
                        await self.claim_staking(http_client, stake_id)
                    else:
                        time_left = finish_at - current_time
                        # logger.info(f"{self.session_name} | Time left until staking can be claimed: {time_left}")
            else:
                logger.info(f"{self.session_name} | No active staking found")

        except Exception as error:
            logger.error(f"{self.session_name} | Error getting current staking info: {error}")

    async def perform_staking(self, http_client: aiohttp.ClientSession) -> None:
        try:
            mining_data = await self.get_mining_data(http_client=http_client)
            balance = int(float(mining_data.get('balance', 0)))

            if balance < 10000000:
                logger.info(f"{self.session_name} | Balance is less than 10,000,000, skipping staking")
                await self.get_current_staking(http_client)
                return

            staking_response = await http_client.get('https://tg-bot-tap.laborx.io/api/v1/staking/active')
            staking_response.raise_for_status()
            staking_data = await staking_response.json()

            staking_options = staking_data.get('stakingInfo', {}).get('options', [])
            if not staking_options:
                logger.error(f"{self.session_name} | No staking options available")
                await self.get_current_staking(http_client)
                return

            def round_amount(amt, base):
                return base * (amt // base)

            if random.randint(1, 3) == 1:
                amount = balance
            else:
                if balance <= 100000:
                    base = 1000
                elif balance <= 1000000:
                    base = 100000
                else:
                    base = 1000000

                min_amount = round_amount(int(balance * 0.7), base)
                max_amount = round_amount(balance, base)
                amount = random.randrange(min_amount, max_amount + 1, base)

            amount_percent = (amount / balance) * 100

            option_weights = [75, 20, 5]
            option_id = random.choices(['1', '2', '3'], weights=option_weights)[0]

            staking_response = await http_client.post(
                'https://tg-bot-tap.laborx.io/api/v1/staking',
                json={'amount': amount, 'optionId': option_id}
            )
            staking_response.raise_for_status()
            staking_result = await staking_response.json()

            if 'stakes' in staking_result:
                stake = staking_result['stakes'][0]
                duration = stake['duration']
                percent = stake['percent']
                finish_at = datetime.fromisoformat(stake['finishAt'].replace('Z', '+00:00'))
                formatted_finish_at = finish_at.strftime('%d/%m/%Y %H:%M')

                logger.success(
                    f"{self.session_name} | Successfully staking | "
                    f"Amount: <c>{amount:,} ({amount_percent:.2f}%)</c> | "
                    f"Duration: <g>{duration} days</g> | "
                    f"Percent: <y>{percent}%</y> | "
                    f"Finish at: <lr>{formatted_finish_at}</lr>"
                )
            else:
                logger.error(f"{self.session_name} | Staking failed: {staking_result}")


        except Exception as error:
            logger.error(f"{self.session_name} | Error during staking: {error}")
            await asyncio.sleep(delay=3)


            await self.get_current_staking(http_client)

    async def run(self) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = random.randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            logger.info(
                f"{self.session_name} | The Bot will go live in <y>{random_delay}s</y>")
            await asyncio.sleep(random_delay)

        await self.init()
        access_token_created_time = 0
        available = False

        proxy_conn = ProxyConnector().from_url(self.proxy) if self.proxy else None
        http_client = aiohttp.ClientSession(headers=self.headers, connector=proxy_conn)
        connection_manager.add(http_client)

        if settings.USE_PROXY:
            if not self.proxy:
                logger.error(f"{self.session_name} | Proxy is not set. Aborting operation.")
                return
            if not await self.check_proxy(http_client):
                logger.error(f"{self.session_name} | Proxy check failed. Aborting operation.")
                return
                
        while True:
            try:
                if http_client.closed:
                    if proxy_conn:
                        if not proxy_conn.closed:
                            await proxy_conn.close()

                    proxy_conn = ProxyConnector().from_url(self.proxy) if self.proxy else None
                    http_client = aiohttp.ClientSession(headers=self.headers, connector=proxy_conn)
                    connection_manager.add(http_client)


                if tm.time() - access_token_created_time >= 3600:
                    tg_web_data = await self.get_tg_web_data()
                    login_data = await self.login(http_client=http_client, tg_web_data=tg_web_data)
                    logger.info(f"{self.session_name} | Logged in successfully!")

                    http_client.headers["Authorization"] = f"Bearer {login_data['token']}"
                    self.headers["Authorization"] = f"Bearer {login_data['token']}"

                    level_num = int(login_data.get('level', 0))
                    levelDescriptions = login_data.get('levelDescriptions', [])

                    access_token_created_time = tm.time()

                    # tasks_data = await self.get_tasks_list(http_client=http_client)

                    # for task in tasks_data:
                    #     task_id = task.get("id")
                    #     task_title = task.get("title", "Unknown")
                    #     task_type = task.get("type")
                    #     if "submission" in task:
                    #         status = task["submission"].get("status")
                    #         if status == "CLAIMED":
                    #             continue

                    #         if status == "COMPLETED":
                    #             task_data_claim = await self.task_claim(http_client=http_client, task_id=task_id)
                    #             if task_data_claim == "OK":
                    #                 logger.success(f"{self.session_name} | Successful claim | "
                    #                                f"Task Title: <g>{task_title}</g>")
                    #                 continue

                    #     if task_type == "TELEGRAM":
                    #         continue

                    #     task_data_submiss = await self.task_submiss(http_client=http_client, task_id=task_id)
                    #     if task_data_submiss != "OK":
                    #         continue

                    #     task_data_x = await self.get_task_data(http_client=http_client, task_id=task_id)
                    #     status = task_data_x.get("submission", {}).get("status")
                    #     if status != "COMPLETED":
                    #         logger.error(f"{self.session_name} | Task is not completed: {task_title}")
                    #         continue

                    #     task_data_claim_x = await self.task_claim(http_client=http_client, task_id=task_id)
                    #     if task_data_claim_x == "OK":
                    #         logger.success(f"{self.session_name} | Successful claim | "
                    #                        f"Task Title: <g>{task_title}</g>")
                    #         continue

                mining_data = await self.get_mining_data(http_client=http_client)

                try:
                    balance = int(float(mining_data.get('balance', 0)))
                    farmingReward = int(mining_data.get('farmingReward', 0))
                    farmingDurationInSec = int(mining_data.get('farmingDurationInSec', 0))
                except (KeyError, ValueError) as e:
                    logger.error(f"{self.session_name} | Error processing mining data: {e}")
                    balance = 0
                    farmingReward = 0
                    farmingDurationInSec = 0

                available = mining_data.get('activeFarmingStartedAt') is not None

                if farmingDurationInSec > 0:
                    settings.SLEEP_BETWEEN_CLAIM = int(farmingDurationInSec / 60)

                logger.info(f"{self.session_name} | Balance: <c>{balance:,}</c> | "
                            f"Earning: <e>{available}</e> | "
                            f"Speed: <g>x{(level_num + 1)}</g>")

                if not available:
                    status_start = await self.start_mine(http_client=http_client)
                    if status_start.get('ok') and status_start.get('code') == 200:
                        logger.success(f"{self.session_name} | Successful Mine Started | "
                                       f"Balance: <c>{balance:,}</c> | "
                                       f"Speed: Farming (<g>x{(level_num + 1)}</g>)")

                if available:
                    retry = 1
                    while retry <= settings.CLAIM_RETRY:
                        status = await self.finish_mine(http_client=http_client)
                        if status.get('ok') and status.get('code') == 200:
                            mining_data = await self.get_mining_data(http_client=http_client)
                            new_balance = int(float(mining_data.get('balance', 0)))
                            balance = new_balance

                            if new_balance == int(status.get('balance', 0)):
                                status_start = await self.start_mine(http_client=http_client)
                                if status_start.get('ok') and status_start.get('code') == 200:
                                    logger.success(f"{self.session_name} | Successful claim | "
                                                   f"Balance: <c>{new_balance:,}</c> (<g>+{farmingReward}</g>)")
                                    break
                        elif status.get('code') == 403:
                            break

                        if retry < settings.CLAIM_RETRY:
                            retry_delay = random.uniform(1, 5)
                            logger.info(
                                f"{self.session_name} | Retry <y>{retry}</y> of <e>{settings.CLAIM_RETRY} with {retry_delay:.2f}s</e>")
                            await asyncio.sleep(delay=retry_delay)
                        retry += 1

                available = False

                if settings.AUTO_UPGRADE_FARM and level_num < settings.MAX_UPGRADE_LEVEL:
                    next_level = level_num + 1
                    max_level_bot = len(levelDescriptions) - 1
                    if next_level <= max_level_bot:
                        for level_data in levelDescriptions:
                            lvl_dt_num = int(level_data.get('level', 0))
                            if next_level == lvl_dt_num:
                                lvl_price = int(level_data.get('price', 0))
                                if lvl_price <= balance:
                                    random_upgrade_delay = random.uniform(3, 8)
                                    logger.info(
                                        f"{self.session_name} | Sleep {random_upgrade_delay:.2f}s before upgrade level farming to {next_level} lvl")
                                    await asyncio.sleep(delay=random_upgrade_delay)

                                    out_data = await self.upgrade_level(http_client=http_client)
                                    if out_data.get('balance'):
                                        logger.success(
                                            f"{self.session_name} | Level farming upgraded to {next_level} lvl | "
                                            f"Balance: <c>{out_data['balance']:.}</c> | "
                                            f"Speed: <g>x{level_data.get('farmMultiplicator', 1)}</g>")

                                        await asyncio.sleep(delay=1)

                await self.perform_staking(http_client=http_client)

            except aiohttp.ClientConnectorError as error:
                delay = random.randint(1800, 3600)
                logger.error(f"{self.session_name} | Connection error: {error}. Retrying in {delay} seconds.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                await asyncio.sleep(delay)


            except aiohttp.ServerDisconnectedError as error:
                delay = random.randint(900, 1800)
                logger.error(f"{self.session_name} | Server disconnected: {error}. Retrying in {delay} seconds.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                await asyncio.sleep(delay)


            except aiohttp.ClientResponseError as error:
                delay = random.randint(3600, 7200)
                logger.error(
                   f"{self.session_name} | HTTP response error: {error}. Status: {error.status}. Retrying in {delay} seconds.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                await asyncio.sleep(delay)


            except aiohttp.ClientError as error:
                delay = random.randint(3600, 7200)
                logger.error(f"{self.session_name} | HTTP client error: {error}. Retrying in {delay} seconds.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                await asyncio.sleep(delay)


            except asyncio.TimeoutError:
                delay = random.randint(7200, 14400)
                logger.error(f"{self.session_name} | Request timed out. Retrying in {delay} seconds.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                await asyncio.sleep(delay)


            except InvalidSession as error:
                logger.critical(f"{self.session_name} | Invalid Session: {error}. Manual intervention required.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                raise error


            except json.JSONDecodeError as error:
                delay = random.randint(1800, 3600)
                logger.error(f"{self.session_name} | JSON decode error: {error}. Retrying in {delay} seconds.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                await asyncio.sleep(delay)

            except KeyError as error:
                delay = random.randint(1800, 3600)
                logger.error(
                    f"{self.session_name} | Key error: {error}. Possible API response change. Retrying in {delay} seconds.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                await asyncio.sleep(delay)


            except Exception as error:
                delay = random.randint(7200, 14400)
                logger.error(f"{self.session_name} | Unexpected error: {error}. Retrying in {delay} seconds.")
                logger.debug(f"Full error details: {traceback.format_exc()}")
                await asyncio.sleep(delay)

            finally:
                await http_client.close()
                if proxy_conn:
                    if not proxy_conn.closed:
                        await proxy_conn.close()
                connection_manager.remove(http_client)

                sleep_delay = random.randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                hours = int(sleep_delay // 3600)
                minutes = (int(sleep_delay % 3600)) // 60
                logger.info(
                    f"{self.session_name} | Sleep before wake up <yellow>{hours} hours</yellow> and <yellow>{minutes} minutes</yellow>")
                await asyncio.sleep(sleep_delay)

async def run_tapper(tg_client: Client, proxy: str | None):
    session_name = tg_client.name
    if settings.USE_PROXY and not proxy:
        logger.error(f"{session_name} | No proxy found for this session")
        return
    try:
        await Tapper(tg_client=tg_client, proxy=proxy).run()
    except InvalidSession:
        logger.error(f"{session_name} | Invalid Session")
