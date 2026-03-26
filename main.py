import requests
import os
import textwrap
import random # 🌟 무작위 사진 선택을 위해 필수!
import subprocess # 🌟 메모장(progress.txt)을 깃허브에 강제로 저장하기 위해 추가
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 🔐 설정 (GitHub Secrets)
token = os.environ.get('TELEGRAM_TOKEN', '').strip()
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '').strip()

# 📖 메시지 리스트 (유저님의 50개 리스트 그대로 사용하시면 됩니다)
KIDS_BIBLE_MESSAGES = [
    ("네 마음을 다하고 목숨을 다하고 뜻을 다하여 주 너의 하나님을 사랑하라 (마 22:37)", "공부보다 더 중요한 건 네 마음 중심에 하나님을 두는 거란다."),
    ("네 이웃을 네 자신 같이 사랑하라 (마 22:39)", "오늘 학교에서 친구 입장을 먼저 생각해보는 멋진 하루 보내렴."),
    # ... (이하 유저님의 50개 리스트 생략하지 말고 그대로 두세요) ...
    ("여호와께서 너를 지켜 모든 환난을 면하게 하시며 (시 121:7)", "오늘 하루도 안전하고 행복하게! 아빠가 많이 사랑한다.")
]

def get_next_index():
    filename = "progress.txt"
    if not os.path.exists(filename): return 0
    try:
        with open(filename, "r") as f: return int(f.read().strip())
    except: return 0

def save_next_index(index):
    # 1. 파일에 숫자 기록
    with open("progress.txt", "w") as f:
        f.write(str(index))
    
    # 2. 🌟 깃허브 서버에 이 파일을 '강제로' 박제 (수정된 부분)
    try:
        subprocess.run(["git", "config", "user.name", "GitHub Actions"])
        subprocess.run(["git", "config", "user.email", "actions@github.com"])
        subprocess.run(["git", "add", "progress.txt"])
        subprocess.run(["git", "commit", "-m", f"Update progress to {index}"])
        # 여기서 'origin main'을 명시해서 확실히 보냅니다.
        subprocess.run(["git", "push", "origin", "main"]) 
    except Exception as e:
        print(f"메모장 업데이트 실패: {e}")

def create_card(bible, daddy):
    try:
        # 🌟 매일 바뀌는 랜덤 배경 사진 리스트 (자연 풍경)
        backgrounds = [
            "https://images.unsplash.com/photo-1490750967868-88aa4486c946?q=80&w=800&auto=format&fit=crop", # 꽃
            "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?q=80&w=800&auto=format&fit=crop", # 들판
            "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=800&auto=format&fit=crop", # 산
            "https://images.unsplash.com/photo-1501854140801-50d01698950b?q=80&w=800&auto=format&fit=crop", # 숲
            "https://images.unsplash.com/photo-1506744626753-1fa28f673fac?q=80&w=800&auto=format&fit=crop", # 호수
            "https://images.unsplash.com/photo-1470071131384-001b85755536?q=80&w=800&auto=format&fit=crop", # 아침안개
            "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=800&auto=format&fit=crop"  # 햇살
        ]
        bg_url = random.choice(backgrounds) # 여기서 랜덤 선택!
        
        res = requests.get(bg_url, timeout=10)
        img = Image.open(BytesIO(res.content))
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 190))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        font_path = "font.ttf"
        if os.path.exists(font_path):
            f_title = ImageFont.truetype(font_path, 26)
            f_b = ImageFont.truetype(font_path, 34)
            f_d = ImageFont.truetype(font_path, 28)
            w, h = img.size
            
            lines_bible = textwrap.wrap(bible, width=22)
            lines_daddy = textwrap.wrap(daddy, width=25)
            
            total_height = 40 + (len(lines_bible) * 45) + 30 + 40 + (len(lines_daddy) * 40)
            y = (h - total_height) / 2
            
            draw.text(((w-draw.textbbox((0,0), "📖 오늘의 말씀", font=f_title)[2])/2, y), "📖 오늘의 말씀", font=f_title, fill="#2c3e50")
            y += 40
            for l in lines_bible:
                draw.text(((w-draw.textbbox((0,0), l, font=f_b)[2])/2, y), l, font=f_b, fill="#2c3e50")
                y += 45
            y += 30
            draw.text(((w-draw.textbbox((0,0), "💬 아빠의 마음", font=f_title)[2])/2, y), "💬 아빠의 마음", font=f_title, fill="#d35400")
            y += 40
            for l in lines_daddy:
                draw.text(((w-draw.textbbox((0,0), l, font=f_d)[2])/2, y), l, font=f_d, fill="#e67e22")
                y += 40
                
            img.save("result.jpg")
            return "result.jpg"
        return None
    except: return None

def send_msg(text, photo=None):
    if photo and os.path.exists(photo):
        requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", data={"chat_id": chat_id, "caption": text, "parse_mode": "HTML"}, files={"photo": open(photo, 'rb')})
    else:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    idx = get_next_index()
    total = len(KIDS_BIBLE_MESSAGES)
    
    if idx < total:
        b, d = KIDS_BIBLE_MESSAGES[idx]
        msg = f"☀️ <b>Day {idx+1}</b>\n\n📖 <b>오늘의 말씀</b>\n{b}\n\n💬 <b>아빠의 마음</b>\n{d}"
       # 현재 번호(idx+1)가 진짜 전체 개수(total)와 같을 때만 마지막 인사를 하도록 바꿉니다.
    if (idx + 1) == total:
       msg += "\n\n🎉 <b>[알림] 50일 마지막 메시지입니다. 다음 말씀을 준비해 주세요!</b>"
            
        card = create_card(b, d)
        send_msg(msg, card)
        
        # 🌟 다음 날을 위해 인덱스 저장 (메모장에 기록!)
        save_next_index(idx + 1)
    else:
        send_msg("📢 모든 메시지가 소진되었습니다!")
