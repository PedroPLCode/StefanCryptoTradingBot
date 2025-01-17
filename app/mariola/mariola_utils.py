import pandas as pd 
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def normalize_df(result_df, bot_settings):
    """
    Normalize the numeric columns in a DataFrame using MinMaxScaler, while replacing infinite values 
    and clipping extreme values. Non-numeric columns are excluded from normalization, and the 
    `result_marker` column (if specified) is retained without modification.

    Args:
        result_df (pd.DataFrame): The input DataFrame containing both numeric and non-numeric columns.
        training_mode (bool): If True, it indicates that the function is being used for training. 
                               In this mode, the `result_marker` column is excluded from the normalization 
                               and included in the final output.
        result_marker (str): The name of the column to exclude from normalization but include in the final DataFrame. 
                             It must be a valid column name in `result_df`. If `None`, no column is excluded.

    Returns:
        pd.DataFrame: A DataFrame with normalized numeric columns and the `result_marker` column added 
                      at the end, if specified.

    Raises:
        ValueError: If `result_df` is `None`, empty, or if `result_marker` is specified but not found 
                    in the DataFrame columns.

    Notes:
        - The function replaces `np.inf` and `-np.inf` values in the DataFrame with 0.
        - Numeric values are clipped to the range [-1.8e308, 1.8e308] to avoid extreme outliers.
        - Non-numeric columns such as booleans, datetimes, and strings are excluded from the normalization process.
        - In training mode, the `result_marker` column is excluded from normalization but included in the final DataFrame.

    Example:
        normalized_df = normalize_df(df, training_mode=True, result_marker='target')
    """
    try:
        
        if result_df is None or result_df.empty:
            raise ValueError("result_df must be provided and cannot be None.")
        
        non_numeric_features = result_df.select_dtypes(
            include=['bool', 'datetime', 'string']
        ).columns.tolist()
        
        numeric_features = result_df.select_dtypes(
            include=['float64', 'int64']
        ).columns.tolist()
        
        result_df = result_df.replace([np.inf, -np.inf], 0)
        
        result_df[numeric_features] = result_df[numeric_features].clip(
            lower=-1.8e308, upper=1.8e308
        )
        
        scaler = MinMaxScaler(feature_range=(0, 1))
        
        df_normalized = pd.DataFrame(
            scaler.fit_transform(result_df[numeric_features]),
            columns=numeric_features
        )
        
        return df_normalized
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in prepare_mariola_df: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in prepare_mariola_df', str(e))
        return None


def handle_pca(df_normalized, bot_settings):
    """
    Perform Principal Component Analysis (PCA) on the normalized DataFrame and add the target marker to the resulting DataFrame.
    
    Args:
        df_normalized (pd.DataFrame): The normalized DataFrame containing only numeric features.
        result_df (pd.DataFrame): The original DataFrame containing the target marker.
        result_marker (str): The name of the column in `result_df` representing the target marker.
    
    Returns:
        pd.DataFrame: A DataFrame with the reduced features (after PCA) and the target marker.
    
    Notes:
        The PCA transformation reduces the features to the specified number of components (`n_components=50`).
    """
    try:
        
        if df_normalized is None or df_normalized.empty:
            raise ValueError("df_normalized must be provided and cannot be None.")
        
        pca = PCA(n_components=50)
        df_reduced = pca.fit_transform(df_normalized)
        df_reduced = pd.DataFrame(df_reduced)
            
        return df_reduced
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in prepare_mariola_df: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in prepare_mariola_df', str(e))
        return None


def create_sequences(df_reduced, lookback, window_size, bot_settings):
    """
    Create sequences of features and corresponding target labels from the reduced DataFrame for time series prediction.
    
    This function takes a DataFrame that contains PCA-transformed features and a target column (`result_marker`), 
    and generates sequences of features (X) and corresponding target labels (y) for time series forecasting. 
    The target label is determined based on the `result_marker` column, and the feature sequence is determined 
    by the `window_size` parameter, which defines how many previous periods are included in each feature sequence.

    Args:
        df_reduced (pd.DataFrame): The DataFrame containing PCA-transformed features and the target marker column.
        lookback (int): The number of periods ahead to predict. This defines the target label based on the index of `result_marker`.
        window_size (int): The number of previous periods used as features in each sequence.
        result_marker (str): The column name in `df_reduced` to be predicted. This column serves as the target label.
        training_mode (bool): If True, generates both feature sequences (X) and corresponding target labels (y). 
                               If False, only generates feature sequences (X) without labels.

    Returns:
        tuple: 
            - X (numpy.ndarray): Array of feature sequences of shape (num_samples, window_size, num_features).
            - y (numpy.ndarray, optional): Array of target labels corresponding to each feature sequence. 
              Only returned if `training_mode=True`.
    
    Notes:
        - The function extracts sequences of length `window_size` from `df_reduced` for the features. 
          For each sequence, it uses the `lookback` value to determine the target label.
        - If `training_mode` is set to `False`, the function returns only the feature sequences (X) and does not generate target labels (y).
        - If any of the arguments are missing or `None`, the function raises a `ValueError`.
    
    Example:
        X, y = create_sequences(df_reduced, lookback=14, window_size=30, result_marker='marker_column', training_mode=True)
        X = create_sequences(df_reduced, lookback=14, window_size=30, result_marker='marker_column', training_mode=False)

    """
    try:
        if (
            df_reduced is None or
            lookback is None or
            window_size is None
        ):
            raise ValueError("All arguments must be provided and cannot be None.")
        
        X = []
        
        df_features = df_reduced

        for i in range(window_size, len(df_reduced) - lookback):
            X.append(df_features.iloc[i-window_size:i].values)
        
        return np.array(X)
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in prepare_mariola_df: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in prepare_mariola_df', str(e))
        return None