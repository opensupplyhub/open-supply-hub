import React from 'react';
import { node, string, func } from 'prop-types';

const RESET_BUTTON_STYLES = {
    display: 'inline',
    margin: 0,
    padding: 0,
    border: 'none',
    background: 'none',
    font: 'inherit',
};

const InteractiveTrigger = ({
    childComponent,
    tooltipId,
    onEnter,
    onLeave,
}) => {
    const handleKeyDownForClone = e => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onEnter();
        }
        childComponent.props?.onKeyDown?.(e);
    };

    if (!React.isValidElement(childComponent)) {
        return (
            <span
                onMouseEnter={onEnter}
                onMouseLeave={onLeave}
                style={{ display: 'inline-flex' }}
            >
                <button
                    type="button"
                    onFocus={onEnter}
                    onBlur={onLeave}
                    onKeyDown={e => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            onEnter();
                        }
                    }}
                    aria-describedby={tooltipId}
                    style={RESET_BUTTON_STYLES}
                >
                    {childComponent}
                </button>
            </span>
        );
    }

    const cloned = React.cloneElement(childComponent, {
        onFocus: e => {
            onEnter();
            childComponent.props.onFocus?.(e);
        },
        onBlur: e => {
            onLeave();
            childComponent.props.onBlur?.(e);
        },
        onKeyDown: handleKeyDownForClone,
        'aria-describedby': tooltipId,
    });
    return (
        <span
            onMouseEnter={onEnter}
            onMouseLeave={onLeave}
            style={{ display: 'inline-flex' }}
        >
            {cloned}
        </span>
    );
};

InteractiveTrigger.propTypes = {
    childComponent: node.isRequired,
    tooltipId: string.isRequired,
    onEnter: func.isRequired,
    onLeave: func.isRequired,
};

export default InteractiveTrigger;
