import React from 'react';
import { string, node, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import learnMoreLinkStyles from './styles';
import { DEFAULT_LINK_TEXT } from './constants';

const LearnMoreLink = ({ href, children, classes }) => (
    <p className={classes.paragraph}>
        <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className={classes.link}
        >
            {children}
        </a>
    </p>
);

LearnMoreLink.propTypes = {
    href: string.isRequired,
    children: node,
    classes: shape({
        paragraph: string.isRequired,
        link: string.isRequired,
    }).isRequired,
};

LearnMoreLink.defaultProps = {
    children: DEFAULT_LINK_TEXT,
};

export default withStyles(learnMoreLinkStyles)(LearnMoreLink);
