import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Chip from '@material-ui/core/Chip';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import Grid from '@material-ui/core/Grid';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import COLOURS from './../util/COLOURS';

function arrowGenerator(color) {
    return {
        '&[x-placement*="bottom"] $arrow': {
            top: 0,
            left: 0,
            marginTop: '-0.95em',
            width: '3em',
            height: '1em',
            '&::before': {
                borderWidth: '0 1em 1em 1em',
                borderColor: `transparent transparent ${color} transparent`,
            },
        },
        '&[x-placement*="top"] $arrow': {
            bottom: 0,
            left: 0,
            marginBottom: '-0.95em',
            width: '3em',
            height: '1em',
            '&::before': {
                borderWidth: '1em 1em 0 1em',
                borderColor: `${color} transparent transparent transparent`,
            },
        },
        '&[x-placement*="right"] $arrow': {
            left: 0,
            marginLeft: '-0.95em',
            height: '3em',
            width: '1em',
            '&::before': {
                borderWidth: '1em 1em 1em 0',
                borderColor: `transparent ${color} transparent transparent`,
            },
        },
        '&[x-placement*="left"] $arrow': {
            right: 0,
            marginRight: '-0.95em',
            height: '3em',
            width: '1em',
            '&::before': {
                borderWidth: '1em 0 1em 1em',
                borderColor: `transparent transparent transparent ${color}`,
            },
        },
    };
}

const styles = () => ({
    modalContainerWrapper: {
        padding: '20px 60px',
    },
    contentContainer: {
        width: '100%',
        maxWidth: '1072px',
    },
    label: {
        fontSize: '14px',
        textTransform: 'uppercase',
        fontWeight: 900,
    },
    titleContentStyle: {
        textAlign: 'center',
        textTransform: 'uppercase',
    },
    icon: {
        color: COLOURS.DARK_GREEN,
        verticalAlign: 'middle',
        marginRight: '10px',
    },
    separator: {
        margin: '20px 0',
        color: COLOURS.GREY,
    },
    dialogContentStyles: {
        textAlign: 'center',
        fontSize: '16px',
    },
    buttonContentStyle: {
        justifyContent: 'space-between',
        alignItems: 'center',
        spacing: 2,
        padding: '0 15px',
    },
    arrow: {
        position: 'absolute',
        fontSize: 6,
        width: '3em',
        height: '3em',
        '&::before': {
            content: '""',
            margin: 'auto',
            display: 'block',
            width: 0,
            height: 0,
            borderStyle: 'solid',
        },
    },
    bootstrapPopper: arrowGenerator(COLOURS.DARK_SLATE_GRAY),
    bootstrapTooltip: {
        fontSize: '14px',
        backgroundColor: COLOURS.DARK_SLATE_GRAY,
    },
    bootstrapPlacementLeft: {
        margin: '0 8px',
    },
    bootstrapPlacementRight: {
        margin: '0 8px',
    },
    bootstrapPlacementTop: {
        margin: '8px 0',
    },
    bootstrapPlacementBottom: {
        margin: '8px 0',
    },
});

const ConfirmProductionLocationModal = ({ classes }) => {
    const [arrowRef, setArrowRef] = useState(null);
    return (
        <Dialog open>
            <div className={classes.modalContainerWrapper}>
                <DialogTitle className={classes.titleContentStyle}>
                    Thanks for adding data for this production location!
                </DialogTitle>
                <DialogContent>
                    <Typography
                        variant="body1"
                        className={classes.dialogContentStyles}
                    >
                        Do you own or manage this location? If so, you can now
                        claim your production location to have a complete,
                        credible and confirmed profile with a green banner and
                        claimed badge. You’ll be able to add more information,
                        like contact details, certifications, native language
                        name, and more.
                    </Typography>
                    <hr className={classes.separator} />
                    <Grid container className={classes.contentContainer}>
                        <Grid item xs={12} md={6}>
                            <Typography className={classes.label}>
                                Facility name
                            </Typography>
                            <Typography className={classes.primaryText}>
                                Unifill Composite Dyeing Mills Ltd.
                            </Typography>
                            <Typography className={classes.label}>
                                Address
                            </Typography>
                            <Typography className={classes.primaryText}>
                                Gobindobari, Bhabanipur, Kashimpur, Gazipur,
                                Bangladesh. Gazipur - 1704 - DHAKA - Bangladesh
                                March 23, 2022 by The WikiRate Project 7 more
                                contributions
                            </Typography>
                            <Typography className={classes.label}>
                                Location type
                            </Typography>
                            <Typography className={classes.primaryText}>
                                Textile or Material Production March 23, 2022 by
                                The WikiRate Project 7 more contributions
                            </Typography>
                            <Typography className={classes.label}>
                                Number of workers
                            </Typography>
                            <Typography className={classes.primaryText}>
                                1,000 - 5,000
                            </Typography>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Typography className={classes.label}>
                                OS ID
                            </Typography>
                            <Typography className={classes.primaryText}>
                                US20243236AZ1R0
                                <Chip
                                    label="Pending"
                                    onDelete={() => {}}
                                    deleteIcon={
                                        <Tooltip
                                            title={
                                                <React.Fragment>
                                                    Your submission is under
                                                    review. You will receive a
                                                    notification once the
                                                    production location is live
                                                    on OS Hub. You can proceed
                                                    to submit a claim while your
                                                    request is pending.
                                                    <span
                                                        className={
                                                            classes.arrow
                                                        }
                                                        ref={setArrowRef}
                                                    />
                                                </React.Fragment>
                                            }
                                            classes={{
                                                tooltip:
                                                    classes.bootstrapTooltip,
                                                popper: classes.bootstrapPopper,
                                                tooltipPlacementLeft:
                                                    classes.bootstrapPlacementLeft,
                                                tooltipPlacementRight:
                                                    classes.bootstrapPlacementRight,
                                                tooltipPlacementTop:
                                                    classes.bootstrapPlacementTop,
                                                tooltipPlacementBottom:
                                                    classes.bootstrapPlacementBottom,
                                            }}
                                            PopperProps={{
                                                popperOptions: {
                                                    modifiers: {
                                                        arrow: {
                                                            enabled: Boolean(
                                                                arrowRef,
                                                            ),
                                                            element: arrowRef,
                                                        },
                                                    },
                                                },
                                            }}
                                        >
                                            <InfoOutlinedIcon />
                                        </Tooltip>
                                    }
                                />
                            </Typography>
                            <Typography className={classes.label}>
                                Product type
                            </Typography>
                            <Typography className={classes.primaryText}>
                                Blouses Shirts
                            </Typography>
                            <Typography className={classes.label}>
                                Processing type
                            </Typography>
                            <Typography className={classes.primaryText}>
                                Textile or Material Production
                            </Typography>
                            <Typography className={classes.label}>
                                Parent company
                            </Typography>
                            <Typography className={classes.primaryText}>
                                Unifill Composite Dyeing Mills Ltd.
                            </Typography>
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Grid container className={classes.buttonContentStyle}>
                        <Grid item>
                            <Button
                                variant="outlined"
                                color="secondary"
                                onClick={() => {
                                    console.log('Init click 1');
                                }}
                            >
                                Search OS Hub
                            </Button>
                        </Grid>
                        <Grid item>
                            <Button
                                variant="outlined"
                                color="primary"
                                onClick={() => {
                                    console.log('Init click 2');
                                }}
                            >
                                Submit another Location
                            </Button>
                        </Grid>
                        <Grid item>
                            <Button
                                variant="outlined"
                                color="primary"
                                onClick={() => {
                                    console.log('Init click 3');
                                }}
                            >
                                Continue to Claim
                            </Button>
                        </Grid>
                    </Grid>
                </DialogActions>
            </div>
        </Dialog>
    );
};

export default withStyles(styles)(ConfirmProductionLocationModal);
