export interface Book {
    id: string;
    title: string;
    author: string;
    reader_id: string;
    reader_name: string; // 독자 이름을 표시하기 위한 필드
    review: string;
    presentation?: string; // 발제문 (선택사항)
    rating: number; // 1-5
    readDate: string;
    coverImage?: string;
    tags: string[];
    genre?: string; // 장르 필드
    purchaseLink?: string; // 구매 링크
    oneLiner?: string; // 한줄평
    motivation?: string; // 고르게 된 계기
    memorableQuotes?: string[]; // 기억에 남는 구절들
}

export interface BookStats {
    totalBooks: number;
    averageRating: number;
    emotionDistribution: Record<string, number>;
    monthlyReads: { month: string; count: number }[];
    topReaders: { reader: string; count: number }[];
}