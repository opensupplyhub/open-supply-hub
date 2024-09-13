import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsId from './SearchByOsId';

function TabContainer(props) {
    return (
        <Typography component="div" style={{ padding: 8 * 3 }}>
            {props.children}
        </Typography>
    );
}

TabContainer.propTypes = {
    children: PropTypes.node.isRequired,
};

const styles = theme => ({
    root: {
        flexGrow: 1,
        backgroundColor: theme.palette.background.paper,
    },
});
// const osId = 'OS ID';
// const nameAndCountry = 'name and country';

const ContributeProductionLocation = ({ classes }) => {
    const [value, setValue] = useState(0);

    const handleChange = (event, v) => {
        setValue(v);
    };

    return (
        <>
            <Typography component="h1" variant="h1" gutterBottom>
                Production Location Search
            </Typography>
            <div className={classes.root}>
                <Tabs value={value} onChange={handleChange}>
                    <Tab label="Search by OS ID" />
                    <Tab label="Search by Name and Address" />
                </Tabs>
                {/* <p>
                    Enter the full name and country to search for a matching
                    profile. Use the field below and click “search”.
                </p> */}
                {value === 0 && <SearchByOsId />}
                {value === 1 && <TabContainer>Item Two</TabContainer>}
            </div>
        </>
    );
};

ContributeProductionLocation.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(ContributeProductionLocation);
