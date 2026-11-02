import sys
sys.stdout.reconfigure(encoding='utf-8')

import zipfile
import os
import shutil

os.makedirs("pptx_images", exist_ok=True)

with zipfile.ZipFile("HealthRoute_AI.pptx", 'r') as z:
    media_files = [f for f in z.namelist() if f.startswith('ppt/media/')]
    print(f"Found {len(media_files)} media files:")
    for mf in sorted(media_files):
        fname = os.path.basename(mf)
        out_path = f"pptx_images/{fname}"
        with z.open(mf) as src, open(out_path, 'wb') as dst:
            shutil.copyfileobj(src, dst)
        print(f"  Extracted: {out_path}")
