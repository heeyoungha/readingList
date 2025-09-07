import { useState, useEffect } from "react";
import { Book } from "./types/book";
import { ActionList } from "./types/actionList";
import BookCard from "./components/BookCard";
import { BookDetailModal } from "./components/BookDetailModal";
import AddBookForm from "./components/AddBookForm";
import { Dashboard } from "./components/Dashboard";
import { MeetingPage } from "./components/MeetingPage";
import { ActionListPage } from "./components/ActionListPage";
import { PersonaChatbot } from "./components/PersonaChatbot";
import { Navigation } from "./components/Navigation";
import { BookOpen } from "lucide-react";
import { getBooks, addBook, getActionLists, addActionList } from "./lib/database";

export default function App() {
  const [books, setBooks] = useState<Book[]>([]);
  const [actionLists, setActionLists] = useState<ActionList[]>([]);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [currentPage, setCurrentPage] = useState<'books' | 'dashboard' | 'meeting' | 'actions' | 'persona'>('books');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 데이터 로드
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [booksData, actionListsData] = await Promise.all([
        getBooks(),
        getActionLists()
      ]);
      setBooks(booksData);
      setActionLists(actionListsData);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddBook = async (newBookData: Omit<Book, 'id' | 'reader_name'>) => {
    try {
      const addedBook = await addBook(newBookData);
      setBooks(prev => [addedBook, ...prev]);
    } catch (err) {
      console.error('Error adding book:', err);
      alert('책을 추가하는데 실패했습니다.');
    }
  };

  const handleAddActionList = async (newActionData: Omit<ActionList, 'id' | 'reader_name' | 'created_at' | 'updated_at'>) => {
    try {
      const addedActionList = await addActionList(newActionData);
      setActionLists(prev => [addedActionList, ...prev]);
    } catch (err) {
      console.error('Error adding action list:', err);
      alert('액션리스트를 추가하는데 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-destructive mb-4">{error}</p>
          <button 
            onClick={loadData}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

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
                    onViewDetails={() => setSelectedBook(book)}
                    onAddActionList={(book) => {
                      const newActionList: Omit<ActionList, 'id' | 'reader_name' | 'created_at' | 'updated_at'> = {
                        title: `${book.title}에서 배운 실천사항`,
                        reader_id: book.reader_id,
                        book_title: book.title,
                        content: '책에서 배운 내용을 실천해보세요.',
                        target_months: [new Date().toLocaleDateString('ko-KR', { month: 'long' })],
                        action_time: '매일 아침',
                        status: '진행전'
                      };
                      handleAddActionList(newActionList);
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        );
      
      case 'actions':
        return (
          <ActionListPage 
            actionLists={actionLists}
            onViewActionList={() => {}} // TODO: Implement action list detail view
            onAddActionList={() => {
              const newActionList: Omit<ActionList, 'id' | 'reader_name' | 'created_at' | 'updated_at'> = {
                title: '새로운 액션리스트',
                reader_id: books[0]?.reader_id || 'default',
                book_title: books[0]?.title || '기본 책',
                content: '새로운 실천 내용을 입력하세요.',
                target_months: [new Date().toLocaleDateString('ko-KR', { month: 'long' })],
                action_time: '매일 아침',
                status: '진행전'
              };
              handleAddActionList(newActionList);
            }}
          />
        );
      
      case 'meeting':
        return (
          <MeetingPage 
            books={books} 
            onBookClick={(book) => setSelectedBook(book)}
            onAddActionList={(book) => {
              const newActionList: Omit<ActionList, 'id' | 'reader_name' | 'created_at' | 'updated_at'> = {
                title: `${book.title}에서 배운 실천사항`,
                reader_id: book.reader_id,
                book_title: book.title,
                content: '책에서 배운 내용을 실천해보세요.',
                target_months: [new Date().toLocaleDateString('ko-KR', { month: 'long' })],
                action_time: '매일 아침',
                status: '진행전'
              };
              handleAddActionList(newActionList);
            }}
          />
        );
      
      case 'dashboard':
        return <Dashboard books={books} />;
      
      case 'persona':
        return <PersonaChatbot />;
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation 
        currentPage={currentPage} 
        onPageChange={setCurrentPage}
        currentUser={null}
        onLoginClick={() => {}}
        onProfileClick={() => {}}
        onEmailVerificationClick={() => {}}
      />
      
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