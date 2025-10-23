# Comprehensive Debugging System for Almanac Futures

## 🚀 Quick Start

### Enable Debugging
```bash
# Run with full debugging enabled
python run.py --enable-debugging --debug --test-schemas

# Run with debugging but no schema tests
python run.py --enable-debugging --debug

# Run without debugging (original behavior)
python run.py --debug
```

### Debug Endpoints
Once running, access these endpoints for debugging:

- **`http://localhost:8085/status`** - Simple status check
- **`http://localhost:8085/debug/health`** - Comprehensive health check
- **`http://localhost:8085/debug/callbacks`** - Callback statistics
- **`http://localhost:8085/debug/validation`** - Validation report
- **`http://localhost:8085/debug/performance`** - Performance metrics
- **`http://localhost:8085/debug/errors`** - Error history
- **`http://localhost:8085/debug/system`** - System information
- **`http://localhost:8085/debug/export-logs`** - Export debug logs

## 🔧 Debugging Components

### 1. CallbackMonitor
- **Purpose**: Real-time monitoring of callback performance and errors
- **Features**:
  - Tracks execution time for each callback
  - Monitors success/failure rates
  - Records performance history
  - Maintains error counts per callback

### 2. CallbackValidator
- **Purpose**: Validates callback schemas and return values
- **Features**:
  - Ensures output count matches return value count
  - Detects schema mismatches immediately
  - Provides detailed error context
  - Maintains validation error history

### 3. DebugErrorHandler
- **Purpose**: Enhanced error handling with comprehensive context
- **Features**:
  - Wraps all callbacks with error handling
  - Captures full error context (args, kwargs, traceback)
  - Provides safe fallback values
  - Maintains detailed error history

### 4. SchemaDocumenter
- **Purpose**: Generates comprehensive documentation of callback schemas
- **Features**:
  - Documents all registered callbacks
  - Exports schema information to JSON
  - Tracks schema changes over time
  - Provides schema validation reports

### 5. HealthChecker
- **Purpose**: Comprehensive health monitoring
- **Features**:
  - Overall system health assessment
  - Callback performance metrics
  - Error rate monitoring
  - Environment information

### 6. AutomatedTestRunner
- **Purpose**: Automated testing of callback schemas
- **Features**:
  - Validates all callback schemas
  - Tests callback execution with mock data
  - Generates comprehensive test reports
  - Exports test results to JSON

## 📊 Debugging Features

### Real-time Monitoring
- **Callback Execution Tracking**: Monitor every callback execution with timing and success/failure
- **Performance Metrics**: Track average execution time, success rates, and error counts
- **Memory Usage**: Monitor memory consumption during callback execution
- **Error Tracking**: Detailed error history with full context

### Schema Validation
- **Output Count Validation**: Ensures callbacks return the expected number of outputs
- **Type Validation**: Validates output types match expected schema
- **Duplicate Detection**: Detects duplicate outputs in callback schemas
- **Best Practice Validation**: Validates schemas against recommended patterns

### Enhanced Error Handling
- **Context Capture**: Captures full context when errors occur (args, kwargs, traceback)
- **Safe Fallbacks**: Provides safe fallback values when callbacks fail
- **Error Classification**: Categorizes errors by type and frequency
- **Recovery Suggestions**: Provides suggestions for fixing common errors

### Health Monitoring
- **System Health**: Overall health assessment of the application
- **Callback Health**: Individual callback health and performance
- **Resource Monitoring**: CPU, memory, and disk usage tracking
- **Environment Monitoring**: Python version, dependencies, and configuration

## 🧪 Testing Framework

### Automated Schema Tests
```python
# Run schema validation tests
from almanac.debugging.testing_framework import run_quick_schema_test

test_results = run_quick_schema_test(app)
print(f"Tests passed: {test_results['summary']['passed']}")
```

### Manual Testing
```python
# Test individual callback schemas
from almanac.debugging.testing_framework import validate_callback_schema

result = validate_callback_schema('my_callback', outputs, inputs, states)
if result['status'] == 'failed':
    print(f"Schema issues: {result['violations']}")
```

## 📝 Logging System

### Log Files
- **`logs/debug.log`** - All debug information
- **`logs/almanac_YYYYMMDD.log`** - Daily application logs
- **Console Output** - Real-time debug information

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages with full context
- **CRITICAL**: Critical errors that may cause application failure

## 🔍 Common Debugging Scenarios

### 1. Callback Schema Mismatch
**Problem**: `SchemaLengthValidationError: Expected length: 31, Received value of length: 32`

**Debug Steps**:
1. Check `/debug/validation` endpoint for detailed error information
2. Review callback schema in `/debug/callbacks`
3. Check error history in `/debug/errors`
4. Use schema documentation to verify expected outputs

**Solution**: Fix the callback return statement to match the schema

### 2. Performance Issues
**Problem**: Callbacks taking too long to execute

**Debug Steps**:
1. Check `/debug/performance` for execution times
2. Review callback statistics in `/debug/callbacks`
3. Monitor memory usage in `/debug/system`
4. Check for errors that might be causing delays

**Solution**: Optimize callback logic or add caching

### 3. Memory Leaks
**Problem**: Application memory usage increasing over time

**Debug Steps**:
1. Monitor memory usage in `/debug/system`
2. Check for callback errors that might be accumulating data
3. Review performance history for memory trends
4. Export logs for detailed analysis

**Solution**: Fix memory leaks in callback logic

### 4. Callback Errors
**Problem**: Callbacks failing with exceptions

**Debug Steps**:
1. Check `/debug/errors` for recent error history
2. Review error context and traceback information
3. Check callback statistics for error patterns
4. Use health check to assess overall system health

**Solution**: Fix the underlying issue causing the callback to fail

## 🛠️ Advanced Debugging

### Custom Debugging
```python
from almanac.debugging import get_debug_system

# Get debug system instance
debug_system = get_debug_system()

# Get comprehensive debug report
report = debug_system.get_debug_report()

# Access individual components
monitor = debug_system.monitor
validator = debug_system.validator
error_handler = debug_system.error_handler
```

### Debugging in Development
```python
# Enable development mode debugging
import os
os.environ['FLASK_ENV'] = 'development'

# This will automatically enable enhanced debugging features
```

### Exporting Debug Information
```bash
# Export all debug logs
curl http://localhost:8085/debug/export-logs

# This creates a timestamped JSON file with all debug information
```

## 📋 Best Practices

### 1. Always Enable Debugging in Development
```bash
python run.py --enable-debugging --debug
```

### 2. Run Schema Tests Regularly
```bash
python run.py --enable-debugging --test-schemas
```

### 3. Monitor Health Endpoints
- Check `/debug/health` regularly for system health
- Monitor `/debug/performance` for performance trends
- Review `/debug/errors` for error patterns

### 4. Use Logging Effectively
- Check log files for detailed error information
- Use different log levels appropriately
- Export logs for analysis when needed

### 5. Test Callback Changes
- Run schema tests after modifying callbacks
- Validate schemas before deploying changes
- Monitor performance after changes

## 🚨 Troubleshooting

### Debugging System Not Working
1. Check that `--enable-debugging` flag is used
2. Verify all dependencies are installed: `pip install -r requirements-debugging.txt`
3. Check log files for initialization errors
4. Ensure debug endpoints are accessible

### Performance Impact
- Debugging system has minimal performance impact
- Monitor system resources if concerned
- Disable debugging in production if needed

### Memory Usage
- Debugging system uses minimal memory
- Error history is limited to prevent memory leaks
- Export logs regularly to clear history

## 📚 Additional Resources

- **Debug Logs**: Check `logs/debug.log` for detailed information
- **Schema Documentation**: Generated automatically in `callback_schemas.json`
- **Test Results**: Exported to timestamped JSON files
- **Health Reports**: Available via debug endpoints

This comprehensive debugging system will help prevent the types of issues that led to the callback schema validation error and provide ongoing monitoring to catch issues early.
