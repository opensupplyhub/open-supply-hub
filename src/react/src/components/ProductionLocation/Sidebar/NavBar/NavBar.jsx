import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Typography from '@material-ui/core/Typography';

import navBarStyles from './styles';

const NavBar = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Jump to
        </Typography>
        <MenuList>
            <MenuItem>
                <Link to="#overview">Overview</Link>
            </MenuItem>
            <MenuItem>
                <Link to="#location">Location</Link>
            </MenuItem>
            <MenuItem>
                <Link to="#claimed_data">Claimed data</Link>
            </MenuItem>
            <MenuItem>
                <Link to="#assessments">Assessments and Audits</Link>
            </MenuItem>
            <MenuItem>
                <Link to="#certifications">Certifications</Link>
            </MenuItem>
            <MenuItem>
                <Link to="#emissions">Emissions</Link>
            </MenuItem>
            <MenuItem>
                <Link to="#living_wage">Living Wage</Link>
            </MenuItem>
            <MenuItem>
                <Link to="#grievance">Grievance Mechanism</Link>
            </MenuItem>
        </MenuList>
    </div>
);

export default withStyles(navBarStyles)(NavBar);
