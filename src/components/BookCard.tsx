import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { BookOpen, Calendar, User, Star, CheckSquare } from "lucide-react";
import { Book } from '../types/book';

interface BookCardProps {
  book: Book;
  onViewDetails: (book: Book) => void;
  onAddActionList: (book: Book) => void;
}

const emotionEmojis: Record<Book['emotion'], string> = {
  happy: '😊',
  sad: '😢',
  thoughtful: '🤔',
  excited: '🤩',
  calm: '😌',
  surprised: '😲'
};

const emotionLabels: Record<Book['emotion'], string> = {
  happy: '행복한',
  sad: '슬픈',
  thoughtful: '생각에 잠긴',
  excited: '흥미진진한',
  calm: '평온한',
  surprised: '놀란'
};

const emotionColors: Record<Book['emotion'], string> = {
  happy: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
  sad: 'bg-blue-100 text-blue-800 hover:bg-blue-200',
  thoughtful: 'bg-purple-100 text-purple-800 hover:bg-purple-200',
  excited: 'bg-orange-100 text-orange-800 hover:bg-orange-200',
  calm: 'bg-green-100 text-green-800 hover:bg-green-200',
  surprised: 'bg-pink-100 text-pink-800 hover:bg-pink-200'
};

export default function BookCard({ book, onViewDetails, onAddActionList }: BookCardProps) {
  const getEmotionColor = (emotion: string) => {
    if (emotion in emotionColors) {
      return emotionColors[emotion as keyof typeof emotionColors];
    }
    return 'bg-gray-100 text-gray-800 hover:bg-gray-200';
  };

  return (
    <Card 
      className="hover:shadow-lg transition-shadow cursor-pointer"
      onClick={() => onViewDetails(book)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <CardTitle className="text-lg font-semibold line-clamp-1 flex-1">
                {book.title}
              </CardTitle>
              <div className="flex items-center gap-2 text-sm text-muted-foreground ml-2">
                <BookOpen className="w-4 h-4" />
                <span>{book.author}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="w-4 h-4" />
              <span>{book.reader_name || '알 수 없음'}</span>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star
                key={star}
                className={`w-4 h-4 ${
                  star <= book.rating
                    ? "fill-yellow-400 text-yellow-400"
                    : "text-gray-300"
                }`}
              />
            ))}
            <span className="ml-1 text-sm text-muted-foreground">
              {book.rating}/5
            </span>
          </div>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Calendar className="w-4 h-4" />
            <span>{new Date(book.readDate).toLocaleDateString('ko-KR')}</span>
          </div>
        </div>
        
        <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
          {book.review}
        </p>
        
        {book.tags && book.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {book.tags.map((tag, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}
        
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1">
            <Badge 
              variant="secondary" 
              className={`text-xs ${getEmotionColor(book.emotion)}`}
            >
              {emotionLabels[book.emotion as keyof typeof emotionLabels] || book.emotion || '기타'}
            </Badge>
          </div>
          
          {book.presentation && (
            <div className="text-sm text-muted-foreground">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 mt-2">
                <span className="text-gray-700 line-clamp-2 text-xs">
                  {book.presentation}
                </span>
              </div>
            </div>
          )}
        </div>
        
        <div className="flex gap-2 mt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onAddActionList(book);
            }}
            className="flex-1"
          >
            <CheckSquare className="w-4 h-4 mr-2" />
            액션리스트 추가
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails(book);
            }}
            className="flex-1"
          >
            자세히 보기
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}