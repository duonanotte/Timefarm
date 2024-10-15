import os
import glob
import asyncio
import argparse
import json

from pyrogram import Client
from bot.config import settings
from bot.utils import logger
from bot.core.tapper import run_tapper
from bot.core.registrator import register_sessions
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.markdown import Markdown
from bot.utils.banner import banner
from bot.utils.documentation import get_documentation
global tg_clients

async def smooth_progress(description, total_steps=100, duration=5):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            refresh_per_second=10
    ) as progress:
        task = progress.add_task(description, total=total_steps)

        for _ in range(total_steps):
            await asyncio.sleep(duration / total_steps)
            progress.update(task, advance=1)

    print()

def display_menu(choices, session_count, proxy_count):
    console = Console()

    menu_text = "\n".join([f"[cyan][{i}][/cyan] {choice}" for i, choice in enumerate(choices, 1)])

    panel_content = (
        f"🛡️  Detected [cyan]{session_count}[/cyan] sessions and [cyan]{proxy_count}[/cyan] proxies\n\n"
        f"{menu_text}"
    )

    panel = Panel(
        panel_content,
        title="Session Information",
        title_align="center",
        border_style="dim cyan",
        style="bold white",
        padding=(1, 4),
    )

    console.print(panel)
    print("")


def get_session_names() -> list[str]:
    session_names = sorted(glob.glob("sessions/*.session"))
    session_names = [
        os.path.splitext(os.path.basename(file))[0] for file in session_names
    ]

    return session_names


def get_proxies() -> dict:
    try:
        with open('bot/config/proxies/session_proxy.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("session_proxy.json file not found")
        return {}
    except json.JSONDecodeError:
        logger.error("Error decoding session_proxy.json")
        return {}


async def get_tg_clients() -> list[Client]:
    global tg_clients

    session_names = get_session_names()

    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tg_clients = [
        Client(
            name=session_name,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir="sessions/",
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]

    return tg_clients

def display_documentation(language='ru'):
    console = Console()

    instructions = get_documentation(language)
    title = "Инструкция по использованию" if language == 'ru' else "Usage Instructions"

    md = Markdown(instructions)
    console.print(Panel(md, title=title, border_style="green", expand=False))

async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    args = parser.parse_args()
    action = args.action

    console = Console()

    while True:
        if action is None:
            choices = [
                "Start the bot",
                "Create session",
                "Documentation",
                "Need some help? Contact us here",
                "Exit"
            ]

            display_menu(choices, session_count=len(get_session_names()), proxy_count=len(get_proxies()))

            choice = console.input("[bold yellow]Select an action: [/bold yellow]")
            print("")

            if not choice.isdigit() or int(choice) not in range(1, 6):
                logger.warning("Invalid input. Please select a number between 1 and 5.")
                continue

            action = int(choice)

        if action == 1:
            await smooth_progress("Starting the bot...", total_steps=100, duration=2)
            tg_clients = await get_tg_clients()
            try:
                await run_tasks(tg_clients=tg_clients)
            except Exception as e:
                logger.error(f"Error running tasks: {e}")
            finally:
                action = None

        elif action == 2:
            await smooth_progress("Creating session...", total_steps=100, duration=2)
            try:
                await register_sessions()
            except Exception as e:
                logger.error(f"Error creating session: {e}")
            finally:
                action = None

        elif action == 3:
            language = console.input("[bold yellow]Choose language (RU/EN): [/bold yellow]").lower()
            if language not in ['ru', 'en']:
                logger.warning("Invalid language. Defaulting to Russian.")
                language = 'ru'
            display_documentation(language)
            input("Press Enter to return to the main menu...")
            action = None

        elif action == 4:
            console.print("\n[bold cyan]Need assistance? Here are the contacts:[/bold cyan]")
            print("")
            console.print("[bold green]Author:[/bold green] by duonanotte")
            console.print("[bold green]Community link:[/bold green] https://t.me/web3community_ru")
            print("")
            input("Press Enter to return to the main menu...")
            action = None

        elif action == 5:
            break

        else:
            logger.warning("Invalid action. Please select a number between 1 and 5.")
            action = None


async def run_tasks(tg_clients: list[Client]):
    console = Console()
    proxies = get_proxies()
    tasks = [
        asyncio.create_task(
            run_tapper(
                tg_client=tg_client,
                proxy=proxies.get(tg_client.name)
            )
        )
        for tg_client in tg_clients
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        console.clear()
    except Exception as e:
        logger.error(f"Error in tasks: {e}")
    finally:
        logger.info("All tasks completed or stopped. Returning to menu.")
        banner()
