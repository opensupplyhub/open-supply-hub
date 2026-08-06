import React from 'react';
import Typography from '@material-ui/core/Typography';
import ListIcon from '@material-ui/icons/List';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';

import { makeProfileRouteLink } from '../../../../../../util/util';
import ContributionDate from '../../../../Shared/ContributionDate/ContributionDate';
import { UPLOADED_VIA_LIST_LABEL, LAST_CONTRIBUTED_LABEL } from './constants';
import publicContributorsSectionStyles from './styles';

const PublicContributorsSection = ({ classes, publicContributors }) => (
    <>
        <div className={classes.contributorList}>
            {publicContributors.map(contributor => (
                <div key={contributor.id} className={classes.contributorEntry}>
                    <Link
                        to={makeProfileRouteLink(contributor.id)}
                        className={classes.contributorName}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {contributor.contributor_name}
                    </Link>
                    {contributor.contributor_type && (
                        <Typography
                            className={classes.contributorType}
                            component="p"
                        >
                            {contributor.contributor_type}
                        </Typography>
                    )}
                    {contributor.lists.length === 0 ? (
                        <div className={classes.lastContributed}>
                            <Typography
                                className={classes.lastContributedLabel}
                                component="span"
                            >
                                {LAST_CONTRIBUTED_LABEL}:
                            </Typography>
                            <ContributionDate
                                date={contributor.last_contributed_at}
                            />
                        </div>
                    ) : (
                        contributor.lists.map(list => (
                            <div
                                key={`${contributor.id}-${list.name}`}
                                className={classes.listEntry}
                            >
                                <Typography
                                    className={classes.listEntryLabel}
                                    component="p"
                                >
                                    <ListIcon className={classes.listIcon} />
                                    {UPLOADED_VIA_LIST_LABEL}
                                </Typography>
                                <Typography
                                    className={classes.listName}
                                    component="p"
                                >
                                    {list.name}
                                </Typography>
                                <div className={classes.listDate}>
                                    <ContributionDate date={list.uploaded_at} />
                                </div>
                            </div>
                        ))
                    )}
                </div>
            ))}
        </div>
    </>
);

export default withStyles(publicContributorsSectionStyles)(
    PublicContributorsSection,
);
