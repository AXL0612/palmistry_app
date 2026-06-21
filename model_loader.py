# -*- coding: utf-8 -*-
"""
model_loader.py
-----------------
Tien ich nap (load) va goi du doan (predict) cho 4 model Keras (.h5):
    Sinh_Dao_model.h5, Su_Nghiep_model.h5, Tam_Dao_model.h5, Tri_Dao_model.h5

Thiet ke "tu thich nghi" (adaptive) vi khong gia dinh truoc kien truoc model:
    - Tu doc input_shape cua moi model -> tu resize anh dau vao cho dung
      (vi du model A train o 128x128, model B train o 224x224 deu duoc).
    - Tu doc output_shape -> phan biet 2 dang pho bien:
        (a) Hoi quy / nhi phan (1 gia tri, vd Dense(1, activation='sigmoid'))
            -> diem so = gia tri do (quy ve thang 0-100%).
        (b) Phan loai nhieu lop (vd Dense(5, activation='softmax'))
            -> diem so = xac suat cua lop co xac suat cao nhat (quy ve %),
               kem chi so lop (tier_index) de doi chieu them neu can.

Nho vay, du 4 file .h5 cua ban duoc train voi kich thuoc anh / kieu output
khac nhau, code van chay dung ma khong can sua tay tung model.
"""

import logging
import os

import numpy as np
from PIL import Image

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")  # giam log rac cua TensorFlow

import tensorflow as tf  # noqa: E402  (import sau khi set env log level)

logger = logging.getLogger(__name__)

# Ten file model mong doi, dat trong thu muc backend/models/
MODEL_FILENAMES = {
    "sinh_dao": "Sinh_Dao_model.h5",
    "su_nghiep": "Su_Nghiep_model.h5",
    "tam_dao": "Tam_Dao_model.h5",
    "tri_dao": "Tri_Dao_model.h5",
}


class PalmLineModel:
    """Boc 1 model Keras + thong tin input/output da duoc "do" san."""

    def __init__(self, key: str, path: str):
        self.key = key
        self.path = path
        self.model = tf.keras.models.load_model(path, compile=False)

        in_shape = self.model.input_shape
        # input_shape co the la tuple (None, H, W, C) hoac list cac tuple
        # (truong hop model nhieu dau vao) -> o day gia dinh 1 dau vao anh.
        if isinstance(in_shape, list):
            in_shape = in_shape[0]
        self.target_h = in_shape[1] or 224
        self.target_w = in_shape[2] or 224
        self.channels = in_shape[3] if len(in_shape) > 3 and in_shape[3] else 3

        out_shape = self.model.output_shape
        if isinstance(out_shape, list):
            out_shape = out_shape[0]
        self.output_dim = out_shape[-1]

        logger.info(
            "[%s] Da nap model '%s' | input=%sx%sx%s | output_dim=%s",
            self.key, os.path.basename(path), self.target_h, self.target_w,
            self.channels, self.output_dim,
        )

    def preprocess(self, pil_image: Image.Image) -> np.ndarray:
        """Resize + chuan hoa anh PIL theo dung input_shape cua model nay."""
        mode = "RGB" if self.channels == 3 else "L"
        img = pil_image.convert(mode)
        img = img.resize((self.target_w, self.target_h))
        arr = np.asarray(img).astype("float32") / 255.0
        if self.channels == 1 and arr.ndim == 2:
            arr = np.expand_dims(arr, axis=-1)
        arr = np.expand_dims(arr, axis=0)  # them batch dimension
        return arr

    def predict_score(self, pil_image: Image.Image) -> dict:
        """
        Tra ve dict: {"score": float 0-100, "tier_index": int|None,
                      "raw_output": list}
        """
        x = self.preprocess(pil_image)
        raw = self.model.predict(x, verbose=0)
        raw = np.asarray(raw).flatten()

        tier_index = None
        if raw.size == 1:
            value = float(raw[0])
        else:
            tier_index = int(np.argmax(raw))
            value = float(np.max(raw))

        # Neu output da nam trong [0, 1] -> hieu la xac suat/ti le -> *100
        # Neu output > 1 (vi du model tu xuat truc tiep thang 0-100) -> giu nguyen
        score = value * 100 if 0.0 <= value <= 1.0001 else value
        score = max(0.0, min(100.0, score))

        return {
            "score": round(score, 1),
            "tier_index": tier_index,
            "raw_output": raw.tolist(),
        }


class PalmModelRegistry:
    """Nap va giu san trong RAM ca 4 model, dung 1 lan khi server khoi dong."""

    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        self.models: dict[str, PalmLineModel] = {}
        self._load_all()

    def _load_all(self):
        missing = []
        for key, filename in MODEL_FILENAMES.items():
            path = os.path.join(self.models_dir, filename)
            if not os.path.isfile(path):
                missing.append(filename)
                continue
            self.models[key] = PalmLineModel(key, path)

        if missing:
            logger.warning(
                "Chua tim thay %d model trong '%s': %s. "
                "Hay dat dung 4 file .h5 vao thu muc nay truoc khi chay that.",
                len(missing), self.models_dir, ", ".join(missing),
            )

    def is_ready(self) -> bool:
        return len(self.models) == len(MODEL_FILENAMES)

    def missing_models(self) -> list:
        return [k for k in MODEL_FILENAMES if k not in self.models]

    def predict_all(self, pil_image: Image.Image) -> dict:
        """Chay anh qua tat ca model da nap, tra ve dict {key: score_info}."""
        results = {}
        for key, plm in self.models.items():
            try:
                results[key] = plm.predict_score(pil_image)
            except Exception as exc:  # bao loi ro tung model, khong sap ca server
                logger.exception("Loi khi du doan voi model '%s'", key)
                results[key] = {"error": str(exc)}
        return results
