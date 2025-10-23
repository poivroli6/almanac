# Volume Comparison Builder

## Overview

The **Volume Comparison Builder** is a companion feature to the Price Comparison Builder, allowing you to create sophisticated volume-based filtering scenarios across different trading sessions and time periods.

## Key Features

### 1. **Volume Field Types**
Choose from four different volume metrics:
- **PM (Pre-Market)** - Volume during pre-market hours
- **Session** - Volume during regular trading session
- **AH (After-Hours)** - Volume during after-hours trading
- **Time Interval (From-To)** - Volume within custom time range

### 2. **Day Offsets (T-0 to T-4)**
Compare volume across up to 5 days:
- **T-0** (Today/Current day)
- **T-1** (1 day ago)
- **T-2** (2 days ago)
- **T-3** (3 days ago)
- **T-4** (4 days ago)

### 3. **Six Comparison Operators**

#### Relative Comparisons (vs. another period)
- **< (Less Than)** - Left volume is less than right volume by threshold %
- **> (Greater Than)** - Left volume is greater than right volume by threshold %
- **Between (Range)** - Left volume is within percentage range of right volume

#### Absolute Value Comparisons
- **< Value** - Left volume is less than a specific number
- **> Value** - Left volume is greater than a specific number
- **Between Values** - Left volume falls within a specific numeric range

### 4. **Time Interval Selection**
When **Time Interval (From-To)** is selected, you can specify:
- **From Time** (HH:MM)
- **To Time** (HH:MM)
- Available on both left and right sides

## Usage Examples

### Example 1: Session Volume Comparison
```
Session1 > 10% Session2
```
**Translation:** Session volume yesterday is at least 10% greater than session volume 2 days ago

**Steps:**
1. Left Side: Select "Session" and offset "T-1"
2. Operator: Select "> (Greater Than)"
3. Threshold: Enter "10.0"
4. Right Side: Select "Session" and offset "T-2"
5. Click "✅ Apply Volume Comparison"

### Example 2: Pre-Market vs After-Hours
```
PM0 < 20% AH1
```
**Translation:** Today's pre-market volume is at least 20% less than yesterday's after-hours volume

**Steps:**
1. Left Side: Select "PM (Pre-Market)" and offset "T-0"
2. Operator: Select "< (Less Than)"
3. Threshold: Enter "20.0"
4. Right Side: Select "AH (After-Hours)" and offset "T-1"
5. Click "✅ Apply Volume Comparison"

### Example 3: Time Interval Comparison
```
TimeInterval0[09:30-10:00] > 15% TimeInterval1[09:30-10:00]
```
**Translation:** Today's volume from 9:30-10:00 is at least 15% greater than the same period yesterday

**Steps:**
1. Left Side: Select "Time Interval (From-To)" and offset "T-0"
2. Set From: 09:30, To: 10:00
3. Operator: Select "> (Greater Than)"
4. Threshold: Enter "15.0"
5. Right Side: Select "Time Interval (From-To)" and offset "T-1"
6. Set From: 09:30, To: 10:00
7. Click "✅ Apply Volume Comparison"

### Example 4: Absolute Value Filter
```
Session0 > Value 50000
```
**Translation:** Today's session volume is greater than 50,000 contracts

**Steps:**
1. Left Side: Select "Session" and offset "T-0"
2. Operator: Select "> Value (Greater Than Value)"
3. Value: Enter "50000"
4. Click "✅ Apply Volume Comparison"

### Example 5: Between Values Range
```
PM1 between 1000 and 5000
```
**Translation:** Yesterday's pre-market volume is between 1,000 and 5,000 contracts

**Steps:**
1. Left Side: Select "PM (Pre-Market)" and offset "T-1"
2. Operator: Select "Between Values (Range)"
3. Lower Value: Enter "1000"
4. Upper Value: Enter "5000"
5. Click "✅ Apply Volume Comparison"

## Dynamic UI Behavior

### Time Interval Pickers
- **Show:** When "Time Interval (From-To)" is selected as a field
- **Hide:** When PM, Session, or AH is selected
- **Includes:** From hour/minute and To hour/minute dropdowns

### Operator-Based Inputs
The UI dynamically shows different inputs based on operator:

| Operator | Shows |
|----------|-------|
| `<` or `>` | Right Side + Threshold (%) |
| `between` | Right Side + Range (lower %, upper %) |
| `< Value` or `> Value` | Value (numeric) |
| `between_values` | Value Range (lower, upper) |

## Scenario Management

### Creating Scenarios
- Each volume comparison creates a **separate scenario**
- Scenarios appear in "📋 Active Scenarios" section
- Labeled with "Vol:" prefix for easy identification

### Scenario Display
Format: `Vol: {left} {operator} {right}`

Examples:
- `Vol: Session1 > 10% Session2` (25 days)
- `Vol: PM0 < Value 5000` (42 days)
- `Vol: TimeInterval0[09:30-10:00] between -5% and +5% Session1` (18 days)

### Managing Scenarios
- ❌ Remove with X button
- AND/OR logic dropdown to combine with other scenarios
- Shows matching day count

## Color Coding

- **Green Section** (Left Side) - First volume metric
- **Yellow Section** (Right Side) - Second volume metric (when applicable)
- **White Section** (Operator & Values) - Comparison settings

## Tips

1. **Session Volume** - Most common and reliable for regular trading analysis
2. **Pre-Market** - Good for gauging early interest
3. **After-Hours** - Useful for reaction to news
4. **Time Intervals** - Powerful for analyzing specific periods (e.g., opening hour)
5. **Value Operators** - Great for filtering low/high volume days absolutely
6. **Percentage Operators** - Better for relative comparisons across different products

## Differences from Price Comparison Builder

| Feature | Price Builder | Volume Builder |
|---------|--------------|----------------|
| Fields | O, H, L, C, Time | PM, Session, AH, Time Interval |
| Day Range | T-0 to T-3 | T-0 to T-4 |
| Operators | 3 types | 6 types (includes Value ops) |
| Time Selection | Single time point | Time range (From-To) |
| Primary Use | Price movements | Volume patterns |

## Integration

- Works alongside Price Comparison Builder
- Both can create scenarios in the same list
- Scenarios can be combined using AND/OR logic
- Both respect Weekday Filters (T-0)

---

**Build sophisticated volume-based trading scenarios!** 📊

