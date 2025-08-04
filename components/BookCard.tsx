import { Book } from "../types/book";
import { Card, CardContent, CardHeader } from "./ui/card";
import { Badge } from "./ui/badge";
import { Star, User, Calendar } from "lucide-react";

interface BookCardProps {
  book: Book;
  onClick: () => void;
}

const emotionEmojis = {
  happy: "😊",
  sad: "😢", 
  thoughtful: "🤔",
  excited: "😄",
  calm: "😌",
  surprised: "😲"
};

const emotionColors = {
  happy: "bg-yellow-100 text-yellow-800",
  sad: "bg-blue-100 text-blue-800",
  thoughtful: "bg-purple-100 text-purple-800", 
  excited: "bg-orange-100 text-orange-800",
  calm: "bg-green-100 text-green-800",
  surprised: "bg-pink-100 text-pink-800"
};

export function BookCard({ book, onClick }: BookCardProps) {
  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-shadow duration-200 h-full"
      onClick={onClick}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="line-clamp-2 mb-1">{book.title}</h3>
            <p className="text-muted-foreground text-sm">by {book.author}</p>
          </div>
          <Badge 
            variant="secondary" 
            className={`ml-2 ${emotionColors[book.emotion]}`}
          >
            {emotionEmojis[book.emotion]}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        <div className="flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              className={`w-4 h-4 ${
                i < book.rating 
                  ? "fill-yellow-400 text-yellow-400" 
                  : "text-gray-300"
              }`}
            />
          ))}
          <span className="text-sm text-muted-foreground ml-1">
            {book.rating}/5
          </span>
        </div>
        
        <p className="text-sm line-clamp-3 text-muted-foreground">
          {book.review}
        </p>
        
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <User className="w-3 h-3" />
            {book.reader}
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {new Date(book.readDate).toLocaleDateString('ko-KR')}
          </div>
        </div>
        
        {book.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {book.tags.slice(0, 3).map((tag, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
            {book.tags.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{book.tags.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}