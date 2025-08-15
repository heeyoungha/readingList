-- 액션리스트 완전 스키마
-- 독서를 통해 얻은 인사이트를 실천으로 옮기기 위한 액션리스트 테이블

CREATE TABLE action_lists (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  reader_id UUID NOT NULL REFERENCES readers(id) ON DELETE CASCADE,
  book_title TEXT NOT NULL,
  content TEXT NOT NULL,
  target_months TEXT[] DEFAULT '{}',
  action_time TEXT,
  status TEXT NOT NULL CHECK (status IN ('진행전', '진행중', '완료', '보류')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_action_lists_reader_id ON action_lists(reader_id);
CREATE INDEX IF NOT EXISTS idx_action_lists_status ON action_lists(status);
CREATE INDEX IF NOT EXISTS idx_action_lists_target_months ON action_lists USING GIN(target_months);
CREATE INDEX IF NOT EXISTS idx_action_lists_created_at ON action_lists(created_at);

-- RLS 정책 설정
ALTER TABLE action_lists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON action_lists FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON action_lists FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for users based on reader" ON action_lists FOR UPDATE USING (true);
CREATE POLICY "Enable delete for users based on reader" ON action_lists FOR DELETE USING (true);

-- 샘플 데이터 추가
INSERT INTO action_lists (title, reader_id, book_title, content, target_months, action_time, status)
SELECT 
  '독서 모임 준비',
  r.id,
  '코스모스',
  '다음 독서 모임에서 발표할 내용을 정리하고 질문 목록을 준비한다. 세이건의 우주에 대한 경이로움을 다른 사람들과 공유할 수 있도록 준비한다.',
  ARRAY['3월', '4월'],
  '매일 저녁 8시',
  '진행중'
FROM readers r 
WHERE r.name = '김독서'
LIMIT 1;

INSERT INTO action_lists (title, reader_id, book_title, content, target_months, action_time, status)
SELECT 
  '아들러 심리학 실천하기',
  r.id,
  '미움받을 용기',
  '아들러 심리학의 교훈을 일상에 적용해보기. 과거에 얽매이지 않고 현재와 미래에 집중하는 삶을 살아보자.',
  ARRAY['5월', '6월'],
  '주말 오후',
  '진행전'
FROM readers r 
WHERE r.name = '박철학'
LIMIT 1;

INSERT INTO action_lists (title, reader_id, book_title, content, target_months, action_time, status)
SELECT 
  '독서 습관 만들기',
  r.id,
  '책 읽는 뇌',
  '매일 30분씩 독서하는 습관을 만들어보자. 책을 읽는 시간을 정하고 꾸준히 실천해보자.',
  ARRAY['1월', '2월', '3월'],
  '매일 아침 7시',
  '완료'
FROM readers r 
WHERE r.name = '이북러버'
LIMIT 1;

INSERT INTO action_lists (title, reader_id, book_title, content, target_months, action_time, status)
SELECT 
  '독서 노트 작성하기',
  r.id,
  '홀론(HOLON) 1',
  '읽은 책의 핵심 내용을 정리하고 개인적인 생각을 기록하는 독서 노트를 작성해보자.',
  ARRAY['7월', '8월'],
  '매주 일요일',
  '보류'
FROM readers r 
WHERE r.name = '김독서'
LIMIT 1; 