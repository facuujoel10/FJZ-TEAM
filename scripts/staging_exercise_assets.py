"""Publish the TEAM FJZ exercise illustrations and validate catalog coverage."""
import pathlib
import zipfile


def package(guides, output):
    destination = output / "exercise-media"
    destination.mkdir(exist_ok=True)
    assets = pathlib.Path(__file__).resolve().parents[1] / "src/modules/activity/illustrations"
    required = {name for guide in guides.values() if guide["src"] == "catalog" for name in guide["files"]}
    written = set()
    for archive in sorted((assets / "catalog").glob("*.zip")):
        with zipfile.ZipFile(archive) as frames:
            for name in frames.namelist():
                if name not in required or name in written or pathlib.Path(name).name != name:
                    raise ValueError(f"Unexpected exercise illustration: {name}")
                (destination / name).write_bytes(frames.read(name))
                written.add(name)
    if written != required:
        raise ValueError(f"Missing exercise illustrations: {sorted(required - written)}")
    for guide in guides.values():
        if guide["src"] == "local":
            for name in guide["files"]:
                (destination / name).write_bytes((assets / name).read_bytes())
        elif guide["src"] not in {"catalog", "fjz"}:
            raise ValueError(f"Unknown illustration source for {guide['name']}")
