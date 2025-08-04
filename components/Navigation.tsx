import { useState } from "react";
import { Button } from "./ui/button";
import { BookOpen, BarChart3, Users } from "lucide-react";

interface NavigationProps {
  currentPage: 'books' | 'dashboard' | 'meeting';
  onPageChange: (page: 'books' | 'dashboard' | 'meeting') => void;
}

export function Navigation({ currentPage, onPageChange }: NavigationProps) {
  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="w-6 h-6" />
            <h1>독후감 공유</h1>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={currentPage === 'books' ? 'default' : 'ghost'}
              onClick={() => onPageChange('books')}
            >
              <BookOpen className="w-4 h-4 mr-2" />
              독후감
            </Button>
            
            <Button
              variant={currentPage === 'meeting' ? 'default' : 'ghost'}
              onClick={() => onPageChange('meeting')}
            >
              <Users className="w-4 h-4 mr-2" />
              모임
            </Button>
            
            <Button
              variant={currentPage === 'dashboard' ? 'default' : 'ghost'}
              onClick={() => onPageChange('dashboard')}
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              대시보드
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}