-- books 테이블에 감정 수치화 필드 추가
-- 행동력 기준: 10점(최고 행동력) → 1점(완전 무기력)

-- 1. books 테이블에 emotion_score 컬럼 추가
ALTER TABLE books ADD COLUMN IF NOT EXISTS emotion_score INTEGER;

-- 2. emotion_score 컬럼에 기본값 설정
ALTER TABLE books ALTER COLUMN emotion_score SET DEFAULT 5;

-- 3. 기존 감정 데이터를 기반으로 감정 점수 업데이트
UPDATE books 
SET emotion_score = CASE 
    WHEN emotion = 'sad' THEN 2        -- 슬픔: 매우 낮은 행동력, 위축됨
    WHEN emotion = 'calm' THEN 4       -- 평온: 차분하지만 적극적이지 않음
    WHEN emotion = 'thoughtful' THEN 6 -- 사색: 내적 에너지는 있지만 외적 행동력은 중간
    WHEN emotion = 'surprised' THEN 7  -- 놀람: 순간적 높은 각성도, 반응적 행동력
    WHEN emotion = 'happy' THEN 8      -- 기쁨: 높은 행동력과 긍정적 에너지
    WHEN emotion = 'excited' THEN 10   -- 흥분: 최고 행동력, 즉각적 움직임 유발
    ELSE 5                             -- 기본값: 중간 행동력
END
WHERE emotion IS NOT NULL;

-- 4. emotion이 NULL인 경우 기본값 설정
UPDATE books 
SET emotion_score = 5 
WHERE emotion IS NULL AND emotion_score IS NULL;

-- 5. emotion_score 컬럼에 제약조건 추가 (1-10 범위)
ALTER TABLE books ADD CONSTRAINT emotion_score_range CHECK (emotion_score >= 1 AND emotion_score <= 10);

-- 6. emotion_score 컬럼에 코멘트 추가
COMMENT ON COLUMN books.emotion_score IS '감정의 행동력 수치 (1: 무기력/위축 → 10: 최고 행동력)';

-- 7. 인덱스 생성 (감정 점수별 조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_books_emotion_score ON books(emotion_score);

-- 8. 감정 점수별 통계를 위한 뷰 생성 (선택사항)
CREATE OR REPLACE VIEW emotion_score_stats AS
SELECT 
    emotion,
    emotion_score,
    COUNT(*) as book_count,
    AVG(rating) as avg_rating,
    COUNT(DISTINCT reader_id) as reader_count
FROM books 
WHERE emotion_score IS NOT NULL
GROUP BY emotion, emotion_score
ORDER BY emotion_score DESC;

-- 9. 확인 쿼리 (실행 후 결과 확인용)
-- SELECT emotion, emotion_score, COUNT(*) as count 
-- FROM books 
-- GROUP BY emotion, emotion_score 
-- ORDER BY emotion_score DESC;

-- 10. 감정별 행동력 매핑표 (참고용 주석)
/*
감정별 행동력 점수 매핑:
- excited (흥분): 10점 - 최고 행동력, 즉각적 움직임 유발
- happy (기쁨): 8점 - 높은 행동력과 긍정적 에너지
- surprised (놀람): 7점 - 순간적 높은 각성도, 반응적 행동력
- thoughtful (사색): 6점 - 내적 에너지는 있지만 외적 행동력은 중간
- calm (평온): 4점 - 차분하지만 적극적이지 않음
- sad (슬픔): 2점 - 매우 낮은 행동력, 위축됨
*/ 