import requests
import os
import textwrap
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 🔐 설정 (GitHub Secrets)
token = os.environ.get('TELEGRAM_TOKEN', '').strip()
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '').strip()

# 📖 51일차~100일차 메시지 리스트 (말씀, 아빠의 마음)
KIDS_BIBLE_MESSAGES = [
    # --- [51일~60일] 평안과 위로 ---
    ("아무 것도 염려하지 말고 다만 모든 일에 기도와 간구로, 너희 구할 것을 감사함으로 하나님께 아뢰라 (빌 4:6-7)", "걱정이 생길 땐 아빠와 하나님께 먼저 이야기해 주렴. 평안이 찾아올 거야."),
    ("두려워하지 말라 내가 너와 함께 함이라 (사 41:10)", "새로운 도전을 앞두고 떨릴 때, 하나님이 네 손을 꽉 잡고 계신단다."),
    ("여호와는 나의 목자시니 내게 부족함이 없으리로다 (시 23:1)", "우리의 참된 목자이신 하나님이 네 길을 가장 좋은 곳으로 안내해 주실 거야."),
    ("수고하고 무거운 짐 진 자들아 다 내게로 오라 내가 너희를 쉬게 하리라 (마 11:28)", "학교 생활과 공부로 지칠 때, 언제든 아빠 품에서 푹 쉬어가렴."),
    ("평안을 너희에게 끼치노니 곧 나의 평안을 너희에게 주노라 (요 14:27)", "세상이 줄 수 없는 진짜 평안이 오늘 네 마음속에 가득하길 기도해."),
    ("하나님은 우리의 피난처시요 힘이시니 환난 중에 만날 큰 도우심이라 (시 46:1)", "힘들고 지칠 때 숨을 수 있는 가장 안전한 피난처가 하나님이란다."),
    ("우리가 알거니와 하나님을 사랑하는 자... 모든 것이 합력하여 선을 이루느니라 (롬 8:28)", "실수나 실패도 결국엔 널 더 멋지게 성장시키는 거름이 될 거야."),
    ("너희 염려를 다 주께 맡기라 이는 그가 너희를 돌보심이라 (벧전 5:7)", "무거운 걱정 배낭은 다 내려놓고 오늘은 가벼운 발걸음으로 하루를 보내자."),
    ("너는 마음을 다하여 여호와를 신뢰하고 네 명철을 의지하지 말라 (잠 3:5)", "네 똑똑한 머리보다 하나님의 지혜를 먼저 구하는 멋진 하루가 되길 바라."),
    ("주께서 심지가 견고한 자를 평강에 평강으로 지키시리니 (사 26:3)", "바람에 흔들리지 않는 깊은 뿌리처럼 단단한 마음을 가지렴."),

    # --- [61일~70일] 용기와 능력 ---
    ("강하고 담대하라 두려워하지 말며 놀라지 말라 (수 1:9)", "두려움을 이기는 가장 큰 무기는 하나님이 함께하신다는 믿음이야."),
    ("내게 능력 주시는 자 안에서 내가 모든 것을 할 수 있느니라 (빌 4:13)", "'난 할 수 있어!'라고 외쳐봐. 네 안엔 이미 엄청난 능력이 있단다."),
    ("하나님이 우리에게 주신 것은 두려워하는 마음이 아니요 오직 능력과 사랑과 절제하는 마음이니 (딤후 1:7)", "불안할 땐 심호흡을 크게 해봐. 넌 용기 내기에 충분한 사람이야."),
    ("나의 힘이신 여호와여 내가 주를 사랑하나이다 (시 18:1)", "기운이 없을 때, '나의 힘'이 되시는 하나님을 한 번 작게 불러보렴."),
    ("깨어 믿음에 굳게 서서 남자답게 강건하라 (고전 16:13)", "어떤 어려움 앞에서도 씩씩하게 어깨를 펴고 당당하게 걸어가자."),
    ("오직 여호와를 앙망하는 자는 새 힘을 얻으리니 독수리가 날개치며 올라감 같을 것이요 (사 40:31)", "쉬어가는 시간은 뒤처지는 게 아니라 독수리처럼 날아오를 준비를 하는 거란다."),
    ("여호와는 내 생명의 능력이시니 내가 누구를 무서워하리요 (시 27:1)", "빛이 되시는 하나님이 네 앞길을 환하게 비춰주시니 무서울 게 없지!"),
    ("그러나 이 모든 일에 우리를 사랑하시는 이로 말미암아 우리가 넉넉히 이기느니라 (롬 8:37)", "결국엔 네가 이기게 되어 있어. 아빠는 항상 네 승리를 응원해."),
    ("우리가 선을 행하되 낙심하지 말지니 포기하지 아니하면 때가 이르매 거두리라 (갈 6:9)", "좋은 일을 하다가 지치더라도 포기하지 마. 꼭 예쁜 열매를 맺을 거야."),
    ("여호와를 바라는 너희들아 강하고 담대하라 (시 31:24)", "주눅 들지 말고 네가 가진 멋진 모습들을 마음껏 펼쳐보렴."),

    # --- [71일~80일] 사랑과 화목 ---
    ("사랑은 오래 참고 사랑은 온유하며 시기하지 아니하며 (고전 13:4)", "오늘은 친구에게 평소보다 한 번 더 다정하게 양보해보는 건 어떨까?"),
    ("우리가 사랑함은 그가 먼저 우리를 사랑하셨음이라 (요일 4:19)", "네가 듬뿍 받은 그 사랑을 오늘 하루 주변에 조금씩 나눠주렴."),
    ("서로 친절하게 하며 불쌍히 여기며 서로 용서하기를 (엡 4:32)", "친절은 돌고 돌아 결국 너에게 더 큰 기쁨으로 돌아온단다."),
    ("무엇보다도 뜨겁게 서로 사랑할지니 사랑은 허다한 죄를 덮느니라 (벧전 4:8)", "누군가의 실수를 덮어주는 넓은 마음이 너를 진짜 멋진 사람으로 만들어."),
    ("서로 사랑하라 내가 너희를 사랑한 것 같이 너희도 서로 사랑하라 (요 13:34)", "오늘 네 짝꿍에게 따뜻한 눈웃음 한 번 먼저 지어주는 하루 되자."),
    ("이 모든 것 위에 사랑을 더하라 이는 온전하게 매는 띠니라 (골 3:14)", "네가 가진 재능 위에 사랑을 더하면 세상에서 제일 예쁜 보석이 될 거야."),
    ("자녀들아 우리가 말과 혀로만 사랑하지 말고 행함과 진실함으로 하자 (요일 3:18)", "마음속에 있는 고마움을 오늘은 꼭 작은 행동으로 표현해볼래?"),
    ("화평하게 하는 자는 복이 있나니 그들이 하나님의 아들이라 일컬음을 받을 것임이요 (마 5:9)", "싸움을 말리고 화해시키는 네 모습 속에서 하나님의 얼굴이 보인단다."),
    ("할 수 있거든 너희로서는 모든 사람과 더불어 화목하라 (롬 12:18)", "조금 다르더라도 서로 이해하고 함께 어울릴 줄 아는 네가 아빠는 자랑스러워."),
    ("마른 떡 한 조각만 있고도 화목하는 것이 제육이 집에 가득하고도 다투는 것보다 나으니라 (잠 17:1)", "가장 큰 행복은 비싼 물건이 아니라 우리 가족이 오순도순 웃는 거란다."),

    # --- [81일~90일] 감사와 기쁨 ---
    ("항상 기뻐하라 쉬지 말고 기도하라 범사에 감사하라 (살전 5:16-18)", "오늘 자기 전에 꼭 아빠한테 네가 감사했던 일 한 가지를 들려줘."),
    ("이 날은 여호와께서 정하신 것이라 이 날에 우리가 기뻐하고 즐거워하리로다 (시 118:24)", "오늘이라는 선물 상자 안에는 어떤 기쁨이 들어있을지 기대하며 열어보자."),
    ("기도를 계속하고 기도에 감사함으로 깨어 있으라 (골 4:2)", "무언가를 달라는 기도보다, 이미 주신 것에 감사하는 기도가 더 큰 능력이 돼."),
    ("감사함으로 그의 문에 들어가며 찬송함으로 그의 궁정에 들어가서 (시 100:4)", "학교 교문을 들어설 때 '오늘도 감사합니다'라고 속으로 외쳐볼까?"),
    ("주 안에서 항상 기뻐하라 내가 다시 말하노니 기뻐하라 (빌 4:4)", "짜증나는 일이 있어도 씩 한 번 웃어버리면 나쁜 마음이 도망간단다."),
    ("무엇을 하든지... 다 주 예수의 이름으로 하고 그를 힘입어 하나님 아버지께 감사하라 (골 3:17)", "작은 일 하나를 할 때도 감사한 마음으로 하면 결과가 훨씬 좋을 거야."),
    ("여호와께 감사하라 그는 선하시며 그 인자하심이 영원함이로다 (시 107:1)", "언제나 좋은 길로 이끌어주시는 하나님께 땡큐! 하고 윙크해보자."),
    ("난 여호와로 말미암아 즐거워하며 나의 구원의 하나님으로 말미암아 기뻐하리로다 (합 3:18)", "원하는 결과가 당장 나오지 않아도, 넌 이미 존재 자체로 아빠의 기쁨이야."),
    ("여호와께서 우리를 위하여 큰 일을 행하셨으니 우리는 기뻐하도다 (시 126:3)", "앞으로 네 인생에 펼쳐질 멋진 일들을 상상하며 오늘도 신나게 출발!"),
    ("범사에 우리 주 예수 그리스도의 이름으로 항상 아버지 하나님께 감사하며 (엡 5:20)", "맛있는 밥, 따뜻한 집, 그리고 네가 있어서 아빠는 매일매일 감사해."),

    # --- [91일~100일] 지혜와 축복 ---
    ("너희 중에 누구든지 지혜가 부족하거든... 하나님께 구하라 그리하면 주시리라 (약 1:5)", "공부하다 막힐 때, '하나님 지혜를 주세요'라고 먼저 기도해보렴."),
    ("여호와는 네게 복을 주시고 너를 지키시기를 원하며 (민 6:24)", "오늘 하루 네 위로 하나님의 따뜻한 햇살 같은 축복이 가득 쏟아질 거야."),
    ("여호와를 경외하는 것이 지식의 근본이거늘 미련한 자는 지혜와 훈계를 멸시하느니라 (잠 1:7)", "책에서 배우는 지식보다 중요한 건 바르고 고운 마음가짐이란다."),
    ("오직 여호와의 율법을 즐거워하여 그의 율법을 주야로 묵상하는도다 (시 1:2)", "매일 아침 읽는 이 작은 말씀이 네 인생의 가장 든든한 뿌리가 될 거야."),
    ("지혜가 제일이니 지혜를 얻으라 네가 얻은 모든 것을 가지고 명철을 얻을지니라 (잠 4:7)", "친구들과 놀 때도, 공부할 때도 언제나 지혜롭게 생각하고 행동하자."),
    ("여호와께서 너희를 곧 너희와 너희의 자손을 더욱 번창하게 하시기를 원하노라 (시 115:14)", "네가 걷는 걸음걸음마다 예쁜 꽃들이 피어나듯 좋은 일들이 가득할 거야."),
    ("사람이 마음으로 자기의 길을 계획할지라도 그의 걸음을 인도하시는 이는 여호와시니라 (잠 16:9)", "계획대로 안 된다고 속상해하지 마. 하나님은 더 멋진 길을 준비해두셨어."),
    ("사랑하는 자여 네 영혼이 잘됨 같이 네가 범사에 잘되고 강건하기를 내가 간구하노라 (요삼 1:2)", "무엇보다 네 몸과 마음이 매일매일 튼튼하고 건강하게 자라길 기도해."),
    ("여호와를 경외하는 것이 지혜의 근본이요 거룩하신 자를 아는 것이 명철이니라 (잠 9:10)", "세상에서 가장 똑똑한 사람은 하나님을 아는 사람이란다. 넌 이미 최고지!"),
    ("네가 들어와도 복을 받고 나가도 복을 받을 것이니라 (신 28:6)", "100일 동안 말씀을 함께 읽은 우리 가족에게 하나님의 넘치는 축복이 함께하길!")
]

def get_next_index():
    filename = "progress.txt"
    if not os.path.exists(filename): return 0
    try:
        with open(filename, "r") as f: return int(f.read().strip())
    except: return 0

def save_next_index(index):
    with open("progress.txt", "w") as f:
        f.write(str(index))
    try:
        subprocess.run(["git", "config", "user.name", "GitHub Actions"])
        subprocess.run(["git", "config", "user.email", "actions@github.com"])
        subprocess.run(["git", "add", "progress.txt"])
        subprocess.run(["git", "commit", "-m", f"Update progress to {index}"])
        subprocess.run(["git", "push", "origin", "main"]) 
    except Exception as e:
        print(f"메모장 업데이트 실패: {e}")

def create_card(bible, daddy):
    try:
        backgrounds = [
            "https://images.unsplash.com/photo-1490750967868-88aa4486c946?q=80&w=800&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?q=80&w=800&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=800&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1501854140801-50d01698950b?q=80&w=800&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1506744626753-1fa28f673fac?q=80&w=800&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1470071131384-001b85755536?q=80&w=800&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=800&auto=format&fit=crop"  
        ]
        bg_url = random.choice(backgrounds)
        
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
    
    # 💡 50일차가 끝나서 progress.txt가 50 이상으로 기록되어 있으면 자동으로 0으로 리셋합니다.
    if idx >= total:
        idx = 0
    
    if idx < total:
        b, d = KIDS_BIBLE_MESSAGES[idx]
        
        # 💡 idx는 0부터 시작하지만 화면에는 Day 51부터 나오게 숫자 51을 더해줍니다.
        msg = f"☀️ <b>Day {idx+51}</b>\n\n📖 <b>오늘의 말씀</b>\n{b}\n\n💬 <b>아빠의 마음</b>\n{d}"
        
        # 마지막 100일 차에만 나오는 알림
        if (idx + 1) == total:
            msg += "\n\n🎉 <b>[알림] 100일 마지막 메시지입니다. 다음 말씀을 준비해 주세요!</b>"
            
        card = create_card(b, d)
        send_msg(msg, card)
        save_next_index(idx + 1)
    else:
        send_msg("📢 모든 메시지가 소진되었습니다!")
