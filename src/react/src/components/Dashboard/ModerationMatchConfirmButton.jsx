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
import Button from '@material-ui/core/Button';

import DialogTooltip from './../Contribute/DialogTooltip';
import { MODERATION_STATUSES_ENUM } from '../../util/constants';

const confirmPotentialMatchButtonTitle = 'Confirm';
const matchedTitle = 'Matched';

const ModerationMatchConfirmButton = ({
    classes,
    match,
    moderation,
    actions: { confirmPotentialMatch },
    isDisabled,
    ariaLabel,
}) => {
    if (!isDisabled) {
        return (
            <Button
                color="secondary"
                variant="contained"
                className={classes.confirmButtonStyles}
                disabled={moderation.fetching}
                onClick={() => confirmPotentialMatch(match.matchOsId)}
            >
                {confirmPotentialMatchButtonTitle}
            </Button>
        );
    }

    const { eventOsId, matchOsId } = match;
    const isMatched =
        eventOsId === matchOsId &&
        moderation.status === MODERATION_STATUSES_ENUM.APPROVED;

    return (
        <DialogTooltip
            text={
                isMatched
                    ? 'Moderation event data has been already matched to this production location.'
                    : `You can't confirm the match when moderation event is ${moderation.status.toLowerCase()}.`
            }
            aria-label={ariaLabel}
            childComponent={
                <span className={classes.claimTooltipWrapper}>
                    <Button
                        color="secondary"
                        variant="contained"
                        className={classes.confirmButtonStyles}
                        disabled
                    >
                        {isMatched
                            ? matchedTitle
                            : confirmPotentialMatchButtonTitle}
                    </Button>
                </span>
            }
        />
    );
};

ModerationMatchConfirmButton.propTypes = {
    classes: object.isRequired,
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
    ariaLabel: string.isRequired,
};

export default ModerationMatchConfirmButton;
