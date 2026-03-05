import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { toast } from 'react-toastify';
import InfoIcon from '@material-ui/icons/Info';

import CopySearch from '../../../CopySearch';
import ContentCopyIcon from '../../../ContentCopyIcon';
import DialogTooltip from '../../../Contribute/DialogTooltip';

import productionLocationDetailsOsIdBadgeStyles from './styles';
import { OS_ID_TOOLTIP_TEXT, OS_ID_LEARN_MORE_URL } from './constants';

const ProductionLocationDetailsOsIdBadge = ({ classes, osId }) => (
    <div className={classes.osIdRow}>
        <span className={classes.osIdValueWithTooltip}>
            <Typography
                component="h2"
                variant="title"
                className={classes.osIdValue}
            >
                <span className={classes.osIdLabel}>OS ID</span>: {osId}
            </Typography>
            <DialogTooltip
                text={OS_ID_TOOLTIP_TEXT}
                textHref={
                    <p style={{ marginTop: 8, marginBottom: 0 }}>
                        <a
                            href={OS_ID_LEARN_MORE_URL}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: 'white' }}
                        >
                            Learn more →
                        </a>
                    </p>
                }
                interactive
                childComponent={
                    <IconButton
                        className={classes.osIdInfoButton}
                        size="small"
                        aria-label="More information about OS ID"
                        disableRipple
                    >
                        <InfoIcon style={{ width: 16, height: 16 }} />
                    </IconButton>
                }
            />
        </span>
        {osId && (
            <span className={classes.osIdActions}>
                <span
                    className={`${classes.copyButtonWrap} ${classes.copyButtonWrapFirst}`}
                >
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
                </span>
                <span className={classes.copyButtonWrap}>
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
            </span>
        )}
    </div>
);

ProductionLocationDetailsOsIdBadge.propTypes = {
    classes: PropTypes.object.isRequired,
    osId: PropTypes.string.isRequired,
};

export default withStyles(productionLocationDetailsOsIdBadgeStyles)(
    ProductionLocationDetailsOsIdBadge,
);
