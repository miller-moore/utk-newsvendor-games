import uuid
from pathlib import Path
from threading import Event, Thread
from typing import Generator, List, Union

import requests
from serpapi import GoogleSearch


class GoogleImageDownloader(Thread):
    def __init__(self, query: str, api_key: str, download_directory: Union[str, Path], max_count: int = 25) -> None:
        self.query = query
        self.download_directory = Path(download_directory).resolve(strict=True)
        assert self.download_directory.is_dir(), f"download_directory is not a directory - got {download_directory!r}"
        self.api_key = api_key
        self.stopped = False
        self.max_count = max_count
        self._stop_event = Event()
        super().__init__(target=self.run, daemon=True)
        self.start()

    def run(self):
        self.downloader()

    def stop(self):
        self._stop_event.set()

    @property
    def smokey_images(self) -> List[Path]:
        return [p for p in self.download_directory.iterdir() if p.name.startswith("smokey") and p.name.endswith(".jpg")]

    def downloader(self) -> None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        for image_url in self.search_images():
            if self._stop_event.is_set() or len(self.smokey_images) >= self.max_count:
                break
            # yield image_url
            response = requests.get(image_url, allow_redirects=True, headers=headers)
            response.raise_for_status()
            # img_filename = image_url.split("/")[-1]
            # if "?" in img_filename:
            #     img_filename = img_filename.split("?")[0]
            img_filename = f"smokey-{uuid.uuid4()}.jpg"
            img_path = self.download_directory.joinpath(img_filename)
            with open(img_path, "wb") as img_file:
                img_file.write(response.content)

        self.stopped = True

    def search_images(self) -> Generator[str, None, None]:
        if self.api_key:
            search = GoogleSearch({"q": self.query, "tbm": "isch", "api_key": self.api_key})
            for image_result in search.get_dict()["images_results"]:
                link = image_result["original"]
                yield link
