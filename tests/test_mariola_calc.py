import pandas as pd
import pytest
from unittest.mock import Mock
from app.mariola.df_utils import is_hammer, is_morning_star, is_bullish_engulfing

bot_settings = Mock()
bot_settings.id = 1


@pytest.fixture
def sample_dataframe():
    data = {
        "open": [100, 105, 110, 95],
        "high": [110, 115, 120, 100],
        "low": [95, 100, 105, 90],
        "close": [105, 110, 100, 98],
    }
    return pd.DataFrame(data)


def test_is_hammer(sample_dataframe):
    result = is_hammer(sample_dataframe, bot_settings)

    assert "hammer" in result.columns
    assert result["hammer"].dtype == bool
    assert result["hammer"].sum() >= 0
    assert result["hammer"].iloc[-1] == False


def test_is_morning_star(sample_dataframe):
    result = is_morning_star(sample_dataframe, bot_settings)

    assert "morning_star" in result.columns
    assert result["morning_star"].dtype == bool
    assert result["morning_star"].sum() >= 0
    assert result["morning_star"].iloc[-1] == False


def test_is_bullish_engulfing(sample_dataframe):
    result = is_bullish_engulfing(sample_dataframe, bot_settings)

    assert "bullish_engulfing" in result.columns
    assert result["bullish_engulfing"].dtype == bool
    assert result["bullish_engulfing"].sum() >= 0
    assert result["bullish_engulfing"].iloc[-1] == False


def test_edge_cases():
    empty_df = pd.DataFrame(columns=["open", "high", "low", "close"])
    with pytest.raises(ValueError):
        is_hammer(empty_df, bot_settings)
    with pytest.raises(ValueError):
        is_morning_star(empty_df, bot_settings)
    with pytest.raises(ValueError):
        is_bullish_engulfing(empty_df, bot_settings)

    incomplete_df = pd.DataFrame({"open": [100], "high": [110]})
    with pytest.raises(KeyError):
        is_hammer(incomplete_df, bot_settings)
