import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Typography from '@material-ui/core/Typography';

/* Apply conditional rendering for each link item */
const navBarStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            marginBottom: theme.spacing.unit,
        }),
    });

const NavBar = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Jump to
        </Typography>
        <MenuList>
            <MenuItem>
                <Link href="#overview">Overview</Link>
            </MenuItem>
            <MenuItem>
                <Link href="#location">Location</Link>
            </MenuItem>
            <MenuItem>
                <Link href="#claimed_data">Claimed data</Link>
            </MenuItem>
            <MenuItem>
                <Link href="#assessments">Assessments and Audits</Link>
            </MenuItem>
            <MenuItem>
                <Link href="#certifications">Certifications</Link>
            </MenuItem>
            <MenuItem>
                <Link href="#emissions">Emissions</Link>
            </MenuItem>
            <MenuItem>
                <Link href="#living_wage">Living Wage</Link>
            </MenuItem>
            <MenuItem>
                <Link href="#grievance">Grievance Mechanism</Link>
            </MenuItem>
        </MenuList>
    </div>
);

export default withStyles(navBarStyles)(NavBar);
