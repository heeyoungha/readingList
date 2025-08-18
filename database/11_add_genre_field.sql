-- books 테이블에 genre 필드 추가
-- 장르별 독서 분석을 위한 필드

-- 1. books 테이블에 genre 컬럼 추가
ALTER TABLE books ADD COLUMN IF NOT EXISTS genre VARCHAR(50);

-- 2. genre 컬럼에 기본값 설정 (기존 데이터를 위해)
UPDATE books 
SET genre = '미분류' 
WHERE genre IS NULL;

-- 3. genre 컬럼에 코멘트 추가 (선택사항)
COMMENT ON COLUMN books.genre IS '책의 장르 (예: 소설, 과학, 자기계발, 역사, 만화 등)';

-- 4. 인덱스 생성 (장르별 조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);

-- 5. 장르별 통계를 위한 뷰 생성 (선택사항)
CREATE OR REPLACE VIEW genre_stats AS
SELECT 
    genre,
    COUNT(*) as book_count,
    AVG(rating) as avg_rating,
    COUNT(DISTINCT reader_id) as reader_count
FROM books 
WHERE genre IS NOT NULL
GROUP BY genre
ORDER BY book_count DESC;

-- 6. 자주 사용되는 장르 목록 (참고용 주석)
/*
일반적인 장르 예시:
- 소설
- 과학
- 자기계발
- 역사
- 철학
- 경제/경영
- 만화
- 시/에세이
- 종교/영성
- 예술
- 정치/사회
- 건강/의학
- 요리
- 여행
- 스포츠
- 기술/IT
- 미분류
*/ 