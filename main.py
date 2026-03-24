import requests
import os
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 🔐 설정 (GitHub Secrets)
token = os.environ.get('TELEGRAM_TOKEN', '').strip()
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '').strip()

# 📖 초등 6학년 맞춤: 성경 원문 & 아빠의 메시지 (30일치)
KIDS_BIBLE_MESSAGES = [
    ("네 마음을 다하고 목숨을 다하고 뜻을 다하여 주 너의 하나님을 사랑하라 (마 22:37)", "공부보다 더 중요한 건 네 마음 중심에 하나님을 두는 거란다."),
    ("네 이웃을 네 자신 같이 사랑하라 (마 22:39)", "오늘 학교에서 친구 입장을 먼저 생각해보는 멋진 하루 보내렴."),
    ("우리는 그가 만드신 바라 그리스도 예수 안에서 선한 일을 위하여 지으심을 받은 자니 (엡 2:10)", "너는 하나님의 특별한 작품이야. 존재만으로도 아빠는 충분히 기뻐."),
    ("내가 네게 명령한 것이 아니냐 강하고 담대하라 두려워하지 말며 놀라지 말라 (수 1:9)", "도전이 두려울 때도 있겠지만, 아빠와 하나님이 늘 뒤에 있단다."),
    ("너희 염려를 다 주께 맡기라 이는 그가 너희를 돌보심이라 (벧전 5:7)", "고민이 있다면 혼자 앓지 말고 아빠나 하나님께 꼭 말해주렴."),
    ("지혜로운 자와 동행하면 지혜를 얻고 미련한 자와 사귀면 해를 받느니라 (잠 13:20)", "좋은 친구는 서로를 성장시킨단다. 오늘 좋은 에너지를 나누렴."),
    ("사람마다 듣기는 속히 하고 말하기는 더디 하며 성내기도 더디 하라 (약 1:19)", "다툼이 생길 것 같을 땐, 딱 3초만 먼저 들어주는 지혜를 발휘해봐."),
    ("우리가 선을 행하되 낙심하지 말지니 포기하지 아니하면 때가 이르매 거두리라 (갈 6:9)", "결과가 당장 안 보여도 실망 마. 너의 노력은 절대 배신하지 않아."),
    ("사람은 외모를 보거니와 나 여호와는 중심을 보느니라 (삼상 16:7)", "남들의 시선보다, 네가 가진 따뜻한 마음이 훨씬 더 소중하단다."),
    ("무슨 일을 하든지 마음을 다하여 주께 하듯 하고 (골 3:23)", "오늘 네가 맡은 작은 일들에 정성을 다하는 모습, 기대할게!"),
    ("항상 기뻐하라 쉬지 말고 기도하라 범사에 감사하라 (살전 5:16-18)", "오늘 감사한 일 3가지만 떠올려보는 행복한 저녁 되길 바란다."),
    ("인내를 온전히 이루라 이는 너희로 온전하고 부족함이 없게 하려 함이라 (약 1:4)", "조금 힘들어도 견디는 시간이 널 더 단단한 어른으로 만들 거야."),
    ("서로 친절하게 하며 불쌍히 여기며 서로 용서하기를 (엡 4:32)", "친구의 실수에 '그럴 수 있지'라고 말하는 넓은 마음을 가져보자."),
    ("너의 행사를 여호와께 맡기라 그리하면 네가 경영하는 것이 이루어지리라 (잠 16:3)", "네가 꿈꾸는 미래들, 아빠가 늘 응원하고 기도하고 있어."),
    ("진실하게 행하는 자는 그의 기뻐하심을 받느니라 (잠 12:22)", "잘못했을 때 솔직하게 말하는 용기가 진짜 멋진 사람의 모습이야."),
    ("오직 겸손한 마음으로 각각 자기보다 남을 낫게 여기고 (빌 2:3)", "겸손은 상대를 존중하는 거야. 오늘 친구의 장점을 찾아봐줄래?"),
    ("너희에게 미래와 희망을 주는 것이니라 (렘 29:11)", "네 미래는 아주 밝단다. 하나님이 주실 희망을 믿고 나아가렴."),
    ("내게 능력 주시는 자 안에서 내가 모든 것을 할 수 있느니라 (빌 4:13)", "어렵게 느껴지는 일도 '난 할 수 있어'라고 믿으면 길이 보인단다."),
    ("무엇이든지 남에게 대접을 받고자 하는 대로 너희도 남을 대접하라 (마 7:12)", "친구가 다가오길 기다리기보다 네가 먼저 환하게 인사해보렴."),
    ("보라 내가 너를 내 손바닥에 새겼고 (사 49:16)", "너는 잊혀질 수 없는 존재야. 아빠 마음에도 늘 네가 있단다."),
    ("유순한 대답은 분노를 쉬게 하여도 과격한 말은 노를 격동하느니라 (잠 15:1)", "화가 날 때일수록 예쁜 말을 고르는 게 진짜 실력이란다."),
    ("너희가 전에는 어둠이더니 이제는 주 안에서 빛이라 (엡 5:8)", "친구들이 너만 보면 기분이 좋아지는 환한 빛 같은 아이가 되렴."),
    ("이같이 너희 빛이 사람 앞에 비치게 하여 그들의 착한 행실을 보고 (마 5:16)", "네 작은 친절 하나가 누군가에겐 큰 위로가 된다는 걸 잊지 마."),
    ("여호와를 찾는 자는 모든 좋은 것에 부족함이 없으리로다 (시 34:10)", "아빠는 네가 물질보다 마음이 풍요로운 사람으로 자라길 바란다."),
    ("거만한 마음은 넘어짐의 앞잡이니라 (잠 16:18)", "잘될 때일수록 감사할 줄 아는 겸손함을 잃지 않는 아들/딸 되자."),
    ("하나님이 주신 것은 두려워하는 마음이 아니요 오직 능력과 사랑이라 (딤후 1:7)", "불안할 땐 깊게 숨을 쉬어봐. 넌 충분히 해낼 힘이 있단다."),
    ("내가 주께 감사하옴은 나를 지으심이 심히 기묘하심이라 (시 139:14)", "세상에 단 하나뿐인 특별한 너, 아빠는 너를 정말 사랑해."),
    ("사랑은 오래 참고 사랑은 온유하며 시기하지 아니하며 (고전 13:4)", "오늘 조금 미운 친구가 있어도 한 번 더 참아주는 사랑을 해볼까?"),
    ("너는 마음을 다하여 여호와를 신뢰하고 네 명철을 의지하지 말라 (잠 3:5)", "네 생각보다 하나님의 지혜를 먼저 구하는 습관을 가져보렴."),
    ("너의 창조주를 기억하라 (전 12:1)", "인생에서 가장 아름다운 지금 이 시기를 하나님과 함께 즐겁게 보내렴.")
]

def create_card(bible_text, daddy_text):
    try:
        # 배경 이미지 (밝고 따뜻한 자연 느낌)
        bg_url = "https://images.unsplash.com/photo-1490750967868-88aa4486c946?q=80&w=800&auto=format&fit=crop"
        res = requests.get(bg_url, timeout=15)
        img = Image.open(BytesIO(res.content))
        
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 160))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # 폰트 파일이 없으면 기본 폰트 사용 (한글 깨짐 주의)
        font_path = "font.ttf"
        if os.path.exists(font_path):
            font_bible = ImageFont.truetype(font_path, 35)
            font_daddy = ImageFont.truetype(font_path, 28)
        else:
            print("폰트 파일이 없어 기본 폰트를 사용합니다. 한글이 깨질 수 있습니다.")
            font_bible = ImageFont.load_default()
            font_daddy = ImageFont.load_default()
        
        w, h = img.size
        
        # 성경 구절 그리기
        lines_bible = textwrap.wrap(bible_text, width=22)
        current_h = h / 2 - 100
        for line in lines_bible:
            bbox = draw.textbbox((0, 0), line, font=font_bible)
            line_w = bbox[2] - bbox[0]
            draw.text(((w - line_w) / 2, current_h), line, font=font_bible, fill="#2c3e50")
            current_h += 50
            
        # 아빠의 한마디 그리기
        current_h += 40
        lines_daddy = textwrap.wrap(daddy_text, width=25)
        for line in lines_daddy:
            bbox = draw.textbbox((0, 0), line, font=font_daddy)
            line_w = bbox[2] - bbox[0]
            draw.text(((w - line_w) / 2, current_h), line, font=font_daddy, fill="#e67e22")
            current_h += 40

        img.save("result.jpg")
        return "result.jpg"
    except Exception as e:
        print(f"이미지 생성 실패: {e}")
        return None

def send_telegram(photo_path, caption):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        payload = {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
        requests.post(url, data=payload, files={"photo": photo})

if __name__ == "__main__":
    bible, daddy = random.choice(KIDS_BIBLE_MESSAGES)
    card_path = create_card(bible, daddy)
    
    if card_path:
        send_telegram(card_path, "👨‍💼 <b>아빠가 보내는 오늘의 말씀 카드</b>")
    else:
        # 이미지 실패 시 텍스트만 전송
        text_msg = f"📖 <b>오늘의 말씀</b>\n{bible}\n\n💬 <b>아빠의 마음</b>\n{daddy}"
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": text_msg, "parse_mode": "HTML"})
