# Coursera Capstone - GSM Plotter with Fixed Map Callbacks

This repository contains the solution for fixing map callback conflicts in a Dash application that were causing the map to reset to [0,0] coordinates after file upload.

## 🐛 Problem Solved

The original implementation had multiple callback conflicts that caused:
- Map resetting to [0,0] coordinates after file upload
- Race conditions between map update callbacks
- flyTo commands getting lost due to timing conflicts
- Unstable map behavior during data processing

## ✅ Solution Implemented

### Key Fixes Applied:

1. **Consolidated Callback Chain** 
   - **Before**: 3 conflicting callbacks with `allow_duplicate=True`
   - **After**: Coordinated chain: Upload → Process → Update Content → Fly To

2. **Single Source of Truth for Map Updates**
   - **Before**: Multiple callbacks updating `map.children` simultaneously
   - **After**: One consolidated callback for all map content updates

3. **Separated flyTo Timing**
   - **Before**: flyTo mixed with content updates causing conflicts
   - **After**: flyTo triggered AFTER map content update completes

4. **Enhanced Coordinate Safeguards**
   - **Before**: Default [0,0] coordinates, no validation
   - **After**: Realistic defaults [23.4869, 58.4834], full validation, cached centers

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python optimized_gsm_plotter.py
```

### Testing the Fix

```bash
# Run validation tests
python test_fixes.py

# Generate test data
python create_test_data.py
```

## 📋 Files Structure

- `optimized_gsm_plotter.py` - Main Dash application with fixes
- `test_gsm_data.csv` - Sample test data (50 GPS sites)
- `test_fixes.py` - Validation test suite
- `CALLBACK_FIXES.md` - Detailed technical documentation
- `requirements.txt` - Python dependencies
- `create_test_data.py` - Test data generator

## 🧪 Validation Results

All tests pass ✅:
- CSV Reading test: 50/50 valid coordinates
- Coordinate Safeguards: 8/8 validation cases pass  
- File Format Support: CSV and Excel processing works
- No [0,0] coordinate resets detected

## 🔧 Technical Details

### Fixed Callback Structure:
```python
# BEFORE: Conflicting callbacks
@app.callback(..., allow_duplicate=True)  # ❌ Race conditions
def initialize_map(): ...

@app.callback(..., allow_duplicate=True)  # ❌ Conflicts 
def update_map_content(): ...

@app.callback(..., allow_duplicate=True)  # ❌ Timing issues
def fly_to_data_center(): ...

# AFTER: Coordinated callback chain  
@app.callback([Output('output-filename'), Output('trigger-map-update')])
def process_uploaded_file(): ...  # ✅ Single source

@app.callback([Output('map', 'children'), Output('map-info')])  
def update_map_content_consolidated(): ...  # ✅ No conflicts

@app.callback(Output('map', 'flyTo'))
def fly_to_data_center_fixed(): ...  # ✅ Proper timing
```

### Coordinate Safety Measures:
- Default coordinates: [23.4869, 58.4834] (realistic UAE location)
- Validation: -90 ≤ lat ≤ 90, -180 ≤ lng ≤ 180
- [0,0] detection with warnings
- Cached center calculation with fallbacks

## 📊 Expected Results

✅ **Map flies to correct calculated coordinates and stays there**  
✅ **No more reset to [0,0] during file upload process**  
✅ **Smooth callback execution without conflicts**  
✅ **Single, coordinated map update workflow**  
✅ **Proper error handling and fallback behavior**

## 📁 Original Project Context

This repository is part of the Coursera Capstone project focused on Seattle collision analysis. The GSM plotter was added to demonstrate advanced mapping capabilities with proper callback handling.

## 🛠 Dependencies

- `dash` - Web application framework
- `dash-leaflet` - Interactive map component  
- `pandas` (optional) - Excel file support
- Built-in Python libraries for CSV support

## 📖 Documentation

See `CALLBACK_FIXES.md` for detailed technical analysis of the problems and solutions implemented.
