import asyncio
import os

from mutiny import Client, events

# Client class can be constructed with a `token` for bot session,
# or `user_id` and `session_token` for user session.
# To get a user session, see `get_session_id_and_token.py` example.

client = Client(token=os.environ["BOT_TOKEN"])


# Listeners can be added by defining a single argument function
# decorated with `@client.listen()` and with its argument type-hinted
# with an appropriate event type:


@client.listen()
async def on_ready(event: events.ReadyEvent) -> None:
    print("I'm ready!")
    print(event.raw_data)


@client.listen()
async def on_message(event: events.MessageEvent) -> None:
    print(event.raw_data)


# Client.start() is the main entry-point for the Client and it does not return
# until the client is closed or gateway connection is lost.

asyncio.run(client.start())
