"use client"

interface ChartProps {
  data: Array<{
    name: string;
    total: number;
  }>
}

export function Chart({ data }: ChartProps) {
  return (
    <div className="w-full h-[350px] flex items-end justify-between p-4 bg-muted rounded-lg">
      {data.map((item, index) => (
        <div key={index} className="flex flex-col items-center">
          <div 
            className="bg-primary rounded-t"
            style={{ 
              height: `${(item.total / Math.max(...data.map(d => d.total))) * 200}px`,
              width: '20px'
            }}
          />
          <span className="text-xs mt-2">{item.name}</span>
        </div>
      ))}
    </div>
  )
} 