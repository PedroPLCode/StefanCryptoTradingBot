import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from app.mariola.mariola_utils import normalize_df, handle_pca, create_sequences
from app.mariola.mariola_predict import check_ml_signal, price_change_pct_predict

@pytest.fixture
def example_df():
    return pd.DataFrame({
        'feature1': [0.1, 0.2, 0.3, 0.4, 0.5],
        'feature2': [1, 2, 3, 4, 5],
        'feature3': [10, 20, 30, 40, 50]
    })

@pytest.fixture
def bot_settings_mock():
    class BotSettings:
        id = 1
        ml_model_filename = 'model.keras'
        ml_window_lookback = 1
        ml_window_size = 2
        ml_mariola_buy_level = 0.5
        ml_mariola_sell_level = -0.5
    return BotSettings()

def test_normalize_df(example_df, bot_settings_mock):
    normalized_df = normalize_df(example_df, bot_settings_mock)
    
    assert normalized_df is not None
    assert normalized_df.shape == example_df.shape
    assert (normalized_df.min().min() >= 0) and (normalized_df.max().max() <= 1)

def test_handle_pca(example_df, bot_settings_mock):
    df_normalized = (example_df - example_df.min()) / (example_df.max() - example_df.min())
    df_reduced = handle_pca(df_normalized, bot_settings_mock)
    
    assert df_reduced is not None
    assert df_reduced.shape[1] == min(50, df_normalized.shape[1])

def test_create_sequences(example_df, bot_settings_mock):
    df_normalized = (example_df - example_df.min()) / (example_df.max() - example_df.min())
    X = create_sequences(df_normalized, 1, 2, bot_settings_mock)
    
    assert X is not None
    assert X.shape[1] == 2
    assert X.shape[0] == len(df_normalized) - 3

@patch('mariola_predict.price_change_pct_predict', return_value=0.6)
def test_check_ml_mariola_signal(mock_predict, example_df, bot_settings_mock):
    signal = check_ml_signal(example_df, 'buy', bot_settings_mock)
    
    assert signal is True
    
    mock_predict.assert_called_once()


@patch('mariola_calc.prepare_mariola_df', return_value=pd.DataFrame())
@patch('mariola_utils.normalize_df', return_value=pd.DataFrame())
@patch('mariola_utils.handle_pca', return_value=pd.DataFrame())
@patch('mariola_utils.create_sequences', return_value=np.random.rand(5, 2, 3))
@patch('tensorflow.keras.models.load_model')
def test_mariola_predict(
    mock_load_model, 
    mock_create_sequences, 
    mock_handle_pca, 
    mock_normalize_df, 
    mock_prepare_df, 
    example_df, 
    bot_settings_mock
):
    mock_model = MagicMock()
    mock_model.predict.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_load_model.return_value = mock_model
    
    result = price_change_pct_predict(example_df, bot_settings_mock)
    
    assert result == 0.5
    
    mock_prepare_df.assert_called_once()
    mock_normalize_df.assert_called_once()
    mock_handle_pca.assert_called_once()
    mock_create_sequences.assert_called_once()
    mock_load_model.assert_called_once()