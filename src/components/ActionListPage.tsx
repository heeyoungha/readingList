import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { CheckSquare, User, Calendar, BookOpen, Plus, Clock } from "lucide-react";
import { ActionList } from '../types/actionList';

interface ActionListPageProps {
  actionLists: ActionList[];
  onViewActionList: (actionList: ActionList) => void;
  onAddActionList: () => void;
}

const statusColors = {
  '진행전': 'bg-gray-100 text-gray-800',
  '진행중': 'bg-blue-100 text-blue-800',
  '완료': 'bg-green-100 text-green-800',
  '보류': 'bg-yellow-100 text-yellow-800'
};

export function ActionListPage({ actionLists, onViewActionList, onAddActionList }: ActionListPageProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">액션리스트</h2>
          <p className="text-muted-foreground">
            독서를 통해 얻은 인사이트를 실천으로 옮겨보세요
          </p>
        </div>
        <Button onClick={onAddActionList}>
          <Plus className="w-4 h-4 mr-2" />
          새 액션리스트
        </Button>
      </div>

      {actionLists.length === 0 ? (
        <div className="text-center py-12">
          <CheckSquare className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="mb-2">아직 액션리스트가 없습니다</h3>
          <p className="text-muted-foreground mb-4">
            독후감에서 액션리스트를 추가하거나 직접 생성해보세요
          </p>
          <Button onClick={onAddActionList}>
            <Plus className="w-4 h-4 mr-2" />
            첫 번째 액션리스트 만들기
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {actionLists.map((actionList) => (
            <Card 
              key={actionList.id} 
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => onViewActionList(actionList)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg font-semibold line-clamp-2">
                    {actionList.title}
                  </CardTitle>
                  <Badge 
                    variant="secondary" 
                    className={`${statusColors[actionList.status]} text-xs`}
                  >
                    {actionList.status}
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <User className="w-4 h-4" />
                    <span>{actionList.reader_name}</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <BookOpen className="w-4 h-4" />
                    <span>{actionList.book_title}</span>
                  </div>
                  
                  {actionList.target_months && actionList.target_months.length > 0 && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Calendar className="w-4 h-4" />
                      <span>목표: {actionList.target_months.join(', ')}</span>
                    </div>
                  )}
                  
                  {actionList.action_time && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>{actionList.action_time}</span>
                    </div>
                  )}
                  
                  <p className="text-sm text-muted-foreground line-clamp-3">
                    {actionList.content}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 