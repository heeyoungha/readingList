import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { CheckSquare, User, Calendar, BookOpen, Plus, Clock, Target, Filter, BarChart3 } from "lucide-react";
import { ActionList } from '../types/actionList';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

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

const getQuarterFromTargetMonths = (targetMonths: string[]): string => {
  if (!targetMonths || targetMonths.length === 0) return '미정';
  
  // 첫 번째 목표 월을 기준으로 분기 계산
  const monthName = targetMonths[0];
  const monthMap: { [key: string]: number } = {
    '1월': 1, '2월': 2, '3월': 3, '4월': 4, '5월': 5, '6월': 6,
    '7월': 7, '8월': 8, '9월': 9, '10월': 10, '11월': 11, '12월': 12
  };
  
  const month = monthMap[monthName];
  if (!month) return '미정';
  
  const quarter = Math.ceil(month / 3);
  const currentYear = new Date().getFullYear();
  return `${currentYear}년 ${quarter}분기`;
};

export function ActionListPage({ actionLists, onViewActionList, onAddActionList }: ActionListPageProps) {
  const [selectedQuarter, setSelectedQuarter] = useState<string>('전체');

  // 통계 계산
  const stats = useMemo(() => {
    const total = actionLists.length;
    const statusCounts = actionLists.reduce((acc, action) => {
      acc[action.status] = (acc[action.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      total,
      planned: statusCounts['진행전'] || 0,
      inProgress: statusCounts['진행중'] || 0,
      completed: statusCounts['완료'] || 0,
      onHold: statusCounts['보류'] || 0
    };
  }, [actionLists]);

  // 분기별 분류
  const quarterOptions = useMemo(() => {
    const quarters = new Set<string>();
    actionLists.forEach(action => {
      const quarter = getQuarterFromTargetMonths(action.target_months);
      quarters.add(quarter);
    });
    return ['전체', ...Array.from(quarters).sort()];
  }, [actionLists]);

  // 필터링된 액션리스트
  const filteredActionLists = useMemo(() => {
    if (selectedQuarter === '전체') return actionLists;
    return actionLists.filter(action => 
      getQuarterFromTargetMonths(action.target_months) === selectedQuarter
    );
  }, [actionLists, selectedQuarter]);

  return (
    <div className="space-y-6">
      {/* 헤더 */}
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

      {/* 통계 카드 */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-700">총 액션리스트</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-700">계획됨</p>
                <p className="text-2xl font-bold text-gray-900">{stats.planned}</p>
              </div>
              <Clock className="w-8 h-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-700">진행중</p>
                <p className="text-2xl font-bold text-blue-900">{stats.inProgress}</p>
              </div>
              <Target className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-700">완료</p>
                <p className="text-2xl font-bold text-green-900">{stats.completed}</p>
              </div>
              <CheckSquare className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-700">보류</p>
                <p className="text-2xl font-bold text-yellow-900">{stats.onHold}</p>
              </div>
              <Calendar className="w-8 h-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 분기별 필터 */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">분기별 필터:</span>
        </div>
        <Select value={selectedQuarter} onValueChange={setSelectedQuarter}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {quarterOptions.map(quarter => (
              <SelectItem key={quarter} value={quarter}>
                {quarter}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="text-sm text-muted-foreground">
          {selectedQuarter === '전체' 
            ? `전체 ${actionLists.length}개` 
            : `${selectedQuarter} ${filteredActionLists.length}개`
          }
        </div>
      </div>

      {/* 액션리스트 목록 */}
      {filteredActionLists.length === 0 ? (
        <div className="text-center py-12">
          <CheckSquare className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="mb-2">
            {selectedQuarter === '전체' 
              ? '아직 액션리스트가 없습니다' 
              : `${selectedQuarter}에 해당하는 액션리스트가 없습니다`
            }
          </h3>
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
          {filteredActionLists.map((actionList) => (
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
                      <Badge variant="outline" className="text-xs">
                        {getQuarterFromTargetMonths(actionList.target_months)}
                      </Badge>
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