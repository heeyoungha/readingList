import { Book } from "../types/book";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Star, User, Calendar, Tag, ExternalLink, Quote, BookOpen, Heart } from "lucide-react";
import { Separator } from "./ui/separator";

interface BookDetailModalProps {
  book: Book | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BookDetailModal({ book, open, onOpenChange }: BookDetailModalProps) {
  if (!book) return null;

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

          {/* 장르와 구매링크 2줄 배치 */}
          {(book.genre || book.purchaseLink) && (
            <>
              <Separator />
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  {book.genre && (
                    <div className="flex items-center gap-2">
                      <BookOpen className="w-4 h-4 text-muted-foreground" />
                      <span className="text-muted-foreground">장르:</span>
                      <Badge variant="outline" className="text-xs">
                        {book.genre}
                      </Badge>
                    </div>
                  )}
                </div>
                <div>
                  {book.purchaseLink && (
                    <div className="flex items-center gap-2">
                      <ExternalLink className="w-4 h-4 text-muted-foreground" />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(book.purchaseLink, '_blank')}
                        className="h-6 px-2 text-xs"
                      >
                        구매 페이지
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {/* 한줄평 */}
          {book.oneLiner && (
            <>
              <Separator />
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Quote className="w-4 h-4" />
                  <h4>한줄평</h4>
                </div>
                <div className="bg-blue-50 border-l-4 border-blue-200 rounded p-3">
                  <p className="text-blue-800 italic">
                    "{book.oneLiner}"
                  </p>
                </div>
              </div>
            </>
          )}

          {/* 고르게 된 계기 */}
          {book.motivation && (
            <>
              <Separator />
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Heart className="w-4 h-4" />
                  <h4>고르게 된 계기</h4>
                </div>
                <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {book.motivation}
                </p>
              </div>
            </>
          )}

          {/* 기억에 남는 구절 */}
          {book.memorableQuotes && book.memorableQuotes.length > 0 && (
            <>
              <Separator />
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Quote className="w-4 h-4" />
                  <h4>기억에 남는 구절</h4>
                </div>
                <div className="space-y-3">
                  {book.memorableQuotes.map((quote, index) => (
                    <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                      <p className="text-gray-700 leading-relaxed whitespace-pre-wrap italic">
                        "{quote}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
          
          <Separator />
          
          <div>
            <h4 className="mb-2">느낀점</h4>
            <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
              {book.review}
            </p>
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