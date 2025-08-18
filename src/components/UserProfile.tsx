import React, { useState } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Separator } from "./ui/separator";
import { User, LogOut, Settings, Mail, Edit, Save, X } from "lucide-react";
import { auth } from '../lib/auth';
import { supabase } from '../lib/supabase';
import { getUserDisplayName } from '../lib/utils';

interface UserProfileProps {
  user: any;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onLogout: () => void;
}

export function UserProfile({ user, open, onOpenChange, onLogout }: UserProfileProps) {
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [saving, setSaving] = useState(false);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await auth.signOut();
      onLogout();
      onOpenChange(false);
    } catch (error) {
      console.error('로그아웃 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 사용자 이름 가져오기 (로컬 함수)
  const getLocalDisplayName = () => {
    return getUserDisplayName(user);
  };

  // 사용자 이름 설정
  const handleSaveDisplayName = async () => {
    if (!displayName.trim()) {
      alert('사용자 이름을 입력해주세요.');
      return;
    }

    setSaving(true);
    try {
      const { error } = await supabase.auth.updateUser({
        data: { display_name: displayName.trim() }
      });

      if (error) {
        throw error;
      }

      alert('사용자 이름이 저장되었습니다!');
      setIsEditing(false);
      // 부모 컴포넌트에 변경 알림
      window.location.reload(); // 임시로 페이지 새로고침
    } catch (error) {
      console.error('사용자 이름 저장 실패:', error);
      alert('사용자 이름 저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  // 편집 모드 시작
  const startEditing = () => {
    setDisplayName(getLocalDisplayName());
    setIsEditing(true);
  };

  // 편집 모드 취소
  const cancelEditing = () => {
    setIsEditing(false);
    setDisplayName('');
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            프로필
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
              {getLocalDisplayName().charAt(0).toUpperCase()}
            </div>
            <div className="flex-1">
              {isEditing ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Input
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder="사용자 이름을 입력하세요"
                      className="flex-1"
                    />
                    <Button
                      size="sm"
                      onClick={handleSaveDisplayName}
                      disabled={saving}
                    >
                      <Save className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={cancelEditing}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <p className="font-medium">{getLocalDisplayName()}</p>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={startEditing}
                    className="h-6 w-6 p-0"
                  >
                    <Edit className="w-3 h-3" />
                  </Button>
                </div>
              )}
              <p className="text-sm text-muted-foreground">
                {user?.email}
              </p>
              <p className="text-sm text-muted-foreground">
                가입일: {new Date(user?.created_at).toLocaleDateString('ko-KR')}
              </p>
            </div>
          </div>
          
          <Separator />
          
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-sm">
              <Mail className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">이메일:</span>
              <span>{user?.email}</span>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">이메일 인증:</span>
              <span className={user?.email_confirmed_at ? 'text-green-600' : 'text-yellow-600'}>
                {user?.email_confirmed_at ? '완료' : '미완료'}
              </span>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">계정 상태:</span>
              <span className={user?.banned_until ? 'text-red-600' : 'text-green-600'}>
                {user?.banned_until ? '정지됨' : '활성'}
              </span>
            </div>
          </div>
          
          <Separator />
          
          <div className="space-y-1.5">
            <Button 
              variant="outline" 
              className="w-full justify-start text-red-600 hover:text-red-700" 
              onClick={handleLogout}
              disabled={loading}
            >
              <LogOut className="w-4 h-4 mr-2" />
              {loading ? '로그아웃 중...' : '로그아웃'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 