-- 사용자 인증을 위한 데이터베이스 스키마 업데이트
-- 기존 테이블에 user_id 컬럼 추가

-- 1. books 테이블에 user_id 컬럼 추가
ALTER TABLE books ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 2. action_lists 테이블에 user_id 컬럼 추가
ALTER TABLE action_lists ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 3. readers 테이블에 user_id 컬럼 추가 (선택사항 - 사용자별 독자 관리)
ALTER TABLE readers ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 4. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_books_user_id ON books(user_id);
CREATE INDEX IF NOT EXISTS idx_action_lists_user_id ON action_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_readers_user_id ON readers(user_id);

-- 5. RLS 정책 업데이트
-- books 테이블 RLS 정책
DROP POLICY IF EXISTS "Enable read access for all users" ON books;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON books;
DROP POLICY IF EXISTS "Enable update for users based on reader" ON books;
DROP POLICY IF EXISTS "Enable delete for users based on reader" ON books;

CREATE POLICY "Users can view their own books" ON books
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own books" ON books
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own books" ON books
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own books" ON books
  FOR DELETE USING (auth.uid() = user_id);

-- action_lists 테이블 RLS 정책
DROP POLICY IF EXISTS "Enable read access for all users" ON action_lists;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON action_lists;
DROP POLICY IF EXISTS "Enable update for users based on reader" ON action_lists;
DROP POLICY IF EXISTS "Enable delete for users based on reader" ON action_lists;

CREATE POLICY "Users can view their own action lists" ON action_lists
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own action lists" ON action_lists
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own action lists" ON action_lists
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own action lists" ON action_lists
  FOR DELETE USING (auth.uid() = user_id);

-- readers 테이블 RLS 정책 (선택사항)
DROP POLICY IF EXISTS "Enable read access for all users" ON readers;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON readers;
DROP POLICY IF EXISTS "Enable update for users based on reader" ON readers;
DROP POLICY IF EXISTS "Enable delete for users based on reader" ON readers;

CREATE POLICY "Users can view their own readers" ON readers
  FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert their own readers" ON readers
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own readers" ON readers
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own readers" ON readers
  FOR DELETE USING (auth.uid() = user_id);

-- 6. 기존 데이터에 기본 user_id 설정 (선택사항)
-- 실제 운영에서는 사용자별로 데이터를 분리해야 함
-- UPDATE books SET user_id = (SELECT id FROM auth.users LIMIT 1) WHERE user_id IS NULL;
-- UPDATE action_lists SET user_id = (SELECT id FROM auth.users LIMIT 1) WHERE user_id IS NULL;
-- UPDATE readers SET user_id = (SELECT id FROM auth.users LIMIT 1) WHERE user_id IS NULL; 