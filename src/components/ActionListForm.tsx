import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { CheckSquare, X, Target } from "lucide-react";
import { ActionList } from '../types/actionList';
import { getReaders } from '../lib/database';

interface ActionListFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAddActionList: (actionList: Omit<ActionList, 'id' | 'reader_name' | 'created_at' | 'updated_at'>) => void;
  initialData?: {
    book_title: string;
    reader_id: string;
    reader_name: string;
  };
}

const statusOptions = [
  { value: '진행전', label: '진행전' },
  { value: '진행중', label: '진행중' },
  { value: '완료', label: '완료' },
  { value: '보류', label: '보류' }
];

export function ActionListForm({ open, onOpenChange, onAddActionList, initialData }: ActionListFormProps) {
  const [readers, setReaders] = useState<{ id: string; name: string }[]>([]);
  const [formData, setFormData] = useState({
    title: '',
    reader_id: '',
    book_title: '',
    content: '',
    target_months: [] as string[],
    action_time: '',
    status: '진행전' as ActionList['status']
  });

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

  // Set initial data when provided
  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({
        ...prev,
        book_title: initialData.book_title,
        reader_id: initialData.reader_id
      }));
    }
  }, [initialData]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.reader_id || !formData.book_title || !formData.content) {
      alert('모든 필수 항목을 입력해주세요.');
      return;
    }

    onAddActionList(formData);

    // Reset form
    setFormData({
      title: '',
      reader_id: '',
      book_title: '',
      content: '',
      target_months: [],
      action_time: '',
      status: '진행전'
    });
    
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5" />
            새 액션리스트 추가
          </DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">제목 *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({...prev, title: e.target.value}))}
              placeholder="액션리스트 제목을 입력하세요"
              required
              className="bg-white border-2"
            />
          </div>
          
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
              <Label htmlFor="book_title">책 제목 *</Label>
              <Input
                id="book_title"
                value={formData.book_title}
                onChange={(e) => setFormData(prev => ({...prev, book_title: e.target.value}))}
                placeholder="책 제목을 입력하세요"
                required
                className="bg-white border-2"
              />
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Target className="w-4 h-4" />
                목표 월
              </Label>
              <div className="grid grid-cols-6 gap-2">
                {['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'].map((month) => (
                  <Button
                    key={month}
                    type="button"
                    variant={formData.target_months.includes(month) ? "default" : "outline"}
                    className={`h-10 ${formData.target_months.includes(month) ? 'bg-blue-600 text-white' : 'bg-white border-2'}`}
                    onClick={() => {
                      const newMonths = formData.target_months.includes(month)
                        ? formData.target_months.filter(m => m !== month)
                        : [...formData.target_months, month];
                      setFormData(prev => ({...prev, target_months: newMonths}));
                    }}
                  >
                    {month}
                  </Button>
                ))}
              </div>
              {formData.target_months.length > 0 && (
                <div className="text-sm text-muted-foreground">
                  선택된 월: {formData.target_months.join(', ')}
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="action_time">액션 시간</Label>
                <Input
                  id="action_time"
                  value={formData.action_time}
                  onChange={(e) => setFormData(prev => ({...prev, action_time: e.target.value}))}
                  placeholder="예: 매일 저녁 8시, 주말 오후"
                  className="bg-white border-2"
                />
              </div>
              
              <div className="space-y-2">
                <Label>상태</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value: ActionList['status']) => 
                    setFormData(prev => ({...prev, status: value}))
                  }
                >
                  <SelectTrigger className="bg-white border-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white border-2">
                    {statusOptions.map(status => (
                      <SelectItem key={status.value} value={status.value}>
                        {status.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="content">내용 *</Label>
            <Textarea
              id="content"
              value={formData.content}
              onChange={(e) => setFormData(prev => ({...prev, content: e.target.value}))}
              placeholder="실천할 내용을 자세히 작성해주세요..."
              className="min-h-[120px] bg-white border-2"
              required
            />
          </div>
          
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              취소
            </Button>
            <Button type="submit">
              액션리스트 추가
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
} 