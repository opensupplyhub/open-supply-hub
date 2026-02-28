import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { toast } from 'react-toastify';
import get from 'lodash/get';

import CopySearch from '../../../CopySearch';
import ContentCopyIcon from '../../../ContentCopyIcon';

import productionLocationDetailsTitleStyles from './styles';

const ProductionLocationDetailsTitle = ({ classes, data }) => {
    const locationName = get(data, 'properties.name', '') || '';
    const osId = get(data, 'properties.os_id', '') || '';

    return (
        <div className={classes.container}>
            <Typography component="h1" className={classes.title} variant="h1">
                {locationName}
            </Typography>
            <div className={classes.osIdRow}>
                <Typography component="span" className={classes.osIdLabel}>
                    OS ID:{' '}
                </Typography>
                <Typography component="span" className={classes.osIdValue}>
                    {osId}
                </Typography>
                {osId && (
                    <span className={classes.osIdActions}>
                        <CopySearch toastText="Copied link">
                            <Button
                                variant="outlined"
                                size="small"
                                className={classes.copyButton}
                                aria-label="Copy link"
                            >
                                <ContentCopyIcon />
                                <span className={classes.buttonText}>
                                    Copy Link
                                </span>
                            </Button>
                        </CopySearch>
                        <CopyToClipboard
                            text={osId}
                            onCopy={() => toast('Copied OS ID to clipboard')}
                        >
                            <Button
                                variant="outlined"
                                size="small"
                                className={classes.copyButton}
                                aria-label="Copy OS ID"
                            >
                                <ContentCopyIcon />
                                <span className={classes.buttonText}>
                                    Copy OS ID
                                </span>
                            </Button>
                        </CopyToClipboard>
                    </span>
                )}
            </div>
        </div>
    );
};

ProductionLocationDetailsTitle.propTypes = {
    classes: PropTypes.object.isRequired,
    data: PropTypes.object,
};

ProductionLocationDetailsTitle.defaultProps = {
    data: null,
};

export default withStyles(productionLocationDetailsTitleStyles)(
    ProductionLocationDetailsTitle,
);
