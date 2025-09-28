import React, { useState, useEffect, useRef } from 'react';
import { User, MessageCircle, Send, Bot, Loader2, Users } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { Book } from '../types/book';
// import { getBooks } from '../lib/database';

interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  metadata?: {
    tokens_used?: number;
    search_count?: number;
    prompt_type?: string;
  };
}

interface Author {
  name: string;
  reviewCount: number;
}

interface PersonaChatbotProps {
  books: Book[]; // 👈 props로 books 받기
}

export function PersonaChatbot({ books }: PersonaChatbotProps) { // 👈 props 받기
  const [authors, setAuthors] = useState<Author[]>([]);
  const [selectedAuthor, setSelectedAuthor] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [sessionId] = useState(`session_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // props로 받은 books 데이터로 작성자 목록 생성
  useEffect(() => {
    if (books && books.length > 0) {
      loadBookReviews();
    }
  }, [books]); // 👈 books가 변경될 때마다 실행

  // 메시지 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadBookReviews = async () => {
    try {
      setIsLoadingData(true);
      
      // props로 받은 books 사용 (getBooks() 호출 제거)
      // const books = await getBooks(); // 👈 이 라인 제거

      // 작성자별로 그룹핑
      const authorMap = new Map<string, number>();
      books?.forEach((book: Book) => {
        const author = book.reader_name || 'Unknown';
        authorMap.set(author, (authorMap.get(author) || 0) + 1);
      });

      const authorsData = Array.from(authorMap.entries()).map(([name, count]) => ({
        name,
        reviewCount: count
      }));

      setAuthors(authorsData);
      console.log('작성자 목록:', authorsData);

    } catch (error) {
      console.error('독후감 데이터 로드 실패:', error);
    } finally {
      setIsLoadingData(false);
    }
  };

  const setupPersonaWithAuthor = async (authorName: string) => {
    try {
      setIsLoading(true);

      // props로 받은 books에서 필터링 (getBooks() 호출 제거)
      // const allBooks = await getBooks(); // 👈 이 라인 제거
      const authorBooks = books.filter(book => book.reader_name === authorName);

      // 페르소나 시스템에 데이터 업로드
      const formattedData = authorBooks?.map((book: Book, index: number) => ({
        id: `book_${book.id}`,
        content: `${book.title}: ${book.review}`,
        author: book.reader_name,
        type: 'book_review',
        date: book.readDate,
        title: book.title
      })) || [];

      // FastAPI 서버에 데이터 전송
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('file', new Blob([JSON.stringify(formattedData)], { type: 'application/json' }), 'author_data.json');

      const uploadResponse = await fetch('http://localhost:8000/api/upload-data', {
        method: 'POST',
        body: formData
      });

      if (!uploadResponse.ok) throw new Error('데이터 업로드 실패');

      // 작성자 선택
      const selectResponse = await fetch('http://localhost:8000/api/select-author', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          author_name: authorName
        })
      });

      if (!selectResponse.ok) throw new Error('작성자 선택 실패');

      setSelectedAuthor(authorName);
      
      // 환영 메시지 추가
      const welcomeMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        content: `안녕하세요! 저는 ${authorName}입니다. 👋\n\n제가 작성한 독후감들을 바탕으로 대화할 수 있어요. 궁금한 것이 있으시면 언제든 말씀해 주세요! ✨`,
        isUser: false,
        timestamp: new Date()
      };

      setMessages([welcomeMessage]);

    } catch (error) {
      console.error('페르소나 설정 실패:', error);
      alert('페르소나 설정에 실패했습니다. 서버가 실행 중인지 확인해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !selectedAuthor) return;

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      content: inputMessage,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
          use_search: true,
          search_k: 5
        })
      });

      const data = await response.json();

      if (data.success) {
        const botMessage: ChatMessage = {
          id: `msg_${Date.now() + 1}`,
          content: data.response,
          isUser: false,
          timestamp: new Date(),
          metadata: data.metadata
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error(data.error || '응답 생성 실패');
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      const errorMessage: ChatMessage = {
        id: `msg_${Date.now() + 1}`,
        content: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (isLoadingData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">독후감 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <Bot className="w-8 h-8 text-blue-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-800">페르소나 챗봇</h1>
        </div>
        <p className="text-gray-600">독후감 작성자의 페르소나와 대화해보세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 사이드바 - 작성자 선택 */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Users className="w-5 h-5 text-purple-600 mr-2" />
              작성자 선택
            </h3>
            
            {authors.length === 0 ? (
              <p className="text-gray-500 text-sm">독후감 데이터가 없습니다.</p>
            ) : (
              <div className="space-y-2">
                {authors.map((author) => (
                  <button
                    key={author.name}
                    onClick={() => setupPersonaWithAuthor(author.name)}
                    disabled={isLoading}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedAuthor === author.name
                        ? 'bg-purple-100 border-2 border-purple-500 text-purple-800'
                        : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                    } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                  >
                    <div className="font-medium">{author.name}</div>
                    <div className="text-sm text-gray-500">독후감 {author.reviewCount}개</div>
                  </button>
                ))}
              </div>
            )}

            {selectedAuthor && (
              <div className="mt-4 p-3 bg-purple-50 rounded-lg">
                <div className="text-sm font-medium text-purple-800">현재 페르소나</div>
                <div className="text-purple-600">{selectedAuthor}</div>
              </div>
            )}
          </div>

          {/* 빠른 질문 */}
          {selectedAuthor && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <MessageCircle className="w-5 h-5 text-blue-600 mr-2" />
                빠른 질문
              </h3>
              <div className="space-y-2">
                {[
                  '안녕하세요! 자기소개 좀 해주세요',
                  '어떤 책들을 읽으셨나요?',
                  '평소 관심사나 취미가 뭔가요?',
                  '요즘 어떤 생각을 하고 계신가요?'
                ].map((question, index) => (
                  <button
                    key={index}
                    onClick={() => setInputMessage(question)}
                    className="w-full text-left p-2 text-sm bg-gray-50 hover:bg-gray-100 rounded transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 메인 채팅 영역 */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-md h-[600px] flex flex-col">
            {/* 채팅 헤더 */}
            <div className="border-b border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold flex items-center">
                  <MessageCircle className="w-5 h-5 text-blue-600 mr-2" />
                  대화
                  {selectedAuthor && (
                    <span className="ml-2 text-sm text-purple-600">with {selectedAuthor}</span>
                  )}
                </h2>
              </div>
            </div>

            {/* 채팅 메시지 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {!selectedAuthor ? (
                <div className="text-center text-gray-500 mt-20">
                  <Bot className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg mb-2">페르소나를 선택해주세요</p>
                  <p className="text-sm">왼쪽에서 작성자를 선택하면 해당 작성자의 페르소나와 대화할 수 있습니다.</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex items-start space-x-3 ${
                      message.isUser ? 'flex-row-reverse space-x-reverse' : ''
                    }`}
                  >
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      message.isUser ? 'bg-green-500' : 'bg-purple-500'
                    }`}>
                      {message.isUser ? (
                        <User className="w-4 h-4 text-white" />
                      ) : (
                        <Bot className="w-4 h-4 text-white" />
                      )}
                    </div>
                    <div className={`max-w-[80%] rounded-lg p-3 ${
                      message.isUser 
                        ? 'bg-green-50 text-green-900' 
                        : 'bg-purple-50 text-purple-900'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      {message.metadata && (
                        <div className="mt-2 text-xs text-gray-500 border-t pt-2">
                          토큰: {message.metadata.tokens_used} | 
                          검색: {message.metadata.search_count}개 | 
                          타입: {message.metadata.prompt_type}
                        </div>
                      )}
                      <div className="text-xs text-gray-400 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))
              )}
              
              {isLoading && (
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* 채팅 입력 */}
            {selectedAuthor && (
              <div className="border-t border-gray-200 p-4">
                <div className="flex space-x-4">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="메시지를 입력하세요..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    rows={2}
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        전송
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 