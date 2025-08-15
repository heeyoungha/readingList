import React from 'react';
import BookCard from './BookCard';
import { Book } from '../types/book';

interface BookListProps {
  books: Book[];
  onViewDetails: (book: Book) => void;
  onAddActionList: (book: Book) => void;
}

export default function BookList({ books, onViewDetails, onAddActionList }: BookListProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {books.map((book) => (
        <BookCard
          key={book.id}
          book={book}
          onViewDetails={onViewDetails}
          onAddActionList={onAddActionList}
        />
      ))}
    </div>
  );
} 