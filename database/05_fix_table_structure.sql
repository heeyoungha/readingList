-- books 테이블 구조를 현재 코드에 맞게 수정
-- reader_id 컬럼을 reader로 변경하고, 외래키 제약 조건 제거

-- 1. 기존 테이블 백업
CREATE TABLE books_backup AS SELECT * FROM books;

-- 2. 새로운 테이블 생성 (reader 필드 사용)
CREATE TABLE books_new (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  reader TEXT NOT NULL,
  review TEXT NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  emotion TEXT NOT NULL,
  read_date DATE NOT NULL,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 기존 데이터 마이그레이션 (reader_id를 reader 이름으로 변환)
INSERT INTO books_new (id, title, author, reader, review, rating, emotion, read_date, tags, created_at, updated_at)
SELECT 
  b.id,
  b.title,
  b.author,
  r.name as reader,
  b.review,
  b.rating,
  b.emotion,
  b.read_date,
  b.tags,
  b.created_at,
  b.updated_at
FROM books b
LEFT JOIN readers r ON b.reader_id = r.id;

-- 4. 기존 테이블 삭제 및 새 테이블 이름 변경
-- (안전을 위해 주석 처리 - 수동으로 실행하세요)
-- DROP TABLE books;
-- ALTER TABLE books_new RENAME TO books;

-- 5. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_books_reader ON books_new(reader);
CREATE INDEX IF NOT EXISTS idx_books_read_date ON books_new(read_date);
CREATE INDEX IF NOT EXISTS idx_books_emotion ON books_new(emotion);

-- 6. RLS 정책 설정 (필요한 경우)
-- ALTER TABLE books_new ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Enable read access for all users" ON books_new FOR SELECT USING (true);
-- CREATE POLICY "Enable insert for authenticated users only" ON books_new FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Enable update for users based on reader" ON books_new FOR UPDATE USING (true);
-- CREATE POLICY "Enable delete for users based on reader" ON books_new FOR DELETE USING (true);

-- 확인용 쿼리
SELECT * FROM books_new LIMIT 5; 