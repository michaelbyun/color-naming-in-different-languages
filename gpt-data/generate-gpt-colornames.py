import openai
import pandas as pd
import random
import re
import os
from tqdm import tqdm

engine = "text-davinci-003"

# def hsv2rgb(h,s,v):
#     return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

# def rgb2hex(rgb):
#     return "#{:02x}{:02x}{:02x}".format(*rgb)

# def generate_colors(num_colors):
#     return [rgb2hex(hsv2rgb(hue, 1, 1)) for hue in [i/num_colors for i in range(num_colors)]]

# hex_colors = generate_colors(36)


openai.api_key = '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'

# Define a list of languages and their prompt templates
# languages = [
#     {"language": "English", "template": "The most common English name for the color {hexcode} is"},
#     {"language": "Chinese", "template": "{hexcode}颜色的最常见的中文名称是："},
#     {"language": "Russian", "template": "Самое распространенное русское название для цвета {hexcode} - это"},
#     {"language": "Korean", "template": "{hexcode} 색상의 가장 일반적인 한국어 이름은"},
# ]
languages = [
    {"language": "English", "template": "The most common name for the color {hexcode} is"},
    {"language": "Chinese", "template": "{hexcode}颜色的最常见名称是："},
    {"language": "Russian", "template": "Самое распространенное название для цвета {hexcode} - это"},
    {"language": "Korean", "template": "{hexcode} 색상의 가장 일반적인 이름은"},
]
# languages = [
#     {"language": "English", "template": "The best name for the color {hexcode} is"},
#     {"language": "Chinese", "template": "{hexcode}颜色的最佳名称是："},
#     {"language": "Russian", "template": "Лучшее название для цвета {hexcode} - это"},
#     {"language": "Korean", "template": "{hexcode} 색상의 가장 적합한 이름은"},
# ]
# languages = [
#     {"language": "English", "template": "Question: What color is {hexcode}? Answer:"},
#     {"language": "Chinese", "template": "问题：{hexcode}是什么颜色？答案："},
#     {"language": "Russian", "template": "Вопрос: Какой цвет {hexcode}? Ответ:"},
#     {"language": "Korean", "template": "질문: {hexcode}의 색깔은 무엇입니까? 답변:"},
# ]

def get_color(s):
    # Remove parentheticals
    s = re.sub(r'\([^)]*\)', '', s)

    match = re.search(r'[a-zA-Z]+(?:[\s-][a-zA-Z]+)*', s)
    if match:
        return re.sub(r'[^a-zA-Z\s-]', '', match.group(0)).strip()

    match = re.search(r'[\u4e00-\u9fff]+(?:[\s-][\u4e00-\u9fff]+)*', s)
    if match:
        return match.group(0).strip()

    match = re.search(r'[\u0400-\u04FF]+(?:[\s-][\u0400-\u04FF]+)*', s)
    if match:
        return re.sub(r'[^a-zA-Z\u0400-\u04FF\s-]', '', match.group(0)).strip()

    match = re.search(r'[\uAC00-\uD7AF]+(?:[\s-][\uAC00-\uD7AF]+)*', s)
    if match:
        color_kor = re.sub(r'[^가-힣\s-]', '', match.group(0))
        color_kor = color_kor.replace("입니다", "")
        return color_kor.strip()

    return None

# Prepare an empty list to store the results
results = []


for j in tqdm(range(1000)):
    # Randomly sample from RGB colorspace
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    code = '#%02x%02x%02x' % (r, g, b)
    # print(code)

    # Loop through each language
    for lang in languages:
        # Format the prompt
        if lang != "Chinese":
            prompt = lang['template'].format(hexcode=code)
        else:
            fw_hexcode = "#" + ''.join([chr(ord(char) + 0xFEE0) if char.isdigit() else char for char in code])
            prompt = lang['template'].format(hexcode=fw_hexcode)

        # Loop through the number of desired queries per hex code per language
        for i in range(1):
            # Call the API
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=0.0,
                max_tokens=50
            )
            
            colorname = get_color(response.choices[0].text.strip())

            # Append the result to the results list
            results.append({
                "colorNameId": "",
                "participantId": "-1",
                "lang0": lang['language'] + " (" + engine + ")",
                "phaseNum":"0",
                "trialNum":"-1",
                "tileNum":"-1",
                "name": colorname,
                "r": str(int(code[1:3], 16)),
                "g": str(int(code[3:5], 16)),
                "b": str(int(code[5:], 16)),
                "studyVersion":"1.1.5",
                "rgbSet":"full",
                "lab_l":"-1",
                "lab_a":"-1",
                "lab_b":"-1",
                "locale":"en"
            })
            # results.append({
            #     'Hex Code': code,
            #     'Language': lang['language'],
            #     'Prompt': prompt,
            #     'Response': response['choices'][0]['text'].strip(),
            #     'Query Number': i + 1  # Add query number to keep track of each query
            # })

# Convert the results to a pandas DataFrame
df = pd.DataFrame(results)

# Step 1: Load color_perception_table_color_names.csv into a DataFrame
color_names_df = pd.read_csv('../raw/color_perception_table_color_names.csv')

# Step 2 and 3: Iterate over each row in df and match with color_names_df
for index, row in df.iterrows():
    name = row['name']
    matching_row = color_names_df.loc[color_names_df['name'] == name]
    
    # Step 4: Populate the colorNameId column in df with the retrieved value
    if not matching_row.empty:
        colorNameId = matching_row.iloc[0]['colorNameId']
        df.at[index, 'colorNameId'] = colorNameId

# Check if the file exists
if not os.path.isfile(f'{engine}_results.csv'):
    # If the file doesn't exist, write the DataFrame to a new CSV file with the header
    df.to_csv(f'{engine}_results.csv', index=False)
else:
    # If the file exists, append to it without the header
    df.to_csv(f'{engine}_results.csv', mode='a', header=False, index=False)