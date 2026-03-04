import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import get from 'lodash/get';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import CopySearch from '../../../CopySearch';
import ContentCopyIcon from '../../../ContentCopyIcon';
import IconComponent from '../../../Shared/IconComponent/IconComponent';
import LearnMoreLink from '../../Shared/LearnMoreLink/LearnMoreLink';

import productionLocationDetailsTitleStyles from './styles';

const ProductionLocationDetailsTitle = ({ classes, data }) => {
    const locationName = get(data, 'properties.name', '') || '';

    return (
        <div className={classes.container}>
            <Typography component="span" className={classes.titleAccent}>
                Location Name
            </Typography>
            <Typography
                component="h1"
                className={classes.title}
                variant="headline"
            >
                {locationName}
            </Typography>
            <div className={classes.osIdRow}>
                <span className={classes.osIdValueWithTooltip}>
                    <Typography
                        component="h2"
                        variant="title"
                        className={classes.osIdValue}
                    >
                        OS ID: {osId}
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
                                onCopy={() =>
                                    toast('Copied OS ID to clipboard')
                                }
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
