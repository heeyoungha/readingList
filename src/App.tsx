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
import { getBooks, addBook, updateBook, deleteBook, getActionLists, addActionList } from "./lib/database";

export default function App() {
  const [books, setBooks] = useState<Book[]>([]);
  const [actionLists, setActionLists] = useState<ActionList[]>([]);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [isEditFormOpen, setIsEditFormOpen] = useState(false);
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

  const handleUpdateBook = async (id: string, updates: Partial<Book>) => {
    try {
      const updatedBook = await updateBook(id, updates);
      setBooks(prev => prev.map(book => book.id === id ? updatedBook : book));
      setEditingBook(null);
      setIsEditFormOpen(false);
      // 현재 선택된 책이 수정된 책이면 업데이트
      if (selectedBook?.id === id) {
        setSelectedBook(updatedBook);
      }
    } catch (err) {
      console.error('Error updating book:', err);
      alert('책을 수정하는데 실패했습니다.');
    }
  };

  const handleDeleteBook = async (book: Book) => {
    try {
      await deleteBook(book.id);
      setBooks(prev => prev.filter(b => b.id !== book.id));
      setSelectedBook(null); // 상세 모달 닫기
    } catch (err) {
      console.error('Error deleting book:', err);
      alert('책을 삭제하는데 실패했습니다.');
    }
  };

  const handleEditClick = (book: Book) => {
    setEditingBook(book);
    setIsEditFormOpen(true);
    setSelectedBook(null); // 상세 모달 닫기
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
                  지금까지 {books.length}권의 책을 읽었습니다
                </p>
              </div>
              <AddBookForm onAddBook={handleAddBook} />
            </div>
            
            {books.length === 0 ? (
              <div className="text-center py-12">
                <BookOpen className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground mb-4">아직 등록된 독후감이 없습니다</p>
                <AddBookForm onAddBook={handleAddBook} />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {books.map((book) => (
                  <BookCard
                    key={book.id}
                    book={book}
                    onViewDetails={setSelectedBook}
                    onAddActionList={(book) => {
                      // 액션리스트 페이지로 이동하면서 책 정보 전달
                      setCurrentPage('actions');
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        );
      case 'dashboard':
        return <Dashboard books={books} />;
      case 'meeting':
        return (
          <MeetingPage 
            books={books} 
            onBookClick={setSelectedBook}
            onAddActionList={(book) => {
              setCurrentPage('actions');
            }}
          />
        );
      case 'actions':
        return (
          <ActionListPage 
            actionLists={actionLists} 
            onViewActionList={() => {}}
            onAddActionList={() => {}}
          />
        );
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
        onLoginClick={() => {}}
        onProfileClick={() => {}}
        onEmailVerificationClick={() => {}}
      />
      
      <main className="container mx-auto px-4 py-8">
        {renderCurrentPage()}
      </main>

      {/* 책 상세 모달 */}
      <BookDetailModal
        book={selectedBook}
        open={!!selectedBook}
        onOpenChange={(open) => !open && setSelectedBook(null)}
        onEditClick={handleEditClick}
        onDeleteClick={handleDeleteBook}
      />

      {/* 편집 폼 모달 */}
      <AddBookForm
        onAddBook={handleAddBook}
        onUpdateBook={handleUpdateBook}
        editBook={editingBook}
        open={isEditFormOpen}
        onOpenChange={(open) => {
          setIsEditFormOpen(open);
          if (!open) {
            setEditingBook(null);
          }
        }}
      />
    </div>
  );
}