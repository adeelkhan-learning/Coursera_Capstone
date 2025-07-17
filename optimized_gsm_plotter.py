"""
Optimized GSM Plotter - Dash application with fixed map callback conflicts
This version implements the fixes to prevent map resetting to [0,0] coordinates
after file upload by consolidating callbacks and fixing timing issues.
"""

import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import base64
import io
import logging
import time
import csv

# Try to import pandas, fallback to CSV if not available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available, using CSV fallback")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__)

# Global variable to store cached data with center coordinates
cached_data = {
    'dataframe': None,
    'center': None,
    'zoom': 2,
    'processed': False
}

# App layout
app.layout = html.Div([
    html.H1("GSM Plotter Dashboard - Fixed Version", style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files'),
                html.Br(),
                html.Small('Supports Excel (.xlsx) and CSV (.csv) files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        
        html.Div(id='output-filename', style={'margin': '10px'}),
        
        # Hidden div to trigger map updates after processing
        html.Div(id='trigger-map-update', style={'display': 'none'}),
        
        dl.Map(
            id='map',
            style={'width': '100%', 'height': '600px'},
            center=[23.4869, 58.4834],  # Default to reasonable location instead of [0,0]
            zoom=8,
            children=[
                dl.TileLayer()
            ]
        ),
        
        html.Div(id='map-info', style={'margin': '10px'}),
        html.Div(id='legend', style={'margin': '10px'})
    ])
])

def read_uploaded_file(contents, filename):
    """
    Read uploaded file (Excel or CSV) with fallback options
    """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Determine file type
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if file_ext == 'csv':
        # Read CSV file
        content_str = decoded.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content_str))
        data = list(csv_reader)
        
        # Convert to simple format
        if data:
            df = {
                'latitude': [float(row.get('latitude', 0)) for row in data if row.get('latitude')],
                'longitude': [float(row.get('longitude', 0)) for row in data if row.get('longitude')]
            }
            # Add additional columns if they exist
            for key in data[0].keys():
                if key not in ['latitude', 'longitude']:
                    df[key] = [row.get(key, '') for row in data]
        else:
            df = {'latitude': [], 'longitude': []}
            
    elif file_ext in ['xlsx', 'xls'] and PANDAS_AVAILABLE:
        # Read Excel file with pandas
        df = pd.read_excel(io.BytesIO(decoded))
        # Convert to dict format for consistency
        df = df.to_dict('list')
        
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    return df

# FIX 1: Process uploaded file and trigger map update chain
@app.callback(
    [Output('output-filename', 'children'),
     Output('trigger-map-update', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def process_uploaded_file(content, filename):
    """
    FIXED: Single callback to process file and trigger update chain.
    No longer conflicts with map initialization.
    """
    global cached_data
    
    if content is None:
        raise PreventUpdate
    
    try:
        # Read file using appropriate method
        df = read_uploaded_file(content, filename)
        
        # Validate required columns
        required_cols = ['latitude', 'longitude']
        if not all(col in df for col in required_cols):
            # Reset cached data on error
            cached_data = {
                'dataframe': None,
                'center': None, 
                'zoom': 2,
                'processed': False
            }
            return html.Div(f"Error: Missing required columns. Need: {required_cols}", 
                          style={'color': 'red'}), no_update
        
        # Filter valid coordinates
        valid_lats = [lat for lat in df['latitude'] if lat and -90 <= lat <= 90]
        valid_lngs = [lng for lng in df['longitude'] if lng and -180 <= lng <= 180]
        
        if len(valid_lats) > 0 and len(valid_lngs) > 0:
            center_lat = sum(valid_lats) / len(valid_lats)
            center_lng = sum(valid_lngs) / len(valid_lngs)
            
            # Calculate appropriate zoom level
            lat_range = max(valid_lats) - min(valid_lats)
            lng_range = max(valid_lngs) - min(valid_lngs)
            max_range = max(lat_range, lng_range)
            
            if max_range > 10:
                zoom = 5
            elif max_range > 1:
                zoom = 8
            else:
                zoom = 12
                
            # Store in cache with safeguards
            cached_data = {
                'dataframe': df,
                'center': [center_lat, center_lng],
                'zoom': zoom,
                'processed': True
            }
            
            logger.info(f"File processed: {filename} with {len(valid_lats)} valid sites")
            logger.info(f"Calculated center: [{center_lat:.6f}, {center_lng:.6f}] with zoom: {zoom}")
        else:
            # No valid coordinates found
            cached_data = {
                'dataframe': df,
                'center': [23.4869, 58.4834],  # Default safe coordinates
                'zoom': 8,
                'processed': False
            }
            logger.warning("No valid coordinates found in uploaded file")
        
        filename_div = html.Div(f"Uploaded: {filename} ({len(valid_lats)} valid sites)")
        trigger_value = f"processed_{int(time.time())}"  # Unique trigger value
        
        return filename_div, trigger_value
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        # Reset cached data on error
        cached_data = {
            'dataframe': None,
            'center': None,
            'zoom': 2,
            'processed': False
        }
        return html.Div(f"Error processing file: {str(e)}", style={'color': 'red'}), no_update

# FIX 2: Consolidated map update callback (single source of truth)
@app.callback(
    [Output('map', 'children'),
     Output('map-info', 'children')],
    [Input('trigger-map-update', 'children')],
    prevent_initial_call=True
)
def update_map_content_consolidated(trigger):
    """
    FIXED: Single callback for updating map content.
    Consolidates initialize_map and update_map_content to prevent conflicts.
    """
    global cached_data
    
    if trigger is None or cached_data['dataframe'] is None:
        raise PreventUpdate
    
    try:
        df = cached_data['dataframe']
        
        # Create markers from valid coordinates
        markers = []
        
        if isinstance(df, dict):
            # Handle dict format (CSV data)
            lats = df.get('latitude', [])
            lngs = df.get('longitude', [])
            
            for idx, (lat, lng) in enumerate(zip(lats, lngs)):
                if lat and lng and -90 <= lat <= 90 and -180 <= lng <= 180:
                    markers.append(
                        dl.Marker(
                            position=[lat, lng],
                            children=[
                                dl.Tooltip(f"Site {idx}: ({lat:.4f}, {lng:.4f})")
                            ]
                        )
                    )
        else:
            # Handle pandas DataFrame format
            valid_coords = df.dropna(subset=['latitude', 'longitude'])
            for idx, row in valid_coords.iterrows():
                markers.append(
                    dl.Marker(
                        position=[row['latitude'], row['longitude']],
                        children=[
                            dl.Tooltip(f"Site {idx}: ({row['latitude']:.4f}, {row['longitude']:.4f})")
                        ]
                    )
                )
        
        # Create map children - single authoritative update
        map_children = [
            dl.TileLayer(),
            dl.MarkerClusterGroup(children=markers) if markers else dl.LayerGroup()
        ]
        
        info_text = f"Displaying {len(markers)} sites on map"
        logger.info(f"Map content updated: {info_text}")
        
        return map_children, info_text
        
    except Exception as e:
        logger.error(f"Error updating map content: {e}")
        return [dl.TileLayer()], f"Error: {str(e)}"

# FIX 3: Separate flyTo callback with proper timing and safeguards  
@app.callback(
    Output('map', 'flyTo'),
    [Input('map-info', 'children')],  # Triggered after map content is updated
    prevent_initial_call=True
)
def fly_to_data_center_fixed(map_info):
    """
    FIXED: Separate flyTo callback that runs after map content update.
    Uses cached center coordinates to prevent [0,0] fallback.
    """
    global cached_data
    
    if (map_info is None or 
        cached_data['center'] is None or 
        not cached_data['processed']):
        raise PreventUpdate
    
    try:
        # Use pre-calculated center coordinates from cache
        center_lat, center_lng = cached_data['center']
        zoom = cached_data['zoom']
        
        # Safeguard against invalid coordinates
        if (not (-90 <= center_lat <= 90) or 
            not (-180 <= center_lng <= 180) or
            (center_lat == 0 and center_lng == 0)):
            logger.warning("Invalid center coordinates detected, using default")
            center_lat, center_lng = 23.4869, 58.4834
            zoom = 8
        
        logger.info(f"Flying to: [{center_lat:.6f}, {center_lng:.6f}] (zoom: {zoom})")
        
        return {"lat": center_lat, "lng": center_lng, "zoom": zoom}
        
    except Exception as e:
        logger.error(f"Error in fly_to_data_center_fixed: {e}")
        # Fallback to safe coordinates
        return {"lat": 23.4869, "lng": 58.4834, "zoom": 8}

# Enhanced debugging callback to track map center changes
@app.callback(
    Output('legend', 'children'),
    [Input('map', 'center')],
    prevent_initial_call=True
)
def show_map_center_debug(center):
    """
    ENHANCED: Display current map center with more detailed debugging info.
    Helps track the [0,0] reset issue.
    """
    if center:
        # Check for problematic [0,0] coordinates
        if center.get('lat') == 0 and center.get('lng') == 0:
            logger.warning("⚠️  Map center reset to [0,0] detected!")
            return html.Div([
                html.Span("⚠️ WARNING: Map reset to [0,0]", style={'color': 'red', 'fontWeight': 'bold'}),
                html.Br(),
                html.Span(f"Current center: {center}")
            ])
        else:
            logger.info(f"✅ Map center: {center}")
            return html.Div([
                html.Span("✅ Map Center: ", style={'color': 'green'}),
                html.Span(f"[{center.get('lat', 'N/A'):.6f}, {center.get('lng', 'N/A'):.6f}]"),
                html.Br(),
                html.Span(f"Zoom: {center.get('zoom', 'N/A')}")
            ])
    
    return html.Div("Map center not available")

# Fixed site jumping functionality (no conflicts)
@app.callback(
    Output('map', 'flyTo', allow_duplicate=True),
    [Input('map', 'click_lat_lng')],
    prevent_initial_call=True,
    allow_duplicate=True
)
def jump_to_site_fixed(click_data):
    """
    FIXED: Site jumping functionality with proper coordinate validation.
    """
    if click_data and 'lat' in click_data and 'lng' in click_data:
        lat, lng = click_data['lat'], click_data['lng']
        
        # Validate coordinates
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            logger.info(f"Jumping to clicked site: [{lat:.6f}, {lng:.6f}]")
            return {"lat": lat, "lng": lng, "zoom": 15}
        else:
            logger.warning(f"Invalid click coordinates: {click_data}")
    
    raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)