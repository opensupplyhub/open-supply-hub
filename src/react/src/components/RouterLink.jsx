import React from 'react';
import { Link } from 'react-router-dom';
import { oneOfType, string, object } from 'prop-types';

const RouterLink = React.forwardRef((props, ref) => {
    const { to, ...other } = props;
    return <Link ref={ref} to={to} {...other} />;
});

RouterLink.propTypes = {
    to: oneOfType([string, object]).isRequired,
};

export default RouterLink;
