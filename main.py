import requests
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 🔐 설정 (GitHub Secrets)
token = os.environ.get('TELEGRAM_TOKEN', '').strip()
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '').strip()

# 📖 30일치 메시지 리스트 (생략 없이 그대로 유지하세요)
KIDS_BIBLE_MESSAGES = [
    ("네 마음을 다하고 목숨을 다하고 뜻을 다하여 주 너의 하나님을 사랑하라 (마 22:37)", "공부보다 더 중요한 건 네 마음 중심에 하나님을 두는 거란다."),
    # ... (중간 메시지들) ...
    ("너의 창조주를 기억하라 (전 12:1)", "인생에서 가장 아름다운 지금 이 시기를 하나님과 함께 즐겁게 보내렴.")
]

# 📝 진행 상황을 저장하고 불러오는 함수
def get_next_index():
    filename = "progress.txt"
    if not os.path.exists(filename):
        return 0
    with open(filename, "r") as f:
        try:
            return int(f.read().strip())
        except:
            return 0

def save_next_index(index):
    with open("progress.txt", "w") as f:
        f.write(str(index))

def create_card(bible_text, daddy_text):
    try:
        bg_url = "https://images.unsplash.com/photo-1490750967868-88aa4486c946?q=80&w=800&auto=format&fit=crop"
        res = requests.get(bg_url, timeout=15)
        img = Image.open(BytesIO(res.content))
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 180))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        font_path = "font.ttf"
        if os.path.exists(font_path):
            font_bible = ImageFont.truetype(font_path, 35)
            font_daddy = ImageFont.truetype(font_path, 28)
            w, h = img.size
            # (중략) 이미지 그리기 로직 수행...
            img.save("result.jpg")
            return "result.jpg"
        return None
    except:
        return None

def send_telegram(text, photo_path=None):
    if photo_path and os.path.exists(photo_path):
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            requests.post(url, data={"chat_id": chat_id, "caption": text, "parse_mode": "HTML"}, files={"photo": photo})
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    current_index = get_next_index()
    total_count = len(KIDS_BIBLE_MESSAGES)
    
    if current_index < total_count:
        bible, daddy = KIDS_BIBLE_MESSAGES[current_index]
        
        # 텍스트 구성
        caption = f"📖 <b>오늘의 말씀 ({current_index + 1}/{total_count})</b>\n{bible}\n\n💬 <b>아빠의 마음</b>\n{daddy}"
        
        # 마지막 날이면 경고 문구 추가
        if current_index == total_count - 1:
            caption += "\n\n⚠️ <b>[알림] 30일 마지막 메시지입니다. 새로운 말씀을 준비해 주세요!</b>"
        
        # 카드 생성 및 전송
        card = create_card(bible, daddy)
        send_telegram(caption, card)
        
        # 다음 날을 위해 인덱스 저장
        save_next_index(current_index + 1)
    else:
        # 30일이 이미 지난 경우
        send_telegram("🚨 <b>알림: 모든 메시지가 소진되었습니다.</b>\n새로운 30일치 리스트를 업데이트해 주세요!")
