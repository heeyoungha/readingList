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

const emotionLabels = {
  happy: "행복한",
  sad: "슬픈",
  thoughtful: "생각에 잠긴",
  excited: "흥미진진한",
  calm: "평온한",
  surprised: "놀란"
};

const emotionColors = {
  happy: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
  sad: 'bg-blue-100 text-blue-800 hover:bg-blue-200',
  thoughtful: 'bg-purple-100 text-purple-800 hover:bg-purple-200',
  excited: 'bg-orange-100 text-orange-800 hover:bg-orange-200',
  calm: 'bg-green-100 text-green-800 hover:bg-green-200',
  surprised: 'bg-pink-100 text-pink-800 hover:bg-pink-200'
};

export function BookDetailModal({ book, open, onOpenChange }: BookDetailModalProps) {
  if (!book) return null;
  
  const getEmotionColor = (emotion: string) => {
    if (emotion in emotionColors) {
      return emotionColors[emotion as keyof typeof emotionColors];
    }
    return 'bg-gray-100 text-gray-800 hover:bg-gray-200';
  };
  


  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto bg-white">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl">{book.title}</DialogTitle>
            <p className="text-muted-foreground">by {book.author}</p>
          </div>
        </DialogHeader>
        
        <div className="space-y-4">
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
          </div>
          
          <Separator />
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">독자:</span>
              <span>{book.reader_name || '알 수 없음'}</span>
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
          
          <Separator />
          
          <div>
            <h4 className="mb-2">감정</h4>
            <Badge 
              variant="secondary" 
              className={`text-sm ${getEmotionColor(book.emotion)}`}
            >
              {emotionLabels[book.emotion as keyof typeof emotionLabels] || book.emotion || '기타'}
            </Badge>
          </div>
          
          {book.presentation && (
            <>
              <Separator />
              <div>
                <h4 className="mb-2">발제문</h4>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {book.presentation}
                  </p>
                </div>
              </div>
            </>
          )}
          
          {book.tags && book.tags.length > 0 && (
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