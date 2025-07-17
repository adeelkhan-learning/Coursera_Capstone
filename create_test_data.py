import csv
import random
import math

# Create sample GSM site data for testing using only built-in Python
random.seed(42)

# Generate test data around UAE/Oman region (similar to original issue)
n_sites = 50
center_lat, center_lng = 23.4869, 58.4834

# Generate coordinates in a realistic distribution
def generate_normal(mean, std_dev):
    """Simple normal distribution using Box-Muller transform"""
    u1 = random.random()
    u2 = random.random()
    z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mean + std_dev * z0

# Create sample data
data = []
data.append(['site_id', 'latitude', 'longitude', 'signal_strength', 'frequency', 'cell_type'])

for i in range(n_sites):
    lat = generate_normal(center_lat, 0.5)
    lng = generate_normal(center_lng, 0.7)
    site_data = [
        f'SITE_{i:03d}',
        lat,
        lng,
        random.uniform(-100, -50),
        random.choice([900, 1800, 2100]),
        random.choice(['2G', '3G', '4G'])
    ]
    data.append(site_data)

# Save to CSV file for testing
with open('/home/runner/work/Coursera_Capstone/Coursera_Capstone/test_gsm_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)

# Calculate stats
lats = [row[1] for row in data[1:]]  # Skip header
lngs = [row[2] for row in data[1:]]  # Skip header

print(f"Created test data with {len(data)-1} sites")
print(f"Coordinate range: Lat {min(lats):.4f} to {max(lats):.4f}")
print(f"                  Lng {min(lngs):.4f} to {max(lngs):.4f}")
print(f"Center: [{sum(lats)/len(lats):.4f}, {sum(lngs)/len(lngs):.4f}]")