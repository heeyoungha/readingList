-- 북 폼 업데이트: 감정 컬럼 의존성 문제 해결 및 새로운 필드 추가
-- 실행 날짜: 2025-09-14

-- 1. 의존하는 뷰 삭제
DROP VIEW IF EXISTS emotion_score_stats CASCADE;

-- 2. 감정 관련 필드 제거
ALTER TABLE books DROP COLUMN IF EXISTS emotion CASCADE;
ALTER TABLE books DROP COLUMN IF EXISTS emotion_score CASCADE;

-- 3. 새로운 필드들 추가
ALTER TABLE books ADD COLUMN IF NOT EXISTS purchase_link TEXT;
ALTER TABLE books ADD COLUMN IF NOT EXISTS one_liner TEXT;
ALTER TABLE books ADD COLUMN IF NOT EXISTS motivation TEXT;
ALTER TABLE books ADD COLUMN IF NOT EXISTS memorable_quotes TEXT[];

-- 4. 필드 설명을 위한 코멘트 추가
COMMENT ON COLUMN books.purchase_link IS '책 구매 링크';
COMMENT ON COLUMN books.one_liner IS '한줄평';
COMMENT ON COLUMN books.motivation IS '고르게 된 계기';
COMMENT ON COLUMN books.memorable_quotes IS '기억에 남는 구절들';

-- 5. 기존 genre 필드에 대한 코멘트 추가 (이미 존재하는 경우)
COMMENT ON COLUMN books.genre IS '장르';

-- 6. 변경 사항 확인
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'books' 
ORDER BY ordinal_position; 