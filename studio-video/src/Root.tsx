import {Composition} from 'remotion';
import {Hello} from './Hello';
import {Counting, COUNTING_FRAMES} from './Counting';
export const Root = () => (
  <>
    <Composition id="Hello" component={Hello} durationInFrames={300} fps={30} width={1080} height={1920} />
    <Composition id="Counting" component={Counting} durationInFrames={COUNTING_FRAMES} fps={30} width={1080} height={1920} />
  </>
);
