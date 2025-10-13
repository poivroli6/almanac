"""
Test CSV export with dictionary-serialized figures (like Dash passes them).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import plotly.graph_objects as go
from almanac.export import export_figure_to_csv, extract_chart_data


def test_dict_figure_export():
    """Test exporting a figure that's been serialized to dict (like Dash does)."""
    print("=" * 60)
    print("Testing CSV Export with Dict-Serialized Figures")
    print("=" * 60)
    
    # Create a real Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[1, 2, 3, 4, 5],
        y=[10, 20, 15, 25, 30],
        mode='lines+markers',
        name='Test Data'
    ))
    fig.update_layout(
        title='Test Chart',
        xaxis_title='Hour',
        yaxis_title='Value'
    )
    
    print("\n[1] Testing with Figure object...")
    csv1 = export_figure_to_csv(fig, "test1.csv")
    print(f"    Result: {len(csv1)} bytes")
    print(f"    Preview:\n{csv1[:200]}")
    
    # Serialize to dict (this is what Dash does in callbacks)
    fig_dict = fig.to_dict()
    print(f"\n[2] Serialized figure to dict (like Dash does)")
    print(f"    Dict keys: {list(fig_dict.keys())}")
    
    # Try to export the dict
    print(f"\n[3] Testing with dict-serialized figure...")
    try:
        csv2 = export_figure_to_csv(fig_dict, "test2.csv")
        print(f"    Result: {len(csv2)} bytes")
        print(f"    Preview:\n{csv2[:200]}")
        
        # Verify they match
        if csv1 == csv2:
            print(f"\n[OK] Both exports match! Fix is working.")
            return True
        else:
            print(f"\n[WARNING] Exports don't match")
            print(f"    Figure: {len(csv1)} bytes")
            print(f"    Dict: {len(csv2)} bytes")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Failed to export dict figure:")
        print(f"    {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_trace_dict():
    """Test with multiple traces."""
    print("\n" + "=" * 60)
    print("Testing Multi-Trace Dict Export")
    print("=" * 60)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1,2,3], y=[10,20,15], name='Mean'))
    fig.add_trace(go.Scatter(x=[1,2,3], y=[12,22,17], name='Trimmed Mean'))
    fig.add_trace(go.Scatter(x=[1,2,3], y=[11,21,16], name='Median'))
    
    # Serialize to dict
    fig_dict = fig.to_dict()
    
    try:
        csv = export_figure_to_csv(fig_dict)
        print(f"\n[OK] Multi-trace export successful")
        print(f"    CSV length: {len(csv)} bytes")
        print(f"    Preview:")
        for line in csv.split('\n')[:5]:
            print(f"      {line}")
        
        # Verify all traces are present
        assert 'Mean' in csv, "Mean trace missing"
        assert 'Trimmed Mean' in csv, "Trimmed Mean missing"
        assert 'Median' in csv, "Median trace missing"
        print(f"\n[OK] All traces present in CSV")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False


def test_empty_dict():
    """Test with empty/None figures."""
    print("\n" + "=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)
    
    # Test None
    csv = export_figure_to_csv(None)
    print(f"\n[OK] None figure handled: {len(csv)} bytes")
    
    # Test empty dict
    csv = export_figure_to_csv({})
    print(f"[OK] Empty dict handled: {len(csv)} bytes")
    
    # Test dict without data
    csv = export_figure_to_csv({'layout': {}})
    print(f"[OK] Dict without data handled: {len(csv)} bytes")
    
    return True


if __name__ == '__main__':
    print("\n")
    
    tests = [
        ("Dict-Serialized Figure", test_dict_figure_export),
        ("Multi-Trace Dict", test_multi_trace_dict),
        ("Edge Cases", test_empty_dict),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n[PASS] {name}")
            else:
                failed += 1
                print(f"\n[FAIL] {name}")
        except Exception as e:
            failed += 1
            print(f"\n[FAIL] {name} - {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)

