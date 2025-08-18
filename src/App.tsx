import React, { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import BookList from './components/BookList';
import { MeetingPage } from './components/MeetingPage';
import { Dashboard } from './components/Dashboard';
import { ActionListPage } from './components/ActionListPage';
import { BookDetailModal } from './components/BookDetailModal';
import { ActionListForm } from './components/ActionListForm';
import AddBookForm from './components/AddBookForm';
import { AuthModal } from './components/AuthModal';
import { UserProfile } from './components/UserProfile';
import { EmailVerificationNotice } from './components/EmailVerificationNotice';
import { Book } from './types/book';
import { ActionList } from './types/actionList';
import { getBooks, addBook, addSampleData, getActionLists, addActionList } from './lib/database';
import { auth } from './lib/auth';
import { Button } from './components/ui/button';
import { User, LogIn } from 'lucide-react';

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

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [showActionListForm, setShowActionListForm] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showUserProfile, setShowUserProfile] = useState(false);
  const [showEmailVerification, setShowEmailVerification] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [actionListInitialData, setActionListInitialData] = useState<{
    book_title: string;
    reader_id: string;
    reader_name: string;
  } | undefined>();

  useEffect(() => {
    loadBooks();
    loadActionLists();
    
    // 인증 상태 확인
    const checkAuth = async () => {
      try {
        const user = await auth.getCurrentUser();
        setCurrentUser(user);
      } catch (error) {
        console.log('로그인되지 않음');
      }
    };
    
    checkAuth();
    
    // 인증 상태 변경 감지
    const { data: { subscription } } = auth.onAuthStateChange((user) => {
      setCurrentUser(user);
    });
    
    return () => subscription.unsubscribe();
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

  const handleAuthSuccess = () => {
    // 인증 성공 시 추가 작업
    console.log('로그인 성공!');
  };

  const handleEmailVerified = () => {
    // 이메일 인증 완료 시 사용자 정보 새로고침
    const checkAuth = async () => {
      try {
        const user = await auth.getCurrentUser();
        setCurrentUser(user);
      } catch (error) {
        console.log('사용자 정보 새로고침 실패');
      }
    };
    checkAuth();
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  const handleAddSampleData = async () => {
    try {
      await addSampleData();
      await loadBooks(); // Reload books after adding sample data
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
      <Navigation 
        currentPage={currentPage} 
        onPageChange={setCurrentPage}
        currentUser={currentUser}
        onLoginClick={() => setShowAuthModal(true)}
        onProfileClick={() => setShowUserProfile(true)}
        onEmailVerificationClick={() => setShowEmailVerification(true)}
      />
      
      <main className="container mx-auto px-4 py-8">
        {currentPage === 'books' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-3xl font-bold">독후감 모음</h1>
              <div className="flex gap-2">
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



      <ActionListForm
        open={showActionListForm}
        onOpenChange={setShowActionListForm}
        onAddActionList={handleAddActionList}
        initialData={actionListInitialData}
      />

      <AuthModal
        open={showAuthModal}
        onOpenChange={setShowAuthModal}
        onAuthSuccess={handleAuthSuccess}
      />

      <UserProfile
        user={currentUser}
        open={showUserProfile}
        onOpenChange={setShowUserProfile}
        onLogout={handleLogout}
      />

      <EmailVerificationNotice
        user={currentUser}
        open={showEmailVerification}
        onOpenChange={setShowEmailVerification}
        onVerified={handleEmailVerified}
      />
    </div>
  );
}

export default App;