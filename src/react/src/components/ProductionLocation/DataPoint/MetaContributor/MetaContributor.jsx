import React from 'react';
import { object, string, oneOfType, number } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import PersonIcon from '@material-ui/icons/PersonOutline';

import { profileRoute } from '../../../../util/constants';
import metaContributorStyles from './styles';

const MetaContributor = ({ classes, contributorName, userId }) => (
    <span className={classes.root} data-testid="data-point-contributor">
        <PersonIcon fontSize="small" className={classes.personIcon} />
        {userId != null ? (
            <Link
                to={profileRoute.replace(':id', String(userId))}
                className={`${classes.name} ${classes.nameLink}`}
                target="_blank"
                rel="noopener noreferrer"
            >
                {contributorName}
            </Link>
        ) : (
            <Typography
                variant="body2"
                component="span"
                className={classes.name}
            >
                {contributorName}
            </Typography>
        )}
    </span>
);

MetaContributor.propTypes = {
    classes: object.isRequired,
    contributorName: string.isRequired,
    userId: oneOfType([string, number]),
};

MetaContributor.defaultProps = {
    userId: null,
};

export default withStyles(metaContributorStyles)(MetaContributor);
