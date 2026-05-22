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
import { Link } from 'react-router-dom';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Typography from '@material-ui/core/Typography';

import ModerationMatchConfirmButton from './ModerationMatchConfirmButton';
import { makeFacilityDetailLink } from '../../util/util';

const ModerationLocationMatchListItem = ({
    classes,
    location,
    match,
    moderation,
    actions,
    isDisabled,
    isConfirmed,
    confirmAriaLabel,
}) => (
    <ListItem
        data-testid="moderation-location-match-list-item"
        className={
            isConfirmed
                ? `${classes.listItemStyle} ${classes.listItemStyle_confirmed}`
                : classes.listItemStyle
        }
    >
        <div>
            <ListItemText
                data-testid="moderation-location-match-osid"
                className={classes.listItemTextStyle}
                primary={
                    <Typography>
                        OS ID:{' '}
                        <Link
                            data-testid="moderation-location-match-osid-link"
                            to={makeFacilityDetailLink(location.osId)}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {location.osId}
                        </Link>
                    </Typography>
                }
            />
            <ListItemText
                data-testid="moderation-location-match-name"
                className={classes.listItemTextStyle}
                primary={`Name: ${location.name}`}
            />
            <ListItemText
                data-testid="moderation-location-match-address"
                className={classes.listItemTextStyle}
                primary={`Address: ${location.address}`}
            />
            <ListItemText
                data-testid="moderation-location-match-claim-status"
                className={classes.listItemTextStyle}
                primary={`Claimed Status: ${location.claimStatus}`}
            />
        </div>
        <ModerationMatchConfirmButton
            classes={classes}
            match={match}
            moderation={moderation}
            actions={actions}
            isDisabled={isDisabled}
            ariaLabel={confirmAriaLabel}
        />
    </ListItem>
);

ModerationLocationMatchListItem.propTypes = {
    classes: object.isRequired,
    location: shape({
        osId: string.isRequired,
        name: string,
        address: string,
        claimStatus: string,
    }).isRequired,
    match: shape({
        matchOsId: string.isRequired,
        eventOsId: oneOfType([string, oneOf([null])]),
    }).isRequired,
    moderation: shape({
        status: string.isRequired,
        fetching: bool.isRequired,
    }).isRequired,
    actions: shape({
        confirmPotentialMatch: func.isRequired,
    }).isRequired,
    isDisabled: bool.isRequired,
    isConfirmed: bool.isRequired,
    confirmAriaLabel: string.isRequired,
};

export default ModerationLocationMatchListItem;
