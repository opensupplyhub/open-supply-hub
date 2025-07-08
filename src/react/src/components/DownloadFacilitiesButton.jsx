import React, { useEffect } from 'react';
import { arrayOf, string, bool, shape, number, object } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import { withStyles, withTheme } from '@material-ui/core/styles';

import { toast } from 'react-toastify';

import downloadFacilities from '../actions/downloadFacilities';
import {
    hideDownloadLimitCheckoutUrlError,
    downloadLimitCheckoutUrl,
} from '../actions/downloadLimit';
import DownloadIcon from './DownloadIcon';
import ArrowDropDownIcon from './ArrowDropDownIcon';
import { hideLogDownloadError } from '../actions/logDownload';
import DownloadMenu from '../components/DownloadMenu';
import {
    FREE_FACILITIES_DOWNLOAD_LIMIT,
    FACILITIES_DOWNLOAD_LIMIT,
} from '../util/constants';

const downloadFacilitiesStyles = theme =>
    Object.freeze({
        listHeaderButtonStyles: Object.freeze({
            height: '45px',
            margin: '5px 0',
            marginRight: '1em',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(theme.palette.action.main),
            fontSize: '16px',
            fontWeight: 900,
            lineHeight: '20px',
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
        buttonText: Object.freeze({
            marginLeft: '0.2rem',
            marginRight: '0.6rem',
        }),
        downloadTooltip: {
            fontSize: '0.875rem',
            fontFamily: theme.typography.fontFamily,
        },
        buttonContent: {
            display: 'flex',
            alignItems: 'center',
            textTransform: 'none',
        },
    });

const DownloadFacilitiesButton = ({
    /* from state */
    dispatch,
    isEmbedded,
    logDownloadError,
    user,
    userAllowedRecords,
    checkoutUrl,
    checkoutUrlError,
    /* from props */
    disabled,
    upgrade,
    setLoginRequiredDialogIsOpen,
    classes,
    theme,
}) => {
    const [anchorEl, setAnchorEl] = React.useState(null);

    const actionContrastText = theme.palette.getContrastText(
        theme.palette.action.main,
    );

    useEffect(() => {
        if (Array.isArray(logDownloadError) && logDownloadError.length > 0) {
            toast(logDownloadError[0]);
            dispatch(hideLogDownloadError());
        }
    }, [logDownloadError]);
    useEffect(() => {
        if (checkoutUrl) {
            window.location.href = checkoutUrl;
        }
        if (checkoutUrlError) {
            toast(checkoutUrlError);
            dispatch(hideDownloadLimitCheckoutUrlError());
        }
    }, [checkoutUrl, checkoutUrlError]);
    const handleUpgrade = () => {
        const redirectPath = window.location.pathname + window.location.search;
        dispatch(downloadLimitCheckoutUrl(redirectPath));
    };
    const handleClick = event => {
        if (upgrade && !user.isAnon) {
            handleUpgrade();
        } else {
            setAnchorEl(event.currentTarget);
        }
    };
    const handleClose = () => setAnchorEl(null);
    const handleDownload = format => {
        dispatch(downloadFacilities(format, { isEmbedded }));
    };
    const selectFormatAndDownload = format => {
        if (!user.isAnon || isEmbedded) {
            handleDownload(format);
        } else {
            setLoginRequiredDialogIsOpen(true);
        }
        handleClose();
    };

    const downloadLimit = isEmbedded
        ? FACILITIES_DOWNLOAD_LIMIT
        : FREE_FACILITIES_DOWNLOAD_LIMIT;

    const tooltipTexts = {
        availableDownloads: `Registered users can download up to ${downloadLimit} production
            locations annually for free. This account has ${userAllowedRecords} production locations
            available to download. Additional downloads are available for purchase.`,
        outOfDownloads:
            "You've reached your annual download limit. Purchase additional downloads for immediate access.",
        limitExceededByResults: `Registered users can download up to ${downloadLimit}
            production locations annually for free. This account has ${userAllowedRecords} production
            locations available to download. Purchase additional downloads for immediate access.`,
    };

    let tooltipText;
    if (upgrade) {
        tooltipText =
            user.allowed_records_number === 0
                ? tooltipTexts.outOfDownloads
                : tooltipTexts.limitExceededByResults;
    } else {
        tooltipText = tooltipTexts.availableDownloads;
    }

    const tooltipTitle = (
        <p className={classes.downloadTooltip}>
            {user.isAnon && !isEmbedded
                ? 'Log in to download this dataset.'
                : tooltipText}
        </p>
    );

    const tooltipTitle2 = (
        <p className={classes.downloadTooltip}>
            Downloads are supported for searches resulting in{' '}
            {isEmbedded ? FACILITIES_DOWNLOAD_LIMIT : userAllowedRecords}{' '}
            production locations or less.
            {user.isAnon && !isEmbedded
                ? ' Log in to download this dataset.'
                : ''}
        </p>
    );

    return (
        <Tooltip title={tooltipTitle} placement="left">
            <div>
                <Button
                    disabled={disabled}
                    variant="outlined"
                    className={classes.listHeaderButtonStyles}
                    aria-owns={anchorEl ? 'download-menu' : undefined}
                    aria-haspopup="true"
                    onClick={handleClick}
                >
                    <div className={classes.buttonContent}>
                        <DownloadIcon
                            color={
                                disabled
                                    ? 'rgba(0, 0, 0, 0.26)'
                                    : actionContrastText
                            }
                        />
                        <span className={classes.buttonText}>
                            {upgrade && !user.isAnon
                                ? 'Purchase More Downloads'
                                : 'Download'}
                        </span>
                        {upgrade ? (
                            ''
                        ) : (
                            <ArrowDropDownIcon
                                color={
                                    disabled
                                        ? 'rgba(0, 0, 0, 0.26)'
                                        : actionContrastText
                                }
                            />
                        )}
                    </div>
                </Button>
                <DownloadMenu
                    anchorEl={anchorEl}
                    onClose={handleClose}
                    onSelectFormat={selectFormatAndDownload}
                />
            </div>
        </Tooltip>
    );
};

DownloadFacilitiesButton.defaultProps = {
    disabled: false,
    upgrade: false,
    userAllowedRecords: FREE_FACILITIES_DOWNLOAD_LIMIT,
    logDownloadError: null,
    checkoutUrl: null,
    checkoutUrlError: null,
};

DownloadFacilitiesButton.propTypes = {
    disabled: bool,
    upgrade: bool,
    userAllowedRecords: number,
    logDownloadError: arrayOf(string),
    user: shape({
        isAnon: bool.isRequired,
    }).isRequired,
    checkoutUrl: string,
    checkoutUrlError: string,
    classes: object.isRequired,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
    logDownload: { error: logDownloadError },
    embeddedMap: { embed: isEmbedded },
    downloadLimit: {
        checkout: { checkoutUrl, error: checkoutUrlError },
    },
}) {
    return {
        user,
        logDownloadError,
        isEmbedded,
        checkoutUrl,
        checkoutUrlError,
    };
}

export default connect(mapStateToProps)(
    withTheme()(withStyles(downloadFacilitiesStyles)(DownloadFacilitiesButton)),
);
