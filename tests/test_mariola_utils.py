import pytest
import pandas as pd
import numpy as np
from app.mariola.ml_utils import normalize_df, handle_pca, create_sequences

@pytest.fixture
def mock_bot_settings():
    class MockBotSettings:
        id = 1
    return MockBotSettings()

def test_normalize_df_happy_path(mock_bot_settings):
    df = pd.DataFrame({
        "numeric1": [1, 2, 3, np.inf],
        "numeric2": [-np.inf, 5, 6, 7],
        "non_numeric": ["a", "b", "c", "d"]
    })
    
    expected_columns = ["numeric1", "numeric2"]
    
    result = normalize_df(df, mock_bot_settings)
    
    assert result is not None
    assert set(result.columns) == set(expected_columns)
    assert result["numeric1"].isnull().sum() == 0
    assert result["numeric2"].isnull().sum() == 0

def test_normalize_df_handles_empty_dataframe(mock_bot_settings):
    df = pd.DataFrame()
    result = normalize_df(df, mock_bot_settings)
    
    assert result is None

def test_normalize_df_with_infinite_values(mock_bot_settings):
    df = pd.DataFrame({
        "numeric": [1, np.inf, -np.inf]
    })
    result = normalize_df(df, mock_bot_settings)
    
    assert result is not None
    assert result.isnull().sum().sum() == 0

def test_handle_pca_happy_path(mock_bot_settings):
    df_normalized = pd.DataFrame(np.random.rand(100, 10))
    result = handle_pca(df_normalized, mock_bot_settings)
    
    assert result is not None
    assert result.shape == (100, 50)

def test_handle_pca_empty_dataframe(mock_bot_settings):
    df_normalized = pd.DataFrame()
    result = handle_pca(df_normalized, mock_bot_settings)
    
    assert result is None

def test_create_sequences_happy_path(mock_bot_settings):
    df_reduced = pd.DataFrame(np.random.rand(100, 10))
    lookback = 5
    window_size = 10
    
    X = create_sequences(df_reduced, lookback, window_size, mock_bot_settings)
    
    assert X is not None
    assert X.shape == (85, 10, 10)

def test_create_sequences_invalid_inputs(mock_bot_settings):
    df_reduced = pd.DataFrame()
    lookback = 5
    window_size = 10
    
    result = create_sequences(df_reduced, lookback, window_size, mock_bot_settings)
    
    assert result is None