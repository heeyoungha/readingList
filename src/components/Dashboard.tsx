import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { BookOpen, Calendar, Star, TrendingUp, BarChart3, Target, Trophy, BookmarkIcon } from "lucide-react";
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

interface GenreData {
  genre: string;
  count: number;
  averageRating: number;
}

interface ReaderRatingData {
  reader: string;
  books: Array<{
    title: string;
    author: string;
    rating: number;
  }>;
}

interface ReadingPatternData {
  title: string;
  author: string;
  date: string;
  rating: number;
  genre: string;
}

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
    
    // 가장 많이 읽은 장르 계산
    const genreCounts = books.reduce((acc, book) => {
      const genre = book.genre || '미분류';
      acc[genre] = (acc[genre] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const topGenre = Object.entries(genreCounts)
      .sort(([,a], [,b]) => b - a)[0];
    
    return {
      totalThisYear,
      monthlyAverage: Math.round(monthlyAverage * 10) / 10,
      averageRating: Math.round(averageRating * 10) / 10,
      topGenre: topGenre ? {
        genre: topGenre[0],
        count: topGenre[1]
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

  // 장르별 분포
  const genreDistribution = useMemo((): GenreData[] => {
    const genreStats = books.reduce((acc, book) => {
      const genre = book.genre || '미분류';
      
      if (!acc[genre]) {
        acc[genre] = { totalBooks: 0, totalRating: 0 };
      }
      
      acc[genre].totalBooks++;
      acc[genre].totalRating += book.rating;
      
      return acc;
    }, {} as Record<string, { totalBooks: number; totalRating: number }>);

    return Object.entries(genreStats)
      .map(([genre, stats]) => ({
        genre,
        count: stats.totalBooks,
        averageRating: Math.round((stats.totalRating / stats.totalBooks) * 10) / 10
      }))
      .sort((a, b) => b.count - a.count);
  }, [books]);

  // 최근 독서 패턴 (최근 10권)
  const recentReadingPattern = useMemo((): ReadingPatternData[] => {
    const recentBooks = books
      .filter(book => {
        const bookDate = new Date(book.readDate);
        const threeMonthsAgo = new Date();
        threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
        return bookDate >= threeMonthsAgo;
      })
      .sort((a, b) => new Date(b.readDate).getTime() - new Date(a.readDate).getTime())
      .slice(0, 10);

    return recentBooks.map(book => ({
      title: book.title,
      author: book.author,
      date: book.readDate,
      rating: book.rating,
      genre: book.genre || '미분류'
    }));
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
                <p className="text-sm font-medium text-purple-700">선호 장르</p>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-purple-900">
                    {basicStats.topGenre?.genre || '없음'}
                  </span>
                </div>
                {basicStats.topGenre && (
                  <p className="text-xs text-purple-600">{basicStats.topGenre.count}권</p>
                )}
              </div>
              <BookmarkIcon className="w-8 h-8 text-purple-600" />
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

      {/* 장르별 분포 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            장르별 독서 분포
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {genreDistribution.map((genreData) => (
              <div key={genreData.genre} className="p-4 border rounded-lg">
                <div className="font-semibold mb-2">{genreData.genre}</div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-muted-foreground">총 {genreData.count}권</div>
                    <div className="flex items-center gap-1 mt-1">
                      <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm font-medium">{genreData.averageRating}점</span>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-lg px-3 py-1">
                    {genreData.count}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 최근 독서 패턴 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            최근 독서 패턴 (최근 3개월)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recentReadingPattern.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              최근 독서 데이터가 없습니다
            </div>
          ) : (
            <div className="space-y-3">
              {recentReadingPattern.map((book, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium">{book.title}</div>
                    <div className="text-sm text-muted-foreground">
                      {book.author} • {book.genre}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <span className="text-muted-foreground">
                      {new Date(book.date).toLocaleDateString('ko-KR')}
                    </span>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className="font-medium">{book.rating}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
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