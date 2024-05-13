import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';

import GroupIcon from './GroupIcon';

const showContributorsButtonStyles = theme =>
    Object.freeze({
        button: {
            fontWeight: 500,
            fontSize: '18px',
            lineHeight: '21px',
            textTransform: 'none',
            padding: 0,
        },
        buttonText: {
            paddingLeft: theme.spacing.unit,
        },
    });

const FacilityDetailsShowContributorsButton = ({
    classes,
    publicContributorsNum,
    onOpen,
}) => {
    const buttonText = () => {
        if (publicContributorsNum) {
            if (publicContributorsNum === 1) {
                return '1 current contributor has uploaded data for this facility';
            }
            return `${publicContributorsNum} current contributors have uploaded data for this facility`;
        }
        return 'Contributors that have uploaded data for this facility';
    };

    return (
        <Button color="primary" className={classes.button} onClick={onOpen}>
            <GroupIcon />{' '}
            <span className={classes.buttonText}>{buttonText()}</span>
        </Button>
    );
};
export default withStyles(showContributorsButtonStyles)(
    FacilityDetailsShowContributorsButton,
);
