import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Plus, X, Users } from "lucide-react";

interface Reader {
  id: string;
  name: string;
  email?: string;
  bio?: string;
}

interface ReaderManagerProps {
  readers: Reader[];
  onReadersChange: () => void;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAddReader: (name: string, email?: string, bio?: string) => Promise<Reader>;
  onDeleteReader: (id: string) => Promise<void>;
}

export function ReaderManager({ 
  readers, 
  onReadersChange, 
  open, 
  onOpenChange, 
  onAddReader, 
  onDeleteReader 
}: ReaderManagerProps) {
  const [newReader, setNewReader] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newBio, setNewBio] = useState('');

  const addReader = async () => {
    if (newReader.trim()) {
      try {
        await onAddReader(newReader.trim(), newEmail.trim() || undefined, newBio.trim() || undefined);
        setNewReader('');
        setNewEmail('');
        setNewBio('');
        onReadersChange();
      } catch (error) {
        // Error is already handled in App.tsx
      }
    }
  };

  const removeReader = async (readerId: string) => {
    try {
      await onDeleteReader(readerId);
      onReadersChange();
    } catch (error) {
      // Error is already handled in App.tsx
    }
  };

  const handleCancel = () => {
    setNewReader('');
    setNewEmail('');
    setNewBio('');
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            독자 목록 관리
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>새 독자 추가</Label>
            <div className="space-y-2">
              <Input
                value={newReader}
                onChange={(e) => setNewReader(e.target.value)}
                placeholder="독자명을 입력하세요"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addReader())}
                className="bg-white border-2"
              />
              <Input
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="이메일 (선택사항)"
                className="bg-white border-2"
              />
              <Input
                value={newBio}
                onChange={(e) => setNewBio(e.target.value)}
                placeholder="소개 (선택사항)"
                className="bg-white border-2"
              />
              <Button type="button" size="sm" onClick={addReader} className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                독자 추가
              </Button>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label>등록된 독자 ({readers.length}명)</Label>
            {readers.length === 0 ? (
              <p className="text-sm text-muted-foreground">등록된 독자가 없습니다.</p>
            ) : (
              <div className="space-y-2">
                {readers.map((reader) => (
                  <div key={reader.id} className="flex items-center justify-between p-2 border rounded">
                    <div>
                      <div className="font-medium">{reader.name}</div>
                      {reader.email && <div className="text-sm text-muted-foreground">{reader.email}</div>}
                      {reader.bio && <div className="text-sm text-muted-foreground">{reader.bio}</div>}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeReader(reader.id)}
                      className="ml-2 hover:text-destructive"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={handleCancel}>
              닫기
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 