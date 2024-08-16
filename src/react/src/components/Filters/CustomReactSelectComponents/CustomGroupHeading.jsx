import React from 'react';
import { components } from 'react-select';
import { withStyles } from '@material-ui/core/styles';
import ButtonBase from '@material-ui/core/ButtonBase';
import IconButton from '@material-ui/core/IconButton';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { makeCustomGroupHeadingStyles } from '../../../util/styles';

const CustomGroupHeading = props => {
    const { data, selectProps, classes } = props;
    const {
        expandedGroups,
        setExpandedGroups,
        selectedOptions,
        setSelectedOptions,
        setMenuIsOpen,
    } = selectProps;
    const isExpanded = expandedGroups.includes(data.label);

    const handleClick = () => {
        if (isExpanded) {
            setExpandedGroups(
                expandedGroups.filter(label => label !== data.label),
            );
        } else {
            setExpandedGroups([...expandedGroups, data.label]);
        }
    };

    const handleGroupSelect = () => {
        const groupOptions = data.options.map(option => option.value);
        const newSelectedOptions = [
            ...selectedOptions.filter(opt => !groupOptions.includes(opt.value)),
            ...data.options,
        ];
        setSelectedOptions(newSelectedOptions);
        setMenuIsOpen(false);
    };

    return (
        <components.GroupHeading {...props}>
            <IconButton
                onClick={handleClick}
                className={classes.groupHeadingIconButton}
            >
                {isExpanded ? <ExpandMoreIcon /> : <ChevronRightIcon />}
            </IconButton>
            <ButtonBase
                onClick={handleGroupSelect}
                className={classes.groupHeadingButtonBase}
            >
                {data.label}
            </ButtonBase>
        </components.GroupHeading>
    );
};

export default withStyles(makeCustomGroupHeadingStyles)(CustomGroupHeading);
