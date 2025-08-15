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

const emotions = [
  { value: 'happy', label: '행복한', emoji: '😊' },
  { value: 'sad', label: '슬픈', emoji: '😢' },
  { value: 'thoughtful', label: '생각에 잠긴', emoji: '🤔' },
  { value: 'excited', label: '흥미진진한', emoji: '🤩' },
  { value: 'calm', label: '평온한', emoji: '😌' },
  { value: 'surprised', label: '놀란', emoji: '😲' }
];

export default function AddBookForm({ onAddBook }: AddBookFormProps) {
  const [open, setOpen] = useState(false);
  const [readers, setReaders] = useState<{ id: string; name: string }[]>([]);
  const [customEmotions, setCustomEmotions] = useState<string[]>([]);
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    reader_id: '',
    review: '',
    presentation: '',
    rating: 5,
    emotion: 'happy' as string,
    readDate: new Date().toISOString().split('T')[0],
    tags: [] as string[]
  });
  const [customEmotion, setCustomEmotion] = useState('');
  const [customReader, setCustomReader] = useState('');
  const [newTag, setNewTag] = useState('');

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
      tags: formData.tags
    });

    onAddBook({
      ...formData,
      tags: formData.tags
    } as Omit<Book, 'id' | 'reader_name'>);

    // Reset form
    setFormData({
      title: '',
      author: '',
      reader_id: '',
      review: '',
      presentation: '',
      rating: 5,
      emotion: 'happy',
      readDate: new Date().toISOString().split('T')[0],
      tags: []
    });
    setCustomEmotion('');
    setCustomReader('');
    setNewTag('');
    setCustomEmotions([]);
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
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="reader">독자 *</Label>
              <div className="space-y-2">
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
                
                <div className="text-xs text-muted-foreground">
                  또는 직접 입력: 
                  <Input
                    placeholder="독자명을 직접 입력하세요"
                    value={customReader}
                    onChange={(e) => {
                      const value = e.target.value;
                      setCustomReader(value);
                      setFormData(prev => ({...prev, reader_id: value}));
                    }}
                    className="mt-1 bg-white border-2"
                  />
                </div>
              </div>
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
          
          <div className="grid grid-cols-2 gap-4">
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
            
            <div className="space-y-2">
              <Label>감정</Label>
              <div className="space-y-2">
                <Select
                  value={formData.emotion}
                  onValueChange={(value: string) => 
                    setFormData(prev => ({...prev, emotion: value}))
                  }
                >
                  <SelectTrigger className="bg-white border-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white border-2">
                    {emotions.map(emotion => (
                      <SelectItem key={emotion.value} value={emotion.value}>
                        {emotion.emoji} {emotion.label}
                      </SelectItem>
                    ))}
                    {customEmotions.length > 0 && (
                      <>
                        <SelectItem value="" disabled>
                          ─── 사용자 추가 감정 ───
                        </SelectItem>
                        {customEmotions.map((emotion, index) => (
                          <SelectItem key={`custom-${index}`} value={emotion}>
                            😊 {emotion}
                          </SelectItem>
                        ))}
                      </>
                    )}
                  </SelectContent>
                </Select>
                
                <div className="text-xs text-muted-foreground">
                  또는 직접 입력: 
                  <div className="flex gap-2 mt-1">
                    <Input
                      placeholder="감정을 직접 입력하세요"
                      value={customEmotion}
                      onChange={(e) => setCustomEmotion(e.target.value)}
                      className="flex-1 bg-white border-2"
                    />
                    <Button
                      type="button"
                      size="sm"
                      onClick={() => {
                        if (customEmotion.trim() && !customEmotions.includes(customEmotion.trim())) {
                          setCustomEmotions(prev => [...prev, customEmotion.trim()]);
                          setFormData(prev => ({...prev, emotion: customEmotion.trim()}));
                          setCustomEmotion('');
                        }
                      }}
                    >
                      추가
                    </Button>
                  </div>
                  {customEmotions.length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs text-muted-foreground mb-1">추가된 감정:</div>
                      <div className="flex flex-wrap gap-1">
                        {customEmotions.map((emotion, index) => (
                          <Badge
                            key={index}
                            variant="outline"
                            className="text-xs cursor-pointer hover:bg-gray-100"
                            onClick={() => setFormData(prev => ({...prev, emotion: emotion}))}
                          >
                            {emotion}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="review">독후감 *</Label>
            <Textarea
              id="review"
              value={formData.review}
              onChange={(e) => setFormData(prev => ({...prev, review: e.target.value}))}
              placeholder="책에 대한 생각과 느낌을 자유롭게 적어주세요..."
              className="min-h-[120px] bg-white border-2"
              required
            />
          </div>
          
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