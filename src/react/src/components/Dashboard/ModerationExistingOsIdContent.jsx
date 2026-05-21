import React from 'react';
import {
    bool,
    func,
    object,
    oneOf,
    oneOfType,
    shape,
    string,
} from 'prop-types';
import CircularProgress from '@material-ui/core/CircularProgress';
import List from '@material-ui/core/List';
import Typography from '@material-ui/core/Typography';

import ModerationLocationMatchListItem from './ModerationLocationMatchListItem';

const ModerationExistingOsIdContent = ({
    classes,
    location,
    moderation,
    actions,
    isDisabled,
}) => {
    if (location.fetching) {
        return (
            <CircularProgress
                data-testid="moderation-existing-osid-loader"
                size={25}
                className={classes.loaderStyles}
            />
        );
    }

    if (location.data) {
        return (
            <List>
                <ModerationLocationMatchListItem
                    classes={classes}
                    location={{
                        osId: location.data.os_id,
                        name: location.data.name,
                        address: location.data.address,
                        claimStatus: location.data.claim_status,
                    }}
                    match={{
                        matchOsId: location.data.os_id,
                        eventOsId: location.data.os_id,
                    }}
                    moderation={moderation}
                    actions={actions}
                    isDisabled={isDisabled}
                    isConfirmed
                    confirmAriaLabel="Confirm existing OS ID button tooltip"
                />
            </List>
        );
    }

    return (
        <div
            data-testid="moderation-existing-osid-empty-state"
            className={classes.emptyBlockStyles}
        >
            <Typography
                data-testid="moderation-existing-osid-empty-text"
                className={classes.emptyTextStyle}
                variant="title"
            >
                Existing location not found
            </Typography>
        </div>
    );
};

ModerationExistingOsIdContent.propTypes = {
    classes: object.isRequired,
    location: shape({
        fetching: bool.isRequired,
        data: oneOfType([
            oneOf([null]),
            shape({
                os_id: string.isRequired,
                name: string,
                address: string,
                claim_status: string,
            }),
        ]),
    }).isRequired,
    moderation: shape({
        status: string.isRequired,
        fetching: bool.isRequired,
    }).isRequired,
    actions: shape({
        confirmPotentialMatch: func.isRequired,
    }).isRequired,
    isDisabled: bool.isRequired,
};

export default ModerationExistingOsIdContent;
