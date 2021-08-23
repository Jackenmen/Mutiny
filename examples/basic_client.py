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


async def main():
    try:
        # Client.start() is the main entry-point for the Client and it does not return
        # until the client is closed or gateway connection is lost.
        await client.start()
    finally:
        # Client.close() should be called to ensure proper cleanup
        # before exiting the application
        await client.close()


if __name__ == "__main__":
    # Note: This example is meant to show basic flow of running Mutiny's Client,
    # and is therefore just using asyncio.run(). In normal asynchronous application,
    # you will often not want to use asyncio.run() as a main entry point as it is
    # lacking in some aspects.
    asyncio.run(main())
