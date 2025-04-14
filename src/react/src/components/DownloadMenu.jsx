import React from 'react';
import { func, oneOfType, Element, instanceOf, oneOf } from 'prop-types';
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
    anchorEl: oneOfType([
        instanceOf(typeof Element !== 'undefined' ? Element : Object),
        oneOf([null]),
    ]),
    onClose: func.isRequired,
    onSelectFormat: func.isRequired,
};

export default DownloadMenu;
