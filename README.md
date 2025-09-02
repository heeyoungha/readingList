# Reading List

독서 목록을 관리하는 프로젝트입니다.

## 🚀 주요 기능

- 📚 독서 목록 추가/삭제/수정
- ✍️ 독후감 작성 및 관리
- 🎯 액션 리스트 생성 및 추적
- 📊 독서 통계 대시보드
- 👥 독자별 독서 기록 관리
- 🏷️ 태그 및 장르별 분류
- 😊 독서 후 감정 기록
- 📅 월별/분기별 독서 현황
- 🤖 **개인 맞춤형 페르소나 시스템** ✅ (Phase 1-2 완료)

## 🛠️ 기술 스택

### Frontend
- **React 18** - 사용자 인터페이스 구축
- **TypeScript** - 타입 안전성 확보
- **Tailwind CSS** - 스타일링
- **Radix UI** - 접근성 높은 컴포넌트
- **React Hook Form** - 폼 관리
- **Zod** - 스키마 검증

### Backend & Database
- **Supabase** - 백엔드 서비스 및 데이터베이스
- **PostgreSQL** - 관계형 데이터베이스
- **Row Level Security (RLS)** - 데이터 보안
- **FastAPI** - 페르소나 시스템 백엔드 API
- **Python** - AI/ML 분석 및 데이터 처리

### 상태 관리 & 라이브러리
- **React Hooks** - 상태 관리
- **date-fns** - 날짜 처리
- **Recharts** - 차트 및 데이터 시각화
- **Lucide React** - 아이콘

### AI/ML & 데이터 분석
- **KoNLPy** - 한국어 자연어 처리
- **sentence-transformers** - 텍스트 임베딩
- **FAISS** - 벡터 데이터베이스
- **scikit-learn** - 토픽 모델링 및 클러스터링

## 📁 프로젝트 구조

```
readingList/
├── src/                          # 소스 코드
│   ├── components/               # React 컴포넌트
│   │   ├── ui/                  # 재사용 가능한 UI 컴포넌트
│   │   ├── Dashboard.tsx        # 독서 통계 대시보드
│   │   ├── BookCard.tsx         # 책 카드 컴포넌트
│   │   ├── BookDetailModal.tsx  # 책 상세 모달
│   │   ├── AddBookForm.tsx      # 책 추가 폼
│   │   ├── ActionListPage.tsx   # 액션 리스트 페이지
│   │   ├── MeetingPage.tsx      # 독서 모임 페이지
│   │   └── Navigation.tsx       # 네비게이션
│   ├── types/                   # TypeScript 타입 정의
│   │   ├── book.ts             # 책 관련 타입
│   │   ├── actionList.ts       # 액션 리스트 타입
│   │   └── auth.ts             # 인증 관련 타입
│   ├── lib/                     # 유틸리티 및 설정
│   │   ├── supabase.ts         # Supabase 클라이언트
│   │   ├── database.ts         # 데이터베이스 함수
│   │   ├── auth.ts             # 인증 관련 함수
│   │   └── utils.ts            # 공통 유틸리티
│   ├── styles/                  # 스타일 파일
│   └── App.tsx                 # 메인 앱 컴포넌트
├── persona_system/               # 🤖 페르소나 시스템
│   ├── backend/                 # FastAPI 백엔드
│   ├── models/                  # AI 모델 및 분석 로직
│   ├── utils/                   # 텍스트 전처리, 감정 분석, 토픽 모델링
│   ├── data/                    # 데이터 처리 및 저장
│   └── test_persona.py         # 테스트 스크립트
├── database/                     # 데이터베이스 스키마 및 마이그레이션
│   ├── 01_initial_schema.sql   # 초기 스키마
│   ├── 02_migrate_to_reader_id.sql
│   ├── 03_legacy_migration.sql
│   └── ...                     # 기타 마이그레이션 파일
├── public/                      # 정적 파일
└── package.json                 # 프로젝트 의존성
```

## 🗄️ 데이터베이스 스키마

### 주요 테이블

#### `readers` (독자)
- `id`: UUID (Primary Key)
- `name`: 독자 이름
- `email`: 이메일
- `bio`: 자기소개

#### `books` (책)
- `id`: UUID (Primary Key)
- `title`: 책 제목
- `author`: 저자
- `reader_id`: 독자 ID (Foreign Key)
- `review`: 독후감
- `rating`: 평점 (1-5)
- `emotion`: 감정 (happy, sad, thoughtful, excited, calm, surprised)
- `emotion_score`: 감정 행동력 수치 (1-10)
- `read_date`: 읽은 날짜
- `tags`: 태그 배열
- `genre`: 장르

#### `action_lists` (액션 리스트)
- `id`: UUID (Primary Key)
- `title`: 액션 제목
- `reader_id`: 독자 ID
- `book_title`: 관련 책 제목
- `content`: 액션 내용
- `target_months`: 목표 월
- `status`: 상태 (진행전, 진행중, 완료, 보류)

## 🎯 주요 컴포넌트

### Dashboard
독서 통계를 시각화하는 대시보드
- 월별/분기별 독서 현황
- 감정별 분포 차트
- 독자별 평점 분석
- 장르별 통계

### Book Management
- **BookCard**: 책 정보를 카드 형태로 표시
- **BookDetailModal**: 책 상세 정보 및 독후감 표시
- **AddBookForm**: 새로운 책 추가 폼

### Action List
독서 후 실천할 액션을 관리
- 액션 생성 및 추적
- 상태별 필터링
- 목표 월 설정

## 📊 주요 기능 상세

### 독서 기록 관리
- 책 제목, 저자, 독후감, 평점, 감정 기록
- 태그 및 장르 분류
- 읽은 날짜 추적

### 감정 분석
- 6가지 감정 카테고리 (기쁨, 슬픔, 사색, 흥분, 평온, 놀람)
- 감정별 행동력 수치 (1-10 스케일)
- 감정 분포 시각화

### 통계 및 분석
- 월별/분기별 독서 현황
- 독자별 독서 패턴 분석
- 장르별 선호도 파악
- 평점 분포 및 트렌드

### 액션 리스트
- 독서 후 실천할 액션 계획
- 진행 상태 추적
- 목표 월 설정 및 관리

### 개인 맞춤형 페르소나 시스템
북클럽 데이터를 활용한 **개인 맞춤형 페르소나 시스템**을 구축하여 사용자의 독서 패턴과 글쓰기 스타일을 분석하고, 맞춤형 프로젝트 추천을 제공합니다.

#### **구현 완료된 기능**
- **텍스트 전처리 시스템**: HTML 태그 제거, 특수문자 정리, 한국어 형태소 분석
- **감정 분석 엔진**: 6가지 감정 카테고리 분석, 긍정/부정/중립 톤 분석
- **토픽 모델링**: 키워드 추출, 카테고리별 분류, 관심사 분석
- **페르소나 생성기**: 글쓰기 스타일, 감정 프로필, 성격 특성 분석
- **FastAPI 백엔드**: RESTful API, 텍스트 분석, 페르소나 생성 엔드포인트
- **임베딩 생성 시스템**: transformers 직접 사용으로 PyTorch 2.2.2 호환, 한국어 텍스트 임베딩 생성 완벽 지원
- **벡터 데이터베이스**: FAISS 기반 고성능 벡터 검색 및 저장, 실제 임베딩으로 의미있는 검색 가능
- **확장 가능한 저장소**: 로컬 저장 + 향후 Supabase 전환을 위한 구조
- **Supabase 전환 준비**: 마이그레이션 계획 및 전환 메서드 구현 완료
- **실제 텍스트 분석**: 한국어 독서 관련 텍스트 분석 및 임베딩 생성 완벽 작동

#### **구현 계획**
- **Phase 1**: 데이터 수집 및 전처리 ✅ **완료**
- **Phase 2**: 임베딩 생성 및 벡터 DB 구축 ✅ **완료** (실제 텍스트 분석 및 임베딩 생성 완벽 작동)
- **Phase 3**: 검색 시스템 구현 ⏳ **대기 중** (Phase 2 완성으로 구현 준비 완료)
- **Phase 4**: 페르소나 챗봇 개발 ⏳ **대기 중**
- **Phase 5**: 사용자 인터페이스 및 테스트 ⏳ **대기 중**

#### **개발 → 운영 전환 계획**
**현재 단계 (개발용)**: 로컬 FAISS 기반으로 빠른 개발 및 테스트
- ✅ **Phase 1-2**: 로컬 환경에서 완벽 구현
- 🔄 **Phase 3**: 로컬 FAISS 기반 검색 시스템 구현
- 🔄 **Phase 4-5**: 로컬 환경에서 페르소나 챗봇 및 UI 완성

**운영 단계 (프로덕션용)**: Supabase 벡터 확장으로 전환하여 Vercel 배포
- 🔄 **Supabase 전환**: 로컬 FAISS → Supabase 벡터 확장
- 🔄 **Vercel 배포**: 완벽한 서버리스 환경에서 운영
- 🔄 **사용자 서비스**: 실제 사용자 대상 서비스 시작

**전환 시점**: 개발 완료 후, Vercel 배포 준비 시
**전환 이유**: Vercel 호환성, 사용자별 데이터 격리, 클라우드 확장성

#### **기술 스택**
- **AI/ML**: OpenAI API, sentence-transformers
- **벡터 DB**: FAISS (로컬 저장) → 향후 Supabase 벡터 확장
- **한국어 처리**: KoNLPy (Okt, Mecab), spaCy
- **데이터 처리**: Python + Pandas, NumPy
- **백엔드**: FastAPI (개발용) → 향후 Vercel API Routes
- **프론트엔드**: React + TypeScript (Vercel 배포용)
- **데이터베이스**: Supabase (PostgreSQL + 벡터 확장)

#### **빠른 시작**
```bash
cd persona_system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Phase 2 테스트
python test_phase2.py                    # 기본 기능 테스트
python test_embedding_extended.py        # 확장된 임베딩 기능 테스트
python test_phase2_complete.py           # Phase 2 완성 및 Supabase 전환 준비 테스트

# 백엔드 실행
python run_backend.py
```
