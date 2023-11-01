"""
The main module of the bot.
"""

import tracemalloc

import decouple
import discord


class Bot(discord.AutoShardedBot):
    """
    The main class of the bot.
    """

    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.all())
        self._client_ready = False
        self.load_extension("src.cogs", recursive=True)

    async def on_shard_connect(self, shard_id: int) -> None:
        """
        The event that is triggered when a shard connected.

        :param shard_id: The shard ID.
        :type shard_id: int
        """
        print(f"Shard {shard_id} connected.")

    async def on_shard_ready(self, shard_id: int) -> None:
        """
        The event that is triggered when a shard is ready.

        :param shard_id: The shard ID.
        :type shard_id: int
        """
        print(f"Shard {shard_id} ready.")

    async def on_shard_resumed(self, shard_id: int) -> None:
        """
        The event that is triggered when a shard resumed.

        :param shard_id: The shard ID.
        :type shard_id: int
        """
        print(f"Shard {shard_id} resumed.")

    async def on_shard_disconnect(self, shard_id: int) -> None:
        """
        The event that is triggered when a shard disconnected.

        :param shard_id: The shard ID.
        :type shard_id: int
        """
        print(f"Shard {shard_id} disconnected.")

    async def on_ready(self) -> None:
        """
        The event that is triggered when the bot is ready.
        """
        if self._client_ready:
            return

        print("-------------------------")
        print(f"Logged in as: {self.user.name}#{self.user.discriminator} ({self.user.id})")
        print(f"Shards Count: {self.shard_count}")
        print(f"Memory Usage: {tracemalloc.get_traced_memory()[0] / 1024 ** 2:.2f} MB")
        print(f" API Latency: {self.latency * 1000:.2f} ms")
        print("-------------------------")
        self._client_ready = True

    async def close(self) -> None:
        """
        Closes the bot.
        """
        await super().close()

    def run(self) -> None:
        """
        Starts the bot.
        """
        super().run(decouple.config("token"))
