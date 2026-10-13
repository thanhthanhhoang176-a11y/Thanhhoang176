import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';
const colors = ['#ff6b6b', '#ffa94d', '#51cf66', '#339af0', '#cc5de8'];
export const Hello = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const text = 'Xin chào các bé!';
  return (
    <AbsoluteFill style={{background: 'linear-gradient(180deg,#ffe3ec,#e3f2ff)', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', padding: 60, fontFamily: 'Arial Rounded MT Bold, Arial, sans-serif', fontSize: 130, fontWeight: 900}}>
        {text.split(' ').map((w, i) => {
          const s = spring({frame: frame - i * 8, fps, config: {damping: 8}});
          const y = interpolate(Math.sin((frame + i * 10) / 8), [-1, 1], [-15, 15]);
          return <span key={i} style={{color: colors[i % 5], margin: '0 20px', transform: `scale(${s}) translateY(${y}px)`, display: 'inline-block'}}>{w}</span>;
        })}
      </div>
    </AbsoluteFill>
  );
};
