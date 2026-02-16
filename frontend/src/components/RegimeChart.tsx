import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { AnalysisResult } from '../types/regime';

interface Props {
  result: AnalysisResult;
}

export const RegimeChart: React.FC<Props> = ({ result }) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    const chart = echarts.init(chartRef.current);

    const dates = result.regime_history.map(item => item.date);
    const regimes = result.regime_history.map(item => item.regime);

    const getRegimeColor = (regime: string) => {
      if (regime.includes('Bull')) return '#10b981';
      if (regime.includes('Bear')) return '#ef4444';
      if (regime.includes('Sideways') || regime.includes('High')) return '#f59e0b';
      return '#8b5cf6';
    };

    const uniqueRegimes = [...new Set(regimes)].sort();

    const option: echarts.EChartsOption = {
      backgroundColor: 'transparent',
      // Thêm toolbox để export ảnh cho báo cáo
      toolbox: {
        show: true,
        feature: {
          saveAsImage: { title: 'Export', backgroundColor: '#1e293b' }
        },
        iconStyle: { borderColor: '#94a3b8' },
        right: 20
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#1e293b',
        borderColor: '#475569',
        borderWidth: 1,
        textStyle: { color: '#f8fafc', fontSize: 13 },
        formatter: (params: any) => {
          const data = params[0];
          const color = getRegimeColor(data.value);
          return `
            <div style="padding: 4px 8px">
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px">${data.name}</div>
              <div style="display: flex; align-items: center; gap: 8px">
                <span style="width: 10px; height: 10px; border-radius: 50%; background: ${color}"></span>
                <span style="font-weight: 700">${data.value}</span>
              </div>
            </div>
          `;
        }
      },
      grid: {
        left: '5%',
        right: '5%',
        bottom: '15%',
        top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          color: '#64748b',
          fontSize: 10,
          rotate: 30,
          interval: Math.ceil(dates.length / 15)
        },
        axisLine: { lineStyle: { color: '#334155' } },
        splitLine: { show: false }
      },
      yAxis: {
        type: 'category',
        data: uniqueRegimes,
        axisLabel: {
          color: '#cbd5e1',
          fontSize: 12,
          fontWeight: 600
        },
        axisLine: { show: false },
        splitLine: { 
          show: true, 
          lineStyle: { color: '#334155', type: 'dashed' } 
        }
      },
      series: [{
        name: 'Regime',
        type: 'line',
        data: regimes,
        step: 'end',
        lineStyle: { width: 3, color: '#6366f1' },
        itemStyle: {
          color: (params: any) => getRegimeColor(params.value)
        },
        // Area style tạo hiệu ứng chuyển màu chuyên nghiệp
        areaStyle: {
          opacity: 0.1,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#6366f1' },
            { offset: 1, color: 'transparent' }
          ])
        },
        symbol: 'circle',
        symbolSize: 8,
        showSymbol: false,
        sampling: 'lttb'
      }]
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.dispose();
    };
  }, [result]);

  return (
    <div className="chart-section">
      <h3 className="chart-title">Market Regime Timeline</h3>
      <div ref={chartRef} className="chart-wrapper" />
    </div>
  );
};