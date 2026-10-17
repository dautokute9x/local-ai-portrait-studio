# License Notes

Dự án này **chỉ dùng cho mục đích cá nhân**. Bảng dưới đây ghi license của từng thành phần.
Ô nào chưa chắc chắn đều ghi **VERIFY BEFORE COMMERCIAL USE**. Ghi chú này không phải tư vấn pháp lý.

## Thư viện đang dùng (Phase 1)

| Component | Library | License | Personal Use | Commercial Notes |
|---|---|---|---|---|
| Desktop UI | PySide6-Essentials / Qt 6 | LGPLv3 (hoặc Qt commercial) | Yes | Nếu phân phối phải tuân thủ LGPL (cho phép thay thư viện Qt) |
| Image I/O, EXIF | Pillow | MIT-CMU (HPND) | Yes | OK |
| Array | numpy | BSD-3-Clause | Yes | OK |
| Test | pytest, pytest-qt | MIT | Yes | Chỉ dùng khi phát triển |
| UI icons | Lucide (`lucide-static` 1.49.0) — 5 file SVG trong `app/ui/icons/` | ISC (một số icon gốc Feather: MIT) | Yes | OK; giữ file `app/ui/icons/LICENSE-lucide.txt` khi phân phối |

## Dự kiến (chưa cài — chốt ở Checkpoint C từng phase)

| Component | Model/Library | License | Personal Use | Commercial Notes |
|---|---|---|---|---|
| Image processing | OpenCV (opencv-contrib-python) | Apache-2.0 | Yes | OK |
| Inference | ONNX Runtime / onnxruntime-gpu | MIT | Yes | OK. CUDA/cuDNN có EULA riêng của NVIDIA |
| Face detection | YuNet (opencv_zoo) | MIT | Yes | VERIFY BEFORE COMMERCIAL USE |
| Landmarks | MediaPipe FaceLandmarker | Apache-2.0 | Yes | VERIFY BEFORE COMMERCIAL USE (model card) |
| Face parsing | BiSeNet (face-parsing) — weights CelebAMask-HQ | Code MIT; dataset **non-commercial** | Yes | **Không dùng thương mại** |
| Background removal | MODNet | Apache-2.0 (repo) | Yes | VERIFY BEFORE COMMERCIAL USE (weights) |
| Object removal | LaMa (big-lama) | Apache-2.0 (code) | Yes | VERIFY BEFORE COMMERCIAL USE (weights) |
| Upscale | Real-ESRGAN (realesr-general-x4v3) | BSD-3-Clause | Yes | VERIFY BEFORE COMMERCIAL USE |
| Face enhance (optional) | GFPGAN v1.4 | Apache-2.0 + thành phần bên thứ ba | Yes | VERIFY BEFORE COMMERCIAL USE |
| Face enhance (optional) | CodeFormer | S-Lab License 1.0 | Yes | **Non-commercial** |

Bản ONNX do bên thứ ba convert phải được kiểm tra license gốc và SHA256 trước khi dùng.
