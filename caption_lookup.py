import pandas as pd
import ast

class CaptionLookup:

    def __init__(self, file_path):
        self.df = pd.read_csv(file_path, on_bad_lines='skip')

        self.mapping = {}

        for _, row in self.df.iterrows():
            try:
                photos = ast.literal_eval(row['photos'])
            except:
                photos = [row['photos']]

            for p in photos:
                self.mapping[p.lower().strip()] = row['image_story']

    def get_caption(self, photos):
        return self.mapping.get(photos.lower().strip(), None)
