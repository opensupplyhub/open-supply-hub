import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { toast } from 'react-toastify';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import CopySearch from '../../../CopySearch';
import ContentCopyIcon from '../../../ContentCopyIcon';
import IconComponent from '../../../Shared/IconComponent/IconComponent';
import LearnMoreLink from '../../Shared/LearnMoreLink/LearnMoreLink';

import productionLocationDetailsOsIdBadgeStyles from './styles';
import { OS_ID_TOOLTIP_TEXT, OS_ID_LEARN_MORE_URL } from './constants';

const ProductionLocationDetailsOsIdBadge = ({ classes, osId }) => (
    <div className={classes.osIdRow}>
        <div className={classes.osIdValueWithTooltip}>
            <Typography
                component="h2"
                variant="title"
                className={classes.osIdValue}
            >
                <span className={classes.osIdLabel}>OS ID</span>: {osId}
            </Typography>
            <IconComponent
                title={
                    <>
                        {OS_ID_TOOLTIP_TEXT}
                        <LearnMoreLink href={OS_ID_LEARN_MORE_URL} />
                    </>
                }
                icon={InfoOutlined}
                className={classes.osIdInfoButton}
            />
        </div>
        {osId && (
            <div className={classes.osIdActions}>
                <span
                    className={`${classes.copyButtonWrap} ${classes.copyButtonWrapFirst}`}
                >
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
                <span className={classes.copyButtonWrap}>
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
            </div>
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
