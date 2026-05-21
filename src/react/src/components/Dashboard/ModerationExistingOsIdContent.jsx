import React from 'react';
import { Link } from 'react-router-dom';
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
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Typography from '@material-ui/core/Typography';

import ModerationMatchConfirmButton from './ModerationMatchConfirmButton';
import { makeFacilityDetailLink } from '../../util/util';

const ModerationExistingOsIdContent = ({
    classes,
    location,
    moderation,
    actions,
    isDisabled,
}) => {
    if (location.fetching) {
        return <CircularProgress size={25} className={classes.loaderStyles} />;
    }

    if (location.data) {
        return (
            <List>
                <ListItem
                    className={`${classes.listItemStyle} ${classes.listItemStyle_confirmed}`}
                >
                    <div>
                        <ListItemText
                            className={classes.listItemTextStyle}
                            primary={
                                <Typography>
                                    OS ID:{' '}
                                    <Link
                                        to={makeFacilityDetailLink(
                                            location.data.os_id,
                                        )}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        {location.data.os_id}
                                    </Link>
                                </Typography>
                            }
                        />
                        <ListItemText
                            className={classes.listItemTextStyle}
                            primary={`Name: ${location.data.name}`}
                        />
                        <ListItemText
                            className={classes.listItemTextStyle}
                            primary={`Address: ${location.data.address}`}
                        />
                        <ListItemText
                            className={classes.listItemTextStyle}
                            primary={`Claimed Status: ${location.data.claim_status}`}
                        />
                    </div>
                    <ModerationMatchConfirmButton
                        classes={classes}
                        match={{
                            matchOsId: location.data.os_id,
                            eventOsId: location.data.os_id,
                        }}
                        moderation={moderation}
                        actions={actions}
                        isDisabled={isDisabled}
                        ariaLabel="Confirm existing OS ID button tooltip"
                    />
                </ListItem>
            </List>
        );
    }

    return (
        <div className={classes.emptyBlockStyles}>
            <Typography className={classes.emptyTextStyle} variant="title">
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
