import React from 'react';

// Stand-in for SVGs imported as React components via vite-plugin-svgr.
const SvgrMock = React.forwardRef((props, ref) => (
    <svg ref={ref} {...props} />
));
SvgrMock.displayName = 'SvgrMock';

export default SvgrMock;
