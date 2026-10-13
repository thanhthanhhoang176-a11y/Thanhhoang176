import {AbsoluteFill, Audio, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

const FPS = 30;
const TOTAL = Math.ceil(21.1 * FPS);

type Scene = {from: number; icon: string; count: number; big: string; sub: string; bg: string};
const scenes: Scene[] = [
  {from: 0, icon: '👋', count: 1, big: 'Xin chào các bé!', sub: 'Hôm nay mình cùng đếm số nhé!', bg: 'linear-gradient(180deg,#ffe3ec,#e3f2ff)'},
  {from: 3.4, icon: '🍎', count: 1, big: '1', sub: 'Một. Có một quả táo đỏ tròn xoe.', bg: 'linear-gradient(180deg,#ffe0e0,#fff3e0)'},
  {from: 6.6, icon: '🦆', count: 2, big: '2', sub: 'Hai. Hai chú vịt con đang bơi.', bg: 'linear-gradient(180deg,#fff9c4,#e1f5fe)'},
  {from: 9.4, icon: '🌸', count: 3, big: '3', sub: 'Ba. Ba bông hoa xinh xinh.', bg: 'linear-gradient(180deg,#fce4ec,#f3e5f5)'},
  {from: 12.0, icon: '🦋', count: 4, big: '4', sub: 'Bốn. Bốn chú bướm bay lượn.', bg: 'linear-gradient(180deg,#e0f7fa,#e8f5e9)'},
  {from: 14.5, icon: '⭐', count: 5, big: '5', sub: 'Năm. Năm ngôi sao lấp lánh.', bg: 'linear-gradient(180deg,#311b92,#5c6bc0)'},
  {from: 17.0, icon: '🎉', count: 1, big: 'Giỏi quá!', sub: 'Các bé đếm được đến năm rồi! Hẹn gặp lại các bé nhé!', bg: 'linear-gradient(180deg,#fff3e0,#ffe0b2)'},
];
const colors = ['#ff6b6b', '#ffa94d', '#51cf66', '#339af0', '#cc5de8'];

const SceneView: React.FC<{s: Scene; dark: boolean}> = ({s, dark}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const isNum = /^\d$/.test(s.big);
  const pop = spring({frame, fps, config: {damping: 9}});
  return (
    <AbsoluteFill style={{background: s.bg, alignItems: 'center', justifyContent: 'center', fontFamily: 'Arial Rounded MT Bold, Arial, sans-serif'}}>
      <div style={{fontSize: isNum ? 420 : 130, fontWeight: 900, color: isNum ? colors[(Number(s.big) - 1) % 5] : '#e8590c', transform: `scale(${pop})`, textAlign: 'center', padding: '0 60px', lineHeight: 1.1, textShadow: '0 8px 0 rgba(0,0,0,0.12)'}}>
        {s.big}
      </div>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', width: 900, marginTop: 40, minHeight: 300}}>
        {Array.from({length: s.count}).map((_, i) => {
          const p = spring({frame: frame - 6 - i * 7, fps, config: {damping: 7}});
          const bob = Math.sin((frame + i * 9) / 7) * 14;
          return <span key={i} style={{fontSize: s.count > 3 ? 190 : 230, transform: `scale(${p}) translateY(${bob}px)`, display: 'inline-block', margin: 8}}>{s.icon}</span>;
        })}
      </div>
      <div style={{position: 'absolute', bottom: 220, width: 920, textAlign: 'center', fontSize: 62, fontWeight: 800, lineHeight: 1.25, color: dark ? '#fff' : '#3b2f2f', background: dark ? 'rgba(0,0,0,0.35)' : 'rgba(255,255,255,0.8)', borderRadius: 40, padding: '28px 36px', opacity: interpolate(frame, [0, 8], [0, 1], {extrapolateRight: 'clamp'})}}>
        {s.sub}
      </div>
    </AbsoluteFill>
  );
};

export const Counting = () => (
  <AbsoluteFill>
    {scenes.map((s, i) => {
      const from = Math.round(s.from * FPS);
      const end = i + 1 < scenes.length ? Math.round(scenes[i + 1].from * FPS) : TOTAL;
      return (
        <Sequence key={i} from={from} durationInFrames={end - from}>
          <SceneView s={s} dark={i === 5} />
        </Sequence>
      );
    })}
    <Audio src={staticFile('voice.mp3')} />
  </AbsoluteFill>
);
export const COUNTING_FRAMES = TOTAL;
