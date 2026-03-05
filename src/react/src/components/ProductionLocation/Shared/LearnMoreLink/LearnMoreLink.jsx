import React from 'react';
import { string, node, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import learnMoreLinkStyles from './styles';
import DEFAULT_LINK_TEXT from './constants';

const LearnMoreLink = ({ href, children, classes }) => (
    <div className={classes.linkContainer}>
        <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className={classes.link}
        >
            {children}
        </a>
    </div>
);

LearnMoreLink.propTypes = {
    href: string.isRequired,
    children: node,
    classes: object.isRequired,
};

LearnMoreLink.defaultProps = {
    children: DEFAULT_LINK_TEXT,
};

export default withStyles(learnMoreLinkStyles)(LearnMoreLink);
