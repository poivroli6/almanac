"""
Advanced Analytics Module

Statistical significance testing, correlation analysis, volatility clustering,
regime detection, and other advanced analytical features.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import warnings

# Try to import optional dependencies
try:
    from scipy import stats
    from scipy.stats import normaltest, jarque_bera, shapiro
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available - some statistical tests will be disabled")

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available - ML features will be disabled")


class StatisticalSignificanceTester:
    """Statistical significance testing for trading patterns."""
    
    @staticmethod
    def t_test_means(group1: pd.Series, group2: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Perform two-sample t-test to compare means.
        
        Args:
            group1: First group of returns/values
            group2: Second group of returns/values
            alpha: Significance level (default: 0.05)
            
        Returns:
            Dictionary with test results
        """
        if not SCIPY_AVAILABLE:
            return {'error': 'scipy not available'}
        
        # Remove NaN values
        clean1 = group1.dropna()
        clean2 = group2.dropna()
        
        if len(clean1) < 2 or len(clean2) < 2:
            return {'error': 'Insufficient data for t-test'}
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(clean1, clean2)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(clean1) - 1) * clean1.var() + 
                             (len(clean2) - 1) * clean2.var()) / 
                            (len(clean1) + len(clean2) - 2))
        cohens_d = (clean1.mean() - clean2.mean()) / pooled_std
        
        return {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < alpha,
            'cohens_d': float(cohens_d),
            'effect_size': 'large' if abs(cohens_d) > 0.8 else 'medium' if abs(cohens_d) > 0.5 else 'small',
            'group1_mean': float(clean1.mean()),
            'group2_mean': float(clean2.mean()),
            'group1_std': float(clean1.std()),
            'group2_std': float(clean2.std()),
            'sample_sizes': (len(clean1), len(clean2))
        }
    
    @staticmethod
    def normality_tests(series: pd.Series) -> Dict[str, Any]:
        """
        Test for normality using multiple tests.
        
        Args:
            series: Time series to test
            
        Returns:
            Dictionary with normality test results
        """
        if not SCIPY_AVAILABLE:
            return {'error': 'scipy not available'}
        
        clean_series = series.dropna()
        if len(clean_series) < 8:
            return {'error': 'Insufficient data for normality tests'}
        
        results = {}
        
        # Shapiro-Wilk test (best for small samples)
        if len(clean_series) <= 5000:
            shapiro_stat, shapiro_p = shapiro(clean_series)
            results['shapiro'] = {
                'statistic': float(shapiro_stat),
                'p_value': float(shapiro_p),
                'normal': shapiro_p > 0.05
            }
        
        # Jarque-Bera test
        jb_stat, jb_p = jarque_bera(clean_series)
        results['jarque_bera'] = {
            'statistic': float(jb_stat),
            'p_value': float(jb_p),
            'normal': jb_p > 0.05
        }
        
        # D'Agostino and Pearson's test
        dagostino_stat, dagostino_p = normaltest(clean_series)
        results['dagostino_pearson'] = {
            'statistic': float(dagostino_stat),
            'p_value': float(dagostino_p),
            'normal': dagostino_p > 0.05
        }
        
        # Overall assessment
        normal_tests = [v['normal'] for v in results.values()]
        results['overall_normal'] = sum(normal_tests) >= len(normal_tests) / 2
        
        return results
    
    @staticmethod
    def confidence_interval(series: pd.Series, confidence: float = 0.95) -> Dict[str, float]:
        """
        Calculate confidence interval for a series.
        
        Args:
            series: Time series
            confidence: Confidence level (default: 0.95)
            
        Returns:
            Dictionary with confidence interval bounds
        """
        clean_series = series.dropna()
        if len(clean_series) < 2:
            return {'error': 'Insufficient data'}
        
        mean = clean_series.mean()
        std = clean_series.std()
        n = len(clean_series)
        
        # Calculate standard error
        se = std / np.sqrt(n)
        
        # Calculate critical value
        alpha = 1 - confidence
        if SCIPY_AVAILABLE:
            critical_value = stats.t.ppf(1 - alpha/2, n - 1)
        else:
            # Approximate with normal distribution for large samples
            critical_value = 1.96 if confidence == 0.95 else 2.576 if confidence == 0.99 else 1.645
        
        margin_of_error = critical_value * se
        
        return {
            'mean': float(mean),
            'lower_bound': float(mean - margin_of_error),
            'upper_bound': float(mean + margin_of_error),
            'margin_of_error': float(margin_of_error),
            'confidence_level': confidence,
            'sample_size': n
        }


class CorrelationAnalyzer:
    """Cross-asset correlation analysis and lead-lag detection."""
    
    @staticmethod
    def cross_asset_correlation(price_data: Dict[str, pd.DataFrame], 
                              window: int = 20) -> pd.DataFrame:
        """
        Calculate rolling correlation matrix between assets.
        
        Args:
            price_data: Dictionary of {asset: DataFrame} with 'close' column
            window: Rolling window size
            
        Returns:
            DataFrame with rolling correlations
        """
        if len(price_data) < 2:
            return pd.DataFrame()
        
        # Extract close prices
        close_prices = {}
        for asset, df in price_data.items():
            if 'close' in df.columns:
                close_prices[asset] = df.set_index('time')['close']
        
        # Align all series to common index
        aligned_data = pd.DataFrame(close_prices)
        aligned_data = aligned_data.dropna()
        
        if len(aligned_data) < window:
            return pd.DataFrame()
        
        # Calculate rolling correlations
        corr_matrix = aligned_data.rolling(window=window).corr()
        
        return corr_matrix
    
    @staticmethod
    def lead_lag_analysis(series1: pd.Series, series2: pd.Series, 
                         max_lag: int = 10) -> Dict[str, Any]:
        """
        Analyze lead-lag relationship between two time series.
        
        Args:
            series1: First time series
            series2: Second time series
            max_lag: Maximum lag to test
            
        Returns:
            Dictionary with lead-lag analysis results
        """
        # Align series
        aligned = pd.DataFrame({'series1': series1, 'series2': series2}).dropna()
        
        if len(aligned) < max_lag + 10:
            return {'error': 'Insufficient data for lead-lag analysis'}
        
        correlations = {}
        
        # Test different lags
        for lag in range(-max_lag, max_lag + 1):
            if lag == 0:
                corr = aligned['series1'].corr(aligned['series2'])
            elif lag > 0:
                # series1 leads series2
                corr = aligned['series1'].shift(-lag).corr(aligned['series2'])
            else:
                # series2 leads series1
                corr = aligned['series1'].corr(aligned['series2'].shift(lag))
            
            correlations[lag] = corr
        
        # Find best correlation
        best_lag = max(correlations.keys(), key=lambda k: abs(correlations[k]))
        best_corr = correlations[best_lag]
        
        return {
            'correlations': correlations,
            'best_lag': best_lag,
            'best_correlation': float(best_corr),
            'series1_leads': best_lag > 0,
            'series2_leads': best_lag < 0,
            'simultaneous': best_lag == 0
        }


class VolatilityAnalyzer:
    """Volatility clustering and GARCH modeling."""
    
    @staticmethod
    def calculate_garch_volatility(returns: pd.Series, 
                                 p: int = 1, q: int = 1) -> Dict[str, Any]:
        """
        Calculate GARCH volatility (simplified implementation).
        
        Args:
            returns: Return series
            p: GARCH order
            q: ARCH order
            
        Returns:
            Dictionary with GARCH results
        """
        if not SCIPY_AVAILABLE:
            return {'error': 'scipy not available for GARCH modeling'}
        
        clean_returns = returns.dropna()
        if len(clean_returns) < 50:
            return {'error': 'Insufficient data for GARCH modeling'}
        
        # Simple GARCH(1,1) implementation
        # This is a simplified version - for production use, consider arch package
        
        # Initialize parameters
        omega = 0.01  # Constant
        alpha = 0.1   # ARCH coefficient
        beta = 0.85   # GARCH coefficient
        
        # Calculate squared returns
        returns_sq = clean_returns ** 2
        
        # Initialize variance
        variance = np.zeros(len(clean_returns))
        variance[0] = returns_sq.var()
        
        # GARCH recursion
        for t in range(1, len(clean_returns)):
            variance[t] = omega + alpha * returns_sq.iloc[t-1] + beta * variance[t-1]
        
        # Calculate volatility
        volatility = np.sqrt(variance)
        
        return {
            'volatility': pd.Series(volatility, index=clean_returns.index),
            'variance': pd.Series(variance, index=clean_returns.index),
            'parameters': {'omega': omega, 'alpha': alpha, 'beta': beta},
            'mean_volatility': float(np.mean(volatility)),
            'volatility_of_volatility': float(np.std(volatility))
        }
    
    @staticmethod
    def detect_volatility_clustering(returns: pd.Series, 
                                   window: int = 20) -> Dict[str, Any]:
        """
        Detect volatility clustering using rolling standard deviation.
        
        Args:
            returns: Return series
            window: Rolling window size
            
        Returns:
            Dictionary with clustering analysis
        """
        clean_returns = returns.dropna()
        if len(clean_returns) < window * 2:
            return {'error': 'Insufficient data for clustering analysis'}
        
        # Calculate rolling volatility
        rolling_vol = clean_returns.rolling(window=window).std()
        
        # Identify high/low volatility periods
        vol_threshold = rolling_vol.quantile(0.75)
        high_vol_periods = rolling_vol > vol_threshold
        
        # Calculate clustering statistics
        high_vol_runs = []
        current_run = 0
        
        for is_high in high_vol_periods:
            if is_high:
                current_run += 1
            else:
                if current_run > 0:
                    high_vol_runs.append(current_run)
                    current_run = 0
        
        if current_run > 0:
            high_vol_runs.append(current_run)
        
        return {
            'rolling_volatility': rolling_vol,
            'high_vol_periods': high_vol_periods,
            'volatility_threshold': float(vol_threshold),
            'high_vol_runs': high_vol_runs,
            'avg_high_vol_run_length': float(np.mean(high_vol_runs)) if high_vol_runs else 0,
            'max_high_vol_run_length': int(np.max(high_vol_runs)) if high_vol_runs else 0,
            'clustering_detected': len(high_vol_runs) > 0
        }


class RegimeDetector:
    """Market regime detection using machine learning."""
    
    @staticmethod
    def detect_trending_vs_ranging(prices: pd.Series, 
                                 window: int = 20,
                                 threshold: float = 0.02) -> Dict[str, Any]:
        """
        Detect trending vs ranging market regimes.
        
        Args:
            prices: Price series
            window: Window for trend calculation
            threshold: Threshold for trend strength
            
        Returns:
            Dictionary with regime detection results
        """
        if len(prices) < window * 2:
            return {'error': 'Insufficient data for regime detection'}
        
        # Calculate rolling statistics
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        
        # Calculate trend strength
        price_change = prices.pct_change(window)
        trend_strength = abs(price_change)
        
        # Classify regimes
        regimes = pd.Series('ranging', index=prices.index)
        regimes[trend_strength > threshold] = 'trending'
        
        # Calculate regime statistics
        regime_counts = regimes.value_counts()
        regime_percentages = regimes.value_counts(normalize=True) * 100
        
        return {
            'regimes': regimes,
            'trend_strength': trend_strength,
            'regime_counts': regime_counts.to_dict(),
            'regime_percentages': regime_percentages.to_dict(),
            'trending_periods': regimes[regimes == 'trending'].index.tolist(),
            'ranging_periods': regimes[regimes == 'ranging'].index.tolist(),
            'threshold_used': threshold
        }
    
    @staticmethod
    def ml_regime_detection(features: pd.DataFrame, 
                          n_regimes: int = 2) -> Dict[str, Any]:
        """
        Use machine learning to detect market regimes.
        
        Args:
            features: DataFrame with features (returns, volatility, volume, etc.)
            n_regimes: Number of regimes to detect
            
        Returns:
            Dictionary with ML regime detection results
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'scikit-learn not available for ML regime detection'}
        
        if len(features) < 50:
            return {'error': 'Insufficient data for ML regime detection'}
        
        # Prepare features
        clean_features = features.dropna()
        if len(clean_features) < 50:
            return {'error': 'Insufficient clean data for ML regime detection'}
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(clean_features)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_regimes, random_state=42, n_init=10)
        regime_labels = kmeans.fit_predict(scaled_features)
        
        # Create regime series
        regimes = pd.Series(regime_labels, index=clean_features.index)
        
        # Calculate regime characteristics
        regime_stats = {}
        for regime in range(n_regimes):
            regime_data = clean_features[regimes == regime]
            regime_stats[f'regime_{regime}'] = {
                'count': len(regime_data),
                'percentage': len(regime_data) / len(clean_features) * 100,
                'mean_returns': float(regime_data.mean().mean()) if 'returns' in regime_data.columns else None,
                'mean_volatility': float(regime_data.std().mean()),
                'features_mean': regime_data.mean().to_dict()
            }
        
        return {
            'regimes': regimes,
            'regime_stats': regime_stats,
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'inertia': float(kmeans.inertia_),
            'n_regimes': n_regimes
        }


class PatternRecognizer:
    """Pattern recognition and anomaly detection."""
    
    @staticmethod
    def detect_anomalies(series: pd.Series, 
                        method: str = 'iqr',
                        threshold: float = 1.5) -> Dict[str, Any]:
        """
        Detect anomalies in a time series.
        
        Args:
            series: Time series to analyze
            method: Detection method ('iqr', 'zscore', 'isolation')
            threshold: Threshold for anomaly detection
            
        Returns:
            Dictionary with anomaly detection results
        """
        clean_series = series.dropna()
        if len(clean_series) < 10:
            return {'error': 'Insufficient data for anomaly detection'}
        
        anomalies = pd.Series(False, index=clean_series.index)
        
        if method == 'iqr':
            # Interquartile Range method
            Q1 = clean_series.quantile(0.25)
            Q3 = clean_series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            anomalies = (clean_series < lower_bound) | (clean_series > upper_bound)
            
        elif method == 'zscore':
            # Z-score method
            z_scores = np.abs((clean_series - clean_series.mean()) / clean_series.std())
            anomalies = z_scores > threshold
            
        elif method == 'isolation' and SKLEARN_AVAILABLE:
            # Isolation Forest (if sklearn available)
            from sklearn.ensemble import IsolationForest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(clean_series.values.reshape(-1, 1))
            anomalies = pd.Series(anomaly_labels == -1, index=clean_series.index)
        
        anomaly_data = clean_series[anomalies]
        
        return {
            'anomalies': anomalies,
            'anomaly_data': anomaly_data,
            'anomaly_count': int(anomalies.sum()),
            'anomaly_percentage': float(anomalies.mean() * 100),
            'method_used': method,
            'threshold_used': threshold
        }
    
    @staticmethod
    def detect_support_resistance(highs: pd.Series, lows: pd.Series,
                                window: int = 20,
                                min_touches: int = 2) -> Dict[str, Any]:
        """
        Detect support and resistance levels.
        
        Args:
            highs: High prices
            lows: Low prices
            window: Window for level detection
            min_touches: Minimum touches to confirm level
            
        Returns:
            Dictionary with support/resistance levels
        """
        if len(highs) < window or len(lows) < window:
            return {'error': 'Insufficient data for support/resistance detection'}
        
        # Find local maxima and minima
        high_peaks = highs.rolling(window=window, center=True).max() == highs
        low_troughs = lows.rolling(window=window, center=True).min() == lows
        
        # Extract peak and trough values
        resistance_levels = highs[high_peaks].dropna()
        support_levels = lows[low_troughs].dropna()
        
        # Group similar levels
        def group_levels(levels, tolerance=0.01):
            if len(levels) == 0:
                return []
            
            levels = sorted(levels)
            groups = []
            current_group = [levels[0]]
            
            for level in levels[1:]:
                if abs(level - current_group[-1]) / current_group[-1] <= tolerance:
                    current_group.append(level)
                else:
                    if len(current_group) >= min_touches:
                        groups.append({
                            'level': np.mean(current_group),
                            'touches': len(current_group),
                            'values': current_group
                        })
                    current_group = [level]
            
            if len(current_group) >= min_touches:
                groups.append({
                    'level': np.mean(current_group),
                    'touches': len(current_group),
                    'values': current_group
                })
            
            return groups
        
        resistance_groups = group_levels(resistance_levels.tolist())
        support_groups = group_levels(support_levels.tolist())
        
        return {
            'resistance_levels': resistance_groups,
            'support_levels': support_groups,
            'resistance_count': len(resistance_groups),
            'support_count': len(support_groups),
            'window_used': window,
            'min_touches_required': min_touches
        }


class RiskMetrics:
    """Risk metrics calculation."""
    
    @staticmethod
    def calculate_var(returns: pd.Series, 
                     confidence_level: float = 0.05) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Return series
            confidence_level: VaR confidence level (default: 5%)
            
        Returns:
            Dictionary with VaR metrics
        """
        clean_returns = returns.dropna()
        if len(clean_returns) < 30:
            return {'error': 'Insufficient data for VaR calculation'}
        
        # Historical VaR
        historical_var = np.percentile(clean_returns, confidence_level * 100)
        
        # Parametric VaR (assuming normal distribution)
        mean_return = clean_returns.mean()
        std_return = clean_returns.std()
        parametric_var = mean_return + std_return * stats.norm.ppf(confidence_level)
        
        return {
            'historical_var': float(historical_var),
            'parametric_var': float(parametric_var),
            'confidence_level': confidence_level,
            'sample_size': len(clean_returns)
        }
    
    @staticmethod
    def calculate_max_drawdown(returns: pd.Series) -> Dict[str, Any]:
        """
        Calculate maximum drawdown.
        
        Args:
            returns: Return series
            
        Returns:
            Dictionary with drawdown metrics
        """
        clean_returns = returns.dropna()
        if len(clean_returns) < 2:
            return {'error': 'Insufficient data for drawdown calculation'}
        
        # Calculate cumulative returns
        cumulative = (1 + clean_returns).cumprod()
        
        # Calculate running maximum
        running_max = cumulative.expanding().max()
        
        # Calculate drawdown
        drawdown = (cumulative - running_max) / running_max
        
        # Find maximum drawdown
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()
        
        # Find recovery date
        recovery_date = None
        if max_dd_date is not None:
            recovery_mask = cumulative.loc[max_dd_date:] >= cumulative.loc[max_dd_date]
            recovery_dates = cumulative.loc[max_dd_date:][recovery_mask].index
            if len(recovery_dates) > 1:
                recovery_date = recovery_dates[1]  # First date after max_dd_date
        
        return {
            'max_drawdown': float(max_dd),
            'max_drawdown_date': max_dd_date,
            'recovery_date': recovery_date,
            'drawdown_duration': (recovery_date - max_dd_date).days if recovery_date else None,
            'current_drawdown': float(drawdown.iloc[-1])
        }
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, 
                             risk_free_rate: float = 0.02) -> Dict[str, float]:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate (default: 2%)
            
        Returns:
            Dictionary with Sharpe ratio metrics
        """
        clean_returns = returns.dropna()
        if len(clean_returns) < 30:
            return {'error': 'Insufficient data for Sharpe ratio calculation'}
        
        # Calculate excess returns
        excess_returns = clean_returns - risk_free_rate / 252  # Daily risk-free rate
        
        # Calculate Sharpe ratio
        sharpe_ratio = excess_returns.mean() / clean_returns.std() * np.sqrt(252)
        
        return {
            'sharpe_ratio': float(sharpe_ratio),
            'annualized_return': float(clean_returns.mean() * 252),
            'annualized_volatility': float(clean_returns.std() * np.sqrt(252)),
            'risk_free_rate': risk_free_rate,
            'sample_size': len(clean_returns)
        }


def create_analytics_summary(data: pd.DataFrame, 
                           product: str,
                           analysis_type: str = 'comprehensive') -> Dict[str, Any]:
    """
    Create a comprehensive analytics summary.
    
    Args:
        data: DataFrame with OHLCV data
        product: Product name
        analysis_type: Type of analysis ('comprehensive', 'basic', 'risk')
        
    Returns:
        Dictionary with analytics summary
    """
    if data.empty:
        return {'error': 'No data provided'}
    
    # Calculate basic metrics
    if 'close' in data.columns and 'open' in data.columns:
        returns = (data['close'] - data['open']) / data['open']
    else:
        returns = pd.Series(dtype=float)
    
    summary = {
        'product': product,
        'analysis_type': analysis_type,
        'data_points': len(data),
        'date_range': {
            'start': data.index.min().strftime('%Y-%m-%d') if hasattr(data.index.min(), 'strftime') else str(data.index.min()),
            'end': data.index.max().strftime('%Y-%m-%d') if hasattr(data.index.max(), 'strftime') else str(data.index.max())
        }
    }
    
    if not returns.empty:
        # Basic statistics
        summary['basic_stats'] = {
            'mean_return': float(returns.mean()),
            'std_return': float(returns.std()),
            'min_return': float(returns.min()),
            'max_return': float(returns.max()),
            'skewness': float(returns.skew()),
            'kurtosis': float(returns.kurtosis())
        }
        
        # Risk metrics
        if analysis_type in ['comprehensive', 'risk']:
            var_results = RiskMetrics.calculate_var(returns)
            drawdown_results = RiskMetrics.calculate_max_drawdown(returns)
            sharpe_results = RiskMetrics.calculate_sharpe_ratio(returns)
            
            summary['risk_metrics'] = {
                'var': var_results,
                'max_drawdown': drawdown_results,
                'sharpe_ratio': sharpe_results
            }
        
        # Statistical tests
        if analysis_type == 'comprehensive' and SCIPY_AVAILABLE:
            normality_results = StatisticalSignificanceTester.normality_tests(returns)
            confidence_interval = StatisticalSignificanceTester.confidence_interval(returns)
            
            summary['statistical_tests'] = {
                'normality': normality_results,
                'confidence_interval': confidence_interval
            }
        
        # Volatility analysis
        if analysis_type == 'comprehensive':
            vol_clustering = VolatilityAnalyzer.detect_volatility_clustering(returns)
            summary['volatility_analysis'] = vol_clustering
        
        # Pattern recognition
        if analysis_type == 'comprehensive' and 'high' in data.columns and 'low' in data.columns:
            anomalies = PatternRecognizer.detect_anomalies(returns)
            support_resistance = PatternRecognizer.detect_support_resistance(
                data['high'], data['low']
            )
            summary['pattern_analysis'] = {
                'anomalies': anomalies,
                'support_resistance': support_resistance
            }
    
    return summary
