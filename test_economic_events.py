"""
Test script for economic events functionality.

Run this to verify the economic events module works correctly.
"""

import sys
from datetime import date, datetime
from almanac.data_sources.economic_events import (
    is_economic_event_date,
    get_economic_event_dates,
    get_all_major_event_dates,
    get_events_on_date,
    ECONOMIC_EVENTS
)


def test_cpi_dates():
    """Test CPI date checking."""
    print("\n=== Testing CPI Dates ===")
    
    # Known CPI date
    test_date = date(2024, 1, 11)
    result = is_economic_event_date(test_date, 'CPI')
    print(f"Is 2024-01-11 a CPI day? {result}")
    assert result == True, "Failed: 2024-01-11 should be a CPI day"
    
    # Non-CPI date
    test_date = date(2024, 1, 15)
    result = is_economic_event_date(test_date, 'CPI')
    print(f"Is 2024-01-15 a CPI day? {result}")
    assert result == False, "Failed: 2024-01-15 should NOT be a CPI day"
    
    print("[PASS] CPI date tests passed")


def test_fomc_dates():
    """Test FOMC date checking."""
    print("\n=== Testing FOMC Dates ===")
    
    # Known FOMC date
    test_date = date(2024, 1, 31)
    result = is_economic_event_date(test_date, 'FOMC')
    print(f"Is 2024-01-31 an FOMC day? {result}")
    assert result == True, "Failed: 2024-01-31 should be an FOMC day"
    
    print("[PASS] FOMC date tests passed")


def test_nfp_dates():
    """Test NFP date checking."""
    print("\n=== Testing NFP Dates ===")
    
    # Known NFP date
    test_date = date(2024, 1, 5)
    result = is_economic_event_date(test_date, 'NFP')
    print(f"Is 2024-01-05 an NFP day? {result}")
    assert result == True, "Failed: 2024-01-05 should be an NFP day"
    
    print("[PASS] NFP date tests passed")


def test_multiple_events():
    """Test dates with multiple events."""
    print("\n=== Testing Multiple Events on Same Date ===")
    
    # Check if any date has multiple events
    all_dates = {}
    for event_type, dates in ECONOMIC_EVENTS.items():
        for date_str in dates:
            if date_str not in all_dates:
                all_dates[date_str] = []
            all_dates[date_str].append(event_type)
    
    # Find dates with multiple events
    multi_event_dates = {d: events for d, events in all_dates.items() if len(events) > 1}
    
    if multi_event_dates:
        print(f"Found {len(multi_event_dates)} dates with multiple events:")
        for date_str, events in list(multi_event_dates.items())[:5]:  # Show first 5
            print(f"  {date_str}: {', '.join(events)}")
            
            # Test get_events_on_date function
            found_events = get_events_on_date(date_str)
            assert set(found_events) == set(events), f"Mismatch for {date_str}"
    else:
        print("No dates with multiple events found")
    
    print("[PASS] Multiple events test passed")


def test_major_event_dates():
    """Test major event date aggregation."""
    print("\n=== Testing Major Event Dates ===")
    
    major_dates = get_all_major_event_dates()
    print(f"Total major event dates: {len(major_dates)}")
    
    # Verify it includes dates from all categories
    for event_type in ['CPI', 'FOMC', 'NFP', 'PPI', 'RETAIL_SALES', 'GDP', 'PCE']:
        event_dates = get_economic_event_dates(event_type)
        assert event_dates.issubset(major_dates), f"{event_type} dates not in major dates"
        print(f"  {event_type}: {len(event_dates)} dates")
    
    print("[PASS] Major event dates test passed")


def test_string_date_input():
    """Test that string dates work correctly."""
    print("\n=== Testing String Date Input ===")
    
    result = is_economic_event_date('2024-01-11', 'CPI')
    print(f"String date '2024-01-11' is CPI day? {result}")
    assert result == True, "Failed: String date should work"
    
    print("[PASS] String date input test passed")


def test_coverage():
    """Test data coverage across years."""
    print("\n=== Testing Data Coverage ===")
    
    for event_type, dates in ECONOMIC_EVENTS.items():
        years = {}
        for date_str in dates:
            year = date_str.split('-')[0]
            years[year] = years.get(year, 0) + 1
        
        print(f"\n{event_type}:")
        for year in sorted(years.keys()):
            print(f"  {year}: {years[year]} dates")
    
    print("\n[PASS] Coverage test complete")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Economic Events Module Tests")
    print("=" * 60)
    
    try:
        test_cpi_dates()
        test_fomc_dates()
        test_nfp_dates()
        test_string_date_input()
        test_major_event_dates()
        test_multiple_events()
        test_coverage()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

