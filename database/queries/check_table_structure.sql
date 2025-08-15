-- 현재 books 테이블 구조 확인
SELECT 
  column_name, 
  data_type, 
  is_nullable, 
  column_default
FROM information_schema.columns 
WHERE table_name = 'books' 
ORDER BY ordinal_position;

-- 현재 books 테이블의 데이터 샘플 확인
SELECT * FROM books LIMIT 5; 