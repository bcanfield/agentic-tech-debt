import {makeProject} from '@motion-canvas/core';

// Local OFL fonts → deterministic renders, no network at render time.
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/800.css';
import '@fontsource/jetbrains-mono/400.css';
import '@fontsource/jetbrains-mono/500.css';

import main from './scenes/main?scene';

export default makeProject({
  scenes: [main],
});
