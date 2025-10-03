import pytest

from bot.handlers.user import command_start_handler

@pytest.mark.asyncio
async def test_command_start_handler():
    class MockUser:
        id = 123456
        first_name = "TestUser"
    class MockMessage:
        from_user = MockUser()
        text = "/start"
        async def answer(self, text):
            assert "бот" in text or "bot" in text
    message = MockMessage()
    await command_start_handler(message)
