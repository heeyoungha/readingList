-- 안전한 마이그레이션 방법 (단계별 실행)

-- 1단계: 독자 테이블 생성
CREATE TABLE IF NOT EXISTS readers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  email TEXT,
  bio TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2단계: 기존 독자 데이터 추출 및 삽입 (중복 방지)
INSERT INTO readers (name, email, bio)
SELECT DISTINCT 
  reader as name,
  reader || '@example.com' as email,
  '독서 애호가' as bio
FROM books
WHERE reader IS NOT NULL
  AND reader NOT IN (SELECT name FROM readers);

-- 3단계: 새 books 테이블 생성 (임시 이름)
CREATE TABLE IF NOT EXISTS books_new (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  reader_id UUID NOT NULL REFERENCES readers(id) ON DELETE CASCADE,
  review TEXT NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  emotion TEXT NOT NULL,
  read_date DATE NOT NULL,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4단계: 기존 데이터를 새 테이블로 마이그레이션
INSERT INTO books_new (title, author, reader_id, review, rating, emotion, read_date, tags)
SELECT 
  b.title,
  b.author,
  r.id as reader_id,
  b.review,
  b.rating,
  b.emotion,
  b.read_date::DATE,
  b.tags
FROM books b
JOIN readers r ON b.reader = r.name
ON CONFLICT DO NOTHING;

-- 5단계: 데이터 확인 (실행 후 확인)
-- SELECT COUNT(*) FROM books; -- 기존 데이터 수
-- SELECT COUNT(*) FROM books_new; -- 새 테이블 데이터 수
-- SELECT COUNT(*) FROM readers; -- 독자 수

-- 6단계: 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_books_new_reader_id ON books_new(reader_id);
CREATE INDEX IF NOT EXISTS idx_books_new_read_date ON books_new(read_date);
CREATE INDEX IF NOT EXISTS idx_books_new_emotion ON books_new(emotion);
CREATE INDEX IF NOT EXISTS idx_readers_name ON readers(name);

-- 7단계: 뷰 생성
CREATE OR REPLACE VIEW books_with_readers AS
SELECT 
  b.id,
  b.title,
  b.author,
  r.name as reader_name,
  r.id as reader_id,
  b.review,
  b.rating,
  b.emotion,
  b.read_date,
  b.tags,
  b.created_at,
  b.updated_at
FROM books_new b
JOIN readers r ON b.reader_id = r.id
ORDER BY b.created_at DESC;

-- 8단계: 테이블 교체 (데이터 확인 후 실행)
-- ALTER TABLE books RENAME TO books_old;
-- ALTER TABLE books_new RENAME TO books;

-- 9단계: 기존 테이블 삭제 (모든 것이 정상 작동하는지 확인 후)
-- DROP TABLE books_old; 