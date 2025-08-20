# Futures Intraday Almanac

A sophisticated futures market analysis tool that provides comprehensive intraday almanac data, developed by Hughes & Company LLC. This advanced platform offers detailed statistical analysis of futures market behavior across different timeframes, enabling traders to identify patterns and optimize their trading strategies.

## Overview

The Futures Intraday Almanac is a professional-grade analytical tool that examines futures market behavior through advanced statistical analysis. It provides detailed insights into hourly and minute-level market patterns, volatility characteristics, and trading opportunities based on historical data analysis. The system supports multiple futures contracts and offers extensive filtering capabilities for customized analysis.

## Features

### 🚀 **Advanced Market Analysis**
- **Multi-Timeframe Analysis**: Hourly and minute-level statistical breakdowns
- **Futures Contract Support**: ES (E-mini S&P 500), NQ (E-mini NASDAQ), GC (Gold)
- **Historical Data Integration**: SQL Server database connectivity for comprehensive data
- **Real-time Calculations**: Dynamic statistical analysis and visualization

### 📊 **Comprehensive Statistical Metrics**
- **Price Change Analysis**: Percentage change and range statistics
- **Volatility Measurement**: Variance analysis across time periods
- **Volume Analysis**: Relative volume comparisons and thresholds
- **Pattern Recognition**: Day-of-week and market condition patterns

### 🎯 **Advanced Filtering System**
- **Weekday Filters**: Monday through Friday specific analysis
- **Previous Day Conditions**: Open/close and percentage change filters
- **Volume Thresholds**: Relative volume comparison filters
- **Time-based Filters**: Specific time period analysis
- **Extreme Value Trimming**: Top/bottom 5% exclusion options

### 📈 **Interactive Visualizations**
- **Hourly Charts**: Average and variance charts for price changes and ranges
- **Minute Charts**: Detailed minute-level statistical analysis
- **Dynamic Updates**: Real-time chart updates based on filter changes
- **Professional Dashboard**: Clean, trading-focused interface

## Installation

### Prerequisites
- Python 3.8+
- SQL Server with HistoricalData database
- ODBC Driver 17 for SQL Server
- pip package manager

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/klefebvre6/almanac.git
cd almanac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure database connection:**
Update the `DB_CONN_STRING` in `Almanac_main.py` to match your SQL Server setup.

4. **Run the application:**
```bash
python Almanac_main.py
```

5. **Access the dashboard:**
Open your browser and navigate to `http://localhost:8085`

## Project Structure

```
Almanac Futures/
├── Almanac_main.py                  # Main almanac analysis application (16KB)
├── reboot_almanac.bat               # Windows service restart script
├── requirements.txt                  # Python dependencies
├── README.md                         # This documentation
└── .gitignore                        # Git ignore rules
```

## Key Components

### **Almanac_main.py** - Main Application
- **Dash Web Framework**: Modern, responsive web interface
- **SQL Server Integration**: Direct database connectivity for historical data
- **Statistical Engine**: Advanced mathematical calculations and analysis
- **Interactive Controls**: Dynamic filtering and parameter adjustment
- **Professional UI**: Trading-focused dashboard design

### **Supported Futures Contracts**
- **ES**: E-mini S&P 500 Futures
- **NQ**: E-mini NASDAQ-100 Futures
- **GC**: Gold Futures

### **Analysis Capabilities**
- **Intraday Patterns**: Hour-by-hour market behavior analysis
- **Minute-level Detail**: Granular statistical breakdowns
- **Volume Analysis**: Relative volume and threshold comparisons
- **Pattern Recognition**: Day-of-week and market condition patterns

## Usage

### **Dashboard Interface**

1. **Product Selection**: Choose from ES, NQ, or GC futures
2. **Date Range**: Set start and end dates for analysis
3. **Time Selection**: Choose specific hours for minute-level analysis
4. **Filter Configuration**: Apply various market condition filters
5. **Threshold Settings**: Set volume and percentage change thresholds
6. **Time Comparisons**: Configure time A vs. time B analysis

### **Filter Options**

- **Weekday Filters**: Monday, Tuesday, Wednesday, Thursday, Friday
- **Previous Day Conditions**: Positive/negative close vs. open
- **Percentage Thresholds**: Previous day change percentage filters
- **Volume Filters**: Relative volume above/below thresholds
- **Time Comparisons**: Time A vs. Time B price comparisons
- **Extreme Value Trimming**: Exclude top/bottom 5% of data

### **Statistical Output**

- **Hourly Statistics**: Average and variance for price changes and ranges
- **Minute Statistics**: Detailed minute-level breakdowns
- **Summary Information**: Comprehensive analysis overview
- **Filter Results**: Detailed breakdown of filtered data

## Technical Specifications

### **Dependencies**
- **Dash**: Web framework for interactive dashboards
- **Pandas**: Data manipulation and analysis
- **SQLAlchemy**: Database ORM and connection management
- **Plotly**: Interactive charting library
- **pyodbc**: SQL Server connectivity

### **Port Configuration**
- **Default Port**: 8085
- **Development Mode**: Debug enabled for development
- **Host**: Localhost (127.0.0.1)

### **Performance Features**
- **Efficient Data Processing**: Optimized SQL queries and calculations
- **Real-time Analysis**: Dynamic statistical computation
- **Responsive Design**: Mobile-friendly interface
- **Fast Loading**: Minimal dependencies for quick startup

## Data Sources

### **Database Integration**
- **SQL Server**: Primary database platform
- **Historical Data**: Comprehensive futures market data
- **Intraday Data**: 1-minute resolution price and volume data
- **Daily Data**: End-of-day summary statistics

### **Data Types**
- **Price Data**: Open, high, low, close prices
- **Volume Data**: Trading volume and relative volume analysis
- **Time Data**: Hourly and minute-level timestamps
- **Statistical Data**: Variance and average calculations

## Statistical Methodology

### **Calculation Methods**
- **Percentage Changes**: (Close - Open) / Open calculations
- **Range Analysis**: High - Low price ranges
- **Variance Scaling**: Scientific notation scaling for large variances
- **Extreme Trimming**: 5th and 95th percentile exclusions

### **Filtering Logic**
- **Weekday Selection**: Day-of-week specific filtering
- **Previous Day Analysis**: Market condition-based filtering
- **Volume Thresholds**: Relative volume comparison filtering
- **Time-based Comparisons**: Specific time period analysis

## Trading Applications

### **Pattern Recognition**
- **Intraday Patterns**: Hour-by-hour market behavior identification
- **Volatility Analysis**: Time-based volatility pattern recognition
- **Volume Patterns**: Trading volume pattern analysis
- **Day-of-Week Effects**: Weekly pattern identification

### **Strategy Development**
- **Entry Timing**: Optimal entry time identification
- **Risk Management**: Volatility-based risk assessment
- **Position Sizing**: Volume-based position sizing
- **Market Timing**: Pattern-based market timing strategies

## Performance Features

### **Efficient Algorithms**
- **Optimized Queries**: Efficient SQL database queries
- **Vectorized Operations**: Fast NumPy and Pandas calculations
- **Memory Management**: Efficient data handling and processing
- **Real-time Updates**: Live statistical analysis updates

### **User Experience**
- **Interactive Controls**: Dynamic parameter adjustments
- **Visual Feedback**: Comprehensive chart visualizations
- **Responsive Interface**: Professional trading dashboard
- **Mobile Compatibility**: Cross-device accessibility

## Development

### **Code Structure**
- **Modular Design**: Separated concerns for maintainability
- **Clean Architecture**: Clear separation of UI and business logic
- **Error Handling**: Comprehensive error handling and validation
- **Professional Standards**: Production-ready code quality

### **Extensibility**
- **Additional Contracts**: Easy to add new futures contracts
- **New Metrics**: Framework for additional statistical measures
- **Data Sources**: Pluggable data provider architecture
- **UI Components**: Reusable Dash components

## Testing

### **Quality Assurance**
- **Data Validation**: Market data integrity checks
- **Calculation Accuracy**: Statistical algorithm verification
- **Performance Testing**: Load and response time analysis
- **User Interface**: Cross-browser compatibility testing

### **Error Handling**
- **Database Failures**: Graceful handling of connection issues
- **Calculation Errors**: Robust error handling and recovery
- **User Input Validation**: Input parameter validation
- **Fallback Mechanisms**: Alternative calculation methods

## Configuration

### **Environment Variables**
- **Database Connection**: SQL Server connection string
- **Port Configuration**: Application port settings
- **Debug Mode**: Development vs. production settings
- **Host Configuration**: Network access settings

### **Customization Options**
- **Contract Selection**: Configurable futures contract support
- **Filter Options**: Customizable filtering capabilities
- **Statistical Measures**: Additional calculation options
- **UI Themes**: Customizable interface appearance

## Security Features

### **Data Protection**
- **Secure Database Access**: Protected database connections
- **Input Validation**: User input sanitization and validation
- **Access Control**: Network access restrictions
- **Error Handling**: Secure error message handling

### **Network Security**
- **Localhost Binding**: Restricted network access
- **Port Configuration**: Configurable port settings
- **Development Mode**: Debug mode controls
- **Access Logging**: Comprehensive access monitoring

## License

This project is proprietary to Hughes & Company LLC. All rights reserved.

## Contact

For questions, support, or collaboration opportunities:
- **Company**: Hughes & Company LLC
- **Email**: dhughes@hughesandco.ltd
- **Website**: www.hughesandco.ltd

## Disclaimer

This software is for educational and informational purposes only. It does not constitute investment advice. Trading futures involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. The almanac analysis should be used as part of a comprehensive trading strategy and risk management plan.
