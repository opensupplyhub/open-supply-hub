import React, { useState } from 'react';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { withStyles } from '@material-ui/core/styles';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { toast } from 'react-toastify';

import ContentCopyIcon from './ContentCopyIcon';
import ArrowDropDownIcon from './ArrowDropDownIcon';
import FlagIcon from './FlagIcon';
import ShowOnly from './ShowOnly';
import ReportFacilityStatusDialog from './ReportFacilityStatusDialog';
import CopySearch from './CopySearch';

import { facilityDetailsActions } from '../util/constants';

import {
    makeContributeProductionLocationUpdateURL,
    makeReportADuplicateEmailLink,
    makeDisputeClaimEmailLink,
} from '../util/util';

const coreFieldsStyles = theme =>
    Object.freeze({
        root: {
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            display: 'flex',
            flexDirection: 'column',
            paddingTop: theme.spacing.unit * 5,
            paddingLeft: theme.spacing.unit * 3,
            paddingBottom: theme.spacing.unit * 3,
            paddingRight: theme.spacing.unit * 3,
        },
        detailsType: {
            fontWeight: 700,
            textTransform: 'uppercase',
        },
        nameRow: {
            marginBottom: theme.spacing.unit * 2,
        },
        name: {
            fontWeight: 900,
            fontSize: '2.5rem',
            [theme.breakpoints.up('md')]: {
                fontSize: '3.5rem',
            },
        },
        buttonContainer: {
            marginTop: '1.25rem',
            gap: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 2}px`,
        },
        buttonText: {
            textTransform: 'none',
            fontSize: '1rem',
            marginLeft: theme.spacing.unit,
            marginRight: theme.spacing.unit,
        },
        osIdWrapper: {
            fontSize: '24px',
            fontWeight: 700,
            [theme.breakpoints.down('sm')]: {
                fontSize: '22px',
            },
        },
        osId: {
            fontWeight: 500,
        },
        menuLink: {
            color: 'inherit',
            textDecoration: 'inherit',
        },
    });

const FacilityDetailsCoreFields = ({
    classes,
    name,
    osId,
    isEmbed,
    isClaimed,
    isClosed,
    facilityIsClaimedByCurrentUser,
    userHasPendingFacilityClaim,
}) => {
    const [showDialog, setShowDialog] = useState(false);
    const [anchorEl, setAnchorEl] = useState();
    const handleClick = event => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => setAnchorEl(null);

    const menu = (
        <Menu
            id="report-menu"
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
        >
            <MenuItem onClick={handleClose}>
                <a
                    href={makeReportADuplicateEmailLink(osId)}
                    target="_blank"
                    rel="noreferrer"
                    className={classes.menuLink}
                >
                    {facilityDetailsActions.REPORT_AS_DUPLICATE}
                </a>
            </MenuItem>
            <MenuItem
                onClick={() => {
                    setShowDialog(true);
                    handleClose();
                }}
            >
                {isClosed
                    ? facilityDetailsActions.REPORT_AS_REOPENED
                    : facilityDetailsActions.REPORT_AS_CLOSED}
            </MenuItem>
            <MenuItem onClick={handleClose}>
                <a
                    href={makeContributeProductionLocationUpdateURL(osId)}
                    target="_blank"
                    rel="noreferrer"
                    className={classes.menuLink}
                >
                    {facilityDetailsActions.SUGGEST_AN_EDIT}
                </a>
            </MenuItem>
            <ShowOnly
                when={
                    !facilityIsClaimedByCurrentUser &&
                    !userHasPendingFacilityClaim &&
                    isClaimed
                }
            >
                <MenuItem onClick={handleClose}>
                    <a
                        href={makeDisputeClaimEmailLink(osId)}
                        target="_blank"
                        rel="noreferrer"
                        className={classes.menuLink}
                    >
                        {facilityDetailsActions.DISPUTE_CLAIM}
                    </a>
                </MenuItem>
            </ShowOnly>
        </Menu>
    );

    return (
        <div className={classes.root}>
            <div className={classes.contentContainer}>
                <Typography className={classes.detailsType}>
                    Facility
                </Typography>
                <Grid container className={classes.nameRow}>
                    <Grid item xs={12} md={isEmbed ? 12 : 7}>
                        <Typography className={classes.name}>{name}</Typography>
                    </Grid>
                    <ShowOnly when={!isEmbed}>
                        <Grid
                            item
                            container
                            xs={12}
                            md={5}
                            className={classes.buttonContainer}
                        >
                            <Grid item>
                                <Button
                                    variant="outlined"
                                    aria-owns={
                                        anchorEl ? 'report-menu' : undefined
                                    }
                                    aria-haspopup="true"
                                    onClick={handleClick}
                                >
                                    <FlagIcon />
                                    <span className={classes.buttonText}>
                                        Report
                                    </span>
                                    <ArrowDropDownIcon />
                                </Button>
                                {menu}
                            </Grid>
                            <Grid item>
                                <CopySearch toastText="Copied link">
                                    <Button variant="outlined">
                                        <ContentCopyIcon />
                                        <span className={classes.buttonText}>
                                            Copy Link
                                        </span>
                                    </Button>
                                </CopySearch>
                            </Grid>
                            <Grid item>
                                <CopyToClipboard
                                    text={osId}
                                    onCopy={() =>
                                        toast('Copied OS ID to clipboard')
                                    }
                                >
                                    <Button variant="outlined">
                                        <ContentCopyIcon />
                                        <span className={classes.buttonText}>
                                            Copy OS ID
                                        </span>
                                    </Button>
                                </CopyToClipboard>
                            </Grid>
                        </Grid>
                    </ShowOnly>
                </Grid>
                <Typography className={classes.osIdWrapper}>
                    OS ID: <span className={classes.osId}>{osId}</span>
                </Typography>
            </div>
            <ReportFacilityStatusDialog
                showDialog={showDialog}
                setShowDialog={setShowDialog}
            />
        </div>
    );
};

export default withStyles(coreFieldsStyles)(FacilityDetailsCoreFields);
