import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsId from './SearchByOsId';
import { makeContributeProductionLocationStyles } from '../../util/styles';

const ContributeProductionLocation = ({ classes }) => {
    const [value, setValue] = useState(0);

    const handleChange = (event, v) => {
        setValue(v);
    };

    return (
        <div className={classes.mainContainer}>
            <Typography component="h1" variant="h1" className={classes.title}>
                Production Location Search
            </Typography>
            <div className={classes.tabsContainer}>
                <Tabs
                    value={value}
                    onChange={handleChange}
                    classes={{
                        root: classes.tabsRoot,
                        indicator: classes.tabsIndicator,
                    }}
                >
                    <Tab
                        classes={{
                            root: classes.tabRoot,
                            selected: classes.tabSelected,
                            labelContainer: classes.tabLabelContainer,
                        }}
                        label="Search by OS ID"
                    />
                    <Tab
                        classes={{
                            root: classes.tabRoot,
                            selected: classes.tabSelected,
                            labelContainer: classes.tabLabelContainer,
                        }}
                        label="Search by Name and Address"
                    />
                </Tabs>
                {value === 0 && <SearchByOsId />}
                {value === 1 && <div>Search by Name and Address</div>}
            </div>
        </div>
    );
};

export default withStyles(makeContributeProductionLocationStyles)(
    ContributeProductionLocation,
);
