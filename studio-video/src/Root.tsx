import {Composition} from 'remotion';
import {Hello} from './Hello';
export const Root = () => (
  <Composition id="Hello" component={Hello} durationInFrames={300} fps={30} width={1080} height={1920} />
);
