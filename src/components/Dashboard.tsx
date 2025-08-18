import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { BookOpen, Calendar, Star, TrendingUp, BarChart3, Heart, Trophy, Target } from "lucide-react";
import { Book } from '../types/book';

interface DashboardProps {
  books: Book[];
}

interface MonthlyData {
  month: string;
  count: number;
  fullDate: string;
}

interface QuarterlyData {
  quarter: string;
  count: number;
}

interface EmotionData {
  emotion: string;
  count: number;
  emoji: string;
}

interface GenreEmotionData {
  genre: string;
  emotions: Record<string, number>;
  totalBooks: number;
}

interface ReaderRatingData {
  reader: string;
  books: Array<{
    title: string;
    author: string;
    rating: number;
  }>;
}

const emotionEmojis = {
  happy: '😊',
  sad: '😢',
  thoughtful: '🤔',
  excited: '🤩',
  calm: '😌',
  surprised: '😲'
};

const emotionLabels = {
  happy: '기쁨',
  sad: '슬픔',
  thoughtful: '사색',
  excited: '흥분',
  calm: '평온',
  surprised: '놀람'
};

// 감정을 수치로 변환 (1-10 스케일)
// 행동력/에너지 기준: 10점(최고 행동력) → 1점(완전 무기력)
const emotionScores = {
  sad: 2,        // 슬픔: 매우 낮은 행동력, 위축됨
  calm: 4,       // 평온: 차분하지만 적극적이지 않음
  thoughtful: 6, // 사색: 내적 에너지는 있지만 외적 행동력은 중간
  surprised: 7,  // 놀람: 순간적 높은 각성도, 반응적 행동력
  happy: 8,      // 기쁨: 높은 행동력과 긍정적 에너지
  excited: 10    // 흥분: 최고 행동력, 즉각적 움직임 유발
};

export function Dashboard({ books }: DashboardProps) {
  const currentYear = new Date().getFullYear();
  
     // 기본 통계 계산
   const basicStats = useMemo(() => {
     const thisYearBooks = books.filter(book => 
       new Date(book.readDate).getFullYear() === currentYear
     );
     
     const totalThisYear = thisYearBooks.length;
     const monthlyAverage = totalThisYear / 12;
     const averageRating = books.length > 0 
       ? books.reduce((sum, book) => sum + book.rating, 0) / books.length 
       : 0;
     
     // 주요 감정 계산 (null이나 undefined 값 처리)
     const emotionCounts = books.reduce((acc, book) => {
       const emotion = book.emotion || 'unknown';
       acc[emotion] = (acc[emotion] || 0) + 1;
       return acc;
     }, {} as Record<string, number>);
     
     const topEmotion = Object.entries(emotionCounts)
       .filter(([emotion]) => emotion !== 'unknown') // unknown 제외
       .sort(([,a], [,b]) => b - a)[0];
     
     return {
       totalThisYear,
       monthlyAverage: Math.round(monthlyAverage * 10) / 10,
       averageRating: Math.round(averageRating * 10) / 10,
       topEmotion: topEmotion ? {
         emotion: topEmotion[0],
         count: topEmotion[1],
         emoji: emotionEmojis[topEmotion[0] as keyof typeof emotionEmojis] || '📖'
       } : null
     };
   }, [books, currentYear]);

  // 월별 독서량 추이
  const monthlyData = useMemo((): MonthlyData[] => {
    const monthCounts: Record<string, number> = {};
    
    books.forEach(book => {
      const date = new Date(book.readDate);
      if (date.getFullYear() === currentYear) {
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        const monthName = `${date.getMonth() + 1}월`;
        monthCounts[monthKey] = (monthCounts[monthKey] || 0) + 1;
      }
    });

    const months = [];
    for (let i = 1; i <= 12; i++) {
      const monthKey = `${currentYear}-${String(i).padStart(2, '0')}`;
      months.push({
        month: `${i}월`,
        count: monthCounts[monthKey] || 0,
        fullDate: monthKey
      });
    }
    
    return months;
  }, [books, currentYear]);

  // 분기별 독서량
  const quarterlyData = useMemo((): QuarterlyData[] => {
    const quarterCounts = [0, 0, 0, 0];
    
    books.forEach(book => {
      const date = new Date(book.readDate);
      if (date.getFullYear() === currentYear) {
        const quarter = Math.floor(date.getMonth() / 3);
        quarterCounts[quarter]++;
      }
    });

    return quarterCounts.map((count, index) => ({
      quarter: `${index + 1}분기`,
      count
    }));
  }, [books, currentYear]);

     // 감정 분포
   const emotionDistribution = useMemo((): EmotionData[] => {
     const emotionCounts = books.reduce((acc, book) => {
       const emotion = book.emotion || 'unknown';
       acc[emotion] = (acc[emotion] || 0) + 1;
       return acc;
     }, {} as Record<string, number>);

     return Object.entries(emotionCounts)
       .filter(([emotion]) => emotion !== 'unknown') // unknown 제외
       .map(([emotion, count]) => ({
         emotion: emotionLabels[emotion as keyof typeof emotionLabels] || emotion,
         count,
         emoji: emotionEmojis[emotion as keyof typeof emotionEmojis] || '📖'
       })).sort((a, b) => b.count - a.count);
   }, [books]);

     // 시간순 감정 패턴 (최근 6개월)
   const emotionPattern = useMemo(() => {
     const recent6Months = books
       .filter(book => {
         const bookDate = new Date(book.readDate);
         const sixMonthsAgo = new Date();
         sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
         return bookDate >= sixMonthsAgo && book.emotion; // emotion이 있는 책만 포함
       })
       .sort((a, b) => new Date(a.readDate).getTime() - new Date(b.readDate).getTime());

     // 중복 제거 - 동일한 책은 최신 것만 유지
     const uniqueBooks = recent6Months.filter((book, index, arr) => 
       arr.findIndex(b => b.title === book.title && b.author === book.author) === index
     );

     // 최근 10권만 선택
     const selectedBooks = uniqueBooks.slice(-10);

     return selectedBooks.map(book => ({
       title: book.title,
       emotion: book.emotion,
       emotionLabel: emotionLabels[book.emotion as keyof typeof emotionLabels] || book.emotion,
       emoji: emotionEmojis[book.emotion as keyof typeof emotionEmojis] || '📖',
       date: book.readDate,
       rating: book.rating,
       emotionScore: book.emotion_score || emotionScores[book.emotion as keyof typeof emotionScores] || 5
     }));
   }, [books]);

   // 감정 수치 그래프 데이터
   const emotionChartData = useMemo(() => {
     if (emotionPattern.length === 0) return [];
     
     return emotionPattern.map((book, index) => ({
       index: index + 1,
       title: book.title.length > 10 ? book.title.substring(0, 10) + '...' : book.title,
       score: book.emotionScore,
       emotion: book.emotion,
       emoji: book.emoji,
       date: new Date(book.date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
     }));
   }, [emotionPattern]);

     // 장르별 감정 분석
   const genreEmotionData = useMemo((): GenreEmotionData[] => {
     const genreData: Record<string, Record<string, number>> = {};
     
     books.forEach(book => {
       const genre = book.genre || '미분류';
       
       if (!genreData[genre]) {
         genreData[genre] = {};
       }
       
       if (book.emotion) {
         genreData[genre][book.emotion] = (genreData[genre][book.emotion] || 0) + 1;
       }
     });

     return Object.entries(genreData)
       .filter(([genre, emotions]) => Object.keys(emotions).length > 0) // 감정 데이터가 있는 장르만
       .map(([genre, emotions]) => ({
         genre,
         emotions,
         totalBooks: Object.values(emotions).reduce((sum, count) => sum + count, 0)
       })).sort((a, b) => b.totalBooks - a.totalBooks);
   }, [books]);

  // 독자별 별점 TOP 3
  const readerTopBooks = useMemo((): ReaderRatingData[] => {
    const readerBooks: Record<string, Book[]> = {};
    
    books.forEach(book => {
      if (!readerBooks[book.reader_name]) {
        readerBooks[book.reader_name] = [];
      }
      readerBooks[book.reader_name].push(book);
    });

    return Object.entries(readerBooks).map(([reader, readerBookList]) => {
      const topBooks = readerBookList
        .sort((a, b) => b.rating - a.rating)
        .slice(0, 3)
        .map(book => ({
          title: book.title,
          author: book.author,
          rating: book.rating
        }));

      return { reader, books: topBooks };
    });
  }, [books]);

  const maxMonthlyCount = Math.max(...monthlyData.map(d => d.count), 1);

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div>
        <h2 className="text-3xl font-bold mb-2">📊 독서 대시보드</h2>
        <p className="text-muted-foreground">
          나의 독서 여정을 한눈에 살펴보세요
        </p>
      </div>

      {/* 기본 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-700">올해 읽은 책</p>
                <p className="text-2xl font-bold text-blue-900">{basicStats.totalThisYear}권</p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-700">월 평균</p>
                <p className="text-2xl font-bold text-green-900">{basicStats.monthlyAverage}권</p>
              </div>
              <Calendar className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-700">평균 별점</p>
                <p className="text-2xl font-bold text-yellow-900">{basicStats.averageRating}점</p>
              </div>
              <Star className="w-8 h-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-700">주요 감정</p>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{basicStats.topEmotion?.emoji}</span>
                  <span className="text-lg font-bold text-purple-900">
                    {emotionLabels[basicStats.topEmotion?.emotion as keyof typeof emotionLabels] || '없음'}
                  </span>
                </div>
              </div>
              <Heart className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 월별 독서량 추이 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              월별 독서량 추이 ({currentYear}년)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {monthlyData.map((data) => (
                <div key={data.month} className="flex items-center gap-3">
                  <span className="w-8 text-sm font-medium">{data.month}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                    <div 
                      className="bg-blue-500 h-6 rounded-full flex items-center justify-end pr-2"
                      style={{ width: `${(data.count / maxMonthlyCount) * 100}%` }}
                    >
                      {data.count > 0 && (
                        <span className="text-white text-xs font-medium">{data.count}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 분기별 독서량 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              분기별 독서량 ({currentYear}년)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {quarterlyData.map((data, index) => (
                <div key={data.quarter} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{data.count}</div>
                  <div className="text-sm text-muted-foreground">{data.quarter}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

                 {/* 감정 수치 변화 그래프 (전체 너비) */}
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="w-5 h-5" />
          감정 수치 변화 그래프
        </CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          독서 후 감정의 행동력을 수치로 확인해보세요 (1점: 무기력 → 10점: 최고 행동력)
        </p>
      </CardHeader>
         <CardContent>
           {emotionChartData.length === 0 ? (
             <div className="text-center py-8 text-muted-foreground">
               감정 데이터가 충분하지 않습니다
             </div>
           ) : (
             <div className="space-y-6">
                           {/* 행동력 범례 */}
            <div className="flex items-center justify-between text-xs text-muted-foreground border-b pb-2">
              <span>무기력/위축 (1-3)</span>
              <span>차분/사색 (4-6)</span>
              <span>활발/적극적 (7-10)</span>
            </div>
               
                           {/* 감정 그래프 */}
            <div className="space-y-4">
              {emotionChartData.length > 1 ? (
                <>
                  {/* 그래프 영역 */}
                  <div className="relative h-64 bg-gray-50 rounded-lg p-4">
                    <svg viewBox="0 0 1000 200" className="w-full h-full">
                      {/* Y축 격자선과 레이블 */}
                      {[2, 4, 6, 8, 10].map((score) => (
                        <g key={score}>
                          <line
                            x1="50"
                            y1={180 - (score / 10) * 160}
                            x2="950"
                            y2={180 - (score / 10) * 160}
                            stroke="#e5e7eb"
                            strokeWidth="1"
                            strokeDasharray="3,3"
                          />
                          <text
                            x="35"
                            y={180 - (score / 10) * 160 + 4}
                            textAnchor="end"
                            fontSize="12"
                            fill="#6b7280"
                          >
                            {score}
                          </text>
                        </g>
                      ))}
                      
                      {/* 감정 라인 */}
                      <polyline
                        fill="none"
                        stroke="#3b82f6"
                        strokeWidth="4"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        points={emotionChartData.map((point, index) => {
                          const x = 50 + (index / (emotionChartData.length - 1)) * 900;
                          const y = 180 - (point.score / 10) * 160;
                          return `${x},${y}`;
                        }).join(' ')}
                      />
                      
                      {/* 감정 포인트와 이모지 */}
                      {emotionChartData.map((point, index) => {
                        const x = 50 + (index / (emotionChartData.length - 1)) * 900;
                        const y = 180 - (point.score / 10) * 160;
                        return (
                          <g key={index}>
                            {/* 포인트 원 */}
                            <circle
                              cx={x}
                              cy={y}
                              r="6"
                              fill="#3b82f6"
                              stroke="white"
                              strokeWidth="2"
                            />
                            {/* 이모지 */}
                            <text
                              x={x}
                              y={y - 15}
                              textAnchor="middle"
                              fontSize="16"
                            >
                              {point.emoji}
                            </text>
                            {/* X축 날짜 */}
                            <text
                              x={x}
                              y="195"
                              textAnchor="middle"
                              fontSize="10"
                              fill="#6b7280"
                            >
                              {point.date}
                            </text>
                          </g>
                        );
                      })}
                    </svg>
                  </div>
                  
                  {/* 하단 책 정보 */}
                  <div className="grid gap-2 text-xs" style={{gridTemplateColumns: `repeat(${emotionChartData.length}, 1fr)`}}>
                    {emotionChartData.map((point, index) => {
                      const emotionData = emotionPattern[index];
                      return (
                        <div key={index} className="text-center p-2 bg-white rounded border">
                          <div className="font-medium truncate mb-1">{point.title}</div>
                          <div className="flex items-center justify-center gap-1">
                            <span className="text-base">{emotionData?.emoji || '📖'}</span>
                            <span className="text-blue-600 font-semibold text-xs">
                              {emotionData?.emotionLabel || '감정없음'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-center h-64 text-muted-foreground bg-gray-50 rounded-lg">
                  충분한 데이터가 없습니다 (최소 2개 필요)
                </div>
              )}
            </div>
               
             </div>
           )}
         </CardContent>
       </Card>

      {/* 장르별 감정 분석 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            장르별 감정 분석
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {genreEmotionData.map((genreData) => (
              <div key={genreData.genre} className="p-4 border rounded-lg">
                <div className="font-semibold mb-2">{genreData.genre}</div>
                <div className="text-sm text-muted-foreground mb-3">총 {genreData.totalBooks}권</div>
                                 <div className="space-y-1">
                   {Object.entries(genreData.emotions).map(([emotion, count]) => (
                     <div key={emotion} className="flex items-center justify-between text-sm">
                       <span className="flex items-center gap-2">
                         <span className="text-base">{emotionEmojis[emotion as keyof typeof emotionEmojis] || '📖'}</span>
                         <span className="font-medium">{emotionLabels[emotion as keyof typeof emotionLabels] || emotion}</span>
                       </span>
                       <Badge variant="outline" className="text-xs">
                         {count}권
                       </Badge>
                     </div>
                   ))}
                 </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 독자별 별점 TOP 3 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="w-5 h-5" />
            독자별 별점 TOP 3
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {readerTopBooks.map((readerData) => (
              <div key={readerData.reader} className="space-y-3">
                <h3 className="font-semibold text-lg">{readerData.reader}</h3>
                <div className="space-y-2">
                  {readerData.books.map((book, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-start justify-between mb-1">
                        <div className="font-medium text-sm truncate pr-2">{book.title}</div>
                        <div className="flex items-center gap-1 shrink-0">
                          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm font-medium">{book.rating}</span>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground">{book.author}</div>
                      {index === 0 && (
                        <Badge className="mt-1 text-xs bg-yellow-100 text-yellow-800">1위</Badge>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}