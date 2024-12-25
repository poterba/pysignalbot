import io
import os
import pytest
from pysignalbot import NativeBot
from PIL import Image

_SIGNAL_BOT_ENDPOINT = os.getenv("SIGNAL_BOT_ENDPOINT", "localhost:8080")
_SIGNAL_BOT_CREATE = os.getenv("SIGNAL_BOT_CREATE", True)


@pytest.fixture(scope="module")
def native_bot():
    bot = NativeBot(_SIGNAL_BOT_ENDPOINT)
    accounts = bot.get_accounts()
    if not accounts:
        if _SIGNAL_BOT_CREATE:
            image = bot.qrcodelink("PYSIGNAL_BOT_TEST")
            Image.open(io.BytesIO(image)).show()
        raise RuntimeError("No linked accounts")
    return bot
