import { Book } from "../types/book";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Badge } from "./ui/badge";
import { Star, User, Calendar, Tag } from "lucide-react";
import { Separator } from "./ui/separator";

interface BookDetailModalProps {
  book: Book | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
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

export function BookDetailModal({ book, open, onOpenChange }: BookDetailModalProps) {
  if (!book) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto bg-white">
        <DialogHeader>
          <DialogTitle className="text-xl">{book.title}</DialogTitle>
          <p className="text-muted-foreground">by {book.author}</p>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${
                      i < book.rating 
                        ? "fill-yellow-400 text-yellow-400" 
                        : "text-gray-300"
                    }`}
                  />
                ))}
                <span className="ml-1">{book.rating}/5</span>
              </div>
              
              <Badge 
                variant="secondary" 
                className={`${emotionColors[book.emotion]}`}
              >
                {emotionEmojis[book.emotion]} 
                {book.emotion === 'happy' && '행복한'}
                {book.emotion === 'sad' && '슬픈'}
                {book.emotion === 'thoughtful' && '생각이 많아지는'}
                {book.emotion === 'excited' && '흥미진진한'}
                {book.emotion === 'calm' && '차분한'}
                {book.emotion === 'surprised' && '놀라운'}
              </Badge>
            </div>
          </div>
          
          <Separator />
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">독자:</span>
              <span>{book.reader}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">읽은 날:</span>
              <span>{new Date(book.readDate).toLocaleDateString('ko-KR')}</span>
            </div>
          </div>
          
          <Separator />
          
          <div>
            <h4 className="mb-2">독후감</h4>
            <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
              {book.review}
            </p>
          </div>
          
          {book.tags.length > 0 && (
            <>
              <Separator />
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Tag className="w-4 h-4" />
                  <h4>태그</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {book.tags.map((tag, index) => (
                    <Badge key={index} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}