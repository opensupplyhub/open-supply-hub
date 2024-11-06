import React from 'react';
import { bool, func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import DownloadIcon from '../DownloadIcon';
import { makeDownloadExcelButtonStyles } from '../../util/styles';

const DownloadExcelButton = ({ fetching, handleDownload, classes }) => (
    <Button
        aria-label="Download Excel"
        className={classes.button}
        onClick={handleDownload}
        disabled={fetching}
    >
        <div className={classes.buttonContent}>
            <DownloadIcon color="inherit" />
            <span className={classes.buttonText}>Download Excel</span>
        </div>
    </Button>
);

DownloadExcelButton.propTypes = {
    fetching: bool.isRequired,
    handleDownload: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeDownloadExcelButtonStyles)(DownloadExcelButton);
