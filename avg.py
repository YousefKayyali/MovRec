import pandas as pd

# Load the CSV file
file_path = r'C:\Users\user\Desktop\movrec_data\update_3\avgrating.CSV'
df = pd.read_csv(file_path)

# Drop the 'count_rating' and 'rank' columns
df = df.drop(columns=['count_rating', 'rank'])

# Multiply the 'rating' column by 2 and round to two decimal places
df['rating'] = (df['rating'] * 2).round(2)

# Rename the columns
df = df.rename(columns={'movie_id': 'movieId', 'rating': 'rating'})

# Save the modified DataFrame back to a CSV file
output_path = r'C:\Users\user\Desktop\movrec_data\update_3\avgrating_modified.CSV'
df.to_csv(output_path, index=False)

print("CSV file has been modified and saved successfully.")