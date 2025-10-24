import React from 'react';
import { useLocation } from 'react-router-dom';
import { useResetScrollPosition } from '../../../util/hooks';

const withScrollReset = WrappedComponent => {
    const WithScrollReset = props => {
        const location = useLocation();
        useResetScrollPosition(location);

        return <WrappedComponent {...props} />;
    };

    // For debugging purposes, set the display name of the wrapped component.
    WithScrollReset.displayName = `withScrollReset(${
        WrappedComponent.name || 'Component'
    })`;

    return WithScrollReset;
};

export default withScrollReset;
