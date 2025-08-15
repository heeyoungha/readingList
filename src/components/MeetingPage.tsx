import { Book } from "../types/book";
import BookCard from "./BookCard";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Users, Calendar, Clock, BookOpen } from "lucide-react";

interface MeetingPageProps {
  books: Book[];
  onBookClick: (book: Book) => void;
  onAddActionList: (book: Book) => void;
}

export function MeetingPage({ books, onBookClick, onAddActionList }: MeetingPageProps) {
  // 각 독자별로 가장 최근 독후감을 찾기
  const getRecentBooksByReader = () => {
    const readerBooks: Record<string, Book> = {};
    
    books.forEach(book => {
      const currentBook = readerBooks[book.reader_name];
      if (!currentBook || new Date(book.readDate) > new Date(currentBook.readDate)) {
        readerBooks[book.reader_name] = book;
      }
    });
    
    return Object.values(readerBooks).sort((a, b) => 
      new Date(b.readDate).getTime() - new Date(a.readDate).getTime()
    );
  };

  const recentBooks = getRecentBooksByReader();
  
  // 다음 모임 날짜 계산 (예시: 매월 첫째, 셋째 주 토요일)
  const getNextMeetingDate = () => {
    const today = new Date();
    const nextSaturday = new Date();
    nextSaturday.setDate(today.getDate() + (6 - today.getDay()));
    return nextSaturday;
  };

  const nextMeeting = getNextMeetingDate();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="mb-2">독서 모임</h2>
        <p className="text-muted-foreground">
          2주마다 진행되는 독서 모임을 위한 참여자들의 최근 독후감
        </p>
      </div>

      {/* 모임 정보 카드 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            다음 모임 정보
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">다음 모임</p>
                <p>{nextMeeting.toLocaleDateString('ko-KR', { 
                  month: 'long', 
                  day: 'numeric',
                  weekday: 'long'
                })}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">참여자</p>
                <p>{recentBooks.length}명</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">논의할 책</p>
                <p>{recentBooks.length}권</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 참여자별 최근 독후감 */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="mb-1">참여자별 최근 독후감</h3>
            <p className="text-muted-foreground text-sm">
              각 참여자가 가장 최근에 읽은 책의 독후감입니다
            </p>
          </div>
          <Badge variant="secondary" className="flex items-center gap-1">
            <Users className="w-3 h-3" />
            {recentBooks.length}명 참여
          </Badge>
        </div>

        {recentBooks.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="mb-2">아직 등록된 독후감이 없습니다</h3>
            <p className="text-muted-foreground mb-4">
              독후감을 등록하면 모임 페이지에 자동으로 표시됩니다
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {recentBooks.map((book) => (
              <div key={book.id} className="relative">
                <BookCard
                  book={book}
                  onViewDetails={onBookClick}
                  onAddActionList={onAddActionList}
                />
                <Badge 
                  variant="default" 
                  className="absolute -top-2 -right-2 bg-black text-white"
                >
                  최신
                </Badge>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 모임 가이드 */}
      <Card>
        <CardHeader>
          <CardTitle>📚 모임 진행 가이드</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="mb-2">💬 토론 주제</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• 책의 핵심 메시지와 인상 깊었던 부분</li>
                <li>• 개인적인 감정과 느낌 공유</li>
                <li>• 일상에 적용할 수 있는 교훈</li>
                <li>• 다른 참여자들에게 추천하고 싶은 이유</li>
              </ul>
            </div>
            
            <div>
              <h4 className="mb-2">⏰ 진행 방식</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• 참여자별 5-10분 발표</li>
                <li>• 자유로운 질문과 토론</li>
                <li>• 서로의 독서 경험 공유</li>
                <li>• 다음 모임까지 읽을 책 추천</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}