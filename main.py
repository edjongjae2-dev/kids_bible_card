if __name__ == "__main__":
    idx = get_next_index()
    total = len(KIDS_BIBLE_MESSAGES)
    
    if idx < total:
        b, d = KIDS_BIBLE_MESSAGES[idx]
        msg = f"☀️ <b>Day {idx+1}</b>\n\n📖 <b>오늘의 말씀</b>\n{b}\n\n💬 <b>아빠의 마음</b>\n{d}"
        
        # 🌟 마지막 날(50일째)에만 안내 메시지 추가
        if (idx + 1) == total:
            msg += "\n\n🎉 <b>[알림] 50일 마지막 메시지입니다. 다음 말씀을 준비해 주세요!</b>"
            
        # 카드 이미지 생성
        card = create_card(b, d)
        
        # 텔레그램 발송
        send_msg(msg, card)
        
        # 🌟 다음 날을 위해 인덱스 저장 (이게 안쪽으로 들어와 있어야 Day 2가 됩니다!)
        save_next_index(idx + 1)
        
    else:
        send_msg("📢 모든 메시지가 소진되었습니다!")
