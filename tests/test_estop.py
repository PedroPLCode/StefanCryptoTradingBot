from datetime import datetime
from django.test import TestCase
from unittest import mock
from app.models import BotSettings
from app.utils.estop_utils import (
    process_bot_emergency_stop,
    handle_no_bots,
    handle_bots_stopped,
)
from app.stefan.api_utils import place_sell_order
from typing import List


class BotEmergencyStopTests(TestCase):

    @mock.patch("..utils.logging.logger.trade")
    @mock.patch("..utils.email_utils.send_admin_email")
    @mock.patch("..stefan.api_utils.place_sell_order")
    def test_process_bot_emergency_stop_success(
        self, mock_place_sell_order, mock_send_email, mock_logger
    ):
        bot_settings = mock.Mock(spec=BotSettings)
        bot_settings.etop_passwd = "correct_password"
        bot_settings.id = 1
        bot_settings.symbol = "BTCUSDC"
        bot_settings.strategy = "Scalping"
        bot_settings.bot_current_trade.is_active = True
        bot_settings.bot_running = True

        result = process_bot_emergency_stop(bot_settings, "correct_password")

        bot_settings.bot_running = False
        mock_logger.assert_called_with(f"Bot 1 BTCUSDC Scalping Emergency stopped.")
        mock_send_email.assert_called_with(
            "Bot 1 Emergency stopped.", "Bot 1 BTCUSDC Scalping Emergency stopped."
        )
        mock_place_sell_order.assert_called_once_with(1)
        self.assertEqual(result, bot_settings)

    @mock.patch("..utils.logging.logger.trade")
    @mock.patch("..utils.email_utils.send_admin_email")
    def test_process_bot_emergency_stop_wrong_password(
        self, mock_send_email, mock_logger
    ):
        bot_settings = mock.Mock(spec=BotSettings)
        bot_settings.etop_passwd = "correct_password"
        bot_settings.id = 1
        bot_settings.symbol = "BTCUSDC"
        bot_settings.strategy = "Scalping"

        result = process_bot_emergency_stop(bot_settings, "wrong_password")

        mock_logger.assert_called_with(
            f"Bot 1 BTCUSDC Scalping - Wrong Emergency stop password."
        )
        mock_send_email.assert_called_with(
            "Bot 1 Emergency stop Error.",
            "Wrong password attempt for Bot 1 BTCUSDC Scalping.",
        )
        self.assertIsNone(result)

    @mock.patch("..utils.logging.logger.trade")
    @mock.patch("..utils.email_utils.send_admin_email")
    def test_handle_no_bots(self, mock_send_email, mock_logger):
        result = handle_no_bots()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mock_logger.assert_called_with("No Bots Found to Emergency stop.")
        mock_send_email.assert_called_with(
            "All Bots Emergency stop Error.",
            f"StafanCryptoTradingBot Emergency stop report.\n{now}\n\nNo Bots Found to Emergency stop.\n\nCheck it as soon as possible.",
        )
        self.assertEqual(result, ("No bots to stop.", 404))

    @mock.patch("..utils.logging.logger.trade")
    @mock.patch("..utils.email_utils.send_admin_email")
    def test_handle_bots_stopped(self, mock_send_email, mock_logger):
        bot_settings_1 = mock.Mock(spec=BotSettings)
        bot_settings_1.id = 1
        bot_settings_1.symbol = "BTCUSDC"
        bot_settings_1.strategy = "Scalping"

        bot_settings_2 = mock.Mock(spec=BotSettings)
        bot_settings_2.id = 2
        bot_settings_2.symbol = "ETHUSDC"
        bot_settings_2.strategy = "Scalping"

        bots_stopped: List[BotSettings] = [bot_settings_1, bot_settings_2]

        result = handle_bots_stopped(bots_stopped)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mock_logger.assert_called_with(f"2 Bots Emergency stopped.")
        mock_send_email.assert_called_with(
            "All Bots Emergency stopped.",
            f"StafanCryptoTradingBot Emergency stop report.\n{now}\n\n2 Bots Emergency stopped.\n\nCheck it as soon as possible.",
        )
        self.assertEqual(result, "2 Bots Emergency stopped.", 200)
