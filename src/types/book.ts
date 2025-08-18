export interface Book {
    id: string;
    title: string;
    author: string;
    reader_id: string;
    reader_name: string; // 독자 이름을 표시하기 위한 필드
    review: string;
    presentation?: string; // 발제문 (선택사항)
    rating: number; // 1-5
    emotion: 'happy' | 'sad' | 'thoughtful' | 'excited' | 'calm' | 'surprised';
    emotion_score?: number; // 감정의 행동력 수치 (1-10)
    readDate: string;
    coverImage?: string;
    tags: string[];
    genre?: string; // 장르 필드 추가
  }
  
  export interface BookStats {
    totalBooks: number;
    averageRating: number;
    emotionDistribution: Record<string, number>;
    monthlyReads: { month: string; count: number }[];
    topReaders: { reader: string; count: number }[];
  }