import React from 'react';
import PropTypes from 'prop-types';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

const DownloadMenu = ({ anchorEl, onClose, onSelectFormat }) => (
    <Menu
        id="download-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={onClose}
    >
        <MenuItem onClick={() => onSelectFormat('csv')}>CSV</MenuItem>
        <MenuItem onClick={() => onSelectFormat('xlsx')}>Excel</MenuItem>
    </Menu>
);

DownloadMenu.defaultProps = {
    anchorEl: null,
};

DownloadMenu.propTypes = {
    anchorEl: PropTypes.oneOfType([
        typeof HTMLElement !== 'undefined'
            ? PropTypes.instanceOf(HTMLElement)
            : PropTypes.any,
        PropTypes.oneOf([null]),
    ]),
    onClose: PropTypes.func.isRequired,
    onSelectFormat: PropTypes.func.isRequired,
};

export default DownloadMenu;
