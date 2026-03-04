import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import learnMoreLinkStyles from './styles';

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
    href: PropTypes.string.isRequired,
    children: PropTypes.node,
    classes: PropTypes.shape({
        paragraph: PropTypes.string.isRequired,
        link: PropTypes.string.isRequired,
    }).isRequired,
};

LearnMoreLink.defaultProps = {
    children: 'Learn more →',
};

export default withStyles(learnMoreLinkStyles)(LearnMoreLink);
