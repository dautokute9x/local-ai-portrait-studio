# Local AI Portrait Studio

Ứng dụng chỉnh ảnh chân dung bằng AI, chạy **hoàn toàn trên máy cá nhân**, ngân sách 0 đồng.
Dự án cá nhân, lấy cảm hứng từ workflow của các app retouch chân dung. Dự án này không dùng code, model hay tài sản độc quyền của bất kỳ sản phẩm nào.

> **Your images stay on your computer.**
> Không upload ảnh, không telemetry, không gọi API ngoài. Chỉ cần internet một lần để tải model (từ Phase 2).

## Trạng thái

| Phase | Nội dung | Trạng thái |
|---|---|---|
| 0 | Kiến trúc & chọn công nghệ | Đã duyệt |
| 1 | Image viewer (mở ảnh, preview, zoom, thumbnail, export) | Đang làm: Step 1.3 mở ảnh |
| 2–10 | Face detection → … → Batch | Chưa bắt đầu |

## Tech stack

- **UI:** PySide6 (Qt 6) — `PySide6-Essentials`
- **Ảnh:** Pillow (EXIF/orientation), numpy; OpenCV từ Phase 2
- **AI:** ONNX Runtime (không cần PyTorch); GPU NVIDIA qua `onnxruntime-gpu` từ Phase 7
- **Python:** 3.11 (hỗ trợ 3.11–3.12)

## Cài đặt (Windows 10/11)

Cần cài sẵn [Python 3.11](https://www.python.org/downloads/) (tick "Add python.exe to PATH").

```bat
cd local-ai-portrait-studio
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Chạy app

```bat
.venv\Scripts\activate
python -m app
```

Log được ghi ra `logs\app.log`.

## Chạy test

```bat
pip install -r requirements-dev.txt
python -m pytest
```

## Cấu trúc thư mục

```text
app/
  main.py            entry point: logging, chống crash, QApplication
  core/              logic không phụ thuộc UI (paths, logging, sau này: params, render)
  ui/                widget Qt
models/              model AI (không commit; tải bằng script từ Phase 2)
tests/               pytest + pytest-qt
```

Quy tắc: `app/core` và `app/ai` **không được import** `app/ui`.
