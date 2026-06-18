import React from 'react';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';
import PeopleOutlineIcon from '@material-ui/icons/PeopleOutline';

import ContributionDate from '../../../../Shared/ContributionDate/ContributionDate';
import { pluralizeContributorType } from '../../utils';
import { LAST_CONTRIBUTED_LABEL } from '../PublicContributorsSection/constants';
import ANONYMIZED_SECTION_TITLE from './constants';
import anonymizedSectionStyles from './styles';

const AnonymizedSection = ({ classes, nonPublicContributors }) => (
    <Grid container>
        <Grid item container className={classes.anonymizedSection}>
            <PeopleOutlineIcon className={classes.anonymizedIcon} />
            <Typography className={classes.sectionLabel} component="p">
                {ANONYMIZED_SECTION_TITLE}
            </Typography>
        </Grid>
        <Grid item container className={classes.anonymizedList}>
            {nonPublicContributors.map((contributor, index) => (
                <React.Fragment key={contributor.contributor_type}>
                    <Typography
                        className={classes.anonymizedType}
                        component="p"
                    >
                        {contributor.count}{' '}
                        {pluralizeContributorType(
                            contributor.contributor_type,
                            contributor.count,
                        )}
                    </Typography>
                    <div className={classes.anonymizedDate}>
                        <Typography
                            className={classes.anonymizedDateLabel}
                            component="span"
                        >
                            {LAST_CONTRIBUTED_LABEL}:
                        </Typography>
                        <ContributionDate
                            date={contributor.last_contributed_at}
                        />
                    </div>
                    {index === nonPublicContributors.length - 1 ? null : (
                        <Divider />
                    )}
                </React.Fragment>
            ))}
        </Grid>
    </Grid>
);

export default withStyles(anonymizedSectionStyles)(AnonymizedSection);
