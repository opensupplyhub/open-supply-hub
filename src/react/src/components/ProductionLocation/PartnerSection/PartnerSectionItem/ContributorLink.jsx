import React from 'react';
import moment from 'moment';
import { withStyles } from '@material-ui/core/styles';
import styles from './styles';

function ContributorLink({ classes, ...props }) {
    return (
        <>
            {moment(props.created_at).format('LL')} by{' '}
            <a
                href={`/profile/${props.contributor_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className={classes.contributorLink}
            >
                {props.contributor_name}
            </a>
        </>
    );
}

export default withStyles(styles)(ContributorLink);
