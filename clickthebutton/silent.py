import discord
from discord.http import handle_message_parameters


async def send_silent(content: str, channel: discord.TextChannel, silent: bool):
    """Custom send function for silent messages in discord.py v2.0.1"""
    if not silent:
        return await channel.send(
            content=content, allowed_mentions=discord.AllowedMentions.none()
        )

    if discord.__version__ != "2.0.1":
        return await channel.send(
            content=content,
            allowed_mentions=discord.AllowedMentions.none(),
            silent=True,
        )

    # https://github.com/Rapptz/discord.py/blob/v2.0.1/discord/abc.py#L1374
    _channel = await channel._get_channel()
    state = _channel._state
    previous_allowed_mention = state.allowed_mentions

    flags = discord.MessageFlags._from_value(4096)

    with handle_message_parameters(
        content=content,
        allowed_mentions=discord.AllowedMentions.none(),
        previous_allowed_mentions=previous_allowed_mention,
        flags=flags,
    ) as params:
        data = await state.http.send_message(_channel.id, params=params)

    ret = state.create_message(channel=_channel, data=data)

    return ret
