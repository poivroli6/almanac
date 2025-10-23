"""
Unit Tests for Profile Page Components

Tests for the modular components of the profile page.
"""

import pytest
import pandas as pd
from datetime import datetime, date
from unittest.mock import Mock, patch
import dash
from dash import html, dcc

# Import the modules to test
from almanac.pages.components.layout import (
    create_preset_row,
    create_sidebar_content,
    create_topbar_content,
    create_profile_layout
)
from almanac.pages.components.filters import (
    create_filter_controls,
    create_threshold_controls,
    create_product_dropdown,
    create_date_range_controls,
    create_calculate_button
)
from almanac.utils.validation import (
    validate_product,
    validate_date_range,
    validate_threshold,
    validate_filters,
    validate_dataframe,
    validate_callback_inputs,
    ValidationError
)


class TestLayoutComponents:
    """Test layout component functions."""
    
    def test_create_preset_row(self):
        """Test preset row creation."""
        preset_id = "test_preset"
        preset_name = "Test Preset"
        day_count = 30
        logic_operator = "AND"
        
        result = create_preset_row(preset_id, preset_name, day_count, logic_operator)
        
        assert isinstance(result, html.Div)
        # Check that the preset name is in the component
        assert any("Test Preset" in str(child) for child in result.children)
    
    def test_create_sidebar_content(self):
        """Test sidebar content creation."""
        result = create_sidebar_content()
        
        assert isinstance(result, html.Div)
        assert len(result.children) > 0
    
    def test_create_topbar_content(self):
        """Test topbar content creation."""
        result = create_topbar_content()
        
        assert isinstance(result, html.Div)
        assert len(result.children) > 0
    
    def test_create_profile_layout(self):
        """Test profile layout creation."""
        result = create_profile_layout()
        
        assert isinstance(result, html.Div)
        assert len(result.children) > 0


class TestFilterComponents:
    """Test filter component functions."""
    
    def test_create_filter_controls(self):
        """Test filter controls creation."""
        result = create_filter_controls()
        
        assert isinstance(result, html.Div)
        assert len(result.children) > 0
    
    def test_create_threshold_controls(self):
        """Test threshold controls creation."""
        result = create_threshold_controls()
        
        assert isinstance(result, html.Div)
        assert len(result.children) > 0
    
    def test_create_product_dropdown(self):
        """Test product dropdown creation."""
        result = create_product_dropdown()
        
        assert isinstance(result, dcc.Dropdown)
        assert result.id == 'product-dropdown'
        assert len(result.options) > 0
    
    def test_create_date_range_controls(self):
        """Test date range controls creation."""
        result = create_date_range_controls()
        
        assert isinstance(result, html.Div)
        assert len(result.children) > 0
    
    def test_create_calculate_button(self):
        """Test calculate button creation."""
        result = create_calculate_button()
        
        assert isinstance(result, html.Div)
        # Check that it contains a button with the correct id
        assert any(hasattr(child, 'id') and child.id == 'calc-btn' for child in result.children)


class TestValidation:
    """Test validation functions."""
    
    def test_validate_product_valid(self):
        """Test product validation with valid products."""
        valid_products = ['ES', 'NQ', 'YM', 'CL', 'GC', 'EURUSD']
        
        for product in valid_products:
            assert validate_product(product) is True
    
    def test_validate_product_invalid(self):
        """Test product validation with invalid products."""
        invalid_products = ['', None, 'INVALID', '123']
        
        for product in invalid_products:
            with pytest.raises(ValidationError):
                validate_product(product)
    
    def test_validate_date_range_valid(self):
        """Test date range validation with valid dates."""
        start_date = "2020-01-01"
        end_date = "2020-12-31"
        
        result_start, result_end = validate_date_range(start_date, end_date)
        
        assert isinstance(result_start, date)
        assert isinstance(result_end, date)
        assert result_start <= result_end
    
    def test_validate_date_range_invalid(self):
        """Test date range validation with invalid dates."""
        # Start date after end date
        with pytest.raises(ValidationError):
            validate_date_range("2020-12-31", "2020-01-01")
        
        # Invalid date format
        with pytest.raises(ValidationError):
            validate_date_range("invalid-date", "2020-01-01")
        
        # Date too far in the past
        with pytest.raises(ValidationError):
            validate_date_range("1990-01-01", "2020-01-01")
    
    def test_validate_threshold_valid(self):
        """Test threshold validation with valid values."""
        assert validate_threshold(150, "volume") == 150.0
        assert validate_threshold(0.5, "percentage") == 0.5
        assert validate_threshold(0, "min") == 0.0
        assert validate_threshold(1000, "max") == 1000.0
    
    def test_validate_threshold_invalid(self):
        """Test threshold validation with invalid values."""
        # None value
        with pytest.raises(ValidationError):
            validate_threshold(None, "test")
        
        # Below minimum
        with pytest.raises(ValidationError):
            validate_threshold(-1, "test")
        
        # Above maximum
        with pytest.raises(ValidationError):
            validate_threshold(1001, "test")
        
        # Non-numeric
        with pytest.raises(ValidationError):
            validate_threshold("invalid", "test")
    
    def test_validate_filters_valid(self):
        """Test filter validation with valid filters."""
        valid_filters = ['high_volume', 'low_volume', 'gap_up', 'gap_down']
        result = validate_filters(valid_filters)
        
        assert result == valid_filters
    
    def test_validate_filters_invalid(self):
        """Test filter validation with invalid filters."""
        # Invalid filter name
        with pytest.raises(ValidationError):
            validate_filters(['invalid_filter'])
        
        # Non-list input
        with pytest.raises(ValidationError):
            validate_filters("not_a_list")
    
    def test_validate_dataframe_valid(self):
        """Test DataFrame validation with valid DataFrame."""
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        result = validate_dataframe(df, "test_df")
        
        assert result.equals(df)
    
    def test_validate_dataframe_invalid(self):
        """Test DataFrame validation with invalid DataFrame."""
        # Not a DataFrame
        with pytest.raises(ValidationError):
            validate_dataframe("not_a_df", "test_df")
        
        # Empty DataFrame
        with pytest.raises(ValidationError):
            validate_dataframe(pd.DataFrame(), "test_df")
        
        # Missing required columns
        df = pd.DataFrame({'col1': [1, 2, 3]})
        with pytest.raises(ValidationError):
            validate_dataframe(df, "test_df", ['col1', 'col2'])
    
    def test_validate_callback_inputs_valid(self):
        """Test callback input validation with valid inputs."""
        prod = "ES"
        start = "2020-01-01"
        end = "2020-12-31"
        filters = ["high_volume"]
        vol_thr = 150
        pct_thr = 0.5
        
        result = validate_callback_inputs(prod, start, end, filters, vol_thr, pct_thr)
        
        assert len(result) == 6
        assert result[0] == prod
        assert isinstance(result[1], date)
        assert isinstance(result[2], date)
        assert result[3] == filters
        assert result[4] == 150.0
        assert result[5] == 0.5
    
    def test_validate_callback_inputs_invalid(self):
        """Test callback input validation with invalid inputs."""
        # Invalid product
        with pytest.raises(ValidationError):
            validate_callback_inputs("INVALID", "2020-01-01", "2020-12-31", [], 150, 0.5)
        
        # Invalid date range
        with pytest.raises(ValidationError):
            validate_callback_inputs("ES", "2020-12-31", "2020-01-01", [], 150, 0.5)


class TestIntegration:
    """Integration tests for the profile page components."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'datetime': pd.date_range('2020-01-01', periods=100, freq='H'),
            'open': [100 + i for i in range(100)],
            'high': [101 + i for i in range(100)],
            'low': [99 + i for i in range(100)],
            'close': [100.5 + i for i in range(100)],
            'volume': [1000 + i * 10 for i in range(100)]
        })
    
    def test_layout_integration(self):
        """Test that layout components work together."""
        layout = create_profile_layout()
        
        assert isinstance(layout, html.Div)
        assert len(layout.children) > 0
    
    def test_filter_integration(self):
        """Test that filter components work together."""
        sidebar = create_sidebar_content()
        
        assert isinstance(sidebar, html.Div)
        assert len(sidebar.children) > 0
    
    def test_validation_integration(self, sample_data):
        """Test that validation works with sample data."""
        # Test DataFrame validation
        validated_df = validate_dataframe(sample_data, "sample", ['datetime', 'open', 'close'])
        assert validated_df.equals(sample_data)
        
        # Test callback inputs
        result = validate_callback_inputs(
            "ES", "2020-01-01", "2020-01-02", ["high_volume"], 150, 0.5
        )
        assert len(result) == 6


if __name__ == "__main__":
    pytest.main([__file__])
