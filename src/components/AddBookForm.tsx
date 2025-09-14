import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Plus, X, Star } from "lucide-react";
import { Book } from '../types/book';
import { getReaders } from '../lib/database';

interface AddBookFormProps {
  onAddBook: (book: Omit<Book, 'id' | 'reader_name'>) => void;
}

export default function AddBookForm({ onAddBook }: AddBookFormProps) {
  const [open, setOpen] = useState(false);
  const [readers, setReaders] = useState<{ id: string; name: string }[]>([]);
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    reader_id: '',
    review: '',
    presentation: '',
    rating: 5,
    readDate: new Date().toISOString().split('T')[0],
    tags: [] as string[],
    genre: '',
    purchaseLink: '',
    oneLiner: '',
    motivation: '',
    memorableQuotes: [] as string[]
  });
  const [newTag, setNewTag] = useState('');
  const [newQuote, setNewQuote] = useState('');

  // Load readers on component mount
  useEffect(() => {
    const loadReaders = async () => {
      try {
        const readersData = await getReaders();
        setReaders(readersData);
      } catch (error) {
        console.error('Error loading readers:', error);
      }
    };
    loadReaders();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('Form submitted:', formData);
    
    if (!formData.title || !formData.author || !formData.reader_id || !formData.review) {
      console.log('Validation failed:', {
        title: !!formData.title,
        author: !!formData.author,
        reader_id: !!formData.reader_id,
        review: !!formData.review
      });
      return;
    }

    console.log('Calling onAddBook with:', {
      ...formData,
      tags: formData.tags,
      memorableQuotes: formData.memorableQuotes
    });

    onAddBook({
      ...formData,
      tags: formData.tags,
      memorableQuotes: formData.memorableQuotes
    } as Omit<Book, 'id' | 'reader_name'>);

    // Reset form
    setFormData({
      title: '',
      author: '',
      reader_id: '',
      review: '',
      presentation: '',
      rating: 5,
      readDate: new Date().toISOString().split('T')[0],
      tags: [],
      genre: '',
      purchaseLink: '',
      oneLiner: '',
      motivation: '',
      memorableQuotes: []
    });
    setNewTag('');
    setNewQuote('');
    setOpen(false);
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const addQuote = () => {
    if (newQuote.trim() && !formData.memorableQuotes.includes(newQuote.trim())) {
      setFormData(prev => ({
        ...prev,
        memorableQuotes: [...prev.memorableQuotes, newQuote.trim()]
      }));
      setNewQuote('');
    }
  };

  const removeQuote = (quoteToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      memorableQuotes: prev.memorableQuotes.filter(quote => quote !== quoteToRemove)
    }));
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          새 독후감 추가
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>새 독후감 추가</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 기본 정보 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="title">책 제목 *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({...prev, title: e.target.value}))}
                placeholder="책 제목을 입력하세요"
                required
                className="bg-white border-2"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="author">저자 *</Label>
              <Input
                id="author"
                value={formData.author}
                onChange={(e) => setFormData(prev => ({...prev, author: e.target.value}))}
                placeholder="저자명을 입력하세요"
                required
                className="bg-white border-2"
              />
            </div>
          </div>
          
          {/* 독자 및 날짜 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="reader">독자 *</Label>
              <Select
                value={formData.reader_id}
                onValueChange={(value) => 
                  setFormData(prev => ({...prev, reader_id: value}))
                }
              >
                <SelectTrigger className="bg-white border-2">
                  <SelectValue placeholder="독자를 선택하세요" />
                </SelectTrigger>
                <SelectContent className="bg-white border-2">
                  {readers.map(reader => (
                    <SelectItem key={reader.id} value={reader.id}>
                      {reader.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="readDate">읽은 날짜</Label>
              <Input
                id="readDate"
                type="date"
                value={formData.readDate}
                onChange={(e) => setFormData(prev => ({...prev, readDate: e.target.value}))}
                className="bg-white border-2"
              />
            </div>
          </div>

          {/* 장르 및 평점 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="genre">장르</Label>
              <Input
                id="genre"
                value={formData.genre}
                onChange={(e) => setFormData(prev => ({...prev, genre: e.target.value}))}
                placeholder="장르를 입력하세요 (예: 소설, 에세이, 자기계발)"
                className="bg-white border-2"
              />
            </div>
            
            <div className="space-y-2">
              <Label>평점</Label>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setFormData(prev => ({...prev, rating: star}))}
                    className="p-1"
                  >
                    <Star
                      className={`w-6 h-6 ${
                        star <= formData.rating
                          ? "fill-yellow-400 text-yellow-400"
                          : "text-gray-300"
                      }`}
                    />
                  </button>
                ))}
                <span className="ml-2">{formData.rating}/5</span>
              </div>
            </div>
          </div>

          {/* 구매링크 및 한줄평 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="purchaseLink">구매 링크</Label>
              <Input
                id="purchaseLink"
                value={formData.purchaseLink}
                onChange={(e) => setFormData(prev => ({...prev, purchaseLink: e.target.value}))}
                placeholder="구매 링크를 입력하세요"
                className="bg-white border-2"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="oneLiner">한줄평</Label>
              <Input
                id="oneLiner"
                value={formData.oneLiner}
                onChange={(e) => setFormData(prev => ({...prev, oneLiner: e.target.value}))}
                placeholder="책에 대한 한줄평을 입력하세요"
                className="bg-white border-2"
              />
            </div>
          </div>

          {/* 고르게 된 계기 */}
          <div className="space-y-2">
            <Label htmlFor="motivation">고르게 된 계기</Label>
            <Textarea
              id="motivation"
              value={formData.motivation}
              onChange={(e) => setFormData(prev => ({...prev, motivation: e.target.value}))}
              placeholder="이 책을 선택하게 된 이유나 계기를 적어주세요..."
              className="min-h-[80px] bg-white border-2"
            />
          </div>

          {/* 기억에 남는 구절 */}
          <div className="space-y-2">
            <Label>기억에 남는 구절</Label>
            <div className="flex gap-2">
              <Textarea
                value={newQuote}
                onChange={(e) => setNewQuote(e.target.value)}
                placeholder="기억에 남는 구절을 입력하세요"
                className="bg-white border-2 min-h-[60px]"
              />
              <Button type="button" size="sm" onClick={addQuote} className="self-start mt-1">
                <Plus className="w-4 h-4" />
              </Button>
            </div>
            
            {formData.memorableQuotes.length > 0 && (
              <div className="space-y-2 mt-2">
                {formData.memorableQuotes.map((quote, index) => (
                  <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg border">
                    <div className="flex-1 text-sm">{quote}</div>
                    <button
                      type="button"
                      onClick={() => removeQuote(quote)}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* 느낀점 */}
          <div className="space-y-2">
            <Label htmlFor="review">느낀점 *</Label>
            <Textarea
              id="review"
              value={formData.review}
              onChange={(e) => setFormData(prev => ({...prev, review: e.target.value}))}
              placeholder="책을 읽고 느낀 점을 자유롭게 적어주세요..."
              className="min-h-[120px] bg-white border-2"
              required
            />
          </div>
          
          {/* 발제문 */}
          <div className="space-y-2">
            <Label htmlFor="presentation">발제문</Label>
            <Textarea
              id="presentation"
              value={formData.presentation}
              onChange={(e) => setFormData(prev => ({...prev, presentation: e.target.value}))}
              placeholder="독서 모임에서 발표할 내용을 작성해주세요... (선택사항)"
              className="min-h-[100px] bg-white border-2"
            />
          </div>
          
          {/* 태그 */}
          <div className="space-y-2">
            <Label>태그</Label>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="태그 추가 (엔터 또는 + 버튼)"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                className="bg-white border-2"
              />
              <Button type="button" size="sm" onClick={addTag}>
                <Plus className="w-4 h-4" />
              </Button>
            </div>
            
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="flex items-center gap-1">
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>
          
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              취소
            </Button>
            <Button type="submit">
              독후감 추가
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}