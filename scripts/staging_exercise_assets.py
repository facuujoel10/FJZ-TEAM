"""Package the licensed exercise stills used by the staging application."""
import concurrent.futures
import hashlib
import io
import pathlib
import urllib.request
import zipfile

REVISION = "f12da458a90f353a86c953f204304d5a8bd98275"
ARCHIVE_SHA256 = "2ead2fcc7e8ee07171c3d08fe23edd13ea2de92b0861117fd6df77249947708c"


def package(guides, output):
    destination = output / "exercise-media"
    destination.mkdir(exist_ok=True)
    assets = pathlib.Path(__file__).resolve().parents[1] / "src/modules/activity/illustrations"
    for guide in guides.values():
        if guide['src'] == 'local':
            for name in guide['files']:
                (destination / name).write_bytes((assets / name).read_bytes())
    url = f"https://codeload.github.com/RepDB/exercise-dataset/zip/{REVISION}"
    with urllib.request.urlopen(url, timeout=90) as response:
        archive = response.read()
    if hashlib.sha256(archive).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Exercise illustration archive checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        prefix = f"exercise-dataset-{REVISION}/images/flat/"
        for name in {p for g in guides.values() if g['src'] == 'rep' for p in g['files']}:
            (destination / name).write_bytes(source.read(prefix + name))

    def save_photo(name):
        path = destination / name
        path.parent.mkdir(exist_ok=True)
        url = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/" + name
        with urllib.request.urlopen(url, timeout=45) as response:
            data = response.read()
        if not data.startswith(b"\xff\xd8"):
            raise ValueError(f"Invalid exercise photo {name}")
        path.write_bytes(data)

    photos = {p for g in guides.values() if g['src'] == 'free' for p in g['files']}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as workers:
        list(workers.map(save_photo, sorted(photos)))
