import { Book } from "../types/book";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";

import { BookOpen, Users, Star, TrendingUp } from "lucide-react";

interface DashboardProps {
  books: Book[];
}

const emotionEmojis = {
  happy: "😊",
  sad: "😢", 
  thoughtful: "🤔",
  excited: "😄",
  calm: "😌",
  surprised: "😲"
};

const emotionLabels = {
  happy: "행복한",
  sad: "슬픈", 
  thoughtful: "생각이 많아지는",
  excited: "흥미진진한",
  calm: "차분한",
  surprised: "놀라운"
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

export function Dashboard({ books }: DashboardProps) {
  // Calculate statistics
  const totalBooks = books.length;
  const averageRating = totalBooks > 0 
    ? (books.reduce((sum, book) => sum + book.rating, 0) / totalBooks).toFixed(1)
    : "0";
  
  // Emotion distribution
  const emotionDistribution = books.reduce((acc, book) => {
    acc[book.emotion] = (acc[book.emotion] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const emotionChartData = Object.entries(emotionDistribution).map(([emotion, count]) => ({
    name: emotionLabels[emotion as keyof typeof emotionLabels],
    value: count,
    emoji: emotionEmojis[emotion as keyof typeof emotionEmojis]
  }));
  
  // Top readers
  const readerStats = books.reduce((acc, book) => {
    acc[book.reader] = (acc[book.reader] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const topReaders = Object.entries(readerStats)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5)
    .map(([reader, count]) => ({ reader, count }));
  
  // Monthly reads (last 6 months)
  const monthlyReads = books.reduce((acc, book) => {
    const date = new Date(book.readDate);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    acc[monthKey] = (acc[monthKey] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const monthlyChartData = Object.entries(monthlyReads)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-6)
    .map(([month, count]) => ({
      month: new Date(month + '-01').toLocaleDateString('ko-KR', { month: 'short' }),
      count
    }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="mb-2">대시보드</h2>
        <p className="text-muted-foreground">
          독서 통계와 현황을 한눈에 확인하세요
        </p>
      </div>
      
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">총 독후감</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{totalBooks}</div>
            <p className="text-xs text-muted-foreground">
              등록된 독후감 수
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">참여자</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{Object.keys(readerStats).length}</div>
            <p className="text-xs text-muted-foreground">
              독서에 참여한 사람 수
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">평균 평점</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{averageRating}</div>
            <p className="text-xs text-muted-foreground">
              5점 만점 기준
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">이번 달</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">
              {books.filter(book => {
                const bookDate = new Date(book.readDate);
                const now = new Date();
                return bookDate.getMonth() === now.getMonth() && 
                       bookDate.getFullYear() === now.getFullYear();
              }).length}
            </div>
            <p className="text-xs text-muted-foreground">
              이번 달 독후감
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>월별 독서량</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="w-full h-[300px] flex items-end justify-between p-4 bg-muted rounded-lg">
              {monthlyChartData.map((item, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div 
                    className="bg-primary rounded-t"
                    style={{ 
                      height: `${(item.count / Math.max(...monthlyChartData.map(d => d.count))) * 200}px`,
                      width: '20px'
                    }}
                  />
                  <span className="text-xs mt-2">{item.month}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>감정 분포</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="w-full h-[300px] flex items-center justify-center">
              <div className="grid grid-cols-2 gap-4">
                {emotionChartData.map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div 
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    <span className="text-sm">{item.name}</span>
                    <span className="text-sm text-muted-foreground">
                      {((item.value / emotionChartData.reduce((sum, d) => sum + d.value, 0)) * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Top Readers */}
      <Card>
        <CardHeader>
          <CardTitle>독서왕 순위</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topReaders.map((reader, index) => (
              <div key={reader.reader} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge variant={index === 0 ? "default" : "secondary"}>
                    #{index + 1}
                  </Badge>
                  <span>{reader.reader}</span>
                </div>
                <Badge variant="outline">
                  {reader.count}권
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}