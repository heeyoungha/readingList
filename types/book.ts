export interface Book {
    id: string;
    title: string;
    author: string;
    reader: string;
    review: string;
    rating: number; // 1-5
    emotion: 'happy' | 'sad' | 'thoughtful' | 'excited' | 'calm' | 'surprised';
    readDate: string;
    coverImage?: string;
    tags: string[];
  }
  
  export interface BookStats {
    totalBooks: number;
    averageRating: number;
    emotionDistribution: Record<string, number>;
    monthlyReads: { month: string; count: number }[];
    topReaders: { reader: string; count: number }[];
  }