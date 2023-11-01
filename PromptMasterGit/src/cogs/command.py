"""
The cog module for the command.
"""

import discord
from discord.ext import commands
from PIL import Image
from io import BytesIO


class Command(commands.Cog):
    """
    The class for the command.
    """

    def __init__(self, client: discord.AutoShardedBot) -> None:
        self.client = client

    @discord.slash_command(description="Obtain the parameters of an image.")
    @discord.option(name="image", description="The image to obtain the parameters of.", required=False)
    @discord.option(name="message_id", description="The message ID of the image to obtain the parameters of.", required=False)
    @discord.option(name="channel", description="The channel of the message.", required=False)
    async def params(self, ctx: discord.ApplicationContext, image: discord.Attachment = None, message_id: str = None, channel: discord.TextChannel = None, dm=False) -> None:
        """
        The function that is triggered when the command is triggered.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param image: The image to obtain the parameters of.
        :type image: discord.Attachment
        :param message_id: The message ID of the image to obtain the parameters of.
        :type message_id: str
        :param channel: The channel of the message.
        :type channel: discord.TextChannel
        """
        await ctx.defer(ephemeral=True)
        if not image and not message_id:
            return await ctx.respond("You must provide an image or a message ID.")
        if message_id:
            if image:
                return await ctx.respond("You must provide either an image or a message ID.")
            if not message_id.isdigit():
                return await ctx.respond("The message ID must be a number.")
            message_id = int(message_id)
            if not channel:
                channel = ctx.channel
            try:
                message = self.client.get_message(message_id) or await channel.fetch_message(message_id)
            except discord.NotFound:
                return await ctx.respond("The message could not be found, try specifying the channel if you did not.")
            if not message.attachments:
                return await ctx.respond("The message has no attachments.")
            image = message.attachments[0]
        if not image.content_type.startswith("image/"):
            return await ctx.respond("The attachment is not an image.")
        (img:=Image.open(BytesIO(await image.read()))).load()
        if not (data := img.info.get("parameters", None)):
            return await ctx.respond("The image has no parameters. Make sure IMG is uploaded from the Automattic111 folder.")
        parts = data.split("Negative prompt: ", 1)
        smaller = parts[1].split("Steps: ", 1)
        other = ""
        for i in f"Steps: {smaller[1]}".split(", "):
            try:
                other += f"\n**{i.split(': ', 1)[0]}: **{i.split(': ', 1)[1]}"
            except IndexError:
                other += f",{i}"
        if not dm:
            await ctx.respond(
                embed=discord.Embed(
                    title="Image Parameters",
                    description=f"**Positive prompt: **{parts[0]}\n**Negative prompt: **{smaller[0]}\n{other}",
                    color=discord.Color.blurple()
                ),ephemeral=True
        )
        if dm:
            await ctx.respond("DM sent")
            try:
                embed=discord.Embed(title="Image Parameters", description=f"**Positive prompt: **{parts[0]}\n**Negative prompt: **{smaller[0]}\n{other}", color=discord.Color.blurple())
                embed.set_image(url=image.url)
                await ctx.author.send(embed=embed)
            except:
                pass

    @discord.message_command(name="Prompt here", description="Obtain the parameters of an image.")
    async def _params(self, ctx: discord.ApplicationContext, message: discord.Message) -> None:
        """
        The function that is triggered when the command is triggered.
        
        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        """
        await self.params(ctx, message_id=str(message.id), channel=message.channel, dm=False)
    
    @discord.message_command(name="Prompt via DM", description="Obtain the parameters of an image and get a dm.")
    async def _params_dm(self, ctx: discord.ApplicationContext, message: discord.Message) -> None:
        """
        The function that is triggered when the command is triggered.
        
        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        """
        await self.params(ctx, message_id=str(message.id), channel=message.channel, dm=True)


def setup(client: discord.AutoShardedBot) -> None:
    """
    The function that is triggered when the cog is loaded.

    :param client: The bot client.
    :type client: discord.AutoShardedBot
    """
    client.add_cog(Command(client))

