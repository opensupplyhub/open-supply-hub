/* eslint no-unused-vars: 0 */
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
import DialogTooltip from './DialogTooltip';
import { mainRoute } from '../../util/constants';
import { makeProductionLocationDialogStyles } from '../../util/styles';

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

const ProductionLocationDialog = ({ classes, data }) => {
    const history = useHistory();

    console.log('@@@ data is ', data);
    const {
        status,
        /* eslint-disable camelcase */
        od_id,
        cleaned_data: {
            raw_json: {
                name: productionLocationName,
                address,
                country: { name: countryName },
            },
        },
    } = data;

    return (
        <Dialog
            open
            aria-labelledby="production-location-dialog-title"
            aria-describedby="production-location-dialog-description"
        >
            <div className={classes.modalContainerWrapper}>
                <DialogTitle
                    id="production-location-dialog-title"
                    className={classes.titleContentStyle}
                >
                    <p className={classes.titleInnerContentStyle}>
                        Thanks for adding data for this production location!
                    </p>
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
                    <Grid container>
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
                                {productionLocationName || 'N/A'}
                            </Typography>
                            <Typography className={classes.label}>
                                Address
                            </Typography>
                            <Typography className={classes.primaryText}>
                                {address || 'N/A'}
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
                            aria-label="Claim button tooltip"
                            childComponent={claimButton(classes)}
                        />
                    </Grid>
                </DialogActions>
            </div>
        </Dialog>
    );
};

export default withStyles(makeProductionLocationDialogStyles)(
    ProductionLocationDialog,
);
