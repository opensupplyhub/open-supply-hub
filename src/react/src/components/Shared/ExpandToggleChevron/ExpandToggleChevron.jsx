import React from 'react';
import { bool, string } from 'prop-types';
import ExpandMore from '@material-ui/icons/ExpandMore';
import ExpandLess from '@material-ui/icons/ExpandLess';

const ExpandToggleChevron = ({
    isExpanded,
    className,
    expandLessTestId,
    expandMoreTestId,
}) =>
    isExpanded ? (
        <ExpandLess className={className} data-testid={expandLessTestId} />
    ) : (
        <ExpandMore className={className} data-testid={expandMoreTestId} />
    );

ExpandToggleChevron.propTypes = {
    isExpanded: bool.isRequired,
    className: string.isRequired,
    expandLessTestId: string.isRequired,
    expandMoreTestId: string.isRequired,
};

export default ExpandToggleChevron;
