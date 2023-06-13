import csv

input_file = 'text-davinci-003_temp0.5_results.csv'
output_file = input_file.replace('.', '_filtered.')

# Open the input CSV file
with open(input_file, 'r') as file:
    reader = csv.DictReader(file)
    data = list(reader)

# Filter out rows with null colorNameId
filtered_data = [row for row in data if row['colorNameId']]

# Calculate the percentage of missing colorNameIds for each language
language_counts = {}
total_rows = len(data)
missing_color_counts = {}

for row in data:
    language = row['lang0']
    if language not in language_counts:
        language_counts[language] = 0
        missing_color_counts[language] = 0

    language_counts[language] += 1

    if not row['colorNameId']:
        missing_color_counts[language] += 1

# Calculate the percentage of missing colorNameIds
percentage_missing = {
    language: (missing_color_counts[language] / language_counts[language]) * 100
    for language in language_counts
}

# Create the output CSV file
fieldnames = ['colorNameId', 'participantId', 'lang0', 'phaseNum', 'trialNum', 'tileNum',
              'name', 'r', 'g', 'b', 'studyVersion', 'rgbSet', 'lab_l', 'lab_a', 'lab_b', 'locale']

with open(output_file, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(filtered_data)

# Print the percentage of missing colorNameIds for each language
for language, percentage in percentage_missing.items():
    print(f"Percentage of missing colorNameIds for {language}: {percentage}%")
