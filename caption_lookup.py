import pandas as pd
import ast

class CaptionLookup:

    def __init__(self, file_path):

        # baca sebagai raw text dulu (anti crash)
        try:
            self.df = pd.read_csv(
                file_path,
                encoding="utf-8",
                sep=",",
                engine="python",  
                on_bad_lines="skip"
            )
        except Exception as e:
            print("ERROR READ CSV:", e)
            self.df = pd.DataFrame(columns=["photos", "image_story"])

        self.mapping = {}

        #
        for _, row in self.df.iterrows():

            raw_photos = str(row.get("photos", "")).strip()
            caption = str(row.get("image_story", "")).strip()

            if not raw_photos or raw_photos == "[]":
                continue

            try:
                # kalau bentuk list
                photos_list = ast.literal_eval(raw_photos)

                if isinstance(photos_list, list):
                    for p in photos_list:
                        self.mapping[p.lower().strip()] = caption

                else:
                    self.mapping[str(photos_list).lower().strip()] = caption

            except:
                # fallback kalau bukan list
                self.mapping[raw_photos.lower().strip()] = caption

    def get_caption(self, filename):
        return self.mapping.get(filename.lower().strip(), None)
