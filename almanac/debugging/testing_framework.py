"""
Automated Testing Framework for Almanac Futures

Provides comprehensive testing capabilities for callbacks and schemas.
"""

import unittest
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)


class CallbackTestSuite:
    """Test suite for validating callback schemas and functionality."""
    
    def __init__(self):
        self.test_results = []
        self.mock_data_generator = MockDataGenerator()
    
    def test_callback_schema(self, callback_name: str, outputs: List[Any], inputs: List[Any], states: List[Any] = None) -> Dict[str, Any]:
        """Test that a callback schema is valid."""
        test_result = {
            'test_name': f'test_{callback_name}_schema',
            'callback_name': callback_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'details': {}
        }
        
        try:
            # Test 1: Validate output count
            output_count = len(outputs)
            test_result['details']['output_count'] = output_count
            
            # Test 2: Validate input count
            input_count = len(inputs)
            test_result['details']['input_count'] = input_count
            
            # Test 3: Validate state count
            state_count = len(states) if states else 0
            test_result['details']['state_count'] = state_count
            
            # Test 4: Check for duplicate outputs
            output_ids = [str(o) for o in outputs]
            duplicate_outputs = [x for x in output_ids if output_ids.count(x) > 1]
            test_result['details']['duplicate_outputs'] = duplicate_outputs
            
            # Test 5: Validate output format
            invalid_outputs = []
            for i, output in enumerate(outputs):
                if not hasattr(output, 'component_id') or not hasattr(output, 'component_property'):
                    invalid_outputs.append(f"Output {i}: {output}")
            test_result['details']['invalid_outputs'] = invalid_outputs
            
            # Determine test status
            if duplicate_outputs or invalid_outputs:
                test_result['status'] = 'failed'
                test_result['error'] = f"Schema validation failed: {len(duplicate_outputs)} duplicates, {len(invalid_outputs)} invalid outputs"
            else:
                test_result['status'] = 'passed'
                test_result['message'] = f"Schema validation passed: {output_count} outputs, {input_count} inputs, {state_count} states"
            
        except Exception as e:
            test_result['status'] = 'error'
            test_result['error'] = str(e)
            test_result['traceback'] = traceback.format_exc()
        
        self.test_results.append(test_result)
        return test_result
    
    def test_callback_execution(self, callback_func, mock_inputs: List[Any], expected_output_count: int) -> Dict[str, Any]:
        """Test that a callback executes and returns the expected number of outputs."""
        test_result = {
            'test_name': f'test_{callback_func.__name__}_execution',
            'callback_name': callback_func.__name__,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'details': {}
        }
        
        try:
            # Execute callback with mock inputs
            result = callback_func(*mock_inputs)
            
            # Validate result
            actual_output_count = len(result)
            test_result['details']['expected_count'] = expected_output_count
            test_result['details']['actual_count'] = actual_output_count
            test_result['details']['result_types'] = [type(v).__name__ for v in result]
            
            if actual_output_count == expected_output_count:
                test_result['status'] = 'passed'
                test_result['message'] = f"Execution test passed: returned {actual_output_count} outputs"
            else:
                test_result['status'] = 'failed'
                test_result['error'] = f"Output count mismatch: expected {expected_output_count}, got {actual_output_count}"
            
        except Exception as e:
            test_result['status'] = 'error'
            test_result['error'] = str(e)
            test_result['traceback'] = traceback.format_exc()
        
        self.test_results.append(test_result)
        return test_result
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'passed')
        failed_tests = sum(1 for result in self.test_results if result['status'] == 'failed')
        error_tests = sum(1 for result in self.test_results if result['status'] == 'error')
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'generated_at': datetime.now().isoformat()
        }


class MockDataGenerator:
    """Generates mock data for testing callbacks."""
    
    def __init__(self):
        self.mock_data_cache = {}
    
    def get_mock_inputs_for_callback(self, callback_name: str, input_count: int) -> List[Any]:
        """Generate mock inputs for a specific callback."""
        if callback_name in self.mock_data_cache:
            return self.mock_data_cache[callback_name]
        
        mock_inputs = []
        
        # Generate mock inputs based on callback name patterns
        if 'calc' in callback_name.lower():
            # Calculation callbacks typically have: n_clicks, product, start_date, end_date, filters, etc.
            mock_inputs = [
                1,  # n_clicks
                'ES',  # product
                '2024-01-01',  # start_date
                '2024-01-31',  # end_date
                [],  # filters
                0.5,  # vol_threshold
                0.1,  # pct_threshold
            ]
        elif 'filter' in callback_name.lower():
            # Filter callbacks
            mock_inputs = [
                'ES',  # product
                '2024-01-01',  # start_date
                '2024-01-31',  # end_date
            ]
        elif 'time' in callback_name.lower():
            # Time-related callbacks
            mock_inputs = [
                datetime.now().isoformat(),  # current_time
            ]
        else:
            # Generic mock inputs
            mock_inputs = [None] * input_count
        
        # Ensure we have the right number of inputs
        while len(mock_inputs) < input_count:
            mock_inputs.append(None)
        
        # Truncate if we have too many
        mock_inputs = mock_inputs[:input_count]
        
        self.mock_data_cache[callback_name] = mock_inputs
        return mock_inputs
    
    def get_mock_figure(self) -> Dict[str, Any]:
        """Generate a mock Plotly figure."""
        return {
            'data': [{'x': [1, 2, 3], 'y': [1, 2, 3], 'type': 'scatter'}],
            'layout': {'title': 'Mock Chart'}
        }
    
    def get_mock_html_div(self) -> Dict[str, Any]:
        """Generate a mock HTML div."""
        return {
            'type': 'Div',
            'props': {'children': 'Mock Content'}
        }


class SchemaValidator:
    """Validates callback schemas against expected patterns."""
    
    def __init__(self):
        self.validation_rules = {
            'output_count_range': (1, 50),  # Reasonable range for outputs
            'input_count_range': (0, 20),   # Reasonable range for inputs
            'state_count_range': (0, 10),   # Reasonable range for states
        }
    
    def validate_schema(self, callback_name: str, outputs: List[Any], inputs: List[Any], states: List[Any] = None) -> Dict[str, Any]:
        """Validate a callback schema against best practices."""
        validation_result = {
            'callback_name': callback_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'violations': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check output count
        output_count = len(outputs)
        if not (self.validation_rules['output_count_range'][0] <= output_count <= self.validation_rules['output_count_range'][1]):
            validation_result['violations'].append(
                f"Output count {output_count} outside recommended range {self.validation_rules['output_count_range']}"
            )
        
        # Check input count
        input_count = len(inputs)
        if not (self.validation_rules['input_count_range'][0] <= input_count <= self.validation_rules['input_count_range'][1]):
            validation_result['violations'].append(
                f"Input count {input_count} outside recommended range {self.validation_rules['input_count_range']}"
            )
        
        # Check for duplicate outputs
        output_ids = [str(o) for o in outputs]
        duplicates = [x for x in output_ids if output_ids.count(x) > 1]
        if duplicates:
            validation_result['violations'].append(f"Duplicate outputs: {duplicates}")
        
        # Check for very large schemas
        total_params = output_count + input_count + (len(states) if states else 0)
        if total_params > 30:
            validation_result['warnings'].append(
                f"Large schema with {total_params} total parameters - consider breaking into smaller callbacks"
            )
        
        # Generate recommendations
        if output_count > 20:
            validation_result['recommendations'].append(
                "Consider splitting callback with many outputs into multiple smaller callbacks"
            )
        
        if input_count > 10:
            validation_result['recommendations'].append(
                "Consider using State parameters for less frequently changing inputs"
            )
        
        # Determine overall status
        if validation_result['violations']:
            validation_result['status'] = 'failed'
        elif validation_result['warnings']:
            validation_result['status'] = 'warning'
        else:
            validation_result['status'] = 'passed'
        
        return validation_result


class AutomatedTestRunner:
    """Runs automated tests on all callbacks."""
    
    def __init__(self):
        self.test_suite = CallbackTestSuite()
        self.schema_validator = SchemaValidator()
        self.mock_generator = MockDataGenerator()
    
    def run_all_tests(self, app) -> Dict[str, Any]:
        """Run all automated tests on the app."""
        logger.info("🧪 Starting automated test suite")
        
        test_results = {
            'started_at': datetime.now().isoformat(),
            'schema_tests': [],
            'execution_tests': [],
            'validation_results': [],
            'summary': {}
        }
        
        try:
            # Test all registered callbacks
            for callback_id, callback_info in app.callback_map.items():
                callback_name = callback_info['callback'].__name__
                outputs = callback_info['outputs']
                inputs = callback_info['inputs']
                states = callback_info.get('state', [])
                
                logger.info(f"Testing callback: {callback_name}")
                
                # Schema validation test
                schema_test = self.test_suite.test_callback_schema(callback_name, outputs, inputs, states)
                test_results['schema_tests'].append(schema_test)
                
                # Schema validation against best practices
                validation_result = self.schema_validator.validate_schema(callback_name, outputs, inputs, states)
                test_results['validation_results'].append(validation_result)
                
                # Note: Execution tests would require actual callback functions
                # This would need to be implemented based on your specific callbacks
        
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            test_results['error'] = str(e)
            test_results['traceback'] = traceback.format_exc()
        
        # Generate summary
        test_results['completed_at'] = datetime.now().isoformat()
        test_results['summary'] = self._generate_test_summary(test_results)
        
        logger.info("✅ Automated test suite completed")
        return test_results
    
    def _generate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of test results."""
        schema_tests = test_results.get('schema_tests', [])
        validation_results = test_results.get('validation_results', [])
        
        total_schema_tests = len(schema_tests)
        passed_schema_tests = sum(1 for test in schema_tests if test['status'] == 'passed')
        
        total_validations = len(validation_results)
        passed_validations = sum(1 for val in validation_results if val['status'] == 'passed')
        
        return {
            'total_callbacks_tested': total_schema_tests,
            'schema_tests_passed': passed_schema_tests,
            'schema_tests_failed': total_schema_tests - passed_schema_tests,
            'validations_passed': passed_validations,
            'validations_failed': total_validations - passed_validations,
            'overall_success_rate': (passed_schema_tests + passed_validations) / (total_schema_tests + total_validations) if (total_schema_tests + total_validations) > 0 else 0
        }
    
    def export_test_results(self, test_results: Dict[str, Any], filename: str = None) -> str:
        """Export test results to JSON file."""
        if filename is None:
            filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        logger.info(f"📊 Test results exported to {filename}")
        return filename


# Utility functions for easy testing
def run_quick_schema_test(app) -> Dict[str, Any]:
    """Run a quick schema validation test on all callbacks."""
    test_runner = AutomatedTestRunner()
    return test_runner.run_all_tests(app)


def validate_callback_schema(callback_name: str, outputs: List[Any], inputs: List[Any], states: List[Any] = None) -> Dict[str, Any]:
    """Quick validation of a single callback schema."""
    validator = SchemaValidator()
    return validator.validate_schema(callback_name, outputs, inputs, states)
