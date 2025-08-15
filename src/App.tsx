import React, { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import BookList from './components/BookList';
import { MeetingPage } from './components/MeetingPage';
import { Dashboard } from './components/Dashboard';
import { ActionListPage } from './components/ActionListPage';
import { BookDetailModal } from './components/BookDetailModal';
import { ActionListForm } from './components/ActionListForm';
import AddBookForm from './components/AddBookForm';
import { ReaderManager } from './components/ReaderManager';
import { Book } from './types/book';
import { ActionList } from './types/actionList';
import { getBooks, addBook, addSampleData, getReaders, addReader, deleteReader, getActionLists, addActionList } from './lib/database';
import { Button } from './components/ui/button';

type Page = 'books' | 'meeting' | 'dashboard' | 'actions';

const initialSampleBooks: Book[] = [
  {
    id: '1',
    title: '코스모스',
    author: '칼 세이건',
    reader_id: '1',
    reader_name: '김독서',
    review: '우주에 대한 경이로움과 과학적 사고의 중요성을 깨닫게 해준 책입니다.',
    presentation: '우주에 대한 경이로움과 과학적 사고의 중요성을 깨닫게 해준 책입니다. 세이건의 시적인 문체로 복잡한 과학 개념들을 쉽게 설명해주어 과학에 대한 흥미를 불러일으켰습니다.',
    rating: 5,
    emotion: 'excited',
    readDate: '2024-01-15',
    tags: ['과학', '우주', '철학']
  },
  {
    id: '2',
    title: '82년생 김지영',
    author: '조남주',
    reader_id: '2',
    reader_name: '이북러버',
    review: '현대 여성이 겪는 현실적인 문제들을 담담하게 그려낸 작품입니다.',
    presentation: '현대 여성이 겪는 현실적인 문제들을 담담하게 그려낸 작품입니다. 읽으면서 많은 생각을 하게 되었고, 우리 사회에 대해 돌아보는 계기가 되었습니다.',
    rating: 4,
    emotion: 'thoughtful',
    readDate: '2024-01-28',
    tags: ['소설', '여성', '사회']
  }
];

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('books');
  const [books, setBooks] = useState<Book[]>([]);
  const [actionLists, setActionLists] = useState<ActionList[]>([]);
  const [readers, setReaders] = useState<{ id: string; name: string; email?: string; bio?: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [showReaderManager, setShowReaderManager] = useState(false);
  const [showActionListForm, setShowActionListForm] = useState(false);
  const [actionListInitialData, setActionListInitialData] = useState<{
    book_title: string;
    reader_id: string;
    reader_name: string;
  } | undefined>();

  useEffect(() => {
    loadBooks();
    loadReaders();
    loadActionLists();
  }, []);

  const loadBooks = async () => {
    try {
      setLoading(true);
      setError(null);
      const booksData = await getBooks();
      setBooks(booksData);
    } catch (err) {
      console.error('Error loading books:', err);
      setError('책 목록을 불러오는데 실패했습니다.');
      // Fallback to sample data
      setBooks(initialSampleBooks);
    } finally {
      setLoading(false);
    }
  };

  const loadReaders = async () => {
    try {
      const readersData = await getReaders();
      setReaders(readersData);
    } catch (err) {
      console.error('Error loading readers:', err);
    }
  };

  const loadActionLists = async () => {
    try {
      const actionListsData = await getActionLists();
      setActionLists(actionListsData);
    } catch (err) {
      console.error('Error loading action lists:', err);
    }
  };

  const handleAddBook = async (newBook: Omit<Book, 'id' | 'reader_name'>) => {
    try {
      console.log('App: handleAddBook called with:', newBook);
      const addedBook = await addBook(newBook);
      console.log('App: Book added successfully:', addedBook);
      setBooks(prev => [addedBook, ...prev]);
    } catch (err) {
      console.error('Error adding book:', err);
      alert('책을 추가하는데 실패했습니다.');
    }
  };

  const handleAddActionList = async (actionList: Omit<ActionList, 'id' | 'reader_name' | 'created_at' | 'updated_at'>) => {
    try {
      const addedActionList = await addActionList(actionList);
      setActionLists(prev => [addedActionList, ...prev]);
    } catch (err) {
      console.error('Error adding action list:', err);
      alert('액션리스트를 추가하는데 실패했습니다.');
    }
  };

  const handleAddReader = async (name: string, email?: string, bio?: string) => {
    try {
      const newReader = await addReader(name, email, bio);
      setReaders(prev => [...prev, newReader]);
      return newReader;
    } catch (err) {
      console.error('Error adding reader:', err);
      alert('독자를 추가하는데 실패했습니다.');
      throw err;
    }
  };

  const handleDeleteReader = async (id: string) => {
    try {
      await deleteReader(id);
      setReaders(prev => prev.filter(reader => reader.id !== id));
    } catch (err) {
      console.error('Error deleting reader:', err);
      alert('독자를 삭제하는데 실패했습니다.');
    }
  };

  const handleViewBookDetails = (book: Book) => {
    setSelectedBook(book);
  };

  const handleCloseModal = () => {
    setSelectedBook(null);
  };

  const handleAddActionListFromBook = (book: Book) => {
    setActionListInitialData({
      book_title: book.title,
      reader_id: book.reader_id,
      reader_name: book.reader_name
    });
    setShowActionListForm(true);
  };

  const handleAddActionListFromPage = () => {
    setActionListInitialData(undefined);
    setShowActionListForm(true);
  };

  const handleAddSampleData = async () => {
    try {
      await addSampleData();
      await loadBooks(); // Reload books after adding sample data
      await loadReaders(); // Reload readers after adding sample data
      await loadActionLists(); // Reload action lists after adding sample data
    } catch (err) {
      console.error('Error adding sample data:', err);
      alert('샘플 데이터 추가에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">책 목록을 불러오는 중...</p>
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
            onClick={loadBooks}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      
      <main className="container mx-auto px-4 py-8">
        {currentPage === 'books' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-3xl font-bold">독후감 모음</h1>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowReaderManager(true)}
                >
                  독자 관리
                </Button>
                <AddBookForm onAddBook={handleAddBook} />
                {books.length === 0 && (
                  <Button
                    variant="outline"
                    onClick={handleAddSampleData}
                  >
                    샘플 데이터 추가
                  </Button>
                )}
              </div>
            </div>
            
            {books.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">아직 독후감이 없습니다.</p>
                <p className="text-sm text-muted-foreground">새로운 독후감을 추가해보세요!</p>
              </div>
            ) : (
              <BookList 
                books={books} 
                onViewDetails={handleViewBookDetails}
                onAddActionList={handleAddActionListFromBook}
              />
            )}
          </div>
        )}
        
        {currentPage === 'meeting' && (
          <MeetingPage 
            books={books} 
            onBookClick={handleViewBookDetails}
            onAddActionList={handleAddActionListFromBook}
          />
        )}

        {currentPage === 'actions' && (
          <ActionListPage
            actionLists={actionLists}
            onViewActionList={() => {}} // TODO: Implement action list detail view
            onAddActionList={handleAddActionListFromPage}
          />
        )}

        {currentPage === 'dashboard' && <Dashboard books={books} />}
      </main>

      {selectedBook && (
        <BookDetailModal 
          book={selectedBook} 
          open={!!selectedBook}
          onOpenChange={(open) => !open && setSelectedBook(null)}
        />
      )}

      <ReaderManager
        readers={readers}
        onReadersChange={loadReaders}
        open={showReaderManager}
        onOpenChange={setShowReaderManager}
        onAddReader={handleAddReader}
        onDeleteReader={handleDeleteReader}
      />

      <ActionListForm
        open={showActionListForm}
        onOpenChange={setShowActionListForm}
        onAddActionList={handleAddActionList}
        initialData={actionListInitialData}
      />
    </div>
  );
}

export default App;