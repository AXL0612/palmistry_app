# Chỉ Tay AI — Xem chỉ tay trực tuyến bằng 4 mô hình AI

Đồ án: web app cho người dùng xem qua webcam (tự động chụp sau khi giữ tay
3 giây trong khung) hoặc tải ảnh lên, sau đó 4 mô hình AI (Keras `.h5`) chấm
điểm + AI sinh luận giải cho 4 "đường chỉ tay": **Sinh Đạo, Sự Nghiệp, Tâm Đạo,
Trí Đạo**.

```
palmistry-ai/
├── frontend/
│   ├── index.html        # Cấu trúc trang
│   ├── style.css          # Giao diện huyền bí - dark mode (tím/vàng gold/teal)
│   └── script.js           # Webcam, MediaPipe Hands, đếm giữ tay 3s, gọi API
└── backend/                # ĐÂY LÀ PHẦN CODE PYTHON nộp cho thầy
    ├── app.py               # Flask server, API /api/predict
    ├── model_loader.py       # Nạp 4 model .h5 + tiền xử lý ảnh + suy luận
    ├── advice_engine.py       # "Tư vấn": luận giải, điểm nổi bật, lời khuyên
    ├── requirements.txt
    └── models/                # ĐẶT 4 FILE .h5 CỦA BẠN VÀO ĐÂY
```

## 1. Cách chạy

### Backend (Python — bắt buộc phải chạy trước)
```bash
cd backend
pip install -r requirements.txt
# Đặt 4 file vào models/: Sinh_Dao_model.h5, Su_Nghiep_model.h5,
# Tam_Dao_model.h5, Tri_Dao_model.h5 (xem models/_DAT_MODEL_VAO_DAY.txt)
python app.py
```
Server chạy tại `http://localhost:5000`. Kiểm tra nhanh model đã nạp đủ chưa
bằng cách mở `http://localhost:5000/api/health` trên trình duyệt.

### Frontend (HTML/CSS/JS)
**Quan trọng:** webcam (`getUserMedia`) chỉ hoạt động khi trang được phục vụ
qua HTTP, KHÔNG mở trực tiếp file `index.html` bằng cách double-click. Hãy
chạy 1 server tĩnh đơn giản:
```bash
cd frontend
python -m http.server 8080
```
rồi mở `http://localhost:8080` trên trình duyệt (Chrome/Edge khuyến nghị).

## 2. Vì sao code Python tách thành 3 file?

| File | Vai trò | Vì sao tách riêng |
|---|---|---|
| `app.py` | Định nghĩa route Flask, nhận ảnh, trả JSON | Chỉ lo "giao tiếp HTTP", không lẫn logic AI |
| `model_loader.py` | Nạp model 1 lần khi khởi động server, tiền xử lý ảnh, suy luận | Tách để dễ kiểm tra/độc lập, có thể tái dùng ở script khác |
| `advice_engine.py` | Cơ sở tri thức + hàm sinh nội dung tư vấn | Thầy/cô có thể đọc riêng phần "tri thức" mà không cần hiểu Flask |

## 3. Thiết kế "tự thích nghi" với model thật của bạn

Vì 4 model có thể được train với **kích thước ảnh khác nhau** và **kiểu đầu
ra khác nhau** (hồi quy 1 điểm số, hoặc phân loại nhiều lớp), `model_loader.py`
**tự đọc** `model.input_shape` và `model.output_shape` của từng model khi nạp,
rồi:
- Tự resize ảnh đầu vào đúng kích thước model đó cần (không hard-code 224×224).
- Nếu output là 1 giá trị (vd `Dense(1, activation='sigmoid')`) → dùng trực
  tiếp làm điểm số.
- Nếu output là nhiều lớp (vd `Dense(5, activation='softmax')`) → lấy xác
  suất của lớp cao nhất làm điểm số, đồng thời biết được chỉ số lớp đó.

→ Bạn **không cần sửa code** dù 4 model có kiến trúc khác nhau. Mình đã test
logic này bằng 2 model giả lập (1 dạng hồi quy, 1 dạng phân loại) và cả 2 đều
chạy đúng qua `/api/predict`.

## 4. Phần "tư vấn" mở rộng (điểm nổi bật + lời khuyên)

`advice_engine.py` chia mỗi đường chỉ tay thành 4 mức điểm (0-35 / 35-60 /
60-80 / 80-100), mỗi mức có sẵn:
- **Luận giải** — diễn giải ý nghĩa đường chỉ tay ở mức điểm đó.
- **Điểm nổi bật** — 2 đặc điểm tích cực gắn với mức điểm.
- **Lời khuyên** — gợi ý thực tế, mang tính xây dựng (không phán xét, không
  bi quan dù điểm thấp).

Bạn có thể mở rộng thêm tier hoặc viết lại văn bản trong `ADVICE_DB` ở đầu
file mà không ảnh hưởng phần còn lại của hệ thống.

## 5. Ghi chú đạo đức / khoa học

Đây là nội dung **chiêm nghiệm - giải trí** theo thuật xem chỉ tay dân gian,
không có cơ sở khoa học được kiểm chứng, và **không phải** kết luận y khoa,
tâm lý hay tài chính. Mình đã để sẵn `DISCLAIMER` trong `advice_engine.py` và
hiển thị ở cuối trang kết quả — nên giữ lại dòng này khi nộp bài, vừa đúng
tinh thần làm AI có trách nhiệm, vừa là điểm cộng khi thầy/cô chấm phần đạo đức
dữ liệu/AI (nếu có).

## 6. Vài điểm có thể nói thêm khi thuyết trình

- **Nhận diện tay thật, không giả lập**: dùng MediaPipe Hands (Google) chạy
  ngay trong trình duyệt để lấy 21 điểm mốc bàn tay, dùng để (a) kiểm tra tay
  có nằm trong khung không, (b) vẽ hiệu ứng "quét đường chỉ tay" theo đúng vị
  trí tay thật trên video.
- **1 API gọi cả 4 model**: thay vì gọi 4 lần riêng lẻ, `/api/predict` chạy cả
  4 model trong 1 request — giảm số lần round-trip, đồng bộ trạng thái loading.
- **Chịu lỗi từng phần**: nếu 1 trong 4 model lỗi khi suy luận, 3 model còn
  lại vẫn trả kết quả bình thường (xem `errors` trong response JSON).


Để chạy được các dòng code trên sẽ phải tạo một file mô hình và đẩy các model đã được train sẵn trong link drive này lên:
https://drive.google.com/drive/folders/1TKL0IH8akyPVKfAaVb3XLAoRkHOeLRvB?usp=sharing
