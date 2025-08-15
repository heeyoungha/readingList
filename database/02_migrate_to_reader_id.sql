-- books 테이블 구조 수정
-- 1. reader 필드를 reader_id로 변경하고 발제문 필드 추가

-- 기존 테이블 백업
CREATE TABLE books_backup AS SELECT * FROM books;

-- 새로운 테이블 생성
CREATE TABLE books_new (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  reader_id UUID NOT NULL REFERENCES readers(id) ON DELETE CASCADE,
  review TEXT NOT NULL,
  presentation TEXT, -- 발제문 필드 추가
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  emotion TEXT NOT NULL,
  read_date DATE NOT NULL,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 기존 데이터에서 사용되는 독자들을 readers 테이블에 추가
INSERT INTO readers (name, email, bio)
SELECT DISTINCT b.reader, NULL, NULL
FROM books b
WHERE b.reader IS NOT NULL
  AND b.reader NOT IN (SELECT name FROM readers)
ON CONFLICT (name) DO NOTHING;

-- 기존 데이터 마이그레이션 (reader를 reader_id로 변환)
INSERT INTO books_new (id, title, author, reader_id, review, presentation, rating, emotion, read_date, tags, created_at, updated_at)
SELECT 
  b.id,
  b.title,
  b.author,
  r.id as reader_id,
  b.review,
  NULL as presentation, -- 기존 테이블에는 없으므로 NULL로 설정
  b.rating,
  b.emotion,
  b.read_date,
  b.tags,
  b.created_at,
  b.updated_at
FROM books b
LEFT JOIN readers r ON b.reader = r.name
WHERE r.id IS NOT NULL; -- reader_id가 NULL인 경우 제외

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_books_reader_id ON books_new(reader_id);
CREATE INDEX IF NOT EXISTS idx_books_read_date ON books_new(read_date);
CREATE INDEX IF NOT EXISTS idx_books_emotion ON books_new(emotion);

-- RLS 정책 설정 (필요한 경우)
-- ALTER TABLE books_new ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Enable read access for all users" ON books_new FOR SELECT USING (true);
-- CREATE POLICY "Enable insert for authenticated users only" ON books_new FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Enable update for users based on reader" ON books_new FOR UPDATE USING (true);
-- CREATE POLICY "Enable delete for users based on reader" ON books_new FOR DELETE USING (true);

-- 확인용 쿼리
SELECT 
  b.id,
  b.title,
  b.author,
  r.name as reader_name,
  b.review,
  b.presentation,
  b.rating,
  b.emotion,
  b.read_date
FROM books_new b
LEFT JOIN readers r ON b.reader_id = r.id
LIMIT 5;

-- 기존 테이블 삭제 및 새 테이블 이름 변경 (안전을 위해 주석 처리)
-- DROP TABLE books;
-- ALTER TABLE books_new RENAME TO books;
-- DROP TABLE books_backup; -- 백업 테이블 삭제 (선택사항) 