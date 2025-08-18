import React from 'react';
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Mail, CheckCircle, AlertCircle } from "lucide-react";
import { auth } from '../lib/auth';

interface EmailVerificationNoticeProps {
  user: any;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onVerified: () => void;
}

export function EmailVerificationNotice({ user, open, onOpenChange, onVerified }: EmailVerificationNoticeProps) {
  const isEmailVerified = user?.email_confirmed_at;

  const handleResendEmail = async () => {
    try {
      await auth.signUp({
        email: user.email,
        password: '', // 재전송이므로 비밀번호는 필요 없음
        confirmPassword: ''
      });
      alert('인증 이메일을 다시 전송했습니다! 📧\n\n이메일을 확인해주세요.');
    } catch (error) {
      console.error('이메일 재전송 실패:', error);
      alert('이메일 재전송에 실패했습니다. 잠시 후 다시 시도해주세요.');
    }
  };

  const handleCheckVerification = async () => {
    try {
      const isVerified = await auth.checkEmailConfirmation();
      if (isVerified) {
        onVerified();
        onOpenChange(false);
        alert('이메일 인증이 완료되었습니다! 🎉');
      } else {
        alert('아직 이메일 인증이 완료되지 않았습니다.\n\n이메일을 확인하여 인증 링크를 클릭해주세요.');
      }
    } catch (error) {
      console.error('인증 확인 실패:', error);
      alert('인증 상태 확인에 실패했습니다.');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="w-5 h-5" />
            이메일 인증
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {isEmailVerified ? (
            <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <div>
                <p className="font-medium text-green-800">이메일 인증 완료!</p>
                <p className="text-sm text-green-600">
                  {new Date(user.email_confirmed_at).toLocaleString('ko-KR')}
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <div>
                <p className="font-medium text-yellow-800">이메일 인증 필요</p>
                <p className="text-sm text-yellow-600">
                  계정을 활성화하려면 이메일 인증이 필요합니다.
                </p>
              </div>
            </div>
          )}
          
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              <strong>{user?.email}</strong>로 인증 이메일을 전송했습니다.
            </p>
            
            <div className="text-xs text-muted-foreground space-y-1">
              <p>• 이메일을 확인하여 인증 링크를 클릭해주세요</p>
              <p>• 스팸함도 확인해보세요</p>
              <p>• 인증 후 페이지를 새로고침하거나 아래 버튼을 클릭하세요</p>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={handleResendEmail}
              className="flex-1"
            >
              이메일 재전송
            </Button>
            
            <Button 
              onClick={handleCheckVerification}
              className="flex-1"
            >
              인증 확인
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 