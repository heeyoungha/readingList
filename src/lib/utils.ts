import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 사용자 이름 가져오기
export function getUserDisplayName(user: any): string {
  if (user?.user_metadata?.display_name) {
    return user.user_metadata.display_name;
  }
  // 이메일에서 @ 앞부분 추출
  return user?.email?.split('@')[0] || '사용자';
} 