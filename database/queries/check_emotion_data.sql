-- emotion 데이터 확인
SELECT 
  id,
  title,
  emotion,
  rating,
  reader_id
FROM books 
LIMIT 10;

-- emotion 값들의 분포 확인
SELECT 
  emotion,
  COUNT(*) as count
FROM books 
GROUP BY emotion
ORDER BY count DESC; 