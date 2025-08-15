export interface ActionList {
  id: string;
  title: string;
  reader_id: string;
  reader_name: string;
  book_title: string;
  content: string;
  target_months: string[];
  action_time?: string;
  status: '진행전' | '진행중' | '완료' | '보류';
  created_at: string;
  updated_at: string;
}

export interface ActionListStats {
  totalActions: number;
  completedActions: number;
  pendingActions: number;
  inProgressActions: number;
  statusDistribution: Record<string, number>;
} 