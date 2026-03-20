import pandas as pd

class CaptionLookup:

    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)

        self.df['photos'] = self.df['photos'].str.lower().str.strip()

    def get_caption(self, photos):

        photos = photos.lower().strip()

        match = self.df[self.df['photos'] == photos]

        if not match.empty:
            return match.iloc[0]['image_story']

        return None