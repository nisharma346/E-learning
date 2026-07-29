from pathlib import Path
root = Path(__file__).resolve().parent.parent
jpg = root / 'static' / 'images' / 'about.jpg'
ico = root / 'static' / 'favicon.ico'
jpg.parent.mkdir(parents=True, exist_ok=True)
if not jpg.exists():
    jpg.write_bytes(bytes.fromhex(
        'ffd8ffe000104a46494600010101004800480000ffdb004300020101020101020202020202020202020202020202020202020202020202020202020202020202020202020202020202ff'
        'c00011080001000103012200021101031101ffc40014000100030002030000000000000000010002030405060000000001020304050607ffc4001401010003000203010000000000000001020304050607ffd'
        'a000c03010002110311003f00d11a001e0a643f01ffd9'
    ))
import base64

if not ico.exists():
    ico_data = base64.b64decode(
        'AAABAAEAEBAAAAAAAAoAAAAQAAAAIAAAACAAQAAAAAAEAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAA'  # 1x1 pixel ICO
    )
    ico.write_bytes(ico_data)
print('created', jpg.exists(), ico.exists())
