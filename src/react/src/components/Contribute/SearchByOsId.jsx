import React from 'react';
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
            textTransform: 'none',
            fontWeight: 'bold',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(theme.palette.action.main),
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
    });

const SearchByOsId = ({ classes }) => {
    console.log('classes >>>', classes);
    const helperText = () => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <InfoOutlinedIcon
                style={{ fontSize: 16, verticalAlign: 'middle' }}
            />
            <Typography>
                To search you need to enter the full ID production location
            </Typography>
        </div>
    );

    return (
        <div>
            <Typography>
                Enter the full name and country to search for a matching
                profile. Use the field below and click “search”.
            </Typography>
            <Paper
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '0 50px 50px 50px',
                    width: '100%',
                    background: '#FFFFFF',
                }}
            >
                <Typography component="h2" variant="h1" gutterBottom>
                    Know the OS ID for your location?
                </Typography>
                <Typography>
                    If you know the OS ID for your production location enter it
                    below, otherwise select the “Search by Name and Address”
                    tab.
                </Typography>
                <TextField
                    id="osId"
                    helperText={helperText()}
                    placeholder="Enter the OS ID"
                    variant="outlined"
                />
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => console.log('Search by ID')}
                    className={classes.buttonStyles}
                    // disabled={!stepInputIsValid(formData)}
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
