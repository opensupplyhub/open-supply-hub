import React from 'react';
import { bool, func, node, object, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Collapse from '@material-ui/core/Collapse';

import ExpandToggleChevron from '../../Shared/ExpandToggleChevron/ExpandToggleChevron';

/*
A section that opens and closes like Operational Details and Industry
Classification, with its open state held by the parent.
*/
const CollapsibleSection = ({
    classes,
    testId,
    title,
    meta,
    isOpen,
    onToggle,
    children,
}) => {
    const handleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            onToggle();
        }
    };

    return (
        <div className={classes.container} data-testid={testId}>
            <div
                className={`${classes.header}${
                    isOpen ? ` ${classes.headerOpen}` : ''
                }`}
                role="button"
                tabIndex={0}
                aria-expanded={isOpen}
                onClick={onToggle}
                onKeyDown={handleKeyDown}
            >
                <div className={classes.headerLeft}>
                    <Typography
                        variant="title"
                        className={classes.title}
                        component="h3"
                    >
                        {title}
                    </Typography>
                    {meta}
                </div>
                <div className={classes.headerRight}>
                    <Typography className={classes.toggleLabel}>
                        {isOpen ? 'Close' : 'Open'}
                    </Typography>
                    <ExpandToggleChevron
                        isExpanded={isOpen}
                        className={classes.chevron}
                        expandLessTestId={`${testId}-expand-less`}
                        expandMoreTestId={`${testId}-expand-more`}
                    />
                </div>
            </div>
            <Collapse in={isOpen}>
                <div className={classes.panel}>{children}</div>
            </Collapse>
        </div>
    );
};

CollapsibleSection.propTypes = {
    classes: object.isRequired,
    testId: string.isRequired,
    title: string.isRequired,
    meta: node,
    isOpen: bool.isRequired,
    onToggle: func.isRequired,
    children: node.isRequired,
};

CollapsibleSection.defaultProps = {
    meta: null,
};

export default CollapsibleSection;
