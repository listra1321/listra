import ast

class CaptionLookup:

    def __init__(self, file_path):

        self.mapping = {}

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # skip header
        for line in lines[1:]:

            line = line.strip()

            if not line:
                continue

            try:
                parts = line.split(",", 1)

                if len(parts) < 2:
                    continue

                raw_photos = parts[0].strip()
                caption = parts[1].strip().strip('"')

                try:
                    photos_list = ast.literal_eval(raw_photos)

                    if isinstance(photos_list, list):
                        for p in photos_list:
                            self.mapping[p.lower().strip()] = caption
                    else:
                        self.mapping[str(photos_list).lower().strip()] = caption

                except:
                    self.mapping[raw_photos.lower().strip()] = caption

            except:
                continue

    def get_caption(self, filename):
        filename = filename.lower().strip()

        if filename in self.mapping:
            return self.mapping[filename]

        for key in self.mapping:
            if filename in key:
                return self.mapping[key]

        return None
