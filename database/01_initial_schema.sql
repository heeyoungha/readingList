-- 독서 목록 앱 데이터베이스 스키마

-- 독자 테이블 생성
CREATE TABLE readers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  email TEXT,
  bio TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 책 테이블 생성 (기존 books 테이블 수정)
CREATE TABLE books (
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

-- 독자 테이블에 샘플 데이터 추가
INSERT INTO readers (name, email, bio) VALUES
('김독서', 'kim@example.com', '과학과 철학에 관심이 많은 독서가'),
('이북러버', 'lee@example.com', '소설과 문학 작품을 즐겨 읽는 독자'),
('박철학', 'park@example.com', '철학과 자기계발 서적을 선호하는 독자'),
('정역사', 'jung@example.com', '역사와 인문학 서적을 주로 읽는 독자');

-- 책 테이블에 샘플 데이터 추가 (reader_id는 위에서 생성된 독자 ID로 연결)
INSERT INTO books (title, author, reader_id, review, rating, emotion, read_date, tags) 
SELECT 
  '코스모스',
  '칼 세이건',
  r.id,
  '우주에 대한 경이로움과 과학적 사고의 중요성을 깨닫게 해준 책입니다. 세이건의 시적인 문체로 복잡한 과학 개념들을 쉽게 설명해주어 과학에 대한 흥미를 불러일으켰습니다.',
  5,
  'excited',
  '2024-01-15',
  ARRAY['과학', '우주', '철학']
FROM readers r WHERE r.name = '김독서';

INSERT INTO books (title, author, reader_id, review, rating, emotion, read_date, tags) 
SELECT 
  '82년생 김지영',
  '조남주',
  r.id,
  '현대 여성이 겪는 현실적인 문제들을 담담하게 그려낸 작품입니다. 읽으면서 많은 생각을 하게 되었고, 우리 사회에 대해 돌아보는 계기가 되었습니다.',
  4,
  'thoughtful',
  '2024-01-28',
  ARRAY['소설', '여성', '사회']
FROM readers r WHERE r.name = '이북러버';

INSERT INTO books (title, author, reader_id, review, rating, emotion, read_date, tags) 
SELECT 
  '미움받을 용기',
  '기시미 이치로, 고가 후미타케',
  r.id,
  '아들러 심리학을 바탕으로 한 대화형식의 책입니다. 타인의 시선에서 벗어나 자신만의 삶을 살아가는 것의 중요성을 배웠습니다. 실천하기는 어렵지만 좋은 방향을 제시해주는 책이었습니다.',
  4,
  'calm',
  '2024-02-10',
  ARRAY['자기계발', '심리학', '철학']
FROM readers r WHERE r.name = '박철학';

INSERT INTO books (title, author, reader_id, review, rating, emotion, read_date, tags) 
SELECT 
  '호모 사피엔스',
  '유발 하라리',
  r.id,
  '인류의 역사를 새로운 관점에서 바라본 흥미진진한 책입니다. 인지혁명, 농업혁명, 과학혁명을 통해 인류가 어떻게 발전해왔는지 명확하게 설명해줍니다.',
  5,
  'surprised',
  '2024-02-25',
  ARRAY['역사', '인류학', '철학']
FROM readers r WHERE r.name = '정역사';

INSERT INTO books (title, author, reader_id, review, rating, emotion, read_date, tags) 
SELECT 
  '원피스 1권',
  '오다 에이치로',
  r.id,
  '루피의 모험이 시작되는 첫 번째 권입니다. 꿈을 향한 열정과 동료애의 소중함을 느낄 수 있었습니다. 만화지만 깊은 메시지가 담겨있어 감동적이었습니다.',
  4,
  'excited',
  '2024-03-05',
  ARRAY['만화', '모험', '우정']
FROM readers r WHERE r.name = '김독서';

INSERT INTO books (title, author, reader_id, review, rating, emotion, read_date, tags) 
SELECT 
  '데미안',
  '헤르만 헤세',
  r.id,
  '자아 찾기와 성장에 대한 깊은 통찰을 제공하는 작품입니다. 싱클레어의 내적 갈등과 성장 과정이 현재의 나와 많이 닮아있어 공감이 되었습니다.',
  5,
  'thoughtful',
  '2024-03-12',
  ARRAY['소설', '성장', '철학']
FROM readers r WHERE r.name = '이북러버';

-- 인덱스 생성 (성능 향상)
CREATE INDEX idx_books_reader_id ON books(reader_id);
CREATE INDEX idx_books_read_date ON books(read_date);
CREATE INDEX idx_books_emotion ON books(emotion);
CREATE INDEX idx_readers_name ON readers(name);

-- 뷰 생성 (독자 정보와 책 정보를 함께 조회)
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

-- RLS (Row Level Security) 설정 (선택사항)
ALTER TABLE readers ENABLE ROW LEVEL SECURITY;
ALTER TABLE books ENABLE ROW LEVEL SECURITY;

-- RLS 정책 (모든 사용자가 읽기 가능, 인증된 사용자만 쓰기 가능)
CREATE POLICY "Readers are viewable by everyone" ON readers FOR SELECT USING (true);
CREATE POLICY "Books are viewable by everyone" ON books FOR SELECT USING (true);
CREATE POLICY "Authenticated users can insert books" ON books FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can update books" ON books FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can delete books" ON books FOR DELETE USING (auth.role() = 'authenticated'); 