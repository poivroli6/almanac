# ML Architecture for Almanac Futures

## 🎯 Overview

Your current structure is **ideal** for ML integration. This document outlines how to extend it.

---

## 🏗️ **Proposed ML Structure**

### **Phase 1: Feature Engineering** (Extend `features/`)

```python
# almanac/features/ml_features.py

def compute_early_session_features(df_minute, cutoff_time='10:15'):
    """
    Extract features from first 45 minutes of trading.
    
    Features:
    - Overnight gap (%)
    - First hour range (% of ATR)
    - First hour volume (vs 10-day avg)
    - Cumulative delta (volume)
    - Number of HOD/LOD tests
    - Price vs VWAP
    """
    pass

def compute_cross_asset_features(primary_df, secondary_dfs):
    """
    Features from related markets.
    
    Features:
    - VIX early move
    - USD index direction
    - 10Y yield change
    - Crude oil session return
    """
    pass

def compute_regime_features(df_daily):
    """
    Market regime indicators.
    
    Features:
    - ATR percentile rank (252d)
    - Days since HOD/LOD
    - Trend strength (ADX)
    - Volatility regime (rolling Garman-Klass)
    """
    pass
```

---

### **Phase 2: ML Module** (New `ml/`)

#### **`ml/labelers.py`** - Generate Training Labels

```python
class DayArchetypeLabeler:
    """
    Multi-class labels: TrendUp, TrendDown, Range, Reversal
    """
    
    def label_by_range_completion(self, df_daily):
        """
        TrendUp: Close in top 33% of range
        TrendDown: Close in bottom 33%
        Range: Close in middle 33%
        """
        pass
    
    def label_by_intraday_structure(self, df_minute):
        """
        Reversal: Open and close on opposite ends of range
        Trend: Directional move with few retracements
        Range: Multiple tests of highs/lows
        """
        pass

class BinaryLabeler:
    """
    Simple: Close > Open (1) or Close < Open (0)
    """
    
    def label_direction(self, df_daily):
        return (df_daily['close'] > df_daily['open']).astype(int)
```

---

#### **`ml/models.py`** - Model Definitions

```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import lightgbm as lgb
import xgboost as xgb

class ModelFactory:
    """Factory for creating models with consistent interfaces."""
    
    @staticmethod
    def create_logistic(params=None):
        """
        Baseline: Fast, interpretable.
        Good for: Understanding feature importance
        """
        default = {'max_iter': 1000, 'random_state': 42}
        params = params or default
        return LogisticRegression(**params)
    
    @staticmethod
    def create_lightgbm(params=None):
        """
        Production: Fast training, good performance.
        Good for: Daily predictions
        """
        default = {
            'num_leaves': 31,
            'learning_rate': 0.05,
            'n_estimators': 100,
            'random_state': 42
        }
        params = params or default
        return lgb.LGBMClassifier(**params)
    
    @staticmethod
    def create_xgboost(params=None):
        """
        Best performance: Slower but accurate.
        Good for: Critical decisions
        """
        default = {
            'max_depth': 6,
            'learning_rate': 0.05,
            'n_estimators': 100,
            'random_state': 42
        }
        params = params or default
        return xgb.XGBClassifier(**params)
```

---

#### **`ml/trainers.py`** - Training Pipelines

```python
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import joblib

class ModelTrainer:
    """
    Train models with proper time-series validation.
    """
    
    def __init__(self, model, scaler=None):
        self.model = model
        self.scaler = scaler or StandardScaler()
    
    def train_walk_forward(self, X, y, n_splits=5):
        """
        Walk-forward validation (no lookahead bias).
        
        Example: 5 splits on 2 years
        - Split 1: Train 0-8mo, Test 8-10mo
        - Split 2: Train 0-12mo, Test 12-14mo
        - etc.
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        scores = []
        
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            score = self.model.score(X_test_scaled, y_test)
            scores.append(score)
        
        return scores
    
    def train_final(self, X, y):
        """Train on all data for production."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def save(self, path):
        """Save model and scaler."""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, path)
```

---

#### **`ml/predictors.py`** - Inference

```python
class ModelPredictor:
    """
    Make predictions with trained models.
    """
    
    def __init__(self, model_path):
        self.checkpoint = joblib.load(model_path)
        self.model = self.checkpoint['model']
        self.scaler = self.checkpoint['scaler']
    
    def predict_proba(self, X):
        """Return class probabilities."""
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)
    
    def predict_with_confidence(self, X, threshold=0.6):
        """
        Only predict if confidence > threshold.
        """
        proba = self.predict_proba(X)
        max_proba = proba.max(axis=1)
        
        predictions = self.model.predict(self.scaler.transform(X))
        predictions[max_proba < threshold] = -1  # "No prediction"
        
        return predictions, max_proba
```

---

#### **`ml/evaluators.py`** - Metrics & Analysis

```python
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import shap

class ModelEvaluator:
    """
    Comprehensive model evaluation.
    """
    
    def evaluate_classification(self, y_true, y_pred, y_proba=None):
        """
        Standard classification metrics.
        """
        metrics = {
            'accuracy': (y_true == y_pred).mean(),
            'confusion_matrix': confusion_matrix(y_true, y_pred),
            'classification_report': classification_report(y_true, y_pred)
        }
        
        if y_proba is not None and len(np.unique(y_true)) == 2:
            metrics['roc_auc'] = roc_auc_score(y_true, y_proba[:, 1])
        
        return metrics
    
    def compute_shap_values(self, model, X, background_samples=100):
        """
        SHAP values for interpretability.
        """
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        return shap_values
    
    def detect_concept_drift(self, model, X_windows, y_windows):
        """
        Rolling AUC to detect model degradation.
        """
        rolling_scores = []
        for X_window, y_window in zip(X_windows, y_windows):
            score = model.score(X_window, y_window)
            rolling_scores.append(score)
        
        return rolling_scores
```

---

#### **`ml/backtester.py`** - Strategy Validation

```python
class MLBacktester:
    """
    Test ML predictions as a trading strategy.
    """
    
    def __init__(self, predictor):
        self.predictor = predictor
    
    def backtest_signals(self, df_daily, features_df, threshold=0.6):
        """
        Generate signals and compute equity curve.
        """
        # Get predictions
        predictions, confidence = self.predictor.predict_with_confidence(
            features_df, threshold=threshold
        )
        
        # Calculate returns
        df_daily['signal'] = predictions
        df_daily['confidence'] = confidence
        df_daily['strategy_return'] = df_daily['day_return'] * df_daily['signal']
        
        # Metrics
        equity_curve = (1 + df_daily['strategy_return']).cumprod()
        sharpe = df_daily['strategy_return'].mean() / df_daily['strategy_return'].std() * np.sqrt(252)
        max_dd = (equity_curve / equity_curve.cummax() - 1).min()
        
        return {
            'equity_curve': equity_curve,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'total_trades': (df_daily['signal'] != 0).sum(),
            'win_rate': (df_daily[df_daily['signal'] != 0]['strategy_return'] > 0).mean()
        }
```

---

## 📊 **ML Workflow**

### **Step 1: Feature Engineering**
```python
from almanac.data_sources import load_daily_data, load_minute_data
from almanac.features.ml_features import compute_early_session_features

# Load data
daily = load_daily_data('ES', '2020-01-01', '2024-12-31')
minute = load_minute_data('ES', '2020-01-01', '2024-12-31')

# Generate features (before 10:15 AM)
features = compute_early_session_features(minute, cutoff_time='10:15')
```

### **Step 2: Label Generation**
```python
from almanac.ml.labelers import BinaryLabeler

labeler = BinaryLabeler()
labels = labeler.label_direction(daily)
```

### **Step 3: Train Model**
```python
from almanac.ml.models import ModelFactory
from almanac.ml.trainers import ModelTrainer

model = ModelFactory.create_lightgbm()
trainer = ModelTrainer(model)

# Walk-forward validation
scores = trainer.train_walk_forward(features, labels, n_splits=5)
print(f"CV Scores: {scores}")
print(f"Mean CV Score: {np.mean(scores):.3f}")

# Train final model
trainer.train_final(features, labels)
trainer.save('models/es_classifier_v1.pkl')
```

### **Step 4: Evaluate**
```python
from almanac.ml.evaluators import ModelEvaluator

evaluator = ModelEvaluator()
metrics = evaluator.evaluate_classification(y_test, y_pred, y_proba)
shap_values = evaluator.compute_shap_values(model, X_test)
```

### **Step 5: Backtest**
```python
from almanac.ml.predictors import ModelPredictor
from almanac.ml.backtester import MLBacktester

predictor = ModelPredictor('models/es_classifier_v1.pkl')
backtester = MLBacktester(predictor)

results = backtester.backtest_signals(daily, features, threshold=0.6)
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Win Rate: {results['win_rate']:.1%}")
```

---

## 🎨 **UI Integration** (`pages/ml_lab.py`)

```python
# New page for ML experimentation

layout = html.Div([
    html.H2("ML Laboratory"),
    
    # Section 1: Feature Engineering
    html.Div([
        html.H3("1. Feature Engineering"),
        dcc.Dropdown(id='feature-sets', 
                     options=['Early Session', 'Cross-Asset', 'Regime']),
        dcc.Graph(id='feature-importance-chart')
    ]),
    
    # Section 2: Model Training
    html.Div([
        html.H3("2. Model Training"),
        dcc.Dropdown(id='model-type', 
                     options=['Logistic', 'LightGBM', 'XGBoost']),
        html.Button('Train Model', id='train-btn'),
        dcc.Graph(id='cv-scores-chart')
    ]),
    
    # Section 3: Evaluation
    html.Div([
        html.H3("3. Model Evaluation"),
        dcc.Graph(id='confusion-matrix'),
        dcc.Graph(id='shap-summary'),
        dcc.Graph(id='drift-monitor')
    ]),
    
    # Section 4: Backtesting
    html.Div([
        html.H3("4. Strategy Backtest"),
        dcc.Graph(id='equity-curve'),
        html.Div(id='metrics-table')
    ])
])
```

---

## ✅ **Why Your Current Structure is Perfect**

### **1. Data Layer is Clean** ✅
- File-based = easy batch processing
- No database locks during training
- Version control friendly

### **2. Feature Module Exists** ✅
- Just extend with `ml_features.py`
- Reuse existing stats functions
- HOD/LOD detection already built

### **3. Modular = Testable** ✅
- ML module can be unit tested independently
- Mock data sources for tests
- Reproducible experiments

### **4. Visualization Ready** ✅
- Extend `viz/` for ML plots
- SHAP, confusion matrix, equity curves
- Existing chart infrastructure

---

## 🎯 **Recommended Implementation Order**

### **Week 1: Foundation**
1. Create `ml/` module structure
2. Implement `ml_features.py` (early session features)
3. Implement `labelers.py` (binary classifier)

### **Week 2: Training**
4. Implement `models.py` (ModelFactory)
5. Implement `trainers.py` (walk-forward validation)
6. Train first model (Logistic Regression)

### **Week 3: Evaluation**
7. Implement `evaluators.py` (metrics, SHAP)
8. Add `ml_plots.py` (visualization)
9. Test for concept drift

### **Week 4: Production**
10. Implement `predictors.py` (inference)
11. Implement `backtester.py` (strategy testing)
12. Add ML Lab page to UI

---

## 📦 **Additional Dependencies**

Add to `requirements.txt`:

```txt
# ML Libraries
scikit-learn>=1.3.0
lightgbm>=4.0.0
xgboost>=2.0.0
shap>=0.43.0

# Optional: Deep Learning (if needed later)
# torch>=2.0.0
# tensorflow>=2.13.0
```

---

## 🔒 **Best Practices for ML**

### **1. Avoid Lookahead Bias**
```python
# BAD: Using EOD data to predict EOD
features = compute_features(df_full_day)
labels = label_direction(df_full_day)

# GOOD: Using 10:15 AM data to predict EOD
features = compute_features(df_minute[df_minute.time < '10:15'])
labels = label_direction(df_daily)  # EOD close
```

### **2. Walk-Forward Validation**
```python
# BAD: Random k-fold (breaks time order)
from sklearn.model_selection import KFold

# GOOD: Time-series split (respects time)
from sklearn.model_selection import TimeSeriesSplit
```

### **3. Feature Lineage**
```python
# Track which data generated each feature
feature_metadata = {
    'gap_pct': {'source': 'daily', 'as_of': 'market_open'},
    'first_hour_range': {'source': 'minute', 'as_of': '10:30'},
}
```

### **4. Model Versioning**
```python
# models/model_registry.json
{
    "es_classifier_v1": {
        "trained_date": "2025-02-01",
        "data_range": "2020-2024",
        "cv_score": 0.57,
        "feature_set": "early_session_v1"
    }
}
```

---

## 🎉 **Summary**

### **Your Current Structure:** ✅ PERFECT
- Modular, testable, extensible
- File-based data ideal for ML
- Features module ready to expand

### **To Add for ML:**
```
ml/              # New module
features/ml_features.py  # Extend existing
viz/ml_plots.py  # Extend existing
pages/ml_lab.py  # New page
```

### **Implementation:** 4 weeks
- Week 1: Foundation
- Week 2: Training
- Week 3: Evaluation  
- Week 4: Production

**No major refactoring needed - just extend!** 🚀
