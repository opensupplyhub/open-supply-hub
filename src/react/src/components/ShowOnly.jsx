import React from 'react';
import { bool, object, node } from 'prop-types';

const ShowOnly = ({ style, children, when }) => {
    if (!when) {
        return null;
    }

    if (Object.keys(style).length) {
        return <span style={style}> {children} </span>;
    }

    return children;
};

ShowOnly.propTypes = {
    when: bool,
    style: object,
    children: node.isRequired,
};

ShowOnly.defaultProps = {
    when: false,
    style: {},
};

export default React.memo(ShowOnly);
