import React from 'react';
import Typography from '@material-ui/core/Typography';
import ListIcon from '@material-ui/icons/List';
import OpenInNewIcon from '@material-ui/icons/OpenInNew';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';

import { makeProfileRouteLink } from '../../../../../../util/util';
import UPLOADED_VIA_LIST_LABEL from './constants';
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
                        <OpenInNewIcon
                            className={classes.contributorNameIcon}
                            aria-hidden
                        />
                    </Link>
                    {contributor.contributor_type && (
                        <Typography
                            className={classes.contributorType}
                            component="p"
                        >
                            {contributor.contributor_type}
                        </Typography>
                    )}
                    {contributor.list_names &&
                        contributor.list_names
                            .map((name, i) => ({
                                name,
                                key: `${contributor.id}-${i}`,
                            }))
                            .filter(({ name }) => name)
                            .map(({ name: listName, key }) => (
                                <div key={key} className={classes.listEntry}>
                                    <Typography
                                        className={classes.listEntryLabel}
                                        component="p"
                                    >
                                        <ListIcon
                                            className={classes.listIcon}
                                        />
                                        {UPLOADED_VIA_LIST_LABEL}
                                    </Typography>
                                    <Typography
                                        className={classes.listName}
                                        component="p"
                                    >
                                        {listName}
                                    </Typography>
                                </div>
                            ))}
                </div>
            ))}
        </div>
    </>
);

export default withStyles(publicContributorsSectionStyles)(
    PublicContributorsSection,
);
