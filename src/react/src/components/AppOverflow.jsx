import React from 'react';
import { bool, node } from 'prop-types';

/*
Wraps a page's content in its own scrolling box. With `scrollsWithPage` the
content is left to scroll with the page instead: a box that scrolls by
itself, and its transform, stop anything inside from staying in view while
the page is scrolled (`position: sticky`), which the Embed settings rely on
to keep the preview beside the settings.
*/
export default function AppOverflow({ children, scrollsWithPage }) {
    if (scrollsWithPage) {
        return <div>{children}</div>;
    }

    return (
        <div
            style={{
                height: '100%',
                overflow: 'auto',
                transform: 'translate3d(0, 0, 0)',
            }}
            className="AppOverflow"
        >
            {children}
        </div>
    );
}

AppOverflow.propTypes = {
    children: node.isRequired,
    scrollsWithPage: bool,
};

AppOverflow.defaultProps = {
    scrollsWithPage: false,
};
