-- books 테이블의 emotion 필드 확인
-- 이 스크립트를 Supabase SQL Editor에서 실행하여 emotion 필드 상태를 확인하세요

-- 1. books 테이블의 모든 컬럼 정보 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'books' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- 2. emotion 필드가 있는 데이터 확인
SELECT 
    id,
    title,
    emotion,
    CASE 
        WHEN emotion IS NULL THEN 'NULL'
        WHEN emotion = '' THEN 'EMPTY STRING'
        ELSE emotion
    END as emotion_status
FROM books 
LIMIT 10;

-- 3. emotion 필드의 값 분포 확인
SELECT 
    emotion,
    COUNT(*) as count
FROM books 
GROUP BY emotion
ORDER BY count DESC;

-- 4. emotion 필드가 NULL인 레코드 개수
SELECT COUNT(*) as null_emotion_count
FROM books 
WHERE emotion IS NULL;

-- 5. emotion 필드에 기본값 설정 (필요한 경우)
-- UPDATE books SET emotion = 'thoughtful' WHERE emotion IS NULL; 