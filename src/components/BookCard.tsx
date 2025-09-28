import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { BookOpen, Calendar, User, Star, CheckSquare, ExternalLink, Quote } from "lucide-react";
import { Book } from '../types/book';

interface BookCardProps {
  book: Book;
  onViewDetails: (book: Book) => void;
  onAddActionList?: (book: Book) => void;
}

export default function BookCard({ book, onViewDetails, onAddActionList }: BookCardProps) {
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

        {/* 장르 표시 */}
        {book.genre && (
          <div className="mb-2">
            <Badge variant="outline" className="text-xs">
              {book.genre}
            </Badge>
          </div>
        )}

        {/* 한줄평 표시 */}
        {book.oneLiner && (
          <div className="mb-3 p-2 bg-blue-50 border-l-4 border-blue-200 rounded">
            <div className="flex items-start gap-2">
              <Quote className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-blue-800 italic line-clamp-2">
                {book.oneLiner}
              </p>
            </div>
          </div>
        )}
        
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
        
        {book.presentation && (
          <div className="text-sm text-muted-foreground mb-3">
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-2">
              <span className="text-gray-700 line-clamp-2 text-xs">
                {book.presentation}
              </span>
            </div>
          </div>
        )}
        
        <div className="mt-auto pt-3 flex justify-center">
          {/* <Button
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
           */}
          {book.purchaseLink ? (
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                window.open(book.purchaseLink, '_blank');
              }}
              className="w-4/5"
            > 구매링크 바로가기
              <ExternalLink className="w-4 h-4 mr-2" />
            </Button>
          ) : (
            <div className="text-center text-sm text-muted-foreground py-2">
              구매 링크 없음
            </div>
          )}
          
          {/* <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails(book);
            }}
            className="flex-1"
          >
            자세히 보기
          </Button> */}
        </div>
      </CardContent>
    </Card>
  );
}