/* eslint no-unused-vars: 0 */
import React, { useEffect, useState } from 'react';
import { func, number, object, string } from 'prop-types';
import { withStyles, withTheme } from '@material-ui/core/styles';
import { useHistory } from 'react-router-dom';
import { size, startCase, round, toLower } from 'lodash';
import Button from '@material-ui/core/Button';
import Chip from '@material-ui/core/Chip';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import ProductionLocationDialogCloseButton from './ProductionLocationDialogCloseButton';
import DialogTooltip from './DialogTooltip';
import ProductionLocationDialogFields from './ProductionLocationDialogFields';
import {
    mainRoute,
    searchByNameAndAddressResultRoute,
    MODERATION_STATUSES_ENUM,
} from '../../util/constants';
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

const getStatusBadgeClass = (classes, status) => {
    switch (status) {
        case MODERATION_STATUSES_ENUM.PENDING:
            return classes.osIdStatusBadge_pending;
        case MODERATION_STATUSES_ENUM.APPROVED:
            return classes.osIdStatusBadge_approved;
        case MODERATION_STATUSES_ENUM.REJECTED:
            return classes.osIdStatusBadge_rejected;
        default:
            return '';
    }
};

const ProductionLocationDialog = ({
    theme,
    innerWidth,
    classes,
    data,
    osID,
    moderationStatus,
    handleShow,
}) => {
    const history = useHistory();

    const [isMobile, setIsMobile] = useState(false);
    useEffect(() => {
        if (innerWidth <= theme.breakpoints.values.sm) {
            setIsMobile(true);
        } else {
            setIsMobile(false);
        }
    }, [innerWidth]);

    const {
        raw_json: { name: productionLocationName, address },
        fields,
    } = data;

    const fieldSetNumber = round(size(fields) / 2);

    return (
        <>
            {isMobile ? (
                <ProductionLocationDialogCloseButton
                    handleShow={handleShow}
                    isMobile={isMobile}
                />
            ) : null}
            <Dialog
                open
                aria-labelledby="production-location-dialog-title"
                aria-describedby="production-location-dialog-description"
                PaperProps={{
                    style: {
                        top: isMobile ? '150px' : 'auto',
                    },
                }}
            >
                <div className={classes.modalContainerWrapper}>
                    <DialogTitle
                        id="production-location-dialog-title"
                        className={classes.titleContentStyle}
                    >
                        <p className={classes.titleInnerContentStyle}>
                            Thanks for adding data for this production location!
                        </p>
                        {!isMobile ? (
                            <ProductionLocationDialogCloseButton
                                handleShow={handleShow}
                                isMobile={isMobile}
                            />
                        ) : null}
                    </DialogTitle>
                    <DialogContent>
                        <Typography
                            variant="body1"
                            className={classes.dialogContentStyles}
                        >
                            Do you own or manage this location? If so, you can
                            now claim your production location to have a
                            complete, credible and confirmed profile with a
                            green banner and claimed badge. You’ll be able to
                            add more information, like contact details,
                            certifications, native language name, and more.
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
                                <ProductionLocationDialogFields
                                    fields={fields}
                                    startTo={fieldSetNumber}
                                    classes={classes}
                                />
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
                                        {osID ? (
                                            <Typography
                                                className={classes.osIDText}
                                            >
                                                {osID}
                                            </Typography>
                                        ) : null}
                                        <Chip
                                            label={startCase(
                                                toLower(moderationStatus),
                                            )}
                                            {...(moderationStatus ===
                                                MODERATION_STATUSES_ENUM.PENDING && {
                                                onDelete: () => {},
                                            })}
                                            className={`${
                                                classes.osIdStatusBadge
                                            } ${getStatusBadgeClass(
                                                classes,
                                                moderationStatus,
                                            )}`}
                                            deleteIcon={
                                                moderationStatus ===
                                                MODERATION_STATUSES_ENUM.PENDING ? (
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
                                                ) : null
                                            }
                                        />
                                    </Grid>
                                </Grid>
                                <ProductionLocationDialogFields
                                    fields={fields}
                                    startFrom={fieldSetNumber}
                                    classes={classes}
                                />
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
                                    history.push(
                                        searchByNameAndAddressResultRoute,
                                    );
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
        </>
    );
};

ProductionLocationDialog.defaultProps = {
    osID: null,
};

ProductionLocationDialog.propTypes = {
    data: object.isRequired,
    osID: string,
    moderationStatus: string.isRequired,
    handleShow: func.isRequired,
    classes: object.isRequired,
    theme: object.isRequired,
    innerWidth: number.isRequired,
};

export default withTheme()(
    withStyles(makeProductionLocationDialogStyles)(ProductionLocationDialog),
);
