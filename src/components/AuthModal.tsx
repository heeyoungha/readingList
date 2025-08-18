import React, { useState } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Separator } from "./ui/separator";
import { Mail, Lock, Eye, EyeOff, AlertCircle } from "lucide-react";
import { auth } from '../lib/auth';
import { SignUpData, SignInData } from '../types/auth';

interface AuthModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAuthSuccess: () => void;
}

export function AuthModal({ open, onOpenChange, onAuthSuccess }: AuthModalProps) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<SignUpData & SignInData>({
    email: '',
    password: '',
    confirmPassword: ''
  });

  const [emailOnly, setEmailOnly] = useState('');
  const [loginEmail, setLoginEmail] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await auth.signIn({
        email: formData.email,
        password: formData.password
      });
      onAuthSuccess();
      onOpenChange(false);
    } catch (err: any) {
      setError(err.message || '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailOnlyLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginEmail.trim()) {
      setError('이메일을 입력해주세요.');
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      await auth.signInWithEmail(loginEmail);
      alert(`📧 로그인 링크를 전송했습니다!\n\n${loginEmail}로 전송된 이메일을 확인하여 로그인 링크를 클릭해주세요.`);
      onOpenChange(false);
    } catch (err: any) {
      setError(err.message || '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailOnlySignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailOnly.trim()) {
      setError('이메일을 입력해주세요.');
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      // 임시 비밀번호로 회원가입 (사용자는 모름)
      const tempPassword = Math.random().toString(36).slice(-10) + Math.random().toString(36).slice(-10);
      
      await auth.signUp({
        email: emailOnly,
        password: tempPassword,
        confirmPassword: tempPassword
      });
      
      alert(`📧 인증 이메일을 전송했습니다!\n\n${emailOnly}로 전송된 이메일을 확인하여 인증 링크를 클릭해주세요.\n\n인증 완료 후 자동으로 로그인됩니다.`);
      onOpenChange(false);
    } catch (err: any) {
      setError(err.message || '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({ email: '', password: '', confirmPassword: '' });
    setEmailOnly('');
    setLoginEmail('');
    setError(null);
    setShowPassword(false);
    setShowConfirmPassword(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center">
            {isSignUp ? '회원가입' : '로그인'}
          </DialogTitle>
        </DialogHeader>
        
        {isSignUp ? (
          // 간단한 이메일 전용 회원가입
          <form onSubmit={handleEmailOnlySignUp} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="emailOnly">이메일</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="emailOnly"
                  type="email"
                  value={emailOnly}
                  onChange={(e) => setEmailOnly(e.target.value)}
                  placeholder="이메일을 입력하세요"
                  className="pl-10"
                  required
                />
              </div>
            </div>
            
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? '처리 중...' : '이메일로 회원가입'}
            </Button>
            
            <div className="text-center text-xs text-muted-foreground">
              이메일을 입력하면 인증 링크가 전송됩니다.
            </div>
          </form>
        ) : (
          // 이메일 전용 로그인
          <form onSubmit={handleEmailOnlyLogin} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="loginEmail">이메일</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="loginEmail"
                  type="email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="이메일을 입력하세요"
                  className="pl-10"
                  required
                />
              </div>
            </div>
            
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? '처리 중...' : '이메일로 로그인'}
            </Button>
            
            <div className="text-center text-xs text-muted-foreground">
              이메일을 입력하면 로그인 링크가 전송됩니다.
            </div>
          </form>
        )}
        
        <div className="text-center text-sm">
          {isSignUp ? '이미 계정이 있으신가요?' : '계정이 없으신가요?'}
          <Button
            variant="link"
            className="p-0 h-auto font-normal"
            onClick={() => {
              setIsSignUp(!isSignUp);
              resetForm();
            }}
          >
            {isSignUp ? '로그인하기' : '회원가입하기'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
} 