
import { Button } from "./ui/button";
import { BookOpen, BarChart3, Users, CheckSquare, User, LogIn, Bot } from "lucide-react";
import { getUserDisplayName } from "../lib/utils";

interface NavigationProps {
  currentPage: 'books' | 'dashboard' | 'meeting' | 'actions' | 'persona';
  onPageChange: (page: 'books' | 'dashboard' | 'meeting' | 'actions' | 'persona') => void;
  currentUser?: any;
  onLoginClick: () => void;
  onProfileClick: () => void;
  onEmailVerificationClick: () => void;
}

export function Navigation({ currentPage, onPageChange, currentUser, onLoginClick, onProfileClick, onEmailVerificationClick }: NavigationProps) {
  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-semibold text-foreground">독후감 공유</h1>
          </div>
          
          <div className="flex items-center gap-2">
            {currentUser ? (
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onProfileClick}
                  className="flex items-center gap-2"
                >
                  <User className="w-4 h-4" />
                  {getUserDisplayName(currentUser)}
                </Button>
                {!currentUser.email_confirmed_at && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onEmailVerificationClick}
                    className="text-yellow-600 border-yellow-300 hover:bg-yellow-50"
                  >
                    인증 필요
                  </Button>
                )}
              </div>
            ) : (
              <Button
                variant="outline"
                size="sm"
                onClick={onLoginClick}
                className="flex items-center gap-2"
              >
                <LogIn className="w-4 h-4" />
                로그인
              </Button>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={currentPage === 'books' ? 'default' : 'ghost'}
              onClick={() => onPageChange('books')}
              className={`transition-all duration-200 font-medium ${
                currentPage === 'books' 
                  ? 'bg-black text-white shadow-md scale-105 border-black hover:bg-black hover:text-white' 
                  : 'hover:bg-accent hover:text-accent-foreground border-transparent'
              }`}
            >
              <BookOpen className="w-4 h-4 mr-2" />
              독후감
            </Button>
            
            <Button
              variant={currentPage === 'meeting' ? 'default' : 'ghost'}
              onClick={() => onPageChange('meeting')}
              className={`transition-all duration-200 font-medium ${
                currentPage === 'meeting' 
                  ? 'bg-black text-white shadow-md scale-105 border-black hover:bg-black hover:text-white' 
                  : 'hover:bg-accent hover:text-accent-foreground border-transparent'
              }`}
            >
              <Users className="w-4 h-4 mr-2" />
              모임
            </Button>
            
            <Button
              variant={currentPage === 'actions' ? 'default' : 'ghost'}
              onClick={() => onPageChange('actions')}
              className={`transition-all duration-200 font-medium ${
                currentPage === 'actions' 
                  ? 'bg-black text-white shadow-md scale-105 border-black hover:bg-black hover:text-white' 
                  : 'hover:bg-accent hover:text-accent-foreground border-transparent'
              }`}
            >
              <CheckSquare className="w-4 h-4 mr-2" />
              액션리스트
            </Button>
            
            <Button
              variant={currentPage === 'dashboard' ? 'default' : 'ghost'}
              onClick={() => onPageChange('dashboard')}
              className={`transition-all duration-200 font-medium ${
                currentPage === 'dashboard' 
                  ? 'bg-black text-white shadow-md scale-105 border-black hover:bg-black hover:text-white' 
                  : 'hover:bg-accent hover:text-accent-foreground border-transparent'
              }`}
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              대시보드
            </Button>
            
            <Button
              variant={currentPage === 'persona' ? 'default' : 'ghost'}
              onClick={() => onPageChange('persona')}
              className={`transition-all duration-200 font-medium ${
                currentPage === 'persona' 
                  ? 'bg-black text-white shadow-md scale-105 border-black hover:bg-black hover:text-white' 
                  : 'hover:bg-accent hover:text-accent-foreground border-transparent'
              }`}
            >
              <Bot className="w-4 h-4 mr-2" />
              페르소나 챗봇
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}