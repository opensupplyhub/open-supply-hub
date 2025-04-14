import React, { useEffect } from 'react';
import { arrayOf, string, bool, shape, number } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import { withStyles, withTheme } from '@material-ui/core/styles';

import { toast } from 'react-toastify';

import downloadFacilities from '../actions/downloadFacilities';
import DownloadIcon from './DownloadIcon';
import ArrowDropDownIcon from './ArrowDropDownIcon';
import { hideLogDownloadError } from '../actions/logDownload';
import DownloadMenu from '../components/DownloadMenu';

const fallbackForTest = {
    main: 'rgb(255, 207, 63)',
    dark: 'rgb(178, 144, 44)',
    fontFamily: 'Darker Grotesque, sans-serif',
};
const downloadFacilitiesStyles = theme =>
    Object.freeze({
        listHeaderButtonStyles: Object.freeze({
            height: '45px',
            margin: '5px 0',
            marginRight: '1em',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(
                theme.palette.action.main || fallbackForTest.main,
            ),
            fontSize: '16px',
            fontWeight: 900,
            lineHeight: '20px',
            '&:hover': {
                backgroundColor:
                    theme.palette.action.dark || fallbackForTest.dark,
            },
        }),
        buttonText: Object.freeze({
            marginLeft: '0.2rem',
            marginRight: '0.6rem',
        }),
        downloadTooltip: {
            fontSize: '0.875rem',
            fontFamily:
                theme.typography.fontFamily || fallbackForTest.fontFamily,
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
    /* from props */
    allowLargeDownloads,
    disabled,
    setLoginRequiredDialogIsOpen,
    classes,
    theme,
}) => {
    const [anchorEl, setAnchorEl] = React.useState(null);

    const actionContrastText = theme.palette.getContrastText(
        theme.palette.action.main || fallbackForTest.main,
    );

    useEffect(() => {
        if (Array.isArray(logDownloadError) && logDownloadError.length > 0) {
            toast(logDownloadError[0]);
            dispatch(hideLogDownloadError());
        }
    }, [logDownloadError]);

    const handleClick = event => setAnchorEl(event.currentTarget);
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
    const tooltipTitle = allowLargeDownloads ? (
        ''
    ) : (
        <p className={classes.downloadTooltip}>
            Downloads are supported for searches resulting in{' '}
            {user.allowed_records_number} production locations or less. Log in
            to download this dataset.
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
                        <span className={classes.buttonText}>Download</span>
                        <ArrowDropDownIcon
                            color={
                                disabled
                                    ? 'rgba(0, 0, 0, 0.26)'
                                    : actionContrastText
                            }
                        />
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
    allowLargeDownloads: false,
    disabled: false,
    logDownloadError: null,
};

DownloadFacilitiesButton.propTypes = {
    allowLargeDownloads: bool,
    disabled: bool,
    logDownloadError: arrayOf(string),
    user: shape({
        allowed_records_number: number.isRequired,
    }).isRequired,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
    logDownload: { error: logDownloadError },
    embeddedMap: { embed: isEmbedded },
}) {
    return {
        user,
        logDownloadError,
        isEmbedded,
    };
}

export default connect(mapStateToProps)(
    withTheme()(withStyles(downloadFacilitiesStyles)(DownloadFacilitiesButton)),
);
