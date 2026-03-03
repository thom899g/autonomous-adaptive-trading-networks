"""
Configuration management for the Autonomous Adaptive Trading Network system.
Centralizes all configuration to ensure consistency and easy adjustments.
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import logging
from datetime import timedelta

# Type hints for Firebase config
@dataclass
class FirebaseConfig:
    """Firebase configuration settings"""
    project_id: str = os.getenv("FIREBASE_PROJECT_ID", "trading-nas-system")
    service_account_path: str = os.getenv("FIREBASE_SERVICE_ACCOUNT", "./service_account.json")
    database_url: str = os.getenv("FIREBASE_DATABASE_URL", "")
    max_retries: int = 3
    timeout_seconds: int = 30

@dataclass
class DataConfig:
    """Data source and preprocessing configuration"""
    data_sources: List[str] = field(default_factory=lambda: [
        "ccxt:binance:btc/usdt:1h",
        "ccxt:binance:eth/usdt:1h",
        "ccxt:coinbase:btc/usdt:1h"
    ])
    lookback_window: int = 100
    features: List[str] = field(default_factory=lambda: [
        "open", "high", "low", "close", "volume",
        "rsi_14", "macd", "bb_upper", "bb_lower"
    ])
    validation_split: float = 0.2
    test_split: float = 0.15
    sequence_length: int = 50

@dataclass
class NASConfig:
    """Neural Architecture Search configuration"""
    search_space: Dict[str, Any] = field(default_factory=lambda: {
        "layer_types": ["LSTM", "GRU", "Dense", "Conv1D"],
        "layer_count_range": (1, 10),
        "units_range": (16, 512),
        "activation_functions": ["relu", "tanh", "leaky_relu", "selu"],
        "dropout_range": (0.0, 0.5),
        "learning_rate_range": (1e-4, 1e-2),
        "batch_size_options": [16, 32, 64, 128, 256]
    })
    population_size: int = 20
    generations: int = 50
    mutation_rate: float = 0.3
    crossover_rate: float = 0.7
    elite_size: int = 2
    evaluation_metric: str = "sharpe_ratio"
    
@dataclass
class TradingConfig:
    """Trading-specific configuration"""
    initial_capital: float = 10000.0
    max_position_size: float = 0.2
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    commission_rate: float = 0.001
    risk_free_rate: float = 0.02
    max_drawdown_limit: float = 0.25

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: int = logging.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_path: str = "./logs/trading_nas.log"
    max_file_size_mb: int = 100
    backup_count: int = 5

@dataclass
class SystemConfig:
    """Main system configuration"""
    firebase: FirebaseConfig = field(default_factory=FirebaseConfig)
    data: DataConfig = field(default_factory=DataConfig)
    nas: NASConfig = field(default_factory=NASConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    check_interval_minutes: int = 5
    max_concurrent_evaluations: int = 3
    model_cache_size: int = 10
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Firebase validation
        if not os.path.exists(self.firebase.service_account_path):
            errors.append(f"Firebase service account not found: {self.firebase.service_account_path}")
        
        # Data validation
        if not 0 < self.data.validation_split < 1:
            errors.append(f"Invalid validation split: {self.data.validation_split}")
        if not 0 < self.data.test_split < 1:
            errors.append(f"Invalid test split: {self.data.test_split}")
        if self.data.validation_split + self.data.test_split >= 1:
            errors.append("Validation + test split must be less than 1")
        
        # NAS validation
        if self.nas.population_size < 1:
            errors.append(f"Invalid population size: {self.nas.population_size}")
        if self