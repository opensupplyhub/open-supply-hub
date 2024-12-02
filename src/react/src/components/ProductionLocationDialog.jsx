import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import { useHistory } from 'react-router-dom';
import Button from '@material-ui/core/Button';
import Chip from '@material-ui/core/Chip';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import COLOURS from '../util/COLOURS';
import DialogTooltip from './DialogTooltip';
import { mainRoute } from '../util/constants';

const styles = theme =>
    Object.freeze({
        modalContainerWrapper: Object.freeze({
            padding: '20px 60px',
            [theme.breakpoints.down('md')]: {
                padding: 0,
            },
        }),
        contentContainer: Object.freeze({
            width: '100%',
            maxWidth: '1072px',
        }),
        label: Object.freeze({
            fontSize: '14px',
            textTransform: 'uppercase',
            fontWeight: 900,
        }),
        titleContentStyle: Object.freeze({
            fontSize: '32px',
            textAlign: 'center',
            fontWeight: 800,
            lineHeight: 1,
        }),
        primaryText: Object.freeze({
            marginBottom: '20px',
        }),
        osIDText: Object.freeze({
            lineHeight: '2.3',
        }),
        leftContainerColumn: Object.freeze({
            paddingRight: '10px',
        }),
        rightContainerColumn: Object.freeze({
            paddingRight: '10px',
        }),
        separator: Object.freeze({
            margin: '20px 0',
            color: COLOURS.GREY,
        }),
        dialogContentStyles: Object.freeze({
            textAlign: 'center',
            fontSize: '16px',
            fontWeight: 600,
        }),
        buttonContentStyle: Object.freeze({
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '0 15px',
            [theme.breakpoints.down('md')]: {
                justifyContent: 'initial',
                flexDirection: 'column',
            },
        }),
        osIdStatusBadge: Object.freeze({
            backgroundColor: '#E7E8EA',
            marginLeft: '10px',
            fontWeight: 'bold',
        }),
        osIdStatusBadgeIcon: Object.freeze({
            color: COLOURS.DARK_GREY,
            marginRight: '5px',
        }),
        button: Object.freeze({
            fontWeight: 'bold',
            textTransform: 'none',
            paddingLeft: '30px',
            paddingRight: '30px',
            boxShadow: 'none',
            [theme.breakpoints.down('md')]: {
                width: '100%',
                marginBottom: '16px',
            },
        }),
        claimTooltipWrapper: Object.freeze({
            display: 'block',
            cursor: 'not-allowed',
            [theme.breakpoints.down('md')]: {
                width: '100%',
            },
        }),
        claimButton: Object.freeze({
            backgroundColor: COLOURS.NAVIGATION,
        }),
    });

const infoIcon = classes => (
    <InfoOutlinedIcon className={classes.osIdStatusBadgeIcon} />
);

const claimButton = classes => (
    <span className={`${classes.claimTooltipWrapper}`}>
        <Button
            variant="contained"
            disabled
            className={`${classes.button} ${classes.claimButton}`}
        >
            Continue to Claim
        </Button>
    </span>
);

const ProductionLocationDialog = ({ classes }) => {
    const history = useHistory();
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
                        <Grid
                            item
                            xs={12}
                            md={6}
                            className={classes.leftContainerColumn}
                        >
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
                        <Grid
                            item
                            xs={12}
                            md={6}
                            className={classes.rightContainerColumn}
                        >
                            <Typography className={classes.label}>
                                OS ID
                            </Typography>
                            <Grid container className={classes.primaryText}>
                                <Grid item>
                                    <Typography className={classes.osIDText}>
                                        US20243236AZ1R0
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Chip
                                        label="Pending"
                                        onDelete={() => {}}
                                        className={classes.osIdStatusBadge}
                                        deleteIcon={
                                            <DialogTooltip
                                                text="Your submission is under
                                                        review. You will receive a
                                                        notification once the
                                                        production location is live
                                                        on OS Hub. You can proceed
                                                        to submit a claim while your
                                                        request is pending."
                                                childComponent={infoIcon(
                                                    classes,
                                                )}
                                            />
                                        }
                                    />
                                </Grid>
                            </Grid>
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
                        <Button
                            variant="contained"
                            color="default"
                            onClick={() => history.push(mainRoute)}
                            className={classes.button}
                        >
                            Search OS Hub
                        </Button>
                        <Button
                            variant="contained"
                            color="secondary"
                            onClick={() => {
                                console.log('submit another location');
                            }}
                            className={classes.button}
                        >
                            Submit another Location
                        </Button>
                        <DialogTooltip
                            text="You'll be able to claim the
                                        location after the moderation is done"
                            childComponent={claimButton(classes)}
                        />
                    </Grid>
                </DialogActions>
            </div>
        </Dialog>
    );
};

export default withStyles(styles)(ProductionLocationDialog);
