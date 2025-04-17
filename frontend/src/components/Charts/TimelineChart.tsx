import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, Spin } from 'antd';

interface TimelineChartProps {
  title: string;
  data: any[];
  loading?: boolean;
  fields: {
    xField: string;
    yFields: {
      key: string;
      title: string;
      color: string;
    }[];
  };
}

const TimelineChart: React.FC<TimelineChartProps> = ({
  title,
  data,
  loading = false,
  fields,
}) => {
  // 数据预处理 - 确保日期排序
  const processedData = React.useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // 对数据按日期排序
    return [...data].sort((a, b) => {
      const dateA = new Date(a[fields.xField]).getTime();
      const dateB = new Date(b[fields.xField]).getTime();
      return dateA - dateB;
    });
  }, [data, fields.xField]);

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
          <LineChart
            data={processedData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey={fields.xField} 
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}-${date.getDate()}`;
              }}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(value) => {
                const date = new Date(value);
                return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
              }}
              formatter={(value: number, name: string) => [value, name]}
            />
            <Legend />
            {fields.yFields.map((field) => (
              <Line
                key={field.key}
                type="monotone"
                dataKey={field.key}
                name={field.title}
                stroke={field.color}
                activeDot={{ r: 8 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 表格视图作为补充 */}
      <div style={{ marginTop: 20, width: '100%', maxHeight: 200, overflow: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={tableHeaderStyle}>{fields.xField}</th>
              {fields.yFields.map((field) => (
                <th 
                  key={field.key} 
                  style={{ ...tableHeaderStyle, color: field.color }}
                >
                  {field.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {processedData.map((item, index) => (
              <tr key={index} style={index % 2 === 0 ? { background: '#f9f9f9' } : {}}>
                <td style={tableCellStyle}>
                  {new Date(item[fields.xField]).toISOString().split('T')[0]}
                </td>
                {fields.yFields.map((field) => (
                  <td 
                    key={field.key} 
                    style={tableCellStyle}
                  >
                    {item[field.key]}
                  </td>
                ))}
              </tr>
            ))}
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

export default TimelineChart; 