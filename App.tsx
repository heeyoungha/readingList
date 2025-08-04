import { useState } from "react";
import { Book } from "./types/book";
import { BookCard } from "./components/BookCard";
import { BookDetailModal } from "./components/BookDetailModal";
import { AddBookForm } from "./components/AddBookForm";
import { Dashboard } from "./components/Dashboard";
import { MeetingPage } from "./components/MeetingPage";
import { Navigation } from "./components/Navigation";
import { BookOpen } from "lucide-react";

// Sample data
const sampleBooks: Book[] = [
  {
    id: "1",
    title: "코스모스",
    author: "칼 세이건",
    reader: "김독서",
    review: "우주에 대한 경이로움과 과학적 사고의 중요성을 깨닫게 해준 책입니다. 세이건의 시적인 문체로 복잡한 과학 개념들을 쉽게 설명해주어 과학에 대한 흥미를 불러일으켰습니다.",
    rating: 5,
    emotion: "excited",
    readDate: "2024-01-15",
    tags: ["과학", "우주", "철학"]
  },
  {
    id: "2", 
    title: "82년생 김지영",
    author: "조남주",
    reader: "이북러버",
    review: "현대 여성이 겪는 현실적인 문제들을 담담하게 그려낸 작품입니다. 읽으면서 많은 생각을 하게 되었고, 우리 사회에 대해 돌아보는 계기가 되었습니다.",
    rating: 4,
    emotion: "thoughtful",
    readDate: "2024-01-28",
    tags: ["소설", "여성", "사회"]
  },
  {
    id: "3",
    title: "미움받을 용기",
    author: "기시미 이치로, 고가 후미타케",
    reader: "박철학",
    review: "아들러 심리학을 바탕으로 한 대화형식의 책입니다. 타인의 시선에서 벗어나 자신만의 삶을 살아가는 것의 중요성을 배웠습니다. 실천하기는 어렵지만 좋은 방향을 제시해주는 책이었습니다.",
    rating: 4,
    emotion: "calm",
    readDate: "2024-02-10",
    tags: ["자기계발", "심리학", "철학"]
  },
  {
    id: "4",
    title: "호모 사피엔스",
    author: "유발 하라리",
    reader: "정역사",
    review: "인류의 역사를 새로운 관점에서 바라본 흥미진진한 책입니다. 인지혁명, 농업혁명, 과학혁명을 통해 인류가 어떻게 발전해왔는지 명확하게 설명해줍니다.",
    rating: 5,
    emotion: "surprised",
    readDate: "2024-02-25",
    tags: ["역사", "인류학", "철학"]
  },
  {
    id: "5",
    title: "원피스 1권",
    author: "오다 에이치로",
    reader: "김독서",
    review: "루피의 모험이 시작되는 첫 번째 권입니다. 꿈을 향한 열정과 동료애의 소중함을 느낄 수 있었습니다. 만화지만 깊은 메시지가 담겨있어 감동적이었습니다.",
    rating: 4,
    emotion: "excited",
    readDate: "2024-03-05",
    tags: ["만화", "모험", "우정"]
  },
  {
    id: "6",
    title: "데미안",
    author: "헤르만 헤세",
    reader: "이북러버",
    review: "자아 찾기와 성장에 대한 깊은 통찰을 제공하는 작품입니다. 싱클레어의 내적 갈등과 성장 과정이 현재의 나와 많이 닮아있어 공감이 되었습니다.",
    rating: 5,
    emotion: "thoughtful",
    readDate: "2024-03-12",
    tags: ["소설", "성장", "철학"]
  }
];

export default function App() {
  const [books, setBooks] = useState<Book[]>(sampleBooks);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [currentPage, setCurrentPage] = useState<'books' | 'dashboard' | 'meeting'>('books');

  const handleAddBook = (newBookData: Omit<Book, 'id'>) => {
    const newBook: Book = {
      ...newBookData,
      id: Date.now().toString()
    };
    setBooks(prev => [newBook, ...prev]);
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'books':
        return (
          <div>
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="mb-2">독후감 모음</h2>
                <p className="text-muted-foreground">
                  총 {books.length}개의 독후감이 있습니다
                </p>
              </div>
              
              <AddBookForm onAddBook={handleAddBook} />
            </div>
            
            {books.length === 0 ? (
              <div className="text-center py-12">
                <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="mb-2">아직 등록된 독후감이 없습니다</h3>
                <p className="text-muted-foreground mb-4">
                  첫 번째 독후감을 추가해보세요!
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {books.map((book) => (
                  <BookCard
                    key={book.id}
                    book={book}
                    onClick={() => setSelectedBook(book)}
                  />
                ))}
              </div>
            )}
          </div>
        );
      
      case 'meeting':
        return (
          <MeetingPage 
            books={books} 
            onBookClick={(book) => setSelectedBook(book)} 
          />
        );
      
      case 'dashboard':
        return <Dashboard books={books} />;
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      
      <main className="container mx-auto px-4 py-8">
        {renderCurrentPage()}
        
        <BookDetailModal
          book={selectedBook}
          open={!!selectedBook}
          onOpenChange={(open) => !open && setSelectedBook(null)}
        />
      </main>
    </div>
  );
}