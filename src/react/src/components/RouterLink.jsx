import React from 'react';
import { Link } from 'react-router-dom';

const RouterLink = React.forwardRef((props, ref) => {
    const { to, ...other } = props;
    return <Link ref={ref} to={to} {...other} />;
});

export default RouterLink;
