import { useState } from "react";
import { Book } from "../types/book";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Plus, X, Star } from "lucide-react";

interface AddBookFormProps {
  onAddBook: (book: Omit<Book, 'id'>) => void;
}

const emotions = [
  { value: 'happy', label: '행복한', emoji: '😊' },
  { value: 'sad', label: '슬픈', emoji: '😢' },
  { value: 'thoughtful', label: '생각이 많아지는', emoji: '🤔' },
  { value: 'excited', label: '흥미진진한', emoji: '😄' },
  { value: 'calm', label: '차분한', emoji: '😌' },
  { value: 'surprised', label: '놀라운', emoji: '😲' }
];

export function AddBookForm({ onAddBook }: AddBookFormProps) {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    reader: '',
    review: '',
    rating: 5,
    emotion: 'happy' as Book['emotion'],
    readDate: new Date().toISOString().split('T')[0],
    tags: [] as string[]
  });
  const [newTag, setNewTag] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.author || !formData.reader || !formData.review) {
      return;
    }

    onAddBook({
      ...formData,
      tags: formData.tags
    });

    // Reset form
    setFormData({
      title: '',
      author: '',
      reader: '',
      review: '',
      rating: 5,
      emotion: 'happy',
      readDate: new Date().toISOString().split('T')[0],
      tags: []
    });
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
        <Button size="lg" className="mb-6">
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
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="reader">독자 *</Label>
              <Input
                id="reader"
                value={formData.reader}
                onChange={(e) => setFormData(prev => ({...prev, reader: e.target.value}))}
                placeholder="독자명을 입력하세요"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="readDate">읽은 날짜</Label>
              <Input
                id="readDate"
                type="date"
                value={formData.readDate}
                onChange={(e) => setFormData(prev => ({...prev, readDate: e.target.value}))}
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
              <Select
                value={formData.emotion}
                onValueChange={(value: Book['emotion']) => 
                  setFormData(prev => ({...prev, emotion: value}))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {emotions.map(emotion => (
                    <SelectItem key={emotion.value} value={emotion.value}>
                      {emotion.emoji} {emotion.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="review">독후감 *</Label>
            <Textarea
              id="review"
              value={formData.review}
              onChange={(e) => setFormData(prev => ({...prev, review: e.target.value}))}
              placeholder="책에 대한 생각과 느낌을 자유롭게 적어주세요..."
              className="min-h-[120px]"
              required
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