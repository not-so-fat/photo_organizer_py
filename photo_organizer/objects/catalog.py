from glob import glob
from pathlib import Path

import pandas


from photo_organizer.settings import RATINGS


class Catalog(object):
    def __init__(self, image_dir, jpeg_extension, raw_extension):
        self.catalog_df = pandas.DataFrame(
            {"photo_id": sorted([Path(f).name for f in glob("{}/*.{}".format(image_dir, jpeg_extension))])}
        )
        self.catalog_df["jpeg_path"] = [Path(image_dir) / photo_id for photo_id in self.catalog_df["photo_id"]]
        self.catalog_df["raw_path"] = [
            _get_raw_file_path(photo_id, image_dir, jpeg_extension, raw_extension)
            for photo_id in self.catalog_df["photo_id"]
        ]
        self.only_jpegs = list(self.catalog_df[self.catalog_df["raw_path"].isnull()]["photo_id"])
        self.catalog_df = self.catalog_df[~self.catalog_df["raw_path"].isnull()]
        self.catalog_df["rating"] = 0
        self.length = len(self.catalog_df)
        self.rating_counter = {}
        self.update_rating_counter()

    def get_jpeg_path(self, index):
        return self.catalog_df.iloc[index]["jpeg_path"]

    def rate_photo(self, index, rating):
        self.catalog_df.iloc[index, self.catalog_df.columns.get_loc('rating')] = rating
        self.update_rating_counter()

    def get_rating(self, index):
        return self.catalog_df.iloc[index]["rating"]

    def update_rating_counter(self):
        value_counts = self.catalog_df["rating"].value_counts().to_dict()
        self.rating_counter = {rating: value_counts.get(rating) or 0 for rating in RATINGS.keys()}

    def get_rating_counter(self):
        return self.rating_counter

    def get_photos_on_rating(self, rating):
        return self.catalog_df[self.catalog_df["rating"]==rating]


def _get_raw_file_path(photo_id, image_dir, jpeg_extension, raw_extension):
    raw_file_path = Path(image_dir) / photo_id.replace(".{}".format(jpeg_extension), ".{}".format(raw_extension))
    if not Path(raw_file_path).exists():
        return None
    else:
        return raw_file_path