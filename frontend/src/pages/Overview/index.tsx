import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Spin, DatePicker, Statistic } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { getOverview, getTimeline, getCountryData, getDeviceData } from '../../services/api';
import { useDateContext } from '../../hooks/useDateContext';
import { formatCurrency, formatNumber } from '../../utils/formatters';
import TimelineChart from '../../components/Charts/TimelineChart';
import PieChart from '../../components/Charts/PieChart';
import DonutChart from '../../components/Charts/DonutChart';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const OverviewPage: React.FC = () => {
  const { dateRange, setDateRange } = useDateContext();
  
  const [loading, setLoading] = useState<boolean>(true);
  const [overviewData, setOverviewData] = useState<any>(null);
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [countryData, setCountryData] = useState<any[]>([]);
  const [deviceData, setDeviceData] = useState<any[]>([]);

  // 加载概览数据
  useEffect(() => {
    const fetchOverviewData = async () => {
      setLoading(true);
      try {
        const overview = await getOverview();
        setOverviewData(overview);
      } catch (error) {
        console.error('获取概览数据失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOverviewData();
  }, []);

  // 加载时间线数据
  useEffect(() => {
    const fetchTimelineData = async () => {
      try {
        const days = 30; // 默认获取30天数据
        const timeline = await getTimeline(days);
        setTimelineData(timeline.items || []);
      } catch (error) {
        console.error('获取时间线数据失败:', error);
      }
    };

    fetchTimelineData();
  }, []);

  // 加载国家数据和设备数据
  useEffect(() => {
    const fetchDistributionData = async () => {
      try {
        const [countries, devices] = await Promise.all([
          getCountryData(),
          getDeviceData()
        ]);
        setCountryData(countries.items || []);
        setDeviceData(devices.items || []);
      } catch (error) {
        console.error('获取分布数据失败:', error);
      }
    };

    fetchDistributionData();
  }, []);

  // 处理日期范围变化
  const handleDateRangeChange = (dates: any) => {
    if (dates && dates.length === 2) {
      const startDate = dayjs(dates[0]).format('YYYY-MM-DD');
      const endDate = dayjs(dates[1]).format('YYYY-MM-DD');
      setDateRange([startDate, endDate]);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="overview-page">
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Card title="日期选择">
            <RangePicker
              value={[dayjs(dateRange[0]), dayjs(dateRange[1])]}
              onChange={handleDateRangeChange}
              style={{ width: '100%' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="用户数"
              value={overviewData?.user_count || 0}
              formatter={(value) => formatNumber(value as number)}
              prefix={<ArrowUpOutlined style={{ color: '#3f8600' }} />}
              suffix={<span style={{ fontSize: '14px', color: '#3f8600' }}>1%</span>}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="事件数"
              value={overviewData?.event_count || 0}
              formatter={(value) => formatNumber(value as number)}
              prefix={<ArrowUpOutlined style={{ color: '#3f8600' }} />}
              suffix={<span style={{ fontSize: '14px', color: '#3f8600' }}>1%</span>}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="设备数"
              value={overviewData?.device_count || 0}
              formatter={(value) => formatNumber(value as number)}
              prefix={<ArrowUpOutlined style={{ color: '#3f8600' }} />}
              suffix={<span style={{ fontSize: '14px', color: '#3f8600' }}>1%</span>}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总收入"
              value={overviewData?.total_revenue || 0}
              formatter={(value) => formatCurrency(value as number)}
              prefix={<ArrowDownOutlined style={{ color: '#cf1322' }} />}
              suffix={<span style={{ fontSize: '14px', color: '#cf1322' }}>1%</span>}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <TimelineChart
            title="日期趋势图"
            data={timelineData}
            fields={{
              xField: 'date',
              yFields: [
                { key: 'user_count', title: '用户数', color: '#1890ff' },
                { key: 'revenue', title: '收入', color: '#faad14' },
              ],
            }}
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <DonutChart
            title="国家分布"
            data={countryData.map(item => ({
              country: item.country,
              value: item.users,
            }))}
            fields={{
              nameField: 'country',
              valueField: 'value',
            }}
          />
        </Col>
        <Col xs={24} md={12}>
          <DonutChart
            title="设备分布"
            data={deviceData.map(item => ({
              device: item.device,
              value: item.users,
            }))}
            fields={{
              nameField: 'device',
              valueField: 'value',
            }}
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} md={12}>
          <PieChart
            title="国家收入分布"
            data={countryData}
            fields={{
              nameField: 'country',
              valueField: 'revenue',
            }}
          />
        </Col>
        <Col xs={24} md={12}>
          <PieChart
            title="设备收入分布"
            data={deviceData}
            fields={{
              nameField: 'device',
              valueField: 'revenue',
            }}
          />
        </Col>
      </Row>
    </div>
  );
};

export default OverviewPage; 