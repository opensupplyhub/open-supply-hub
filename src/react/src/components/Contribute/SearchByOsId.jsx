import React, { useState } from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';

const searchByOsIdStyles = theme =>
    Object.freeze({
        buttonStyles: Object.freeze({
            width: '200px',
            borderRadius: '0',
            textTransform: 'none',
            fontWeight: 'bold',
            backgroundColor: theme.palette.action.main,
            marginTop: '26px',
            color: theme.palette.getContrastText(theme.palette.action.main),
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
        searchInputRoot: Object.freeze({}),
        searchInput: Object.freeze({
            fontSize: '18px',
            fontWeight: '600',
            lineHeight: '22px',
            padding: '16px',
        }),
        notchedOutline: Object.freeze({
            borderRadius: 0,
        }),
    });

const helperText = () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <InfoOutlinedIcon style={{ fontSize: 16, verticalAlign: 'middle' }} />
        <Typography
            style={{
                fontSize: '16px',
                fontWeight: '600',
                color: '#6E707E',
            }}
        >
            To search you need to enter the full ID production location
        </Typography>
    </div>
);

const SearchByOsId = ({ classes }) => {
    const [value, setValue] = useState('');

    const handleChange = event => {
        const uppercaseValue = event.target.value.toUpperCase();
        setValue(uppercaseValue);
    };

    return (
        <div>
            <Typography
                style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    margin: '24px 0 32px 0',
                }}
            >
                Enter the full OS ID to search for a matching profile. Use the
                field below and click “search”.
            </Typography>
            <Paper
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '40px 110px',
                    borderRadius: '0',
                    boxShadow: 'none',
                }}
            >
                <Typography
                    component="h2"
                    variant="h2"
                    style={{
                        fontSize: '36px',
                        fontWeight: '700',
                    }}
                >
                    Know the OS ID for your location?
                </Typography>
                <Typography
                    style={{
                        fontSize: '21px',
                        fontWeight: '600',
                        margin: '8px 0 24px 0',
                    }}
                >
                    If you know the OS ID for your production location enter it
                    below, otherwise select the “Search by Name and Address”
                    tab.
                </Typography>
                <TextField
                    id="osId"
                    style={{
                        maxWidth: '528px',
                    }}
                    value={value}
                    onChange={handleChange}
                    helperText={helperText()}
                    placeholder="Enter the OS ID"
                    variant="outlined"
                    InputProps={{
                        classes: {
                            input: classes.searchInput,
                            root: classes.searchInputRoot,
                            notchedOutline: classes.notchedOutline,
                        },
                        inputProps: {
                            maxLength: 15,
                        },
                    }}
                />
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => console.log('Search by ID >>>')}
                    className={classes.buttonStyles}
                    disabled={value.length < 15}
                >
                    Search by ID
                </Button>
            </Paper>
        </div>
    );
};

const mapStateToProps = () => ({
    // formData: state.form.formData,
});

const mapDispatchToProps = () => ({
    // updateFormData: data => dispatch(updateFormData(data)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(searchByOsIdStyles)(SearchByOsId));
