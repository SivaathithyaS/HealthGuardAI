import React, { useState } from 'react';
import { Eye, Layers, Sliders, Maximize2, Shield } from 'lucide-react';

export default function HeatmapOverlay({ originalImage, heatmapBase64, sliceLabel = "Axial T1-Gd MRI Slice" }) {
  const [opacity, setOpacity] = useState(0.65);
  const [viewMode, setViewMode] = useState('overlay'); // 'overlay' | 'side-by-side' | 'anatomy' | 'heatmap'

  // Format heatmap src: support raw base64 or prefixed
  const heatmapSrc = heatmapBase64 
    ? (heatmapBase64.startsWith('data:') ? heatmapBase64 : `data:image/png;base64,${heatmapBase64}`)
    : null;

  // Fallback synthetic anatomical slice if originalImage isn't provided (e.g. from backend sample)
  const defaultAnatomySvg = (
    <svg viewBox="0 0 224 224" style={{ width: '100%', height: '100%', display: 'block', background: '#090D0C' }}>
      {/* Cranium */}
      <ellipse cx="112" cy="112" rx="92" ry="92" fill="#4B5563" stroke="#9CA3AF" strokeWidth="3" />
      {/* Brain parenchyma */}
      <ellipse cx="112" cy="112" rx="84" ry="84" fill="#374151" />
      {/* Lateral ventricles */}
      <ellipse cx="98" cy="108" rx="8" ry="22" fill="#111827" />
      <ellipse cx="126" cy="108" rx="8" ry="22" fill="#111827" />
      {/* Internal capsule & basal ganglia */}
      <ellipse cx="88" cy="116" rx="6" ry="12" fill="#4B5563" />
      <ellipse cx="136" cy="116" rx="6" ry="12" fill="#4B5563" />
    </svg>
  );

  return (
    <div style={{ background: '#0F1714', borderRadius: 'var(--radius-md)', padding: '16px', border: '1px solid #1E2D27' }}>
      {/* Header Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={14} color="#4ADE80" />
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#E2E8F0', fontFamily: 'var(--font-mono)' }}>
            {sliceLabel}
          </span>
        </div>

        {/* View Mode Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', background: '#1E2D27', padding: '3px', borderRadius: '6px' }}>
          <button
            onClick={() => setViewMode('overlay')}
            style={{
              background: viewMode === 'overlay' ? 'var(--brand-accent)' : 'transparent',
              color: viewMode === 'overlay' ? '#FFF' : '#94A3B8',
              border: 'none', borderRadius: '4px', padding: '3px 8px', fontSize: '0.7rem',
              cursor: 'pointer', fontWeight: 600
            }}
          >
            Overlay
          </button>
          <button
            onClick={() => setViewMode('side-by-side')}
            style={{
              background: viewMode === 'side-by-side' ? 'var(--brand-accent)' : 'transparent',
              color: viewMode === 'side-by-side' ? '#FFF' : '#94A3B8',
              border: 'none', borderRadius: '4px', padding: '3px 8px', fontSize: '0.7rem',
              cursor: 'pointer', fontWeight: 600
            }}
          >
            Side-by-Side
          </button>
          <button
            onClick={() => setViewMode('anatomy')}
            style={{
              background: viewMode === 'anatomy' ? 'var(--brand-accent)' : 'transparent',
              color: viewMode === 'anatomy' ? '#FFF' : '#94A3B8',
              border: 'none', borderRadius: '4px', padding: '3px 8px', fontSize: '0.7rem',
              cursor: 'pointer', fontWeight: 600
            }}
          >
            Anatomy
          </button>
          <button
            onClick={() => setViewMode('heatmap')}
            style={{
              background: viewMode === 'heatmap' ? 'var(--brand-accent)' : 'transparent',
              color: viewMode === 'heatmap' ? '#FFF' : '#94A3B8',
              border: 'none', borderRadius: '4px', padding: '3px 8px', fontSize: '0.7rem',
              cursor: 'pointer', fontWeight: 600
            }}
          >
            Heatmap
          </button>
        </div>
      </div>

      {/* Main Display Container */}
      {viewMode === 'side-by-side' ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', alignItems: 'center', justifyContent: 'center' }}>
          {/* Anatomy Frame */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ position: 'relative', width: '224px', height: '224px', margin: '0 auto', borderRadius: '8px', overflow: 'hidden', border: '1px solid #2D3748' }}>
              {originalImage ? (
                <img src={originalImage} alt="Anatomical MRI" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              ) : (
                defaultAnatomySvg
              )}
            </div>
            <div style={{ marginTop: '6px', fontSize: '0.7rem', color: '#94A3B8', fontFamily: 'var(--font-mono)' }}>
              Axial MRI Slice (Input)
            </div>
          </div>

          {/* Heatmap Frame */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ position: 'relative', width: '224px', height: '224px', margin: '0 auto', borderRadius: '8px', overflow: 'hidden', border: '1px solid #2D3748', background: '#090D0C' }}>
              {heatmapSrc ? (
                <img src={heatmapSrc} alt="Grad-CAM Heatmap" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              ) : (
                <div style={{ padding: '80px 10px', color: '#94A3B8', fontSize: '0.74rem' }}>Generating Heatmap...</div>
              )}
            </div>
            <div style={{ marginTop: '6px', fontSize: '0.7rem', color: '#F59E0B', fontFamily: 'var(--font-mono)' }}>
              Grad-CAM Class Activation Map
            </div>
          </div>
        </div>
      ) : (
        /* Overlay / Single Mode */
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ 
            position: 'relative', 
            width: '260px', 
            height: '260px', 
            borderRadius: '8px', 
            overflow: 'hidden', 
            border: '1px solid #2D3748',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            background: '#090D0C'
          }}>
            {/* Layer 1: Anatomical Base (hidden in 'heatmap' mode) */}
            {viewMode !== 'heatmap' && (
              <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
                {originalImage ? (
                  <img src={originalImage} alt="Anatomical MRI" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                ) : (
                  defaultAnatomySvg
                )}
              </div>
            )}

            {/* Layer 2: Grad-CAM Heatmap (hidden in 'anatomy' mode) */}
            {viewMode !== 'anatomy' && heatmapSrc && (
              <img 
                src={heatmapSrc} 
                alt="Grad-CAM Activation" 
                style={{ 
                  position: 'absolute', 
                  top: 0, 
                  left: 0, 
                  width: '100%', 
                  height: '100%', 
                  objectFit: 'contain',
                  opacity: viewMode === 'heatmap' ? 1.0 : opacity,
                  transition: 'opacity 0.15s ease'
                }} 
              />
            )}

            {/* Crosshair coordinate markers */}
            <div style={{ position: 'absolute', top: '10px', left: '10px', fontSize: '0.66rem', color: 'rgba(255,255,255,0.6)', fontFamily: 'var(--font-mono)' }}>
              R
            </div>
            <div style={{ position: 'absolute', top: '10px', right: '10px', fontSize: '0.66rem', color: 'rgba(255,255,255,0.6)', fontFamily: 'var(--font-mono)' }}>
              L
            </div>
            <div style={{ position: 'absolute', bottom: '10px', left: '10px', fontSize: '0.66rem', color: 'rgba(255,255,255,0.6)', fontFamily: 'var(--font-mono)' }}>
              A
            </div>
            <div style={{ position: 'absolute', bottom: '10px', right: '10px', fontSize: '0.66rem', color: 'rgba(255,255,255,0.6)', fontFamily: 'var(--font-mono)' }}>
              P
            </div>
          </div>
        </div>
      )}

      {/* Opacity Slider Control (in overlay mode) */}
      {viewMode === 'overlay' && (
        <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', color: '#94A3B8', fontFamily: 'var(--font-mono)' }}>
            <Sliders size={12} />
            <span>Heatmap Blend:</span>
          </div>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.05" 
            value={opacity} 
            onChange={(e) => setOpacity(parseFloat(e.target.value))}
            style={{ width: '160px', accentColor: '#4ADE80', cursor: 'pointer' }}
          />
          <span style={{ fontSize: '0.72rem', color: '#E2E8F0', fontFamily: 'var(--font-mono)', minWidth: '40px' }}>
            {Math.round(opacity * 100)}%
          </span>
        </div>
      )}

      {/* Grad-CAM Colorbar Legend */}
      <div style={{ marginTop: '12px', borderTop: '1px solid #1E2D27', paddingTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ fontSize: '0.7rem', color: '#94A3B8', fontFamily: 'var(--font-mono)' }}>
          Grad-CAM Saliency Attribution:
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.68rem', color: '#64748B', fontFamily: 'var(--font-mono)' }}>0.0 (Low)</span>
          <div style={{ 
            width: '120px', 
            height: '8px', 
            borderRadius: '4px', 
            background: 'linear-gradient(to right, #0000FF, #00FFFF, #00FF00, #FFFF00, #FF0000)' 
          }} />
          <span style={{ fontSize: '0.68rem', color: '#EF4444', fontFamily: 'var(--font-mono)' }}>1.0 (Peak)</span>
        </div>
      </div>
    </div>
  );
}
