# -*- coding: utf-8 -*-
"""
advice_engine.py
-----------------
Module "tu van" (consultation): bien doi diem so (%) tu 4 model AI thanh
noi dung doc duoc bang tieng Viet, gom 3 phan cho moi duong chi tay:
    - luan_giai     : doan van luan giai chinh
    - diem_noi_bat   : 2-3 diem manh / dac diem noi bat
    - loi_khuyen     : loi khuyen thuc te, mang tinh tich cuc

Thiet ke tach rieng khoi app.py de:
    1. De doc, de cham diem (giao vien co the xem rieng phan "tri thuc" nay)
    2. De mo rong / sua noi dung ma khong dung vao logic Flask
    3. De tai su dung neu sau nay doi sang FastAPI / script khac

QUAN TRONG: Day la noi dung mang tinh chiem nghiem dan gian / giai tri,
khong phai ket luan y khoa, tam ly hay tai chinh chinh xac. Co disclaimer
rieng o cuoi file (DISCLAIMER) de hien thi tren UI.
"""

import random

# ----------------------------------------------------------------------------
# CO SO DU LIEU NOI DUNG
# Moi duong chi tay co 4 "tier" theo khoang diem (min <= score < max)
# ----------------------------------------------------------------------------

ADVICE_DB = {
    "sinh_dao": {
        "ten_duong": "Đường Sinh Đạo",
        "ten_model": "Sinh_Dao_model",
        "chu_de": "Sức khỏe & Tuổi thọ",
        "icon": "leaf",
        "tiers": [
            {
                "min": 0, "max": 35, "nhan": "Cần bồi dưỡng",
                "luan_giai": [
                    "Đường Sinh Đạo hiện khá mảnh và đứt đoạn ở vài điểm, cho thấy nguồn năng lượng nền của bạn đang bị phân tán nhiều hơn là được nạp lại. Đây là dấu hiệu cơ thể đang \"nhắc nhở\" bạn chậm lại, chứ không phải điều gì đáng lo ngại.",
                    "Giai đoạn này bạn dễ bị cuốn vào nhịp sống gấp, ngủ không đủ hoặc ăn uống thất thường, khiến thể lực phục hồi chậm hơn bình thường.",
                ],
                "diem_noi_bat": [
                    "Khả năng nhận biết sớm khi cơ thể quá tải — bạn thường \"biết\" trước khi kiệt sức thật sự.",
                    "Sức bền tinh thần tốt, có thể gồng gánh ổn dù thể lực đang yếu.",
                ],
                "loi_khuyen": "Hãy ưu tiên giấc ngủ và một bữa ăn đều đặn trong 2 tuần tới trước khi nghĩ đến việc tập luyện nặng. Một thói quen nhỏ duy trì đều còn quý hơn một kế hoạch lớn bỏ giữa đường.",
            },
            {
                "min": 35, "max": 60, "nhan": "Ổn định",
                "luan_giai": [
                    "Đường Sinh Đạo có độ sâu vừa phải và khá liền mạch, phản ánh một nền thể lực ổn định — không bứt phá nhưng cũng không có dấu hiệu cảnh báo rõ rệt.",
                    "Bạn đang ở trạng thái \"đủ dùng\": đáp ứng được nhịp sống hiện tại, nhưng chưa có nhiều dư địa cho những giai đoạn áp lực kéo dài.",
                ],
                "diem_noi_bat": [
                    "Nhịp sinh hoạt khá đều, ít rơi vào trạng thái cực đoan (kiệt sức hoặc lười vận động hẳn).",
                    "Khả năng hồi phục sau mệt mỏi ở mức tốt, chỉ cần thời gian nghỉ hợp lý.",
                ],
                "loi_khuyen": "Đây là thời điểm tốt để xây thêm \"đệm năng lượng\" — thêm 15-20 phút vận động mỗi ngày hoặc một mốc khám sức khỏe định kỳ, để biến sự ổn định hiện tại thành nền tảng lâu dài.",
            },
            {
                "min": 60, "max": 80, "nhan": "Khá dồi dào",
                "luan_giai": [
                    "Đường Sinh Đạo rõ, sâu và kéo dài đẹp — đặc trưng của một thể lực và sức bền đang ở giai đoạn thuận lợi.",
                    "Bạn có khả năng phục hồi nhanh sau những giai đoạn bận rộn, cơ thể đáp ứng tốt với thay đổi nhịp sống.",
                ],
                "diem_noi_bat": [
                    "Sức đề kháng và khả năng thích nghi với áp lực bên ngoài (thời tiết, lịch trình dày) tốt hơn mức trung bình.",
                    "Năng lượng duy trì ổn định suốt cả ngày, ít bị \"sụt pin\" giữa buổi.",
                ],
                "loi_khuyen": "Tận dụng giai đoạn sung sức này để xây những thói quen bền vững (tập luyện, dinh dưỡng) — nền tảng tốt hôm nay là vốn để dùng cho những giai đoạn áp lực sau này.",
            },
            {
                "min": 80, "max": 101, "nhan": "Xuất sắc",
                "luan_giai": [
                    "Đường Sinh Đạo dài, sâu và gần như không đứt đoạn — hình ảnh thường gắn với một thể trạng dồi dào năng lượng và khả năng chống chịu tốt trước biến động.",
                    "Đây là một trong những chỉ số tích cực nhất trong 4 đường, cho thấy bạn đang ở trạng thái sinh lực rất tốt.",
                ],
                "diem_noi_bat": [
                    "Khả năng hồi phục nhanh gần như vượt trội, ít bị ảnh hưởng bởi những cú \"sốc\" ngắn hạn (thiếu ngủ, đổi múi giờ...).",
                    "Tinh thần và thể chất hỗ trợ lẫn nhau tốt, tạo cảm giác tràn đầy năng lượng kéo dài.",
                ],
                "loi_khuyen": "Năng lượng dồi dào dễ khiến bạn quên giới hạn của cơ thể. Hãy chủ động đặt ra điểm dừng và nghỉ ngơi phòng ngừa, thay vì chỉ nghỉ khi đã thấy mệt.",
            },
        ],
    },
    "su_nghiep": {
        "ten_duong": "Đường Sự Nghiệp",
        "ten_model": "Su_Nghiep_model",
        "chu_de": "Thành công & Công danh",
        "icon": "path",
        "tiers": [
            {
                "min": 0, "max": 35, "nhan": "Đang tìm hướng",
                "luan_giai": [
                    "Đường Sự Nghiệp hiện còn mờ và chưa định hình rõ một hướng đi cố định — thường gặp ở giai đoạn bạn đang thử nghiệm, chuyển hướng hoặc chưa tìm thấy \"đúng việc, đúng người\".",
                    "Đây không phải dấu hiệu của sự thiếu năng lực, mà nhiều khả năng là bạn đang ở giữa một giai đoạn chuyển tiếp.",
                ],
                "diem_noi_bat": [
                    "Sự linh hoạt cao, không bị bó vào một con đường duy nhất — dễ thích nghi khi cơ hội mới xuất hiện.",
                    "Khả năng học hỏi nhanh từ những thử nghiệm chưa thành công.",
                ],
                "loi_khuyen": "Thay vì tìm một kế hoạch 5 năm hoàn hảo, hãy chọn một bước đi nhỏ, cụ thể trong 1-2 tháng tới để kiểm chứng hướng đi. Sự rõ ràng thường đến từ hành động, không phải từ suy nghĩ thêm.",
            },
            {
                "min": 35, "max": 60, "nhan": "Tiến triển đều",
                "luan_giai": [
                    "Đường Sự Nghiệp khá thẳng và liền mạch, phản ánh một quá trình tích lũy đều đặn — không có cú nhảy vọt lớn nhưng cũng không có bước lùi đáng kể.",
                    "Bạn đang xây dựng nền tảng theo cách bền vững hơn là nóng vội.",
                ],
                "diem_noi_bat": [
                    "Tính kiên trì và khả năng duy trì cam kết dài hạn với công việc.",
                    "Được đánh giá là người đáng tin cậy trong mắt đồng nghiệp/cấp trên.",
                ],
                "loi_khuyen": "Đây là thời điểm hợp lý để chủ động đề xuất một dự án hoặc trách nhiệm mới — sự đều đặn của bạn là lợi thế để được tin tưởng giao thêm cơ hội.",
            },
            {
                "min": 60, "max": 80, "nhan": "Nhiều cơ hội",
                "luan_giai": [
                    "Đường Sự Nghiệp rõ nét, có nhánh phụ hướng lên — dấu hiệu truyền thống cho giai đoạn nhiều cơ hội mở ra, đặc biệt là các cơ hội đến từ mối quan hệ hoặc sự công nhận từ người khác.",
                    "Bạn đang ở vị trí thuận lợi để bứt phá nếu chọn đúng thời điểm hành động.",
                ],
                "diem_noi_bat": [
                    "Khả năng nắm bắt thời cơ tốt, phản xạ nhanh với thay đổi của môi trường làm việc.",
                    "Tạo được thiện cảm và sự tín nhiệm với người xung quanh — một lợi thế ngầm trong sự nghiệp.",
                ],
                "loi_khuyen": "Đừng để cơ hội tốt trôi qua vì chờ \"chắc chắn 100%\". Hãy chủ động lên tiếng, kết nối và xin phản hồi — giai đoạn này thuận cho người dám đề xuất.",
            },
            {
                "min": 80, "max": 101, "nhan": "Bứt phá",
                "luan_giai": [
                    "Đường Sự Nghiệp dài, sâu và vươn thẳng lên gần gốc các ngón tay — hình ảnh thường gắn với giai đoạn thành quả rõ rệt, được công nhận xứng đáng với nỗ lực đã bỏ ra.",
                    "Đây là chỉ số tích cực, cho thấy những gì bạn xây dựng trong thời gian qua đang đến giai đoạn \"trổ quả\".",
                ],
                "diem_noi_bat": [
                    "Năng lực lãnh đạo hoặc khả năng tạo ảnh hưởng đang ở mức cao.",
                    "Khả năng biến áp lực thành động lực, thay vì để áp lực làm chậm bước tiến.",
                ],
                "loi_khuyen": "Khi mọi thứ thuận lợi, dễ quên dành thời gian ghi nhận chính mình. Hãy chủ động chia sẻ thành quả với những người đã hỗ trợ bạn — thành công bền vững thường đi cùng với mạng lưới quan hệ tốt.",
            },
        ],
    },
    "tam_dao": {
        "ten_duong": "Đường Tâm Đạo",
        "ten_model": "Tam_Dao_model",
        "chu_de": "Tình duyên & Cảm xúc",
        "icon": "heart",
        "tiers": [
            {
                "min": 0, "max": 35, "nhan": "Cần lắng nghe bản thân",
                "luan_giai": [
                    "Đường Tâm Đạo hiện hơi đứt đoạn, cho thấy đời sống cảm xúc gần đây có những khoảng lặng hoặc xáo trộn nhỏ — có thể bạn đang giữ cảm xúc cho riêng mình nhiều hơn là chia sẻ.",
                    "Đây thường là giai đoạn cần thời gian quay về bên trong trước khi mở lòng với người khác.",
                ],
                "diem_noi_bat": [
                    "Khả năng tự nhận biết cảm xúc của chính mình khá tốt, dù chưa hẳn đã chia sẻ ra ngoài.",
                    "Có ranh giới cá nhân rõ ràng, không dễ bị cuốn theo cảm xúc của người khác.",
                ],
                "loi_khuyen": "Hãy cho phép mình một khoảng thời gian \"không cần giải thích\" với ai cả. Khi cảm xúc đã ổn định trở lại, việc kết nối với người khác sẽ tự nhiên hơn là cố gắng ép buộc.",
            },
            {
                "min": 35, "max": 60, "nhan": "Hài hòa",
                "luan_giai": [
                    "Đường Tâm Đạo có độ cong vừa phải và khá liền mạch — phản ánh một trạng thái cảm xúc tương đối hài hòa, biết cân bằng giữa cho và nhận trong các mối quan hệ.",
                    "Bạn không quá nồng nhiệt cũng không quá khép kín, mà giữ một nhịp ổn định, dễ duy trì lâu dài.",
                ],
                "diem_noi_bat": [
                    "Khả năng lắng nghe tốt, tạo cảm giác an toàn cho người đối diện khi chia sẻ.",
                    "Ít để cảm xúc chi phối các quyết định quan trọng.",
                ],
                "loi_khuyen": "Sự hài hòa hiện tại là nền tốt để chủ động hơn một chút — thử chia sẻ một điều bạn vẫn giữ trong lòng với người mình tin tưởng, thay vì chỉ chờ người khác mở lời trước.",
            },
            {
                "min": 60, "max": 80, "nhan": "Nồng nhiệt",
                "luan_giai": [
                    "Đường Tâm Đạo rõ và cong đẹp hướng lên, dấu hiệu truyền thống của một người sống tình cảm, chân thành và dễ tạo kết nối sâu với người khác.",
                    "Đời sống cảm xúc giai đoạn này khá sôi động, có thể có những thay đổi tích cực trong mối quan hệ gần đây.",
                ],
                "diem_noi_bat": [
                    "Khả năng đồng cảm cao, dễ nhận ra cảm xúc thật của người xung quanh.",
                    "Sức hút tự nhiên trong giao tiếp — người khác thường cảm thấy thoải mái khi ở gần bạn.",
                ],
                "loi_khuyen": "Cảm xúc nồng nhiệt là lợi thế, nhưng hãy giữ một phần lý trí khi đưa ra quyết định lớn liên quan đến mối quan hệ. Cho mối quan hệ đủ thời gian để chứng minh, đừng chỉ dựa vào cảm giác ban đầu.",
            },
            {
                "min": 80, "max": 101, "nhan": "Sâu sắc",
                "luan_giai": [
                    "Đường Tâm Đạo dài, sâu và rõ nét hiếm thấy — thường gắn với những người có đời sống nội tâm phong phú và khả năng yêu thương sâu sắc, bền lâu.",
                    "Đây là giai đoạn cảm xúc của bạn có chiều sâu rõ rệt, không hời hợt hay nhất thời.",
                ],
                "diem_noi_bat": [
                    "Lòng trung thành và sự kiên định trong tình cảm ở mức cao.",
                    "Khả năng tạo ra những mối quan hệ ý nghĩa, không chỉ dừng ở mức bề mặt.",
                ],
                "loi_khuyen": "Tình cảm sâu sắc đôi khi khiến bạn kỳ vọng nhiều ở người khác. Hãy nói rõ điều bạn mong đợi, thay vì để đối phương tự đoán — sự chân thành cần đi cùng sự rõ ràng.",
            },
        ],
    },
    "tri_dao": {
        "ten_duong": "Đường Trí Đạo",
        "ten_model": "Tri_Dao_model",
        "chu_de": "Trí tuệ & Tư duy",
        "icon": "eye",
        "tiers": [
            {
                "min": 0, "max": 35, "nhan": "Cần thời gian tập trung",
                "luan_giai": [
                    "Đường Trí Đạo hiện khá ngắn và có vài điểm gãy nhỏ, cho thấy tâm trí gần đây dễ bị phân tán bởi nhiều luồng thông tin hoặc việc cùng lúc.",
                    "Đây là dấu hiệu cho thấy bạn cần một không gian yên tĩnh hơn để tư duy sâu, chứ không phải là hạn chế về năng lực.",
                ],
                "diem_noi_bat": [
                    "Khả năng xử lý đa nhiệm (multitask) khá linh hoạt trong thời gian ngắn.",
                    "Tư duy cởi mở, dễ tiếp nhận góc nhìn mới.",
                ],
                "loi_khuyen": "Hãy thử chặn riêng 30-45 phút mỗi ngày không thông báo, không gián đoạn, chỉ để tập trung vào một việc. Trí tuệ sắc bén thường cần không gian tĩnh để bộc lộ, không phải cần thêm thông tin.",
            },
            {
                "min": 35, "max": 60, "nhan": "Tư duy ổn định",
                "luan_giai": [
                    "Đường Trí Đạo thẳng và rõ vừa phải, phản ánh một tư duy thực tế, có hệ thống — bạn ra quyết định dựa trên cân nhắc hợp lý hơn là cảm tính.",
                    "Đây là một nền tư duy chắc chắn, phù hợp để xử lý các vấn đề đòi hỏi sự kiên nhẫn.",
                ],
                "diem_noi_bat": [
                    "Khả năng phân tích vấn đề theo từng bước rõ ràng, ít bị cuốn theo cảm xúc nhất thời.",
                    "Tư duy logic tốt, đặc biệt với các vấn đề có cấu trúc rõ ràng.",
                ],
                "loi_khuyen": "Nền tư duy ổn định là lợi thế lớn — hãy thử áp dụng nó vào một vấn đề bạn vẫn đang trì hoãn vì \"chưa đủ thông tin\". Đôi khi bạn đã có đủ dữ liệu để quyết định rồi.",
            },
            {
                "min": 60, "max": 80, "nhan": "Sắc bén",
                "luan_giai": [
                    "Đường Trí Đạo dài và rõ, hơi nghiêng xuống nhẹ — dấu hiệu truyền thống của một tư duy sắc bén, kết hợp tốt giữa lý trí và sự nhạy cảm trực giác.",
                    "Bạn có khả năng nhìn ra vấn đề nhanh hơn người khác, đặc biệt trong các tình huống cần phản ứng linh hoạt.",
                ],
                "diem_noi_bat": [
                    "Tư duy phản biện tốt, không dễ bị thuyết phục bởi lập luận hời hợt.",
                    "Khả năng kết nối những ý tưởng tưởng như không liên quan để tìm ra giải pháp mới.",
                ],
                "loi_khuyen": "Trí tuệ sắc bén dễ khiến bạn thấy mọi việc \"đơn giản với mình nhưng khó với người khác\" — hãy kiên nhẫn hơn khi giải thích, sự sắc bén sẽ phát huy tốt nhất khi truyền đạt được cho người khác hiểu.",
            },
            {
                "min": 80, "max": 101, "nhan": "Vượt trội",
                "luan_giai": [
                    "Đường Trí Đạo dài, sâu và rõ nét bất thường — thường gắn với khả năng tư duy vượt trội, sự sáng tạo cao và năng lực tiếp thu nhanh những lĩnh vực mới.",
                    "Đây là một trong những chỉ số ấn tượng nhất, cho thấy tiềm năng trí tuệ của bạn đang ở giai đoạn rất tốt để khai phá.",
                ],
                "diem_noi_bat": [
                    "Khả năng học hỏi liên ngành (kết hợp kiến thức từ nhiều lĩnh vực) tốt hơn mức trung bình.",
                    "Tư duy chiến lược, nhìn được bức tranh tổng thể trước khi đi vào chi tiết.",
                ],
                "loi_khuyen": "Tiềm năng lớn dễ bị lãng phí nếu dàn trải vào quá nhiều thứ. Hãy chọn 1-2 lĩnh vực để đầu tư sâu trong giai đoạn này — chiều sâu sẽ tạo ra giá trị lớn hơn chiều rộng vào lúc này.",
            },
        ],
    },
}

DISCLAIMER = (
    "Kết quả được tạo bởi mô hình AI dựa trên đặc điểm hình ảnh bàn tay, mang tính "
    "chiêm nghiệm - giải trí theo thuật xem chỉ tay dân gian, KHÔNG phải kết luận y khoa, "
    "tâm lý hay tài chính chính xác. Vui lòng không dùng kết quả này để thay thế cho lời "
    "khuyên của chuyên gia trong các lĩnh vực liên quan."
)


def _pick_tier(line_key: str, score: float) -> dict:
    """Tra ve tier (khoang diem) phu hop voi score cho 1 duong chi tay."""
    tiers = ADVICE_DB[line_key]["tiers"]
    for tier in tiers:
        if tier["min"] <= score < tier["max"]:
            return tier
    # fallback an toan (vd score dung 100 hoac le do float)
    return tiers[-1] if score >= 50 else tiers[0]


def get_consultation(line_key: str, score: float) -> dict:
    """
    Sinh noi dung tu van day du cho 1 duong chi tay.

    Args:
        line_key: 1 trong "sinh_dao" | "su_nghiep" | "tam_dao" | "tri_dao"
        score: diem so 0-100 (da duoc chuan hoa tu output cua model)

    Returns:
        dict gom: ten_duong, chu_de, icon, score, nhan, luan_giai,
                  diem_noi_bat, loi_khuyen
    """
    if line_key not in ADVICE_DB:
        raise ValueError(f"Khong nhan dien duoc duong chi tay: {line_key}")

    info = ADVICE_DB[line_key]
    tier = _pick_tier(line_key, score)

    return {
        "key": line_key,
        "ten_duong": info["ten_duong"],
        "ten_model": info["ten_model"],
        "chu_de": info["chu_de"],
        "icon": info["icon"],
        "score": round(score, 1),
        "nhan": tier["nhan"],
        "luan_giai": " ".join(tier["luan_giai"]),
        "diem_noi_bat": tier["diem_noi_bat"],
        "loi_khuyen": tier["loi_khuyen"],
    }


def get_all_consultations(scores: dict) -> dict:
    """
    scores: dict {"sinh_dao": 72.3, "su_nghiep": 41.0, "tam_dao": 88.5, "tri_dao": 60.2}
    Tra ve dict cung key, gia tri la noi dung tu van day du cho tung duong.
    """
    return {key: get_consultation(key, score) for key, score in scores.items()}


if __name__ == "__main__":
    # Demo nhanh khi chay truc tiep file nay (python advice_engine.py)
    demo_scores = {
        "sinh_dao": random.uniform(0, 100),
        "su_nghiep": random.uniform(0, 100),
        "tam_dao": random.uniform(0, 100),
        "tri_dao": random.uniform(0, 100),
    }
    import json
    print(json.dumps(get_all_consultations(demo_scores), ensure_ascii=False, indent=2))
    print("\nDISCLAIMER:", DISCLAIMER)
