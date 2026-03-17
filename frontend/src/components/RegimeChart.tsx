// src/components/RegimeChart.tsx
import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";
import type { AnalysisResult } from "../types/regime";

interface Props {
  result: AnalysisResult;
}

export const RegimeChart: React.FC<Props> = ({ result }) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current) return;
    const chart = echarts.init(chartRef.current);
    const history = result.regime_history;

    const getRegimeColor = (regime: string): string => {
      if (regime.includes("Bull")) return "#10b981";
      if (regime.includes("Bear")) return "#ef4444";
      if (regime.includes("Sideways")) return "#f59e0b";
      return "#8b5cf6";
    };

    const dates = history.map((h) => h.date);
    const prices = history.map((h) => h.close ?? null);
    const hasPrices = prices.some((p) => p !== null);

    // ── Build markArea bands: collapse consecutive same-regime into segments ──
    type Band = [
      { xAxis: string; itemStyle: { color: string; opacity: number } },
      { xAxis: string },
    ];
    const bands: Band[] = [];
    let segStart = 0;

    for (let i = 1; i <= history.length; i++) {
      const ended =
        i === history.length || history[i].regime !== history[i - 1].regime;
      if (ended) {
        bands.push([
          {
            xAxis: history[segStart].date,
            itemStyle: {
              color: getRegimeColor(history[i - 1].regime),
              opacity: 0.25,
            },
          },
          { xAxis: history[i - 1].date },
        ]);
        segStart = i;
      }
    }

    // ── Legend entries ──
    const uniqueRegimes = [...new Set(history.map((h) => h.regime))];

    const option: echarts.EChartsOption = {
      backgroundColor: "transparent",
      animation: false,

      legend: {
        data: uniqueRegimes.map((r) => ({
          name: r,
          itemStyle: { color: getRegimeColor(r) },
        })),
        top: 4,
        right: 60,
        textStyle: { color: "#94a3b8", fontSize: 11 },
        itemWidth: 12,
        itemHeight: 12,
        borderRadius: 2,
      },

      toolbox: {
        show: true,
        feature: {
          dataZoom: { title: { zoom: "Zoom", back: "Reset" } },
          saveAsImage: { title: "Export", backgroundColor: "#1e293b" },
        },
        iconStyle: { borderColor: "#94a3b8" },
        right: 8,
        top: 4,
      },

      tooltip: {
        trigger: "axis",
        backgroundColor: "#1e293b",
        borderColor: "#475569",
        borderWidth: 1,
        textStyle: { color: "#f8fafc", fontSize: 12 },
        axisPointer: { lineStyle: { color: "#475569", type: "dashed" } },
        formatter: (params: any) => {
          const p = Array.isArray(params) ? params[0] : params;
          const date = p.axisValue;
          const item = history.find((h) => h.date === date);
          if (!item) return "";
          const color = getRegimeColor(item.regime);
          const priceRow =
            item.close != null
              ? `<div style="color:#94a3b8;margin-top:4px">Close: <b style="color:#f8fafc">$${item.close.toFixed(2)}</b></div>`
              : "";
          return `
            <div style="padding:6px 10px;min-width:140px">
              <div style="font-size:11px;color:#64748b;margin-bottom:6px">${date}</div>
              <div style="display:flex;align-items:center;gap:8px">
                <span style="width:10px;height:10px;border-radius:2px;background:${color};display:inline-block;flex-shrink:0"></span>
                <span style="font-weight:700;font-size:13px">${item.regime}</span>
              </div>
              ${priceRow}
            </div>`;
        },
      },

      dataZoom: [
        {
          type: "slider",
          xAxisIndex: 0,
          bottom: 2,
          height: 18,
          borderColor: "#334155",
          fillerColor: "rgba(99,102,241,0.15)",
          handleStyle: { color: "#6366f1" },
          moveHandleStyle: { color: "#6366f1" },
          textStyle: { color: "#64748b", fontSize: 10 },
          start: 0,
          end: 100,
        },
        { type: "inside", xAxisIndex: 0 },
      ],

      grid: {
        left: 60,
        right: 20,
        top: 40,
        bottom: 50,
      },

      xAxis: {
        type: "category",
        data: dates,
        axisLabel: {
          color: "#64748b",
          fontSize: 10,
          rotate: 30,
          interval: Math.ceil(dates.length / 10),
        },
        axisLine: { lineStyle: { color: "#334155" } },
        splitLine: { show: false },
      },

      yAxis: {
        type: "value",
        name: hasPrices ? "Price (USD)" : "",
        nameTextStyle: { color: "#64748b", fontSize: 10 },
        axisLabel: {
          color: "#64748b",
          fontSize: 10,
          formatter: (v: number) => `$${v.toFixed(0)}`,
        },
        axisLine: { show: false },
        splitLine: { lineStyle: { color: "#1e293b", type: "solid" } },
        scale: true,
      },

      series: [
        // ── Background bands (colored by regime) ──
        {
          name: "Regime Bands",
          type: "line",
          data: hasPrices ? prices : dates.map((_, i) => i),
          lineStyle: { opacity: 0 }, // invisible line, just carries the markArea
          symbol: "none",
          markArea: {
            silent: true,
            data: bands as any,
          },
        },

        // ── Price line, colored segment by segment ──
        ...uniqueRegimes.map((regime) => {
          // Build a sparse data array: only fill in values where this regime is active,
          // null everywhere else — ECharts connects non-null points per series
          const segmentData = history.map((h) =>
            h.regime === regime ? (h.close ?? null) : null,
          );
          return {
            name: regime,
            type: "line" as const,
            data: segmentData,
            connectNulls: false,
            lineStyle: { color: getRegimeColor(regime), width: 2 },
            itemStyle: { color: getRegimeColor(regime) },
            symbol: "none",
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: getRegimeColor(regime)
                    .replace(")", ", 0.15)")
                    .replace("rgb", "rgba"),
                },
                { offset: 1, color: "transparent" },
              ]),
            },
          };
        }),
      ],
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [result]);

  return (
    <div className="chart-section">
      <h3 className="chart-title">
        Market Regime Timeline
        <span
          style={{
            fontSize: "0.7rem",
            color: "#64748b",
            marginLeft: 12,
            fontWeight: 400,
          }}
        >
          {result.regime_history.length} trading days — scroll to zoom
        </span>
      </h3>
      <div ref={chartRef} className="chart-wrapper" />
    </div>
  );
};
