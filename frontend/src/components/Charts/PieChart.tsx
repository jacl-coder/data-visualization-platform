import React from 'react';
import { PieChart as RechartsPieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, Spin } from 'antd';

interface PieChartProps {
  title: string;
  data: any[];
  loading?: boolean;
  fields: {
    nameField: string;
    valueField: string;
  };
}

// 定义饼图颜色
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#A28FD0', '#FFC658', '#FF6E76', '#4CAF50', '#E91E63'];

const PieChart: React.FC<PieChartProps> = ({
  title,
  data,
  loading = false,
  fields,
}) => {
  // 数据预处理 - 排序并格式化数据以供Recharts使用
  const processedData = React.useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // 对数据排序（从大到小）并取前10项
    return [...data]
      .sort((a, b) => b[fields.valueField] - a[fields.valueField])
      .slice(0, 10)
      .map(item => ({
        name: item[fields.nameField],
        value: item[fields.valueField]
      }));
  }, [data, fields]);

  // 计算总和以便计算百分比
  const total = processedData.reduce((sum, item) => sum + item.value, 0);

  if (loading) {
    return (
      <Card title={title}>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin />
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card title={title}>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <p>暂无数据</p>
        </div>
      </Card>
    );
  }

  return (
    <Card title={title}>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsPieChart>
            <Pie
              data={processedData}
              cx="50%"
              cy="50%"
              labelLine={true}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
            >
              {processedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value: number) => [`${value} (${((value / total) * 100).toFixed(1)}%)`, '值']} 
              labelFormatter={(name) => `${name}`}
            />
            <Legend />
          </RechartsPieChart>
        </ResponsiveContainer>
      </div>

      {/* 表格视图作为补充 */}
      <div style={{ marginTop: 20, width: '100%', maxHeight: 200, overflow: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={tableHeaderStyle}>{fields.nameField}</th>
              <th style={tableHeaderStyle}>{fields.valueField}</th>
              <th style={tableHeaderStyle}>百分比</th>
            </tr>
          </thead>
          <tbody>
            {processedData.map((item, index) => {
              const percentage = (item.value / total * 100).toFixed(1);
              return (
                <tr key={index} style={index % 2 === 0 ? { background: '#f9f9f9' } : {}}>
                  <td style={tableCellStyle}>{item.name}</td>
                  <td style={tableCellStyle}>{item.value}</td>
                  <td style={tableCellStyle}>{percentage}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

const tableHeaderStyle: React.CSSProperties = {
  padding: '10px',
  textAlign: 'left',
  borderBottom: '2px solid #ddd',
  fontWeight: 'bold'
};

const tableCellStyle: React.CSSProperties = {
  padding: '8px',
  textAlign: 'left',
  borderBottom: '1px solid #ddd'
};

export default PieChart; 