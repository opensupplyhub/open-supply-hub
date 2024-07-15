import React, { useEffect } from 'react';
import { arrayOf, string, func } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import { withStyles, withTheme } from '@material-ui/core/styles';

import { toast } from 'react-toastify';

import DownloadIcon from './DownloadIcon';

import { downloadFacilityClaims } from '../actions/claimFacilityDashboard';

import { facilityClaimsListPropType } from '../util/propTypes';

const downloadFacilityClaimsButtonStyles = theme =>
    Object.freeze({
        button: Object.freeze({
            marginBottom: '44px',
            padding: '14px 13px',
            color: theme.palette.getContrastText(theme.palette.action.main),
            fontSize: '18px',
            fontWeight: 900,
            lineHeight: '20px',
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
            backgroundColor: theme.palette.action.main,
        }),
        buttonText: Object.freeze({
            marginLeft: '0.2rem',
        }),
        buttonContent: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            textTransform: 'none',
        }),
    });

const DownloadFacilityClaimsButton = ({
    downloadClaims,
    downloadError,
    data,
    classes,
    theme,
}) => {
    const actionContrastText = theme.palette.getContrastText(
        theme.palette.action.main,
    );

    useEffect(() => {
        if (downloadError) {
            toast('A problem prevented downloading the facility claims');
        }
    }, [downloadError]);

    const handleDownload = () => {
        downloadClaims(data);
    };

    return (
        <Button
            className={classes.button}
            onClick={() => handleDownload()}
            disabled={!data.length}
        >
            <div className={classes.buttonContent}>
                <DownloadIcon
                    color={
                        !data.length
                            ? 'rgba(0, 0, 0, 0.26)'
                            : actionContrastText
                    }
                />
                <span className={classes.buttonText}>Download Excel</span>
            </div>
        </Button>
    );
};

DownloadFacilityClaimsButton.defaultProps = {
    downloadError: null,
};

DownloadFacilityClaimsButton.propTypes = {
    downloadClaims: func.isRequired,
    downloadError: arrayOf(string),
    data: facilityClaimsListPropType.isRequired,
};

function mapStateToProps({
    claimFacilityDashboard: {
        facilityClaimsDownloadStatus: { error: downloadError },
    },
}) {
    return {
        downloadError,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        downloadClaims: facilityClaims =>
            dispatch(downloadFacilityClaims(facilityClaims)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(
    withTheme()(
        withStyles(downloadFacilityClaimsButtonStyles)(
            DownloadFacilityClaimsButton,
        ),
    ),
);
