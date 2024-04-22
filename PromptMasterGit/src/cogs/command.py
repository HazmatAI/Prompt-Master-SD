"""
The cog module for the command.
"""
import json

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
        if data := img.info.get("parameters"):
            parts = data.split("Negative prompt: ", 1)
            smaller = parts[1].split("Steps: ", 1)
            other = ""
            for i in f"Steps: {smaller[1]}".split(", "):
                try:
                    other += f"\n**{i.split(': ', 1)[0]}: **{i.split(': ', 1)[1]}"
                except IndexError:
                    other += f",{i}"
        elif data := img.info.get("Description"):
            parts = [img.info.get("Description")[1:] + "\n\n"]
            smaller = [json.loads(img.info.get("Comment"))["uc"]]
            other = ""
            # There are some more settings that are given in the image metadata but that are the most important one
            # Feel free to add more:
            # "steps": 28, "height": 1216, "width": 832, "scale": 5.0, "uncond_scale": 1.0, "cfg_rescale": 0.0, "seed": 199606024, "n_samples": 1, "hide_debug_overlay": false, "noise_schedule": "native", "sampler": "k_euler", "controlnet_strength": 1.0, "controlnet_model": null, "dynamic_thresholding": false, "dynamic_thresholding_percentile": 0.999, "dynamic_thresholding_mimic_scale": 10.0, "sm": false, "sm_dyn": false, "skip_cfg_below_sigma": 0.0, "lora_unet_weights": null, "lora_clip_weights": null, "signed_hash": "pLmfj2OdW+fuDySDRsNpmmNcFk8iYn2OVXxRY1Wl9M8d3748f5lbwxbZVJtmgoTIHLJFSQwphcpbfkzcpB7SDQ=="}
            image_data = json.loads(img.info.get("Comment"))
            other += "\n\n"
            other += str(f"**Steps**: {image_data['steps']}\n")
            other += str(f"**Sampler**: {image_data['sampler']}\n")
            other += str(f"**CFG scale**: {image_data['scale']}\n")
            other += str(f"**Seed**: {image_data['seed']}\n")
            other += str(f"**Size**: {image_data['width']}x{image_data['height']}\n")
            other += str(f"**Signed hash**: {image_data['signed_hash']}\n")
            other += str(f"**CFG rescale**: {image_data['cfg_rescale']}\n")
        elif data := img.info.get("prompt"):
            parts = [json.loads(img.info.get("prompt"))["6"]["inputs"]["text"] + "\n\n"]
            smaller = [json.loads(img.info.get("prompt"))["7"]["inputs"]["text"]]
            image_data = json.loads(img.info.get("prompt"))
            other = ""
            other += "\n\n"
            other += str(f"**Steps**: {image_data['3']['inputs']['steps']}\n")
            other += str(f"**Sampler**: {image_data['3']['inputs']['sampler_name']}\n")
            other += str(f"**CFG Scale**: {image_data['3']['inputs']['cfg']}\n")
            other += str(f"**Seed**: {image_data['3']['inputs']['seed']}\n")
            other += str(f"**Size**: {image_data['5']['inputs']['width']}x{image_data['5']['inputs']['height']}\n")
            other += str(f"**VAE**: {image_data['4']['inputs']['ckpt_name']}\n")
            other += str(f"**Model**: {image_data['11']['inputs']['filename_prefix']}\n")
        else:
            return await ctx.respond(
                "The image has no parameters. Make sure IMG is uploaded from the Automattic111 folder.")
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

