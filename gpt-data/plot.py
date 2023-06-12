import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import colorsys
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
from scipy.spatial import Voronoi, voronoi_plot_2d

# load csv file
df = pd.read_csv('text-davinci-003_results.csv')
# df = pd.read_csv('text-davinci-003_temp0.5_results.csv')

# convert RGB to HSV
def convert_rgb_to_hsv(row):
    r = row['r'] / 255.0
    g = row['g'] / 255.0
    b = row['b'] / 255.0
    hsv = colorsys.rgb_to_hsv(r, g, b)
    return pd.Series(hsv)

df[['h', 's', 'v']] = df.apply(convert_rgb_to_hsv, axis=1)

# filter out names that occur less than 5 times
df['name'] = df['name'].str.lower()
df = df.groupby('name').filter(lambda x: len(x) >= 10)

# create a plot for each language
languages = df['lang0'].unique()

# Find a font that can handle the characters
# for font in fm.findSystemFonts():
#     fp = fm.FontProperties(fname=font)
#     if fp.get_name() == 'Arial Unicode MS':
#         break
fp = fm.FontProperties(fname='/System/Library/Fonts/Supplemental/Arial Unicode.ttf')

# Set the font to "Noto Sans" which supports a wide range of characters
# font = FontProperties(fname='/Users/michaelbyun/Library/Fonts/NotoSans-Regular.ttf')

for lang in languages:
    df_lang = df[df['lang0'] == lang]
    
    # Calculate average location for each unique color name
    df_lang = df_lang.groupby('name').agg({'h': 'mean', 's': 'mean', 'v': 'mean'}).reset_index()

    # create HSV color space as an image
    hsv_image = np.zeros((100, 100, 3))
    for i in range(100):
        for j in range(100):
            hsv_image[i, j, 0] = j / 100.0
            hsv_image[i, j, 1] = i / 100.0
            hsv_image[i, j, 2] = 1  # set value (brightness) to maximum

    # Convert the HSV image to RGB
    hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)
    rgb_image = hsv_to_rgb(hsv_image[..., 0], hsv_image[..., 1], hsv_image[..., 2])
    rgb_image = np.dstack(rgb_image)  # stack along the third dimension

    # Create Voronoi diagram
    vor = Voronoi(df_lang[['h', 's']].values)

    plt.figure(figsize=(10, 8))
    plt.imshow(rgb_image, origin='lower', extent=[0, 1, 0, 1])
    voronoi_plot_2d(vor, show_points=False, show_vertices=False, ax=plt.gca())

    plt.title(f'Color space for {lang}')
    plt.xlabel('Hue')
    plt.ylabel('Saturation')

    # Add color names as annotations
    for i, txt in enumerate(df_lang['name']):
        plt.annotate(txt, (df_lang['h'].iloc[i], df_lang['s'].iloc[i]), 
                     fontproperties=fp, ha='center', va='center')
        
    plt.tight_layout()
    plt.savefig(f'color_space_{lang}.png')
    plt.show()