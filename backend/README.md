# rve-backend-py

pip install --pre -r  requirements.txt --extra-index-url https://download.pytorch.org/whl/test/cu126

## New Features (v2.4.2)

### PNG Sequence Input

Process a folder of numbered PNG frames as input using ffmpeg:

```bash
python3 rve-backend.py \
  -i /path/to/frames/frame%04d.png \
  --input_is_png_sequence \
  --input_png_sequence_start_number 1 \
  -o output.mp4 \
  --upscale_model /path/to/model.pth
```

### PNG Sequence Output

Save processed output as numbered PNGs by using a `%Nd.png` pattern as the output path:

```bash
python3 rve-backend.py \
  -i input.mp4 \
  -o /path/to/output/frame%08d.png \
  --upscale_model /path/to/model.pth
```

### Downscale to Original Resolution After Upscale

Use `--ffmpeg_downscale_to_original` to run `ffmpeg -vf scale=WxH` after upscaling, outputting at the original input resolution:

```bash
python3 rve-backend.py \
  -i input.mp4 \
  -o output.mp4 \
  --upscale_model /path/to/model.pth \
  --ffmpeg_downscale_to_original
```
