# Comparison Builder Feature

## Overview

The Almanac Futures application now features a powerful **Comparison Builder** that replaces the old preset filter system. This allows you to create custom comparisons between price values at different time offsets and specific times.

## Key Features

### 1. **Flexible Price Field Selection**
Compare any of the following price fields:
- **O** (Open)
- **H** (High)
- **L** (Low)
- **C** (Close)
- **Time** (Value at specific time)

### 2. **Day Offsets**
Select from T-0 through T-3:
- **T-0** (Today/Current day)
- **T-1** (1 day ago)
- **T-2** (2 days ago)
- **T-3** (3 days ago)

### 3. **Time-Specific Values**
When you select "Time Value" as a field, you can specify the exact time (HH:MM) to retrieve the price at that moment. 
- **Example:** Selecting Time @ 09:30 is equivalent to selecting Open (O)

### 4. **Comparison Operators**
Three types of comparisons:
- **<** (Less Than) - Left side is less than right side by threshold %
- **>** (Greater Than) - Left side is greater than right side by threshold %
- **Between** (Range) - Left side is within a percentage range of right side

### 5. **Weekday Filters**
Filter by day of the week (applies to T-0):
- Monday through Friday
- When T-1 is selected with Monday filter, it captures Friday of the previous week

## Usage Examples

### Example 1: Basic Comparison
```
H2 vs O3 < 2%
```
**Translation:** High of 2 days ago is less than Open of 3 days ago by up to 2%

**Steps:**
1. Left Side: Select "High (H)" and offset "T-2"
2. Operator: Select "< (Less Than)"
3. Right Side: Select "Open (O)" and offset "T-3"
4. Threshold: Enter "2.0"
5. Click "✅ Apply Comparison"

### Example 2: Time-Specific Comparison
```
Time2@12:00 vs C1 > 1.5%
```
**Translation:** Price at 12:00 PM two days ago is greater than Close of 1 day ago by at least 1.5%

**Steps:**
1. Left Side: Select "Time Value" and offset "T-2"
2. Set time to 12:00
3. Operator: Select "> (Greater Than)"
4. Right Side: Select "Close (C)" and offset "T-1"
5. Threshold: Enter "1.5"
6. Click "✅ Apply Comparison"

### Example 3: Between Range
```
C0 between -1% and +1% of O1
```
**Translation:** Today's close is within ±1% of yesterday's open

**Steps:**
1. Left Side: Select "Close (C)" and offset "T-0"
2. Operator: Select "Between (Range)"
3. Right Side: Select "Open (O)" and offset "T-1"
4. Lower Range: Enter "-1.0"
5. Upper Range: Enter "1.0"
6. Click "✅ Apply Comparison"

## Scenario Management

### Adding Scenarios
- Each comparison becomes a **separate scenario** when you click "✅ Apply Comparison"
- Scenarios appear in the "📋 Active Scenarios" section
- Each scenario shows:
  - Comparison description
  - Number of matching days
  - AND/OR logic operator dropdown
  - ❌ button to remove

### Multiple Comparisons
- Add multiple scenarios by building and applying comparisons one at a time
- Each scenario filters the data independently
- Use the AND/OR dropdown to control how scenarios combine

### Removing Scenarios
- Click the ❌ button on any scenario row to remove it

## UI Organization

The comparison builder is organized into color-coded sections:

- **Blue Section** (Left Side) - First value to compare
- **White Section** (Operator) - How to compare
- **Orange Section** (Right Side) - Second value to compare
- **Threshold Section** - Percentage difference or range

## Weekday Filters

Located below the comparison builder:
- Apply to T-0 (current day)
- Select multiple weekdays to filter
- Works in combination with comparisons
- **Smart offset logic:** If Monday is selected and you use T-1, the system looks at Friday

## Technical Details

### Time Values
- When field type is "Time", additional time pickers appear
- Time is specified in HH:MM format (24-hour)
- Available time slots: 00, 15, 30, 45 minutes
- Hours exclude trading halts (5, 6)

### Threshold Logic
- **< and >**: Single percentage threshold
- **Between**: Two values creating a range (lower, upper)
- Thresholds are calculated as percentage difference from the reference value

### Backward Compatibility
- Old filter system components are hidden but remain functional
- Existing callbacks continue to work
- Smooth transition for saved presets

## Tips

1. **Start Simple**: Begin with basic O, H, L, C comparisons before using Time values
2. **Use Weekdays**: Combine comparisons with weekday filters for more precise scenarios
3. **Experiment**: Try different combinations and see the case count update
4. **Save Presets**: Once you find useful comparisons, save them as presets for reuse
5. **Multiple Scenarios**: Build complex analysis by adding multiple comparison scenarios

## Benefits Over Old System

✅ **More Flexible** - Compare any field against any other field  
✅ **Time-Specific** - Get exact values at specific times  
✅ **Day Offsets** - Look back up to 3 days  
✅ **Cleaner UI** - Intuitive builder interface  
✅ **Better Control** - Precise percentage thresholds  
✅ **Expandable** - Easy to add new operators and fields  

---

**Enjoy building custom comparisons!** 🎯

