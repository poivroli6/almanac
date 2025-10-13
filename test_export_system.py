"""
Test script for export system functionality.

This tests the export modules without running the full Dash app.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import plotly.graph_objects as go
import pandas as pd
from almanac.export import (
    export_figure_to_csv,
    get_png_download_config,
    generate_shareable_url,
    get_current_page_url,
    parse_url_parameters,
    extract_chart_data
)


def test_csv_export():
    """Test CSV export functionality."""
    print("Testing CSV export...")
    
    # Create a sample Plotly figure
    x_data = [1, 2, 3, 4, 5]
    y_data = [10, 20, 15, 25, 30]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines+markers',
        name='Test Data'
    ))
    fig.update_layout(
        title='Test Chart',
        xaxis_title='X Axis',
        yaxis_title='Y Axis'
    )
    
    # Extract data
    df = extract_chart_data(fig)
    print(f"[OK] Extracted DataFrame shape: {df.shape}")
    print(f"     Columns: {list(df.columns)}")
    
    # Export to CSV
    csv_string = export_figure_to_csv(fig, "test_chart.csv")
    print(f"[OK] CSV export successful ({len(csv_string)} characters)")
    print(f"     First 200 chars: {csv_string[:200]}...")
    
    return True


def test_png_config():
    """Test PNG export configuration."""
    print("\nTesting PNG configuration...")
    
    # Test default config
    config = get_png_download_config('test_chart')
    print(f"[OK] Default config created")
    print(f"     Keys: {list(config.keys())}")
    
    # Test custom config
    custom_config = get_png_download_config(
        filename='custom_chart',
        width=1920,
        height=1080,
        scale=3
    )
    print(f"[OK] Custom config created")
    print(f"     Image size: {custom_config['toImageButtonOptions']['width']}x{custom_config['toImageButtonOptions']['height']}")
    print(f"     Scale: {custom_config['toImageButtonOptions']['scale']}x")
    
    return True


def test_url_generation():
    """Test shareable URL generation."""
    print("\nTesting URL generation...")
    
    # Generate base URL
    base_url = get_current_page_url(hostname='localhost', port=8085)
    print(f"[OK] Base URL: {base_url}")
    
    # Generate shareable URL with filters
    url = generate_shareable_url(
        base_url=base_url,
        product='ES',
        start_date='2025-01-01',
        end_date='2025-02-01',
        minute_hour=9,
        filters=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
        trim_percentage=5.0,
        stat_measures=['mean', 'median']
    )
    print(f"[OK] Shareable URL generated ({len(url)} characters)")
    print(f"     URL: {url}")
    
    # Parse URL back
    params = parse_url_parameters(url)
    print(f"[OK] URL parsed successfully")
    print(f"     Product: {params.get('product')}")
    print(f"     Date range: {params.get('start_date')} to {params.get('end_date')}")
    print(f"     Filters: {params.get('filters')}")
    
    # Verify round-trip
    assert params.get('product') == 'ES', "Product mismatch"
    assert params.get('start_date') == '2025-01-01', "Start date mismatch"
    assert params.get('end_date') == '2025-02-01', "End date mismatch"
    assert params.get('minute_hour') == 9, "Minute hour mismatch"
    print(f"[OK] Round-trip verification passed")
    
    return True


def test_multi_trace_figure():
    """Test CSV export with multiple traces."""
    print("\nTesting multi-trace CSV export...")
    
    # Create figure with multiple traces
    fig = go.Figure()
    
    x_data = [1, 2, 3, 4, 5]
    
    fig.add_trace(go.Scatter(
        x=x_data,
        y=[10, 20, 15, 25, 30],
        mode='lines',
        name='Mean'
    ))
    
    fig.add_trace(go.Scatter(
        x=x_data,
        y=[12, 22, 17, 27, 32],
        mode='lines',
        name='Trimmed Mean'
    ))
    
    fig.add_trace(go.Scatter(
        x=x_data,
        y=[11, 21, 16, 26, 31],
        mode='lines',
        name='Median'
    ))
    
    # Export to CSV
    csv_string = export_figure_to_csv(fig)
    
    # Check that all traces are in CSV
    assert 'Mean' in csv_string, "Mean trace missing"
    assert 'Trimmed Mean' in csv_string, "Trimmed Mean trace missing"
    assert 'Median' in csv_string, "Median trace missing"
    
    print(f"[OK] Multi-trace export successful")
    print(f"     CSV preview:")
    for line in csv_string.split('\n')[:6]:
        print(f"       {line}")
    
    return True


def test_edge_cases():
    """Test edge cases."""
    print("\nTesting edge cases...")
    
    # Empty figure
    empty_fig = go.Figure()
    csv = export_figure_to_csv(empty_fig)
    print(f"[OK] Empty figure handled (output length: {len(csv)})")
    
    # Very long URL test
    url = generate_shareable_url(
        base_url='http://localhost:8085',
        product='ES',
        start_date='2025-01-01',
        end_date='2025-12-31',
        filters=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 
                 'prev_pos', 'prev_neg', 'relvol_gt', 'trim_extremes'],
        vol_threshold=1.5,
        pct_threshold=2.0,
        trim_percentage=10.0,
        stat_measures=['mean', 'trimmed_mean', 'median', 'mode'],
        timeA_hour=9,
        timeA_minute=30,
        timeB_hour=15,
        timeB_minute=45
    )
    print(f"[OK] Complex URL generated ({len(url)} characters)")
    
    if len(url) > 2000:
        print(f"     [WARNING] URL exceeds 2000 characters (may have browser compatibility issues)")
    else:
        print(f"     [OK] URL length is acceptable for all browsers")
    
    return True


def run_all_tests():
    """Run all export system tests."""
    print("=" * 60)
    print("EXPORT SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("CSV Export", test_csv_export),
        ("PNG Configuration", test_png_config),
        ("URL Generation", test_url_generation),
        ("Multi-Trace Export", test_multi_trace_figure),
        ("Edge Cases", test_edge_cases),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n[PASS] {test_name}")
            else:
                failed += 1
                print(f"\n[FAIL] {test_name}")
        except Exception as e:
            failed += 1
            print(f"\n[FAIL] {test_name} with exception:")
            print(f"       {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

