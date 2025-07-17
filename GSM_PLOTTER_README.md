# GSM Frequency Plotter - OpenStreetMap Tile Fix

This application visualizes GSM frequency data on an interactive map using Dash and Leaflet. This version includes comprehensive fixes for OpenStreetMap background tile display issues.

## Issues Fixed

### 1. Map Initialization Problems
- **Fixed**: Added default center coordinates (Toronto: 43.6532, -79.3832)
- **Fixed**: Added proper zoom level (11)
- **Before**: Map container appeared but without visible background
- **After**: Map displays with proper geographic context

### 2. Tile Provider Reliability
- **Fixed**: Replaced unreliable OpenStreetMap tiles with CartoDB as primary provider
- **Fixed**: Added multiple fallback tile providers (OpenStreetMap, Stamen Terrain)
- **Before**: Tiles failed to load or displayed inconsistently
- **After**: Robust tile loading with automatic fallbacks

### 3. CSS Conflicts
- **Fixed**: Added Leaflet-specific CSS rules to prevent tile rendering conflicts
- **Fixed**: Proper z-index hierarchy for map elements
- **Fixed**: Ensured tile opacity and positioning
- **Before**: Custom CSS interfered with tile display
- **After**: Clean tile rendering without visual artifacts

### 4. Enhanced Error Handling
- **Added**: Tile load error detection and user feedback
- **Added**: Debug information display
- **Added**: Graceful fallback mechanisms
- **Before**: No feedback when tiles failed to load
- **After**: Clear status messages and automatic recovery

### 5. Improved Tile Layer Implementation
- **Added**: Proper maxZoom and attribution parameters
- **Added**: Error tile URLs for failed tile requests
- **Added**: Multiple subdomain support for load balancing
- **Before**: Basic tile configuration prone to failures
- **After**: Production-ready tile layer configuration

## Features

### Core Functionality
- **GSM Sector Visualization**: Interactive markers showing frequency, power, and operator data
- **Frequency Filtering**: Filter sectors by GSM frequency bands (850, 1900, 2100, 2600 MHz)
- **Interactive Tooltips**: Detailed information on hover
- **Responsive Design**: Works on desktop and mobile devices

### Enhanced Map Features
- **Multiple Tile Providers**: Choose between CartoDB, OpenStreetMap, and Stamen Terrain
- **Automatic Fallbacks**: Seamless switching if primary tiles fail
- **Real-time Status**: Live feedback on map loading and tile status
- **Site Navigation**: Jump to specific GSM sites with enhanced functionality

### Technical Improvements
- **Robust Error Handling**: Comprehensive error detection and recovery
- **Performance Optimization**: Efficient tile loading and caching
- **Debug Information**: Technical details for troubleshooting
- **CSS Isolation**: Prevents styling conflicts with map tiles

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python gsm_frequency_plotter.py
```

3. Open your browser to: http://localhost:8050

## Usage

### Basic Operation
1. **View GSM Sectors**: The map displays all GSM frequency sectors as colored circles
2. **Filter by Frequency**: Use the dropdown to show only specific frequency bands
3. **Change Tile Provider**: Switch between different map backgrounds
4. **Hover for Details**: Mouse over sectors to see detailed information

### Color Coding
- **Red**: 850 MHz frequency band
- **Blue**: 1900 MHz frequency band  
- **Green**: 2100 MHz frequency band
- **Orange**: 2600 MHz frequency band

### Circle Size
- Circle radius represents signal power (larger = stronger signal)

## Technical Details

### Tile Provider Configuration
- **Primary**: CartoDB Light (most reliable)
- **Fallback 1**: OpenStreetMap
- **Fallback 2**: Stamen Terrain

### Map Parameters
- **Center**: Toronto coordinates (43.6532, -79.3832)
- **Default Zoom**: 11
- **Max Zoom**: 19 (CartoDB/OSM), 18 (Stamen)

### Error Recovery
- Automatic tile provider switching on failures
- Error tile display for failed requests
- User notification system for loading states
- Debug information for troubleshooting

## Troubleshooting

### Tiles Not Loading
1. Check internet connectivity
2. Try switching tile providers using the dropdown
3. Look for error messages in the status area
4. Check browser console for detailed error logs

### Performance Issues
1. Reduce the number of visible sectors using frequency filter
2. Try different tile providers (CartoDB is usually fastest)
3. Ensure good internet connection for tile loading

### Site Navigation Problems
1. Verify sector data is loaded correctly
2. Check that coordinates are valid
3. Use the test button to verify tile loading

## Data Format

The application expects GSM sector data with the following format:
- `sector_id`: Unique identifier for each sector
- `latitude`, `longitude`: Geographic coordinates
- `frequency`: GSM frequency band (MHz)
- `power`: Signal power (dBm)
- `operator`: Network operator name

## Future Enhancements

- Additional tile providers (satellite imagery, etc.)
- Sector clustering for dense areas
- Real-time data updates
- Export functionality for sector data
- Advanced filtering options (by operator, power level)

## Dependencies

- Dash 2.10.0+
- Dash Leaflet 0.1.23+
- Pandas 1.5.0+
- NumPy 1.21.0+
- Plotly 5.10.0+