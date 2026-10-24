import React, { useState } from 'react';
import { Activity, Zap, Info } from 'lucide-react';

export default function EcgWaveform({ signal, saliency, lead = "II", fs = 100 }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  if (!signal || signal.length === 0) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontStyle: 'italic' }}>
        No ECG waveform data available to render.
      </div>
    );
  }

  const svgWidth = 900;
  const svgHeight = 220;
  const paddingX = 20;
  const paddingY = 25;
  const drawWidth = svgWidth - paddingX * 2;
  const drawHeight = svgHeight - paddingY * 2;

  // Scale calculations: map sample index to X, voltage to Y
  const numPoints = signal.length;
  const minV = Math.min(-0.8, ...signal);
  const maxV = Math.max(1.8, ...signal);
  const rangeV = (maxV - minV) || 2.0;

  const getX = (idx) => paddingX + (idx / (numPoints - 1)) * drawWidth;
  const getY = (val) => paddingY + drawHeight - ((val - minV) / rangeV) * drawHeight;

  // Generate SVG path points
  const points = signal.map((v, i) => `${getX(i).toFixed(1)},${getY(v).toFixed(1)}`).join(' ');

  // Saliency segments: split points into segments for colored strokes or highlights
  // Find high-saliency zones (saliency > 0.6)
  const highSaliencyIntervals = [];
  if (saliency && saliency.length === signal.length) {
    let inInterval = false;
    let startIdx = 0;
    for (let i = 0; i < saliency.length; i++) {
      if (saliency[i] >= 0.55 && !inInterval) {
        inInterval = true;
        startIdx = i;
      } else if (saliency[i] < 0.55 && inInterval) {
        inInterval = false;
        highSaliencyIntervals.push({ start: startIdx, end: i - 1 });
      }
    }
    if (inInterval) {
      highSaliencyIntervals.push({ start: startIdx, end: saliency.length - 1 });
    }
  }

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const normX = (mouseX / rect.width) * svgWidth;
    const sampleIdx = Math.round(((normX - paddingX) / drawWidth) * (numPoints - 1));
    if (sampleIdx >= 0 && sampleIdx < numPoints) {
      setHoveredIndex(sampleIdx);
    } else {
      setHoveredIndex(null);
    }
  };

  const hoveredVoltage = hoveredIndex !== null ? signal[hoveredIndex] : null;
  const hoveredSaliency = (hoveredIndex !== null && saliency && saliency[hoveredIndex]) !== undefined 
    ? saliency[hoveredIndex] 
    : null;
  const hoveredTime = hoveredIndex !== null ? (hoveredIndex / fs).toFixed(2) : null;

  return (
    <div style={{ background: '#0F1714', borderRadius: 'var(--radius-md)', padding: '16px', border: '1px solid #1E2D27' }}>
      {/* Header telemetry ribbon */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ 
            fontFamily: 'var(--font-mono)', fontSize: '0.74rem', fontWeight: 600, 
            background: 'rgba(63, 143, 107, 0.2)', color: '#4ADE80', 
            padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(74, 222, 128, 0.3)' 
          }}>
            Lead {lead} Rhythm Strip
          </span>
          <span style={{ fontSize: '0.72rem', color: '#94A3B8', fontFamily: 'var(--font-mono)' }}>
            25 mm/s • 10 mm/mV • {fs} Hz • {(numPoints / fs).toFixed(1)}s Duration
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#38BDF8' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#38BDF8' }} />
            Cardiac Signal
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#F59E0B' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#F59E0B' }} />
            Temporal Saliency Focus (&gt;0.55)
          </span>
        </div>
      </div>

      {/* SVG Container */}
      <div style={{ position: 'relative', width: '100%', overflowX: 'auto' }}>
        <svg 
          viewBox={`0 0 ${svgWidth} ${svgHeight}`} 
          style={{ width: '100%', height: 'auto', display: 'block', cursor: 'crosshair' }}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoveredIndex(null)}
        >
          <defs>
            {/* Minor grid pattern */}
            <pattern id="ecgMinorGrid" width="10" height="10" patternUnits="userSpaceOnUse">
              <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(42, 60, 52, 0.4)" strokeWidth="0.5" />
            </pattern>
            {/* Major grid pattern */}
            <pattern id="ecgMajorGrid" width="50" height="50" patternUnits="userSpaceOnUse">
              <rect width="50" height="50" fill="url(#ecgMinorGrid)" />
              <path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(52, 85, 70, 0.6)" strokeWidth="1" />
            </pattern>
            {/* Glow filter */}
            <filter id="ecgGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background Grid */}
          <rect width={svgWidth} height={svgHeight} fill="#09110E" />
          <rect width={svgWidth} height={svgHeight} fill="url(#ecgMajorGrid)" />

          {/* Isoelectric Zero Reference Line */}
          <line 
            x1={paddingX} 
            y1={getY(0)} 
            x2={svgWidth - paddingX} 
            y2={getY(0)} 
            stroke="rgba(148, 163, 184, 0.25)" 
            strokeDasharray="4 4" 
            strokeWidth="1" 
          />
          <text 
            x={paddingX + 4} 
            y={getY(0) - 4} 
            fill="rgba(148, 163, 184, 0.5)" 
            fontSize="9" 
            fontFamily="var(--font-mono)"
          >
            0.0 mV
          </text>

          {/* High Saliency Attention Shading / Interval Highlights */}
          {highSaliencyIntervals.map((interval, i) => {
            const x1 = getX(interval.start);
            const x2 = getX(interval.end);
            return (
              <g key={`sal-int-${i}`}>
                <rect 
                  x={x1} 
                  y={paddingY} 
                  width={Math.max(x2 - x1, 4)} 
                  height={drawHeight} 
                  fill="rgba(245, 158, 11, 0.12)" 
                />
                <line 
                  x1={x1} y1={paddingY} 
                  x2={x1} y2={paddingY + drawHeight} 
                  stroke="rgba(245, 158, 11, 0.4)" 
                  strokeWidth="0.8" 
                  strokeDasharray="2 2" 
                />
                <line 
                  x1={x2} y1={paddingY} 
                  x2={x2} y2={paddingY + drawHeight} 
                  stroke="rgba(245, 158, 11, 0.4)" 
                  strokeWidth="0.8" 
                  strokeDasharray="2 2" 
                />
              </g>
            );
          })}

          {/* Waveform Base Polyline */}
          <polyline 
            fill="none" 
            stroke="#38BDF8" 
            strokeWidth="1.8" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            points={points} 
          />

          {/* High-Saliency Segment Overlays */}
          {highSaliencyIntervals.map((interval, i) => {
            const subPoints = signal
              .slice(interval.start, interval.end + 1)
              .map((v, idx) => `${getX(interval.start + idx).toFixed(1)},${getY(v).toFixed(1)}`)
              .join(' ');
            return (
              <polyline 
                key={`sal-wave-${i}`}
                fill="none" 
                stroke="#F59E0B" 
                strokeWidth="2.4" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                filter="url(#ecgGlow)"
                points={subPoints} 
              />
            );
          })}

          {/* Hover Crosshair Marker */}
          {hoveredIndex !== null && (
            <g>
              <line 
                x1={getX(hoveredIndex)} y1={paddingY} 
                x2={getX(hoveredIndex)} y2={paddingY + drawHeight} 
                stroke="#E2E8F0" 
                strokeWidth="1" 
                strokeDasharray="3 3" 
              />
              <circle 
                cx={getX(hoveredIndex)} 
                cy={getY(signal[hoveredIndex])} 
                r="4.5" 
                fill="#F59E0B" 
                stroke="#FFFFFF" 
                strokeWidth="1.5" 
              />
            </g>
          )}

          {/* Bottom Saliency Density Bar */}
          {saliency && (
            <g transform={`translate(${paddingX}, ${svgHeight - 12})`}>
              {saliency.map((s, idx) => {
                if (idx % 2 !== 0) return null; // optimize SVG dom elements
                const x = (idx / (numPoints - 1)) * drawWidth;
                const w = (2 / (numPoints - 1)) * drawWidth;
                const r = Math.round(245 * s);
                const g = Math.round(158 * (1 - s) + 80 * s);
                const b = Math.round(11 * (1 - s));
                return (
                  <rect 
                    key={`bar-${idx}`} 
                    x={x} 
                    y="0" 
                    width={Math.max(w, 1.2)} 
                    height="7" 
                    fill={`rgba(${r}, ${g}, ${b}, ${0.2 + s * 0.8})`} 
                  />
                );
              })}
            </g>
          )}
        </svg>
      </div>

      {/* Interactive Readout Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px', fontSize: '0.72rem', color: '#94A3B8', fontFamily: 'var(--font-mono)' }}>
        <div>
          {hoveredIndex !== null ? (
            <span>
              Time: <strong style={{ color: '#E2E8F0' }}>{hoveredTime}s</strong> | Voltage: <strong style={{ color: '#38BDF8' }}>{hoveredVoltage?.toFixed(3)} mV</strong> | Saliency: <strong style={{ color: '#F59E0B' }}>{((hoveredSaliency || 0) * 100).toFixed(1)}%</strong>
            </span>
          ) : (
            <span>Hover over waveform tracing to inspect millivolts & temporal attribution.</span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Zap size={11} color="#F59E0B" />
          <span>Gradient Saliency Attribution</span>
        </div>
      </div>
    </div>
  );
}
