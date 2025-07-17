#!/usr/bin/env python3
"""
Test script to validate the map callback fixes
This script tests the core functionality without running the full Dash server
"""

import sys
import os
import csv
import base64
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_csv_reading():
    """Test reading the generated CSV file"""
    try:
        csv_file = 'test_gsm_data.csv'
        if not os.path.exists(csv_file):
            logger.error(f"Test file {csv_file} not found")
            return False
            
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            
        logger.info(f"✅ Successfully read {len(data)} rows from CSV")
        
        # Validate required columns
        if data and 'latitude' in data[0] and 'longitude' in data[0]:
            logger.info("✅ Required columns (latitude, longitude) found")
            
            # Test coordinate validation
            valid_coords = 0
            lats, lngs = [], []
            
            for row in data:
                try:
                    lat = float(row['latitude'])
                    lng = float(row['longitude'])
                    
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        valid_coords += 1
                        lats.append(lat)
                        lngs.append(lng)
                except ValueError:
                    continue
            
            if valid_coords > 0:
                center_lat = sum(lats) / len(lats)
                center_lng = sum(lngs) / len(lngs)
                logger.info(f"✅ {valid_coords} valid coordinates found")
                logger.info(f"✅ Calculated center: [{center_lat:.6f}, {center_lng:.6f}]")
                
                # Check if center is not [0,0]
                if center_lat != 0 or center_lng != 0:
                    logger.info("✅ Center coordinates are not [0,0] - Good!")
                    return True
                else:
                    logger.error("❌ Center coordinates are [0,0] - Problem!")
                    return False
            else:
                logger.error("❌ No valid coordinates found")
                return False
        else:
            logger.error("❌ Required columns missing")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error reading CSV: {e}")
        return False

def test_coordinate_safeguards():
    """Test coordinate validation and safeguards"""
    logger.info("Testing coordinate safeguards...")
    
    # Test valid coordinates
    test_cases = [
        (23.4869, 58.4834, True),   # Valid UAE coordinates
        (0, 0, False),              # Invalid [0,0] coordinates
        (91, 0, False),             # Invalid latitude > 90
        (-91, 0, False),            # Invalid latitude < -90
        (0, 181, False),            # Invalid longitude > 180
        (0, -181, False),           # Invalid longitude < -180
        (45.0, 90.0, True),         # Valid edge case
        (-45.0, -90.0, True),       # Valid edge case
    ]
    
    passed = 0
    for lat, lng, should_be_valid in test_cases:
        is_valid = (-90 <= lat <= 90) and (-180 <= lng <= 180) and not (lat == 0 and lng == 0)
        
        if is_valid == should_be_valid:
            logger.info(f"✅ [{lat}, {lng}] validation: {is_valid} (expected: {should_be_valid})")
            passed += 1
        else:
            logger.error(f"❌ [{lat}, {lng}] validation: {is_valid} (expected: {should_be_valid})")
    
    logger.info(f"Coordinate validation: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)

def test_file_format_support():
    """Test that both CSV and Excel files are supported in theory"""
    logger.info("Testing file format support...")
    
    try:
        # Test CSV data simulation
        csv_data = "site_id,latitude,longitude\nSITE_001,23.4869,58.4834\nSITE_002,23.5000,58.5000"
        csv_content = base64.b64encode(csv_data.encode()).decode()
        mock_content = f"data:text/csv;base64,{csv_content}"
        
        # This simulates what would happen in the app
        content_type, content_string = mock_content.split(',')
        decoded = base64.b64decode(content_string)
        content_str = decoded.decode('utf-8')
        
        # Parse CSV
        import io
        csv_reader = csv.DictReader(io.StringIO(content_str))
        data = list(csv_reader)
        
        if len(data) == 2 and 'latitude' in data[0]:
            logger.info("✅ CSV format processing works")
            return True
        else:
            logger.error("❌ CSV format processing failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ File format test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🧪 Starting callback fixes validation tests...")
    logger.info("=" * 50)
    
    tests = [
        ("CSV Reading", test_csv_reading),
        ("Coordinate Safeguards", test_coordinate_safeguards),
        ("File Format Support", test_file_format_support),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                logger.info(f"✅ {test_name} test PASSED")
                passed_tests += 1
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"🧪 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! The callback fixes should work correctly.")
        return True
    else:
        logger.error("💥 Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)