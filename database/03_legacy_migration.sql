-- 기존 books 테이블을 새 스키마로 마이그레이션

-- 1. 기존 books 테이블 백업
CREATE TABLE books_backup AS SELECT * FROM books;

-- 2. 독자 테이블 생성
CREATE TABLE readers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  email TEXT,
  bio TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 독자 테이블 생성
CREATE TABLE readers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  email TEXT,
  bio TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 새 books 테이블 생성

->

-- 2. 독자 테이블 생성
CREATE TABLE readers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  email TEXT,
  bio TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 기존 독자 데이터 추출 및 삽입
INSERT INTO readers (name, email, bio)
SELECT DISTINCT 
  reader as name,
  reader || '@example.com' as email,
  '독서 애호가' as bio
FROM books_backup
WHERE reader IS NOT NULL;

-- 4. 새 books 테이블 생성

-- 4. 새 books 테이블 생성
CREATE TABLE books_new (
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

-- 5. 기존 데이터를 새 테이블로 마이그레이션
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
FROM books_backup b
JOIN readers r ON b.reader = r.name;

-- 6. 기존 테이블 삭제 및 새 테이블 이름 변경
DROP TABLE books;
ALTER TABLE books_new RENAME TO books;

-- 7. 인덱스 생성
CREATE INDEX idx_books_reader_id ON books(reader_id);
CREATE INDEX idx_books_read_date ON books(read_date);
CREATE INDEX idx_books_emotion ON books(emotion);
CREATE INDEX idx_readers_name ON readers(name);

-- 8. 뷰 생성
CREATE VIEW books_with_readers AS
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
FROM books b
JOIN readers r ON b.reader_id = r.id
ORDER BY b.created_at DESC;

-- 9. 백업 테이블 삭제 (마이그레이션 완료 후)
-- DROP TABLE books_backup; 