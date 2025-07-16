class MessageManager:
    def __init__(self, state, bot):
        self.state = state
        self.bot = bot

    async def push(self, message):
        data = await self.state.get_data()
        if "last_msg_id" in data:
            try:
                await self.bot.delete_message(message.chat.id, data["last_msg_id"])
            except Exception:
                pass
        await self.state.update_data(last_msg_id=message.message_id)
