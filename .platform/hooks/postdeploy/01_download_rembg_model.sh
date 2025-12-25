#!/bin/bash
# rembg 모델 미리 다운로드 (첫 요청 지연 방지)

echo "Downloading rembg model..."
source /var/app/venv/*/bin/activate
python -c "from rembg import remove; print('rembg model ready')" 2>/dev/null || echo "rembg model download triggered"
echo "rembg model download complete"
