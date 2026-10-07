import React from 'react';
import PropTypes from 'prop-types';
import ChevronRight from '@material-ui/icons/ChevronRight';

const DataSourceItem = ({
    classes,
    Icon,
    iconClassName,
    title,
    onSelect,
    tabIndex,
    buttonRef,
}) => (
    <button
        type="button"
        ref={buttonRef}
        className={classes.item}
        onClick={onSelect}
        tabIndex={tabIndex}
        data-testid={`data-label-item-${title}`}
    >
        <Icon className={iconClassName} aria-hidden />
        <span className={classes.itemLabel}>{title}</span>
        <ChevronRight className={classes.chevron} aria-hidden />
    </button>
);

DataSourceItem.propTypes = {
    classes: PropTypes.object.isRequired,
    Icon: PropTypes.oneOfType([PropTypes.func, PropTypes.object]).isRequired,
    iconClassName: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    onSelect: PropTypes.func.isRequired,
    tabIndex: PropTypes.number,
    buttonRef: PropTypes.func,
};

DataSourceItem.defaultProps = {
    tabIndex: 0,
    buttonRef: undefined,
};

export default DataSourceItem;
